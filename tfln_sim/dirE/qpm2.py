import sys,json,numpy as np; sys.path.insert(0,'/workspace/tfln_sim/iterations'); import psrlib as P
from multiprocessing import Pool
def te0(a):
    w,H,e,lam=a
    ms=P.build(w,H=H,etch=e,angle=60,orient='XcutY',clad='air',lam=lam,nmodes=3,res=50)
    d=ms.solve(); n=d.n_eff.values[0]; t=d.pol_fraction.te.values[0]
    te=[x for x,y in zip(n,t) if y>0.5]; tm=[x for x,y in zip(n,t) if y<=0.5]
    return a,[float(max(te)) if te else None,float(max(tm)) if tm else None]
if __name__=='__main__':
    C=[(1.2,0.4,0.28),(1.25,0.4,0.28),(1.15,0.4,0.28),(1.2,0.4,0.26),(1.2,0.4,0.30),(1.2,0.39,0.28),(1.2,0.41,0.28)]
    J=[(w,H,e,l) for (w,H,e) in C for l in (0.775,1.50,1.55,1.60)]
    R=[]
    with Pool(8) as p:
        for r in p.imap(te0,J): R.append(r); print(r,flush=True)
    json.dump([[list(a),n] for a,n in R],open('qpm2_neff.json','w'))
