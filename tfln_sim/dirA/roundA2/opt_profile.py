"""Optimise taper profile z(w) (monotone, 6 knots) for min worst-case conversion loss over 1500-1600 nm at fixed L."""
import sys,pickle,json,numpy as np; sys.path.insert(0,"..")
from scipy.optimize import minimize
import eme
Ds={l:pickle.load(open(f"D_{l}.pkl","rb")) for l in [1.5,1.55,1.6]}; W=Ds[1.55]["W"]; nW=len(W)
def prof(p):
    d=np.exp(np.concatenate([[0],p])); cz=np.concatenate([[0],np.cumsum(d)]); cz/=cz[-1]
    kn=np.linspace(0,1,len(cz)); return np.interp(np.linspace(0,1,nW),kn,cz)
def cost(p,L):
    z=prof(p); return max(1-(lambda a:a[1]/a.sum())(eme.propagate(Ds[l],z,L)) for l in Ds)
res={}
for L in [200,300,400,500,700,900]:
    best=None
    for seed in range(4):
        p0=np.random.default_rng(seed).normal(0,0.5,7)
        r=minimize(cost,p0,args=(L,),method="Nelder-Mead",options=dict(maxiter=600,xatol=1e-3,fatol=1e-5))
        if best is None or r.fun<best.fun: best=r
    res[L]=dict(worst_loss=float(best.fun),eta_min=float(1-best.fun),p=best.x.tolist())
    print(L,"worst-case eta over 1500-1600:",round(1-best.fun,4),flush=True)
    json.dump(res,open("opt_profile.json","w"))
