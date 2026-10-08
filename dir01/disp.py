# Round1: group index of TFLN ridge modes (semi-vectorial FD, reuse dir15/modes.py). Saves to data/disp.json incrementally.
import sys,json,os,numpy as np; sys.path.insert(0,'/workspace/dir15'); import modes
def ne(l): l2=l*l; return np.sqrt(1+2.9804*l2/(l2-0.02047)+0.5981*l2/(l2-0.0666)+8.9543*l2/(l2-416.08))   # Zelmon97 cLN
def no(l): l2=l*l; return np.sqrt(1+2.6734*l2/(l2-0.01764)+1.2290*l2/(l2-0.05914)+12.614*l2/(l2-474.6))
def ns(l): l2=l*l; return np.sqrt(1+0.6961663*l2/(l2-0.0684043**2)+0.4079426*l2/(l2-0.1162414**2)+0.8974794*l2/(l2-9.896161**2))
T=0.6
def neff(lam,w,pol,t=T,h=0.3,dx=0.02):
    modes.lam=lam; modes.k0=2*np.pi/lam
    X,Y=5.0,2.6; x=np.arange(-X/2,X/2,dx)+dx/2; y=np.arange(-1.2,1.4,dx)+dx/2
    XX,YY=np.meshgrid(x,y,indexing='ij')
    nLN=ne(lam) if pol=='TE' else no(lam)
    eps=np.where(YY<0,ns(lam)**2,1.0)
    slab=(YY>=0)&(YY<t-h); rib=(YY>=0)&(YY<t)&(abs(XX)<w/2)
    eps=np.where(slab|rib,nLN**2,eps)
    if pol=='TM': eps=eps.T  # discontinuity handling along E (vertical)
    n,_=modes.solve(eps,dx,dx,nLN,1); return n[0]
def ng(lam,w,pol,**k):
    d=0.01; a=neff(lam-d,w,pol,**k); b=neff(lam+d,w,pol,**k); c=neff(lam,w,pol,**k)
    return c, c-lam*(b-a)/(2*d)
if __name__=="__main__":
    f='data/disp.json'; D=json.load(open(f)) if os.path.exists(f) else {}
    for t in (0.6,0.59,0.61):
     for w in (1.0,1.2,1.4,1.6,1.8,2.0):
      for lam,pol in ((1.55,'TE'),(1.55,'TM'),(0.775,'TE'),(0.775,'TM')):
        key=f'{t}_{w}_{lam}_{pol}'
        if key in D: continue
        D[key]=ng(lam,w,pol,t=t); json.dump(D,open(f,'w'),indent=0); print(key,D[key],flush=True)
