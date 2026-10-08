import sys,json,os,itertools,numpy as np
os.environ["OMP_NUM_THREADS"]="1"
from multiprocessing import Pool
import psrlib as P
def job(c):
    kw=dict(c); wmin=kw.pop("wmin",0.8); wmax=kw.pop("wmax",6.0)
    try:
        nte,ntm=P.slab_neff(**kw); r=P.find_cross(kw,wmin,wmax)
        r["slab_te"]=nte; r["slab_tm"]=ntm
    except Exception as e: r=dict(found=False,err=str(e),rows=[])
    lam=kw.get("lam",1.55); pick=None
    for c0 in r.get("cands",[]):
        tx=c0["te_x"]; nlo=c0["neff_x"]-c0["g"]/2
        c0["valid"]=bool(0.25<tx[0]<0.75 and 0.25<tx[1]<0.75 and np.isfinite(c0["alpha"]) and c0["alpha"]>0 and nlo>max(r["slab_te"],P.clad_index(kw.get("clad","air"),lam))+0.03)
        if c0["valid"] and pick is None: pick=c0
    r["valid"]=pick is not None
    if pick: r.update(pick)
    if pick:
        r["leak_margin"]=float(r["neff_x"]-r["g"]/2-r["slab_te"])
        L,S=P.lz_length(r["g"],r["alpha"],lam); r["L99_um"]=float(L); r["span"]=float(S)
    r["cfg"]=c; print(json.dumps({k:v for k,v in r.items() if k not in("rows",)},default=float),flush=True); return r
if __name__=="__main__":
    cfgs=json.load(open(sys.argv[1])); out=sys.argv[2]
    with Pool(8) as p: R=p.map(job,cfgs,chunksize=1)
    json.dump(R,open(out,"w"),default=float)
