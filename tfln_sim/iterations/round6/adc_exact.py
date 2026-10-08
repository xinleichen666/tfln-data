"""Exact (supermode-expansion) ADC transfer: isolated-arm modes projected on coupled supermodes.
Gives TE1(wide)->TE0(narrow), TE0(wide)->TE0(narrow) crosstalk, TE0(wide)->TE0(wide) through."""
import sys,os,json,numpy as np; os.environ["OMP_NUM_THREADS"]="1"; sys.path.insert(0,"/workspace/tfln_sim/iterations")
from multiprocessing import Pool
import psrlib as P
kw0=dict(orient="XcutZ",H=0.6,etch=0.3,angle=60,clad="air")
def fields(W,wn,gap,lam,only,nm,kw,dx=0.02):
    ms=P.build2(W,wn,gap,lam=lam,nmodes=nm,target=2.05,only=only,**kw); d=ms.solve()
    X=(W+wn+gap)/2+1.5; xc0=((-(gap/2+W/2))+(gap/2+wn/2))/2
    xg=np.arange(xc0-X,xc0+X,dx); yg=np.arange(-0.8,kw["H"]+0.8,dx)
    F={}
    for c in ["Ex","Ey","Hx","Hy"]:
        f=getattr(d,c).isel(f=0); f=f.squeeze("z",drop=True) if "z" in f.dims else f
        F[c]=f.interp(x=xg,y=yg).fillna(0).transpose("mode_index","x","y").values
    n=d.n_eff.values[0]; te=d.pol_fraction.te.values[0]
    for i in range(nm):
        o=np.sqrt(0.5*np.sum(F["Ex"][i]*F["Hy"][i]-F["Ey"][i]*F["Hx"][i])*2*dx*dx+0j)
        for c in F: F[c][i]/=o
    return dict(F=F,n=n,te=te,dA=dx*dx)
def ov(A,i,B,j,dA): return 0.5*np.sum(A["Ex"][i]*B["Hy"][j]-A["Ey"][i]*B["Hx"][j]+B["Ex"][j]*A["Hy"][i]-B["Ey"][j]*A["Hx"][i])*dA
def run(a):
    W,wn,gap,lam,kw=a
    S=fields(W,wn,gap,lam,None,10,kw); A=fields(W,wn,gap,lam,0,4,kw); B=fields(W,wn,gap,lam,1,3,kw)
    def pick(M,k): # k-th TE-like mode
        idx=[i for i in range(len(M["n"])) if M["te"][i]>0.8]; return idx[k]
    iTE0w,iTE1w,iTE0n=pick(A,0),pick(A,1),pick(B,0)
    dA=S["dA"]; ns=len(S["n"])
    cin={k:np.array([ov(S["F"],j,A["F"],i,dA) for j in range(ns)]) for k,i in [("TE0w",iTE0w),("TE1w",iTE1w)]}
    cout={k:np.array([ov(B["F"] if k=="TE0n" else A["F"],i,S["F"],j,dA) for j in range(ns)]) for k,i in [("TE0n",iTE0n),("TE0w",iTE0w),("TE1w",iTE1w)]}
    Ls=np.linspace(0,150,601); k0=2*np.pi/lam; ph=np.exp(-1j*k0*np.outer(Ls,S["n"]))
    res={}
    for a_ in cin:
        for b_ in cout: res[f"{a_}->{b_}"]=(np.abs((ph*cin[a_][None,:]*cout[b_][None,:]).sum(1))**2).tolist()
    return dict(W=W,wn=wn,gap=gap,lam=lam,Ls=Ls.tolist(),res=res,n=dict(TE0w=float(A["n"][iTE0w]),TE1w=float(A["n"][iTE1w]),TE0n=float(B["n"][iTE0n])))
if __name__=="__main__":
    W,wn,gap=float(sys.argv[1]),float(sys.argv[2]),float(sys.argv[3]); out=sys.argv[4]
    kw=dict(kw0); 
    if len(sys.argv)>5: kw.update(json.loads(sys.argv[5]))
    lams=[1.45,1.5,1.55,1.6,1.65]
    with Pool(5) as p: R=p.map(run,[(W,wn,gap,l,kw) for l in lams])
    json.dump(R,open(out,"w")); print("saved",out)
