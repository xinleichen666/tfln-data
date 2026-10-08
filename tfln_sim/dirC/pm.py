import sys,numpy as np; sys.path.insert(0,'/workspace/tfln_sim/iterations'); import psrlib as P
from multiprocessing import Pool
kw=dict(H=0.4,etch=0.28,angle=60,orient='XcutY',clad='air',lam=1.55,nmodes=5,res=30)
def te(w,k):
    r=P.solve((w,kw)); idx=[i for i in range(5) if r['te'][i]>0.8]; return r['neff'][idx[k]] if len(idx)>k else np.nan
def f(a): return a[0],a[1],te(a[0],a[1])
if __name__=='__main__':
    J=[(W,1) for W in (2.4,2.6,2.8)]+[(w,0) for w in np.arange(0.6,1.41,0.1)]
    with Pool(4) as p:
        for r in p.map(f,J): print(r)
