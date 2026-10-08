# Semi-vectorial quasi-TE FD mode solver (vectorized). Validated below vs slab analytic.
import numpy as np, scipy.sparse as sp, scipy.sparse.linalg as sla
lam=1.55; k0=2*np.pi/lam
def solve(eps,dx,dy,nguess,nm=1):
    Nx,Ny=eps.shape; e=eps
    ep=np.pad(e,((1,1),(0,0)),mode='edge'); er=ep[2:,:]; el=ep[:-2,:]
    ar=2*er/(er+e)/dx**2; al=2*el/(el+e)/dx**2; br=2*e/(er+e)/dx**2; bl=2*e/(el+e)/dx**2
    d=-(br+bl)-2/dy**2+k0**2*e
    I=np.arange(Nx*Ny).reshape(Nx,Ny)
    r=[I.ravel()];c=[I.ravel()];v=[d.ravel()]
    r+= [I[:-1].ravel()]; c+=[I[1:].ravel()]; v+=[ar[:-1].ravel()]
    r+= [I[1:].ravel()]; c+=[I[:-1].ravel()]; v+=[al[1:].ravel()]
    r+= [I[:,:-1].ravel()]; c+=[I[:,1:].ravel()]; v+=[np.full(Nx*(Ny-1),1/dy**2)]
    r+= [I[:,1:].ravel()]; c+=[I[:,:-1].ravel()]; v+=[np.full(Nx*(Ny-1),1/dy**2)]
    A=sp.csr_matrix((np.concatenate(v),(np.concatenate(r),np.concatenate(c))),shape=(Nx*Ny,)*2)
    w,V=sla.eigs(A,k=nm,sigma=(k0*nguess)**2)
    o=np.argsort(-w.real); n=np.sqrt(w.real[o])/k0
    return n, [np.real(V[:,i]).reshape(Nx,Ny) for i in o]
def grid(X,Y,dx): 
    x=np.arange(-X/2,X/2,dx)+dx/2; y=np.arange(-Y/2,Y/2,dx)+dx/2
    return x,y,*np.meshgrid(x,y,indexing='ij')
def overlap(E1,E2):  # power coupling (scalar)
    return abs(np.sum(E1*np.conj(E2)))**2/(np.sum(abs(E1)**2)*np.sum(abs(E2)**2))
def gauss(XX,YY,w,x0=0,y0=0): return np.exp(-((XX-x0)**2+(YY-y0)**2)/w**2)
if __name__=="__main__":
    # validation: symmetric slab (1D in y), compare with analytic TE0 neff
    from scipy.optimize import brentq
    n1,n2,t=2.138,1.444,0.3
    f=lambda ne: np.tan(k0*np.sqrt(n1**2-ne**2)*t/2)-np.sqrt(ne**2-n2**2)/np.sqrt(n1**2-ne**2)
    na=brentq(f,n2+1e-6,n1-1e-6)
    # solver: TE in x-polarization -> slab varying in x (index discontinuity normal to E): that's TM for slab normal x. use slab normal y -> TE
    for dx in (0.02,0.01):
        x,y,XX,YY=grid(0.2,4,dx); eps=np.where(abs(YY)<t/2,n1**2,n2**2)
        n,_=solve(eps,dx,dx,n1)
        print('dx',dx,'FD',n[0],'analytic',na)
