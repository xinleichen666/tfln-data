import clib as C,numpy as np,itertools,sys,os
avail=[(c,l) for c in C.CORNERS for l in C.LAMS if os.path.exists(f"data/{c}_{l}.pkl")]
def prof_from_w(w):
    z=np.concatenate([[0],np.cumsum(w)]); return z/z[-1]
def evalp(ws,we,zf,L):
    R={}
    for c,l in avail:
        o=C.run(C.load(c,l),ws,we,zf,L); R[(c,l)]=o
    return R
def metr(R):
    conv=min(R[k]["TE1w->TE0n"] for k in R); res=max(R[k]["TE1w->TE1w"] for k in R); xt=max(R[k]["TE0w->TE0n"] for k in R)
    return 10*np.log10(conv),10*np.log10(res),10*np.log10(xt)
if __name__=="__main__":
    print(avail)
    for ws,we in [(0.9,1.6),(0.9,1.5),(1.0,1.5)]:
        Cs=np.array([C.adiab(C.load(c,l),ws,we) for c,l in avail]); wmax=Cs.max(0)
        for p in [1.0,2.0]:
            zf=prof_from_w(wmax**p)
            for L in [100,150,200,300,400,600]:
                print(ws,we,"p",p,L,np.round(metr(evalp(ws,we,zf,L)),2),flush=True)
