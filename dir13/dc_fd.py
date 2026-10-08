# Self-written semi-vectorial (quasi-TE, Ex) finite-difference mode solver for TFLN rib directional coupler.
# femwell installed but gmsh needs libGLU (no root) -> FD fallback. Isotropic n_e approximation (X-cut, TE along z-axis, y-propagation).
import numpy as np, scipy.sparse as sp, scipy.sparse.linalg as sla, json
lam=1.55; k0=2*np.pi/lam; nLN=2.138; nOx=1.444; H=0.6; slab=0.3
dx=0.01; dy=0.01; X=8.0; Y=3.0
x=np.arange(-X/2,X/2,dx)+dx/2; y=np.arange(-1.2,Y-1.2,dy)+dy/2
def eps_map(w,g,dw=0.0):
    XX,YY=np.meshgrid(x,y,indexing='ij'); e=np.full(XX.shape,nOx**2)
    e[(YY>0)&(YY<slab)]=nLN**2
    ww=w+dw
    for c in (-(g+w)/2,(g+w)/2):
        e[(np.abs(XX-c)<ww/2)&(YY>=slab)&(YY<H)]=nLN**2
    return e
def solve(e,nm=2):
    Nx,Ny=e.shape; N=Nx*Ny; idx=lambda i,j:i*Ny+j
    rows=[];cols=[];vals=[]
    ep=np.pad(e,((1,1),(0,0)),mode='edge')
    for i in range(Nx):
        for j in range(Ny):
            p=idx(i,j); ei=e[i,j]; er=ep[i+2,j]; el=ep[i,j]
            ar=2*er/(er+ei)/dx**2; al=2*el/(el+ei)/dx**2
            br=2*ei/(er+ei)/dx**2; bl=2*ei/(el+ei)/dx**2
            d=-(br+bl)-2/dy**2+k0**2*ei
            rows.append(p);cols.append(p);vals.append(d)
            if i<Nx-1: rows.append(p);cols.append(idx(i+1,j));vals.append(ar)
            if i>0: rows.append(p);cols.append(idx(i-1,j));vals.append(al)
            if j<Ny-1: rows.append(p);cols.append(idx(i,j+1));vals.append(1/dy**2)
            if j>0: rows.append(p);cols.append(idx(i,j-1));vals.append(1/dy**2)
    A=sp.csr_matrix((vals,(rows,cols)),shape=(N,N))
    w,v=sla.eigs(A,k=nm,sigma=(k0*nLN)**2)
    n=np.sqrt(np.real(w))/k0; o=np.argsort(-n); return n[o]
if __name__=="__main__":
    out=[]
    n1=solve(eps_map(1.2,100.0),1)  # far apart ~ isolated (check single-mode index)
    for w in [1.1,1.2,1.3]:
        for g in [0.5,0.6,0.7,0.8,0.9,1.0]:
            ne,no=solve(eps_map(w,g)); Lc=lam/(2*(ne-no))
            out.append(dict(w=w,g=g,ne=ne,no=no,Lc_um=Lc)); print(out[-1],flush=True)
    json.dump(out,open('dc_supermodes.json','w'),indent=1)
