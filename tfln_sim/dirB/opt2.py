import clib as C,numpy as np,os,json,sys
from scipy.optimize import minimize
C.SUB=3; C.DATA=os.environ.get("DATA","data")
ws,we,L=float(sys.argv[1]),float(sys.argv[2]),float(sys.argv[3])
av=[(c,l) for c in C.CORNERS for l in C.LAMS if os.path.exists(f"{C.DATA}/{c}_{l}.pkl")]
D0=C.load("nom",1.55); WN=D0["WN"][C.idx(D0,ws):C.idx(D0,we)+1]
Cs=np.array([C.adiab(C.load(c,l),ws,we) for c,l in av]); base=np.sqrt(Cs.max(0))
knots=np.linspace(ws,we,7); mid=0.5*(WN[1:]+WN[:-1])
def prof(x):
    w=base*np.exp(np.interp(mid,knots,x)); z=np.concatenate([[0],np.cumsum(w)]); return z/z[-1]
def run1(c,l,z):
    C.ADIAB_ENDS=True; D=C.load(c,l)
    # only TE1w source
    return C.run(D,ws,we,z,L)["TE1w->TE0n"]
def f(x):
    z=prof(x); r=[1-run1(c,l,z) for c,l in av]; return 10*np.log10(max(r))
x0=np.zeros(7); print("start",f(x0),flush=True)
res=minimize(f,x0,method="Nelder-Mead",options=dict(maxiter=120,xatol=1e-3,fatol=1e-3))
print("best",res.fun,res.x.tolist(),flush=True)
json.dump(dict(ws=ws,we=we,L=L,x=res.x.tolist(),f=res.fun,knots=knots.tolist(),zf=prof(res.x).tolist(),WN=WN.tolist(),corners=av),open(f"opt_{C.DATA}_{ws}_{we}_{int(L)}.json","w"))
