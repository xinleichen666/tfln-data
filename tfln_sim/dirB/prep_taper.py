import sys,os,pickle,numpy as np; os.environ["OMP_NUM_THREADS"]="1"; sys.path.insert(0,"../iterations")
from multiprocessing import Pool
import eme
W=list(np.round(np.arange(1.2,2.701,0.025),4))
CORN={"ep20":{"etch":.32},"em20":{"etch":.28},"a55":{"angle":55},"a65":{"angle":65}}
if __name__=="__main__":
    os.makedirs("taper",exist_ok=True)
    with Pool(8) as p:
        for c,k in CORN.items():
            for lam in [1.45,1.55,1.65]:
                f=f"taper/{c}_{lam}.pkl"
                if os.path.exists(f): continue
                kw=dict(orient="XcutZ",H=0.6,etch=0.3,angle=60,clad="air",lam=lam); kw.update(k)
                pickle.dump(eme.prepare(W,kw,nm=6,dx=0.02,pool=p),open(f,"wb")); print("done",f,flush=True)
