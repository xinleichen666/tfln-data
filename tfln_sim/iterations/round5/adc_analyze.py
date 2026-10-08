import json,numpy as np,matplotlib;matplotlib.use("Agg");import matplotlib.pyplot as plt
R=json.load(open("singles.json")); S=json.load(open("super.json"))
lams=[1.45,1.5,1.55,1.6,1.65]
def te_sorted(n,te): return sorted([a for a,b in zip(n,te) if b>0.9],reverse=True)
def nTE0(w,l):
    pts=sorted((r[0],te_sorted(r[2],r[3])[0]) for r in R if r[1]==l and r[0]<2); x,y=zip(*pts); return np.interp(w,x,y)
nTE1w={l:te_sorted(*[r for r in R if r[0]==2.6 and r[1]==l][0][2:])[1] for l in lams}
nTE0w={l:te_sorted(*[r for r in R if r[0]==2.6 and r[1]==l][0][2:])[0] for l in lams}
out={}
for gap in [0.4,0.6,0.8]:
    rows=[]
    for l in lams:
        s=[r for r in S if r["gap"]==gap and r["lam"]==l and r["wn"]==1.21][0]
        split=s["neff"][1]-s["neff"][2]; dn=nTE1w[l]-nTE0(1.21,l)
        kn=np.sqrt(max(split**2-dn**2,1e-12))/2      # kappa in index units
        rows.append(dict(lam=l,split=split,dn=dn,kn=kn))
    k0=2*np.pi/1.55; kap=k0*rows[2]["kn"]; Lc=np.pi/(2*kap)
    # ADC (uniform, L=Lc) and TE0 crosstalk
    lam_f=np.linspace(1.45,1.65,81)
    kn_f=np.interp(lam_f,lams,[r["kn"] for r in rows]); dn_f=np.interp(lam_f,lams,[r["dn"] for r in rows])
    K=2*np.pi/lam_f*kn_f; D=np.pi/lam_f*dn_f
    Pc=K**2/(K**2+D**2)*np.sin(np.sqrt(K**2+D**2)*Lc)**2
    # TE0 (through) crosstalk into narrow arm: TE0 wide vs TE0 narrow mismatch, coupling ~ same kappa (upper bound)
    dn0=np.array([nTE0w[l]-nTE0(1.21,l) for l in lams]); D0=np.pi/lam_f*np.interp(lam_f,lams,dn0)
    X0=K**2/(K**2+D0**2)*np.sin(np.sqrt(K**2+D0**2)*Lc)**2
    # adiabatic ADC: narrow arm tapered across match: LZ with alpha = d(dn)/dw_n
    slope=(nTE0(1.31,1.55)-nTE0(1.11,1.55))/0.2
    span=0.4; L_ad99=np.log(100)*1.55*slope*span/(np.pi**2*(2*rows[2]["kn"])**2)
    out[gap]=dict(rows=rows,Lc_um=Lc,Pc_min_1450_1650=float(Pc.min()),bw_Pc95_nm=float(1000*(lam_f[Pc>0.95].max()-lam_f[Pc>0.95].min())) if (Pc>0.95).any() else 0,
                  TE0_xtalk_max_dB=float(10*np.log10(X0.max())),L_adiabatic99_um=float(L_ad99),slope=slope)
    plt.plot(lam_f*1000,10*np.log10(Pc),label=f"ADC gap {gap} µm, L={Lc:.0f} µm")
plt.ylim(-6,0.2);plt.xlabel("λ (nm)");plt.ylabel("TE1→TE0 (narrow) coupling (dB)");plt.legend();plt.grid(alpha=.3);plt.savefig("adc_spectrum.png",dpi=150)
json.dump(out,open("adc_results.json","w"),indent=1,default=float)
for g,o in out.items(): print(g,{k:(round(v,4) if isinstance(v,float) else v) for k,v in o.items() if k!="rows"}); print([ (r["lam"],round(r["dn"],4),round(r["kn"],4)) for r in o["rows"]])
