import json, numpy as np, modes as M, os
from scipy.optimize import minimize
out='data/iter1_tips.json'; R=json.load(open(out)) if os.path.exists(out) else {}
nLN,nOx,nP=2.138,1.444,1.53
dx=0.04; x,y,XX,YY=M.grid(12,10,dx)
def tip_eps(w,t,nclad):
    e=np.where(YY<0,nOx**2,nclad**2); e[(abs(XX)<w/2)&(YY>=0)&(YY<t)]=nLN**2; return e
def bestgauss(E):
    I=abs(E)**2; yc=np.sum(I*YY)/I.sum()
    f=lambda p: -M.overlap(E,M.gauss(XX,YY,abs(p[0]),0,p[1]))
    r=minimize(f,[2.0,yc],method='Nelder-Mead'); return -r.fun,abs(r.x[0]),r.x[1]
def mfd(E):
    I=abs(E)**2; I/=I.sum(); xc=(I*XX).sum(); yc=(I*YY).sum()
    return 4*np.sqrt((I*(XX-xc)**2).sum()), 4*np.sqrt((I*(YY-yc)**2).sum())   # D4sigma
if __name__=="__main__":
 for lam in (1.55,):
  M.k0=2*np.pi/lam
  for t in (0.3,0.6):
    for clad,nc in (('oxide',nOx),('polymer',nP)):
      for w in (0.1,0.15,0.2,0.3,0.4,0.6,0.8):
        key=f'{lam}_{t}_{clad}_{w}'
        if key in R: continue
        n,V=M.solve(tip_eps(w,t,nc),dx,dx,1.9); E=V[0]
        I=abs(E)**2; edge=(I[:5].sum()+I[-5:].sum()+I[:,:5].sum()+I[:,-5:].sum())/I.sum()
        eS=M.overlap(E,M.gauss(XX,YY,5.2,0,(I*YY).sum()/I.sum()))
        eB,w0,y0=bestgauss(E); mx,my=mfd(E)
        R[key]=dict(lam=lam,t=t,clad=clad,w=w,neff=float(n[0]),D4s_x=mx,D4s_y=my,
          eta_SMF28_direct=eS,eta_bestGauss=eB,w0=w0,y0=y0,edge_frac=float(edge))
        print(key,{k:round(v,4) if isinstance(v,float) else v for k,v in R[key].items()},flush=True)
        json.dump(R,open(out,'w'),indent=1)
        if key.endswith('_0.1'): np.save(f'data/field_{key}.npy',E)
