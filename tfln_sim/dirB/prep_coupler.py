"""Adiabatic (tapered) ADC supermode-EME data: narrow arm swept wn over grid at fixed W/gap, per fab corner & wavelength."""
import sys,os,pickle,json,numpy as np; os.environ["OMP_NUM_THREADS"]="1"; sys.path.insert(0,"../iterations")
from multiprocessing import Pool
import psrlib as P
G0=float(os.environ.get("G0","0.3")); TAG=os.environ.get("TAG","data")
WN=np.round(np.arange(0.90,1.601,0.025),4) if G0==0.3 else np.round(np.arange(1.0,1.501,0.025),4); ENDS=[0.9,1.0,1.4,1.5,1.6] if G0==0.3 else [1.0,1.1,1.4,1.5]
CORN={"nom":dict(b=0,g=0,kw={}),"wp50":dict(b=.05,g=-.05,kw={}),"wm50":dict(b=-.05,g=.05,kw={}),
 "gp30":dict(b=0,g=.03,kw={}),"gm30":dict(b=0,g=-.03,kw={}),"ep20":dict(b=0,g=0,kw={"etch":.32}),"em20":dict(b=0,g=0,kw={"etch":.28}),
 "a55":dict(b=0,g=0,kw={"angle":55}),"a65":dict(b=0,g=0,kw={"angle":65})}
LAMS=[1.45,1.55,1.65]; W0=2.6; DX=0.02; NM=8
def grid(): return np.arange(-4.6,4.6+1e-9,DX), np.arange(-0.8,1.4+1e-9,DX)
def fl(ms):
    d=ms.solve(); xg,yg=grid(); F={}
    for c in ["Ex","Ey","Hx","Hy"]:
        f=getattr(d,c).isel(f=0); f=f.squeeze("z",drop=True) if "z" in f.dims else f
        F[c]=f.interp(x=xg,y=yg).fillna(0).transpose("mode_index","x","y").values.astype(np.complex64)
    n=d.n_eff.values[0]; te=d.pol_fraction.te.values[0]
    for i in range(len(n)):
        o=np.sqrt(np.sum(F["Ex"][i]*F["Hy"][i]-F["Ey"][i]*F["Hx"][i])*DX*DX+0j)
        for c in F: F[c][i]/=o
    return dict(F=F,n=n,te=te)
def ov(A,i,B,j): return 0.5*np.sum(A["Ex"][i]*B["Hy"][j]-A["Ey"][i]*B["Hx"][j]+B["Ex"][j]*A["Hy"][i]-B["Ey"][j]*A["Hx"][i])*DX*DX
def geom(c,wn):
    C=CORN[c]; kw=dict(orient="XcutZ",H=0.6,etch=0.3,angle=60,clad="air"); kw.update(C["kw"])
    W=W0+C["b"]; w=wn+C["b"]; g=G0+C["g"]
    # keep wide arm fixed in absolute x: build2 centers between arms; shift handled since interp on absolute coords with x1=-(g/2+W/2)
    return W,w,g,kw
def job(a):
    c,lam=a; out=f"{TAG}/{c}_{lam}.pkl"
    if os.path.exists(out): return out
    Ms=[]
    for wn in WN:
        W,w,g,kw=geom(c,wn); Ms.append(fl(P.build2(W,w,g,lam=lam,nmodes=NM,target=2.05,**kw)))
    T=[np.array([[ov(Ms[k+1]["F"],i,Ms[k]["F"],j) for j in range(NM)] for i in range(NM)]) for k in range(len(WN)-1)]
    W,w,g,kw=geom(c,1.2); A=fl(P.build2(W,w,g,lam=lam,nmodes=5,target=2.05,only=0,**kw))
    iso={}
    for e in ENDS:
        W,w,g,kw=geom(c,e); B=fl(P.build2(W,w,g,lam=lam,nmodes=3,target=2.05,only=1,**kw))
        k=list(np.round(WN,4)).index(e); S=Ms[k]
        iso[e]=dict(nB=B["n"],teB=B["te"],nA=A["n"],teA=A["te"],
            inA=np.array([[ov(S["F"],j,A["F"],i) for j in range(NM)] for i in range(len(A["n"]))]),
            outA=np.array([[ov(A["F"],i,S["F"],j) for j in range(NM)] for i in range(len(A["n"]))]),
            outB=np.array([[ov(B["F"],i,S["F"],j) for j in range(NM)] for i in range(len(B["n"]))]))
    pickle.dump(dict(WN=WN,neff=np.array([m["n"] for m in Ms]),te=np.array([m["te"] for m in Ms]),T=T,iso=iso,lam=lam),open(out,"wb"))
    print("done",out,flush=True); return out
if __name__=="__main__":
    os.makedirs(TAG,exist_ok=True)
    cs=sys.argv[1].split(",") if len(sys.argv)>1 else list(CORN)
    with Pool(8) as p: p.map(job,[(c,l) for c in cs for l in LAMS],chunksize=1)
