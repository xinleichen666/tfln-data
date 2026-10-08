import sys,pickle,glob,json,numpy as np,matplotlib;matplotlib.use("Agg");import matplotlib.pyplot as plt
sys.path.insert(0,"/workspace/tfln_sim/iterations"); import eme
d=sys.argv[1]; Ds={float(f.split("_")[-1][:-4]):pickle.load(open(f,"rb")) for f in sorted(glob.glob(f"{d}/D_*.pkl"))}
k0=int(sys.argv[2]) if len(sys.argv)>2 else 0
k1=int(sys.argv[3]) if len(sys.argv)>3 else None
tag=sys.argv[4] if len(sys.argv)>4 else ""
for l,D in Ds.items():
    e=None if k1 is None else k1+1
    D["W"]=D["W"][k0:e];D["neff"]=D["neff"][k0:e];D["te"]=D["te"][k0:e];D["T"]=D["T"][k0:(None if k1 is None else k1)]
lams=sorted(Ds); D0=Ds[1.55]; nW=len(D0["W"])
def ca_profile(D,inp=1):
    # constant adiabaticity: dz_k ∝ sum_j |T_kj|/|dn_ij| for coupling out of adiabatic mode inp
    c=[]
    for k in range(nW-1):
        dn=np.abs((D["neff"][k]+D["neff"][k+1])/2-((D["neff"][k][inp]+D["neff"][k+1][inp])/2))
        t=np.abs(D["T"][k][:,inp]); s=t[inp+1]/max(dn[inp+1],1e-3)+1e-3*0
        c.append(s)
    c=np.array(c); c=c+0.15*c.mean(); z=np.concatenate([[0],np.cumsum(c)]); return z/z[-1]
lin=np.linspace(0,1,nW); ca=ca_profile(D0)
Ls=np.round(np.geomspace(10,600,70),1); res={}
for name,zf in [("linear",lin),("const-adiabatic",ca)]:
    res[name]={lam:[float((lambda p:p[1]/p.sum())(eme.propagate(Ds[lam],zf,L))) for L in Ls] for lam in lams}
    res[name+"_TE0"]={lam:[float((lambda p:p[0]/p.sum())(eme.propagate(Ds[lam],zf,L,inp=0))) for L in Ls] for lam in lams}
def Lmin(name,th=0.99):
    for i,L in enumerate(Ls):
        if all(min(res[name][l][i:]) >= th for l in lams): return float(L)
out={n:{"L99_all_lams":Lmin(n),"L95_all_lams":Lmin(n,0.95),"L99_1550":next((float(L) for i,L in enumerate(Ls) if min(res[n][1.55][i:])>=0.99),None)} for n in ["linear","const-adiabatic"]}
out["lams"]=lams; out["Ls"]=Ls.tolist(); out["res"]={k:{str(l):v for l,v in vv.items()} for k,vv in res.items()}
out["W"]=D0["W"].tolist(); out["ca_profile"]=ca.tolist()
json.dump(out,open(f"{d}/eme_results{tag}.json","w"))
fig,ax=plt.subplots(1,3,figsize=(15,4))
for name,ls in [("linear","--"),("const-adiabatic","-")]:
    for l in lams: ax[0].semilogx(Ls,1-np.array(res[name][l]),ls,label=f"{name} {l*1000:.0f} nm")
ax[0].set_yscale("log");ax[0].set_ylim(1e-4,1);ax[0].set_xlabel("taper length L (µm)");ax[0].set_ylabel("1 − η(TM0→TE1)");ax[0].legend(fontsize=6)
ax[1].plot(lin,D0["W"],"--",label="linear");ax[1].plot(ca,D0["W"],label="const-adiabatic");ax[1].set_xlabel("z/L");ax[1].set_ylabel("w (µm)");ax[1].legend()
for i in range(4): ax[2].scatter(D0["W"],D0["neff"][:,i],c=D0["te"][:,i],cmap="coolwarm",vmin=0,vmax=1,s=8)
ax[2].set_xlabel("w (µm)");ax[2].set_ylabel("neff @1550")
fig.tight_layout();fig.savefig(f"{d}/eme_taper{tag}.png",dpi=150)
print(json.dumps({k:out[k] for k in ["linear","const-adiabatic"]}))
