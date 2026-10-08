import sys,os,json,numpy as np; os.environ["OMP_NUM_THREADS"]="1"; sys.path.insert(0,"..")
from multiprocessing import Pool
import psrlib as P
kw=dict(orient="XcutZ",H=0.6,etch=0.3,angle=60,clad="air")
def single(a):
    w,lam=a; r=P.solve((w,dict(kw,lam=lam))); return (w,lam,r["neff"],r["te"])
if __name__=="__main__":
    lams=[1.45,1.5,1.55,1.6,1.65]
    jobs=[(2.6,l) for l in lams]+[(w,l) for w in np.round(np.arange(0.9,1.61,0.05),3) for l in lams]
    with Pool(8) as p: R=p.map(single,jobs)
    json.dump(R,open("singles.json","w"),default=float); print("ok")
