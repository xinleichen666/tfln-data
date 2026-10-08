from modes import *
from scipy.optimize import brentq
n1,n2,t=2.138,1.444,0.3
f=lambda ne: np.tan(k0*np.sqrt(n1**2-ne**2)*t/2)-np.sqrt(ne**2-n2**2)/np.sqrt(n1**2-ne**2)
na=brentq(f,n2+1e-6,n1-1e-6)
for dx in (0.02,0.01):
    X=4.0; x,y,XX,YY=grid(X,4,dx); eps=np.where(abs(YY)<t/2,n1**2,n2**2)
    n,_=solve(eps,dx,dx,1.9)
    Xe=X+dx  # Dirichlet effective width
    print('dx',dx,'FD',n[0],'analytic(with box kx)',np.sqrt(na**2-(np.pi/Xe/k0)**2))
