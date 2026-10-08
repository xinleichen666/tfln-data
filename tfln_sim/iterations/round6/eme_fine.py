import sys,os,pickle,numpy as np; os.environ["OMP_NUM_THREADS"]="1"; sys.path.insert(0,"..")
from multiprocessing import Pool
import eme
kw=dict(orient="XcutZ",H=0.6,etch=0.3,angle=60,clad="air",lam=1.55)
W=np.round(np.linspace(1.2,2.6,113),4)
if __name__=="__main__":
    if not os.path.exists("Dfine_1.55.pkl"):
        with Pool(8) as p: D=eme.prepare(list(W),dict(kw,res=60),nm=6,dx=0.01,pool=p)
        pickle.dump(D,open("Dfine_1.55.pkl","wb"))
    D=pickle.load(open("Dfine_1.55.pkl","rb")); C=pickle.load(open("../round4/D_1.55.pkl","rb"))
    for k in ["W","neff","te"]: C[k]=C[k][16:]
    C["T"]=C["T"][16:]
    import json; prof=json.load(open("../round4/eme_results.json"))
    zc=np.interp(D["W"],prof["W"],prof["ca_profile"]); zc_c=np.array(prof["ca_profile"])
    out={}
    for L in [50,75,101,125,153,200,300,500,800]:
        a=eme.propagate(D,zc,L); b=eme.propagate(C,zc_c,L)
        out[L]=dict(fine=float(a[1]/a.sum()),fine_tot=float(a.sum()),coarse=float(b[1]/b.sum()),coarse_tot=float(b.sum()))
        print(L,out[L],flush=True)
    json.dump(out,open("eme_fine_check.json","w"))
