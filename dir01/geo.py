# Round2: general ridge neff with separate dx (horizontal) / dy (vertical), etch depth h, film t.
import sys,numpy as np; sys.path.insert(0,'/workspace/dir15'); import modes
from disp import ne,no,ns
def neff(lam,w,pol,t,h,dx=0.02,dy=0.005,X=5.0,ytop=None):
    modes.lam=lam; modes.k0=2*np.pi/lam
    x=np.arange(-X/2,X/2,dx)+dx/2; y=np.arange(-1.0,t+0.6,dy)+dy/2
    XX,YY=np.meshgrid(x,y,indexing='ij')
    nLN=ne(lam) if pol=='TE' else no(lam)
    eps=np.where(YY<0,ns(lam)**2,1.0)
    # fractional fill at film top/slab top boundaries (sub-cell accuracy for thickness)
    def frac(top): return np.clip((top-(YY-dy/2))/dy,0,1)*(YY+dy/2>0)
    fslab=frac(t-h); frib=frac(t)*(abs(XX)<w/2)
    f=np.maximum(fslab,frib)
    eps=eps*(1-f)+nLN**2*f
    if pol=='TM': n,_=modes.solve(eps.T,dy,dx,nLN,1)
    else: n,_=modes.solve(eps,dx,dy,nLN,1)
    return float(n[0])
