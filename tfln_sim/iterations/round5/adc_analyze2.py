import json,numpy as np,matplotlib;matplotlib.use("Agg");import matplotlib.pyplot as plt
R=json.load(open("singles.json")); S=json.load(open("super.json"))+json.load(open("super2.json"))
lams=[1.45,1.5,1.55,1.6,1.65]
ts=lambda n,t: sorted([a for a,b in zip(n,t) if b>0.9],reverse=True)
def nTE0(w,l):
    pts=sorted(set((r[0],ts(r[2],r[3])[0]) for r in R if r[1]==l and r[0]<1.7)); x,y=zip(*pts); return np.interp(w,x,y)
def wide(W,l): r=[r for r in R if r[0]==W and r[1]==l][0]; return r[2][0],r[2][1]
lam_f=np.linspace(1.45,1.65,81); out={}
plt.figure(figsize=(6,4))
for W,wn,gap in [(2.6,1.21,0.4),(2.6,1.21,0.6),(2.2,1.006,0.3),(2.2,1.006,0.4)]:
    rows=[]
    for l in lams:
        s=[r for r in S if r.get("W",2.6)==W and r["gap"]==gap and r["lam"]==l and abs(r["wn"]-wn)<1e-6][0]
        # supermodes: the pair nearest TE1wide
        t1=wide(W,l)[1]; n=sorted(s["neff"],key=lambda a:abs(a-t1))[:2]; split=abs(n[0]-n[1])
        dn=t1-nTE0(wn,l); kn=np.sqrt(max(split**2-dn**2,1e-12))/2
        dn0=wide(W,l)[0]-nTE0(wn,l); rows.append(dict(lam=l,split=split,dn=dn,kn=kn,dn0=dn0))
    kap=2*np.pi/1.55*rows[2]["kn"]; Lc=np.pi/(2*kap)
    K=2*np.pi/lam_f*np.interp(lam_f,lams,[r["kn"] for r in rows]); D=np.pi/lam_f*np.interp(lam_f,lams,[r["dn"] for r in rows])
    Pc=K**2/(K**2+D**2)*np.sin(np.sqrt(K**2+D**2)*Lc)**2
    D0=np.pi/lam_f*np.interp(lam_f,lams,[r["dn0"] for r in rows]); X0=K**2/(K**2+D0**2)*np.sin(np.sqrt(K**2+D0**2)*Lc)**2
    m=Pc>0.95; key=f"W{W}_wn{wn}_gap{gap}"
    out[key]=dict(Lc_um=float(Lc),Pc_min=float(Pc.min()),bw95_nm=float(1000*(lam_f[m].max()-lam_f[m].min())) if m.any() else 0.0,
                  bw90_nm=float(1000*np.ptp(lam_f[Pc>0.9])) if (Pc>0.9).any() else 0.0,TE0_xtalk_max_dB=float(10*np.log10(X0.max())),rows=rows,
                  Pc=Pc.tolist())
    plt.plot(lam_f*1000,10*np.log10(Pc),label=f"W={W}, w_n={wn}, gap={gap}: L={Lc:.0f} µm")
plt.ylim(-3,0.1);plt.xlabel("λ (nm)");plt.ylabel("TE1→TE0 transfer (dB)");plt.legend(fontsize=7);plt.grid(alpha=.3);plt.tight_layout();plt.savefig("adc_spectrum.png",dpi=150)
json.dump({"lam":lam_f.tolist(),**out},open("adc_results.json","w"),indent=1,default=float)
for k,o in out.items(): print(k,{a:round(b,3) for a,b in o.items() if a not in("rows","Pc")})
