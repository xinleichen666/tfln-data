"""Local first-order EME (forward-only) for slowly varying tapers, using Tidy3D local ModeSolver.
Modes computed at a set of widths; slice interfaces via unconjugated overlap matrices; any taper
length/profile is then evaluated cheaply."""
import numpy as np, os, json, psrlib as P, tidy3d as td
from multiprocessing import Pool
def mode_fields(args):
    w,kw,nm,xg,yg=args
    ms=P.build(w,nmodes=nm,**kw); d=ms.solve()
    out={}
    for c in ["Ex","Ey","Hx","Hy"]:
        f=getattr(d,c).isel(f=0).squeeze("z",drop=True) if "z" in getattr(d,c).dims else getattr(d,c).isel(f=0)
        out[c]=f.interp(x=xg,y=yg).fillna(0).transpose("mode_index","x","y").values
    return dict(w=w,neff=d.n_eff.values[0],te=d.pol_fraction.te.values[0],**out)
def ov(a,i,b,j,dA):
    return 0.5*np.sum(a["Ex"][i]*b["Hy"][j]-a["Ey"][i]*b["Hx"][j]+b["Ex"][j]*a["Hy"][i]-b["Ey"][j]*a["Hx"][i])*dA
def prepare(W,kw,nm=6,dx=0.02,pool=None):
    X=max(W)/2+1.5; xg=np.arange(-X,X+1e-9,dx); yg=np.arange(-0.8,kw.get("H",0.6)+0.8,dx)
    dA=dx*dx
    M=(pool.map if pool else map)(mode_fields,[(w,kw,nm,xg,yg) for w in W]); M=list(M)
    for m in M:
        for i in range(nm):
            n=np.sqrt(ov(m,i,m,i,dA)+0j)
            for c in ["Ex","Ey","Hx","Hy"]: m[c][i]=m[c][i]/n
    T=[np.array([[ov(M[k+1],i,M[k],j,dA) for j in range(nm)] for i in range(nm)]) for k in range(len(M)-1)]
    return dict(W=np.array(W),neff=np.array([m["neff"] for m in M]),te=np.array([m["te"] for m in M]),T=T,lam=kw.get("lam",1.55))
def propagate(D,zfrac,L,inp=1):
    """zfrac: positions (0..1) of each width sample along taper (monotonic). Returns |amplitudes|^2 at output."""
    k0=2*np.pi/D["lam"]; z=np.asarray(zfrac)*L
    a=np.zeros(D["neff"].shape[1],complex); a[inp]=1
    for k in range(len(z)-1):
        dz=z[k+1]-z[k]; nav=D["neff"][k]  # half step in k, half in k+1
        a=a*np.exp(-1j*k0*nav*dz/2); a=D["T"][k]@a; a=a*np.exp(-1j*k0*D["neff"][k+1]*dz/2)
    return np.abs(a)**2
