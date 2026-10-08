import sys,os,json,numpy as np; os.environ["OMP_NUM_THREADS"]="1"; sys.path.insert(0,"..")
from multiprocessing import Pool
import psrlib as P
kw=dict(orient="XcutZ",H=0.6,etch=0.3,angle=60,clad="air")
lams=[1.45,1.5,1.55,1.6,1.65]
def single(a):
    w,lam=a; r=P.solve((w,dict(kw,lam=lam))); return (w,lam,r["neff"],r["te"])
def sup(a):
    W,gap,lam,wn=a; d=P.build2(W,wn,gap,lam=lam,nmodes=6,target=1.97,**kw).solve()
    return dict(W=W,gap=gap,lam=lam,wn=wn,neff=d.n_eff.values[0].tolist(),te=d.pol_fraction.te.values[0].tolist())
if __name__=="__main__":
    R=json.load(open("singles.json"))
    with Pool(8) as p:
        if not any(r[0]==2.2 for r in R):
            R+= p.map(single,[(W,l) for W in [2.0,2.2] for l in lams]); json.dump(R,open("singles.json","w"),default=float)
        ts=lambda n,t: sorted([a for a,b in zip(n,t) if b>0.9],reverse=True)
        jobs=[]
        for W in [2.0,2.2]:
            rr=[r for r in R if r[0]==W and r[1]==1.55][0]; t1=rr[2][1]; print(W,rr[3][:3])
            pts=sorted((r[0],ts(r[2],r[3])[0]) for r in R if r[1]==1.55 and r[0]<1.7); x,y=zip(*pts)
            wn=float(np.round(np.interp(t1,y,x),3)); print("W",W,"match wn",wn,flush=True)
            jobs+=[(W,g,l,wn) for g in [0.3,0.4] for l in lams]
        S=p.map(sup,jobs)
    json.dump(S,open("super2.json","w")); print("ok")
