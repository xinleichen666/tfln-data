# Round1 experiments. Period-level model: weight q_j in {0,1} (deleted-domain) or 1 (uniform); local phase phi(z).
import json,os,numpy as np
from jsa import A,B,S,LAM
from scipy.optimize import minimize_scalar
rng=np.random.default_rng(1)
def weights(L,kind,sig=0.25):
    n=int(L/LAM); z=(np.arange(n)+0.5)*LAM-L/2
    if kind=='uni': return z,np.ones(n)
    tgt=np.exp(-z**2/(2*(sig*L)**2)); q=np.zeros(n); acc=0.
    for j in range(n):
        acc+=tgt[j]
        if acc>=0.5: q[j]=1; acc-=1
    return z,q
def grids(L,N=128):
    span=14*2*np.pi/(abs(B)*L)*np.sqrt(abs(B/A))**0.5
    W=np.linspace(-span/2,span/2,N); return np.meshgrid(W,W,indexing='ij')
def Phi(z,q,phi,Ws,Wi):
    d=A*Ws+B*Wi; dl=np.linspace(d.min(),d.max(),2000)
    line=(q*np.exp(1j*phi))@np.exp(1j*np.outer(z,dl))
    return np.interp(d,dl,line.real)+1j*np.interp(d,dl,line.imag)
def P(F,Ws,Wi,tau,chirp=0.):
    f=np.exp(-((Ws+Wi)*tau)**2/2+1j*chirp*(Ws+Wi)**2)*F; sv=np.linalg.svd(f,compute_uv=False)**2; sv/=sv.sum(); return float((sv**2).sum())
def best(F,Ws,Wi,L,chirp=0.):
    r=minimize_scalar(lambda x:-P(F,Ws,Wi,np.exp(x),chirp),bounds=(np.log(0.05*L),np.log(20*L)),method='bounded'); return -r.fun,float(np.exp(r.x))
def gp(z,sig_nm,lc):  # Gaussian-correlated thickness error (nm)
    if sig_nm==0: return np.zeros_like(z)
    dz=z[1]-z[0]; k=np.exp(-(np.arange(-int(3*lc/dz),int(3*lc/dz)+1)*dz)**2/(2*lc**2))
    x=np.convolve(rng.standard_normal(len(z)+len(k)-1),k,'valid'); x=x/x.std()*sig_nm; return x-x.mean()
def phase(z,dt): return np.cumsum(S*dt)*(z[1]-z[0])
out='data/run1.json'; R=json.load(open(out)) if os.path.exists(out) else {}
def save(): json.dump(R,open(out,'w'),indent=1)
L=5.0; Ws,Wi=grids(L)
# E1 ideal: uniform vs gaussian (scan sigma)
if 'E1' not in R:
    z,q=weights(L,'uni'); pu=best(Phi(z,q,0*z,Ws,Wi),Ws,Wi,L)
    sg={}
    for s in (0.15,0.2,0.25,0.3,0.35):
        z,q=weights(L,'gauss',s); sg[s]=best(Phi(z,q,0*z,Ws,Wi),Ws,Wi,L)+(float(q.mean()),)
    R['E1']={'uniform':pu,'gauss':sg}; save()
print('E1',R['E1'])
# convergence check
if 'conv' not in R:
    z,q=weights(L,'gauss',0.25); W2=grids(L,192); R['conv']=best(Phi(z,q,0*z,*W2),*W2,L); save()
print('conv N=192',R['conv'])
# E2/E3: thickness nonuniformity, ensemble of 12; strategies: none / adapted poling with map error eps
for sig in (0.5,1.0,2.0,4.0):
  for lc in (0.5,2.0):
    k=f'E2_{sig}_{lc}'
    if k in R: continue
    res={'none':[],'adapt20':[],'adapt0':[],'bright_none':[],'bright_adapt0':[]}
    z,q=weights(L,'gauss',0.25); F0=Phi(z,q,0*z,Ws,Wi); b0=abs(F0).max()**2
    for r in range(12):
        dt=gp(z,sig,lc); ph=phase(z,dt)
        for name,ph2 in (('none',ph),('adapt20',0.2*ph),('adapt0',0*ph)):
            F=Phi(z,q,ph2,Ws,Wi); res[name].append(best(F,Ws,Wi,L)[0])
            if name in('none','adapt0'): res['bright_'+name].append(float(abs(F).max()**2/b0))
    R[k]={a:[float(np.mean(v)),float(np.std(v))] for a,v in res.items()}; save(); print(k,R[k],flush=True)
# E4 pump chirp (quadratic spectral phase C, in units of tau_opt^2)
if 'E4' not in R:
    z,q=weights(L,'gauss',0.25); F=Phi(z,q,0*z,Ws,Wi); p0,t0=best(F,Ws,Wi,L)
    R['E4']={str(c):P(F,Ws,Wi,t0,c*t0**2) for c in (0,0.25,0.5,1,2)}; save()
print('E4',R['E4'])
