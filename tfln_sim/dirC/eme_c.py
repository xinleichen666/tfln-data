import sys,json,numpy as np
sys.path.insert(0,'/workspace/tfln_sim/iterations')
from multiprocessing import Pool
import psrlib as P, eme as E
W=np.linspace(1.1,2.4,53).tolist()
cases=[(H,e,a,lam) for lam in (1.45,1.5,1.55,1.6,1.65) for (H,e,a) in [(0.4,0.28,60)]]+\
      [(H,e,a,lam) for lam in (1.45,1.55,1.65) for (H,e,a) in [(0.4,0.26,60),(0.4,0.30,60),(0.39,0.28,60),(0.41,0.28,60),(0.4,0.28,55),(0.4,0.28,65)]]
Ls=[50,100,150,200,250,300,400]
res=[]
if __name__=='__main__':
  with Pool(8) as pool:
    for H,e,a,lam in cases:
        kw=dict(H=H,etch=e,angle=a,orient='XcutY',clad='air',lam=lam,res=30)
        D=E.prepare(W,kw,nm=6,pool=pool)
        te0=D['te'][0]; i_tm=int(np.argmin(te0[:4])); 
        teN=D['te'][-1]; tes=[i for i in range(6) if teN[i]>0.6]; i_te1=tes[1]
        r={}
        for L in Ls:
            p=E.propagate(D,np.linspace(0,1,len(W)),L,inp=i_tm); r[L]=dict(conv=float(p[i_te1]),tot=float(p.sum()))
        out=dict(H=H,etch=e,angle=a,lam=lam,i_tm=i_tm,i_te1=i_te1,r=r); res.append(out)
        print(json.dumps(out),flush=True)
        json.dump(res,open('eme_c.json','w'))
