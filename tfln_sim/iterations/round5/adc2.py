import sys,os,json,numpy as np; os.environ["OMP_NUM_THREADS"]="1"; sys.path.insert(0,"..")
from multiprocessing import Pool
import psrlib as P
kw=dict(orient="XcutZ",H=0.6,etch=0.3,angle=60,clad="air")
def sup(a):
    gap,lam,wn=a; ms=P.build2(2.6,wn,gap,lam=lam,nmodes=6,target=1.97,**kw); d=ms.solve()
    return dict(gap=gap,lam=lam,wn=wn,neff=d.n_eff.values[0].tolist(),te=d.pol_fraction.te.values[0].tolist())
if __name__=="__main__":
    jobs=[(g,l,1.21) for g in [0.4,0.6,0.8] for l in [1.45,1.5,1.55,1.6,1.65]]+[(0.6,1.55,wn) for wn in [1.0,1.1,1.3,1.4]]
    with Pool(8) as p: R=p.map(sup,jobs)
    json.dump(R,open("super.json","w")); print("ok")
