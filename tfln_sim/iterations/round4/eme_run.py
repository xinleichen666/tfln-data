import sys,os,pickle,numpy as np
os.environ["OMP_NUM_THREADS"]="1"; sys.path.insert(0,"..")
from multiprocessing import Pool
import eme
kw=dict(orient="XcutZ",H=0.6,etch=0.3,angle=60,clad="air")
W=np.round(np.linspace(0.8,2.6,73),4)
if __name__=="__main__":
    with Pool(8) as p:
        for lam in [1.55,1.50,1.60,1.45,1.65]:
            f=f"D_{lam}.pkl"
            if os.path.exists(f): continue
            D=eme.prepare(list(W),dict(kw,lam=lam),nm=6,pool=p)
            pickle.dump(D,open(f,"wb")); print("done",lam,flush=True)
