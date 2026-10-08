# 2D TE (Ez) FDFD, periodic in x, SC-PML in z, TF/SF injection of arbitrary forward field. Rigorous (scalar exact in 2D TE).
import numpy as np, scipy.sparse as sp, scipy.sparse.linalg as sla
def build(eps,dx,dz,lam,npml=25):
    Nx,Nz=eps.shape; k0=2*np.pi/lam; w=1.0
    def sfun(zz):  # zz in cell units
        d=np.maximum(np.maximum(npml-zz,zz-(Nz-1-npml)),0)/npml
        return 1+1j*5.0*d**3
    zc=np.arange(Nz); sc=sfun(zc); sh=sfun(zc+0.5)
    # Dzz: (1/sc) d/dz (1/sh d/dz)
    e=np.ones(Nz)
    Df=sp.diags([-e,e[:-1]],[0,1],shape=(Nz,Nz))/dz   # forward diff -> half points
    Dzz=sp.diags(1/sc)@(-Df.T)@sp.diags(1/sh)@Df
    ex=np.ones(Nx); Dx=sp.diags([-ex,ex[:-1]],[0,1],shape=(Nx,Nx)).tolil(); Dx[Nx-1,0]=1; Dx=Dx.tocsr()/dx
    Dxx=-Dx.T@Dx
    A=sp.kron(Dxx,sp.eye(Nz))+sp.kron(sp.eye(Nx),Dzz)+sp.diags(k0**2*eps.ravel())
    return A.tocsc()
def tfsf_solve(lu,A,Einc,iz0):
    Nx,Nz=Einc.shape; Q=np.zeros((Nx,Nz)); Q[:,iz0:]=1; q=sp.diags(Q.ravel())
    b=(A@(q@Einc.ravel())-q@(A@Einc.ravel()))
    return lu.solve(b).reshape(Nx,Nz)
def as_field(E0,dx,lam,zs,n=1.0):  # forward angular spectrum of 1D field E0(x) to planes zs (relative)
    fx=np.fft.fftfreq(len(E0),dx); kz=2*np.pi*np.sqrt((n/lam)**2-fx**2+0j)
    F=np.fft.fft(E0); return np.array([np.fft.ifft(F*np.exp(1j*kz*z)) for z in zs]).T
if __name__=="__main__":
    # validation: flat slab n=1.53 thickness T at normal incidence -> Airy transmission
    lam=1.55; dx=0.05; dz=0.04; Nx=64; T=2.0
    z=np.arange(260)*dz; eps=np.ones((Nx,260)); iz0=40; zs0=60*dz
    eps[:,(z>=zs0)&(z<zs0+T)]=1.53**2
    A=build(eps,dx,dz,lam); lu=sla.splu(A)
    E0=np.ones(Nx,complex); Einc=as_field(E0,dx,lam,z-iz0*dz)
    E=tfsf_solve(lu,A,Einc,iz0); izo=220
    t_fd=E[:,izo].mean()/Einc[:,izo].mean()
    n=1.53; k0=2*np.pi/lam; r=(1-n)/(1+n); t12=2/(1+n); t21=2*n/(1+n); dl=k0*n*T
    t_an=t12*t21*np.exp(1j*dl)/(1-r**2*np.exp(2j*dl))*np.exp(-1j*k0*T)
    print('FDFD |t|^2',abs(t_fd)**2,'phase',np.angle(t_fd),' Airy',abs(t_an)**2,np.angle(t_an))
def build_tm(eps,dx,dz,lam,npml=25):
    """2D TM (Hy): d/dx(1/eps dH/dx) + (1/sz)d/dz(1/(sz eps) dH/dz) + k0^2 H = 0, periodic x."""
    Nx,Nz=eps.shape; k0=2*np.pi/lam
    def sfun(zz):
        d=np.maximum(np.maximum(npml-zz,zz-(Nz-1-npml)),0)/npml; return 1+1j*5.0*d**3
    sc=sfun(np.arange(Nz)); sh=sfun(np.arange(Nz)+0.5)
    ie=1/eps; iex=0.5*(ie+np.roll(ie,-1,0)); iez=0.5*(ie+np.concatenate([ie[:,1:],ie[:,-1:]],1))
    I=np.arange(Nx*Nz).reshape(Nx,Nz); rows=[];cols=[];vals=[]
    # x part (periodic)
    ip=np.roll(I,-1,0); im=np.roll(I,1,0); iexm=np.roll(iex,1,0)
    rows+= [I.ravel()]*3; cols+=[ip.ravel(),im.ravel(),I.ravel()]; vals+=[(iex/dx**2).ravel(),(iexm/dx**2).ravel(),(-(iex+iexm)/dx**2).ravel()]
    # z part
    a=(iez/sh[None,:])/(sc[None,:]*dz**2); am=np.concatenate([np.zeros((Nx,1)),a[:,:-1]*0+ (iez[:,:-1]/sh[None,:-1])/(sc[None,1:]*dz**2)],1)
    jp=I[:,1:]; jm=I[:,:-1]
    rows+=[I[:,:-1].ravel(),I[:,1:].ravel()]; cols+=[jp.ravel(),jm.ravel()]; vals+=[a[:,:-1].ravel(),am[:,1:].ravel()]
    rows+=[I.ravel()]; cols+=[I.ravel()]; vals+=[(-a-am+k0**2).ravel()]
    return sp.csr_matrix((np.concatenate(vals),(np.concatenate(rows),np.concatenate(cols))),shape=(Nx*Nz,)*2).tocsc()
