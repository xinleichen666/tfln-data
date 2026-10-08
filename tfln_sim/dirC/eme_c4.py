import sys,json,numpy as np
sys.path.insert(0,'/workspace/tfln_sim/iterations')
from multiprocessing import Pool
import psrlib as P, eme as E
W=np.linspace(1.1,2.9,73).tolist()
cases=[(0.4,0.28,60,l) for l in (1.45,1.55,1.65)]+[(0.4,0.30,60,1.65),(0.39,0.28,60,1.65),(0.4,0.26,60,1.65),(0.4,0.28,55,1.65)]
Ls=[100,150,200,250,300,400]
if __name__=='__main__':
  res=[]
  with Pool(8) as pool:
    for H,e,a,lam in cases:
        kw=dict(H=H,etch=e,angle=a,orient='XcutY',clad='air',lam=lam,res=40)
        D=E.prepare(W,kw,nm=8,dx=0.015,pool=pool)
        i_tm=int(np.argmin(D['te'][0][:4]))
        r={}
        for L in Ls:
            p=E.propagate(D,np.linspace(0,1,len(W)),L,inp=i_tm); r[L]=[float(x) for x in p]
        out=dict(H=H,etch=e,angle=a,lam=lam,i_tm=i_tm,neffN=D['neff'][-1].real.tolist(),teN=D['te'][-1].tolist(),r=r)
        res.append(out); print(json.dumps(out),flush=True); json.dump(res,open('eme_c4.json','w'))
