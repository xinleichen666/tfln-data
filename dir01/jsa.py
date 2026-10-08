# Round1 JSA/purity model: type-II (pump TE775 -> signal TE1550 + idler TM1550), x-cut 600nm, w=1.4um, etch 300nm.
import json,numpy as np
D=json.load(open('data/disp.json')); T=json.load(open('data/dt.json'))
c=0.299792458 # mm/ps
w=1.4; g=lambda l,p: D[f'0.6_{w}_{l}_{p}'][1]
ngp,ngs,ngi=g(0.775,'TE'),g(1.55,'TE'),g(1.55,'TM')
A=(ngp-ngs)/c; B=(ngp-ngi)/c   # ps/mm ; dk = A*Ws + B*Wi
def dk0(t): return 2*np.pi*(T[f'{t}_{w}_0.775_TE']/0.775-T[f'{t}_{w}_1.55_TE']/1.55-T[f'{t}_{w}_1.55_TM']/1.55)*1e3 # rad/mm
DK0=dk0(0.6); S=(dk0(0.64)-dk0(0.56))/40  # rad/mm per nm
LAM=2*np.pi/abs(DK0)  # mm
def domains(L,kind,sig=0.25):
    n=int(L/(LAM/2)); zc=(np.arange(n)+0.5)*LAM/2-L/2; s=np.where(np.arange(n)%2==0,1.,-1.)
    if kind=='gauss':  # deleted-domain: keep inverted domain if local target density says so (error diffusion)
        tgt=np.exp(-zc**2/(2*(sig*L)**2)); acc=0; keep=np.ones(n)
        for j in range(0,n,2):
            acc+=tgt[j]
            if acc>=0.5: acc-=1
            else: keep[j]=0; keep[j+1 if j+1<n else j]=0
        s=np.where(keep>0,s,1.0)*1.0; s=np.where(keep>0,s,np.where(np.arange(n)%2==0,1,1.))  # deleted pair -> both unflipped(+1 pair cancels? no: both +1)
        # deleted pair = two +1 half-domains -> contributes ~0 at QPM order
        s=np.where(keep>0,np.where(np.arange(n)%2==0,1.,-1.),1.)
    return zc,s
def pmf(zc,s,phi,dks,L):
    # Phi(d)= sum_j s_j exp(i(phi_j + d z_j)) ; phi_j = local accumulated mismatch phase relative to nominal
    h=LAM/2; return (s*np.exp(1j*phi))[None,:]@np.exp(1j*np.outer(zc,dks))*h
def purity(L,kind,phi=None,sig=0.25,tau=None,N=161,span=None,ret=False):
    zc,s=domains(L,kind,sig)
    # QPM: multiply by exp(-i*DK0... ) handled analytically: s_j already +-1 at half period; first-order component carries phase e^{i pi j}; demodulate:
    s=s*np.where(np.arange(len(s))%2==0,1.,-1.)   # demodulated (uniform -> all +1, deleted pair -> +1,-1 ~0)
    if phi is None: phi=np.zeros(len(zc))
    span=span or 12*2*np.pi/(min(abs(A),abs(B))*L)
    W=np.linspace(-span/2,span/2,N); Ws,Wi=np.meshgrid(W,W,indexing='ij')
    dks=np.unique(np.round((A*Ws+B*Wi).ravel(),9))
    Phi_line=pmf(zc,s,phi,dks,L).ravel()
    Phi=np.interp(A*Ws+B*Wi,dks,Phi_line.real)+1j*np.interp(A*Ws+B*Wi,dks,Phi_line.imag)
    def P(tau):
        f=np.exp(-((Ws+Wi)*tau)**2/2)*Phi; sv=np.linalg.svd(f,compute_uv=False)**2; sv/=sv.sum(); return (sv**2).sum()
    if tau is None:
        taus=np.geomspace(0.05,20,40)*L*np.sqrt(abs(A*B)); ps=[P(t) for t in taus]; i=int(np.argmax(ps))
        from scipy.optimize import minimize_scalar
        r=minimize_scalar(lambda x:-P(np.exp(x)),bracket=(np.log(taus[max(i-1,0)]),np.log(taus[i]),np.log(taus[min(i+1,39)])))
        tau=float(np.exp(r.x)); return (-r.fun,tau)
    return P(tau),tau
if __name__=="__main__":
    print('ng p,s,i',ngp,ngs,ngi,'A,B ps/mm',A,B,'Lambda um',LAM*1e3,'dDk/dt rad/mm/nm',S)
