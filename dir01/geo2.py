# Round4: trapezoidal ridge (top width w, sidewall angle th deg), sub-cell fill in x via 4x supersampling.
import sys,numpy as np; sys.path.insert(0,'/workspace/dir15'); import modes
from disp import ne,no,ns
def neff(lam,w,pol,t,h,th=90,dx=0.01,dy=0.005,X=3.0):
    modes.lam=lam; modes.k0=2*np.pi/lam
    x=np.arange(-X/2,X/2,dx)+dx/2; y=np.arange(-1.0,t+0.6,dy)+dy/2
    nLN=ne(lam) if pol=='TE' else no(lam)
    S=4; xs=(np.arange(S)+0.5)/S-0.5
    f=np.zeros((len(x),len(y)))
    for a in xs:
      for b in xs:
        XX,YY=np.meshgrid(x+a*dx,y+b*dy,indexing='ij')
        hw=w/2+(t-YY)/np.tan(np.radians(th))
        f+=((YY>=0)&(YY<t-h))|((YY>=t-h)&(YY<t)&(abs(XX)<hw))
    f/=S*S; XX,YY=np.meshgrid(x,y,indexing='ij')
    eps=np.where(YY<0,ns(lam)**2,1.0)*(1-f)+nLN**2*f
    if pol=='TM': n,_=modes.solve(eps.T,dy,dx,nLN,1)
    else: n,_=modes.solve(eps,dx,dy,nLN,1)
    return float(n[0])
