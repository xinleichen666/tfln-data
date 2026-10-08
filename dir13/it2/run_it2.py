# Iteration 2: fair head-to-head of clear-box characterization (Fyrillas-2024-like) vs coherent-pair variant,
# with/without crosstalk parameters, equal sample budget. d=4 Clements, 50 chips.
import sys,json,time,numpy as np,jax,jax.numpy as jnp
sys.path.insert(0,'/workspace/dir13'); from lib4 import dc,ph,adam_scan
from mesh import layout
from functools import partial
N=int(sys.argv[1]) if len(sys.argv)>1 else 4
lay=layout(N,'clements'); K=len(lay); NP=2*K
SIG,SOFF,NPH,NCH=0.05,0.3,1e6,int(sys.argv[2]) if len(sys.argv)>2 else 50
def U_of(set_th,set_ph,out,m):  # m: model dict e1,e2,d(2K),X(2K,2K)
    s=jnp.concatenate([set_th,set_ph]); r=s+m['d']+m['X']@s
    th,phh=r[:K],r[K:]
    U=jnp.eye(N,dtype=complex)
    for k,mm in enumerate(lay):
        T=dc(m['e2'][k])@ph(th[k])@dc(m['e1'][k])@ph(phh[k]); U=U.at[mm:mm+2,:].set(T@U[mm:mm+2,:])
    return jnp.exp(1j*out)[:,None]*U
def fidp(Ut,M): d=Ut.shape[0]; return jnp.abs(jnp.trace(Ut.conj().T@M))**2/d**2
def fid_gauge(Ut,M):  # max over input/output diagonal phases (alternating maximisation)
    A=Ut.conj().T  # maximise |sum_ij A_ji D1_i M_ij D2_j|
    d2=jnp.ones(N,dtype=complex)
    for _ in range(20):
        d1=jnp.exp(-1j*jnp.angle(jnp.einsum('ji,ij,j->i',A,M,d2))); d2=jnp.exp(-1j*jnp.angle(jnp.einsum('ji,ij,i->j',A,M,d1)))
    return jnp.abs(jnp.einsum('ji,ij,i,j->',A,M,d1,d2))**2/N**2
def famp(Ut,M): return jnp.sum(jnp.abs(Ut)*jnp.abs(M))/N
INS=[np.eye(N)[i] for i in range(N)]
COH=[(np.eye(N)[i]+np.eye(N)[i+1])/np.sqrt(2) for i in range(N-1)]+[(np.eye(N)[i]+1j*np.eye(N)[i+1])/np.sqrt(2) for i in range(N-1)]
INS=jnp.array(np.array(INS),dtype=complex); COH=jnp.array(np.array(COH),dtype=complex)
def truth(key,xt):
    k=jax.random.split(key,5)
    X=jnp.zeros((NP,NP))
    if xt>0:  # thermal-like nearest-neighbour crosstalk between physically adjacent heaters (index-adjacent)
        off=xt*jax.random.uniform(k[3],(NP-1,)); X=X+jnp.diag(off,1)+jnp.diag(off,-1)
    return dict(e1=SIG*jax.random.normal(k[0],(K,)),e2=SIG*jax.random.normal(k[1],(K,)),d=SOFF*jax.random.normal(k[2],(NP,)),X=X)
def meas(m,S,V,key):  # S: settings (n,2K), V: input vectors (n,N) -> noisy normalized distributions
    out0=jnp.zeros(N)
    P=jax.vmap(lambda s,v:jnp.abs(U_of(s[:K],s[K:],out0,m)@v)**2)(S,V)
    P=P+jax.random.normal(key,P.shape)*jnp.sqrt(jnp.maximum(P,1e-12)/NPH)
    return P/P.sum(1,keepdims=True)
def pred(m,S,V):
    out0=jnp.zeros(N); P=jax.vmap(lambda s,v:jnp.abs(U_of(s[:K],s[K:],out0,m)@v)**2)(S,V); return P/P.sum(1,keepdims=True)
def fit(S,V,P,useX,m0,steps=3000):
    def loss(m):
        mm=dict(m); 
        if not useX: mm['X']=jnp.zeros((NP,NP))
        r=pred(mm,S,V)-P
        pri=((m['e1']/SIG)**2).sum()+((m['e2']/SIG)**2).sum()+((m['d']/SOFF)**2).sum()+(useX*(m['X']/0.02)**2).sum()
        return (r**2).sum()*NPH*N/2+pri/2
    m,_=adam_scan(loss,m0,steps,0.005)
    if not useX: m=dict(m); m['X']=jnp.zeros((NP,NP))
    return m
def phi_ifm(m,true,key,P_=8):  # Fyrillas-style phase fringe: sweep each phase shifter, re-estimate its passive offset by grid search
    ks=jax.random.split(key,NP); base=jax.random.uniform(key,(NP,))*2*np.pi
    grid=jnp.linspace(-np.pi,np.pi,129)
    def one(k,kk):
        mz=k%K; port=jnp.array(lay)[mz]
        sw=jnp.linspace(0,2*np.pi,P_,endpoint=False)
        S=jnp.tile(base,(P_,1)).at[:,k].set(sw); V=jnp.tile(INS[port],(P_,1))
        y=meas(true,S,V,kk)
        def cost(g): mm=dict(m); mm['d']=m['d'].at[k].set(g); return ((pred(mm,S,V)-y)**2).sum()
        c=jax.vmap(cost)(grid); return grid[jnp.argmin(c)]
    newd=jax.vmap(one)(jnp.arange(NP),ks)
    mm=dict(m); mm['d']=newd; return mm
def compile_eval(Ut,mest,true):
    p0=dict(th=jnp.zeros(K)+1.0,ph=jnp.zeros(K)+0.5,out=jnp.zeros(N))
    best=None
    def L(p): return 1-fidp(Ut,U_of(p['th'],p['ph'],p['out'],mest))
    ps=[adam_scan(L,dict(th=jax.random.uniform(jax.random.PRNGKey(r),(K,))*2*np.pi,ph=jax.random.uniform(jax.random.PRNGKey(r+9),(K,))*2*np.pi,out=jnp.zeros(N)),2000,0.03) for r in range(3)]
    Ls=jnp.array([q[1] for q in ps]); i=jnp.argmin(Ls)
    p=jax.tree.map(lambda *a:jnp.stack(a)[i],*[q[0] for q in ps])
    M=U_of(p['th'],p['ph'],p['out'],true)
    return jnp.array([fidp(Ut,M),fid_gauge(Ut,M),famp(Ut,M)])
@partial(jax.jit,static_argnums=(2,3,4,5))
def run_chip(key,Ut,xt,ns,method,useX):
    k=jax.random.split(key,6); tr=truth(k[0],xt)
    m0=dict(e1=jnp.zeros(K),e2=jnp.zeros(K),d=jnp.zeros(NP),X=jnp.zeros((NP,NP)))
    n_ifm=NP*8 if method=='fyr' else 0
    n1=ns-n_ifm; S=jax.random.uniform(k[1],(n1,NP))*2*np.pi
    if method=='coh':
        pool=jnp.concatenate([INS,COH]); V=pool[jax.random.randint(k[2],(n1,),0,pool.shape[0])]
    else: V=INS[jax.random.randint(k[2],(n1,),0,N)]
    P=meas(tr,S,V,k[3])
    if method=='fyr':  # ML -> phi-IFM -> ML (one iteration of Fyrillas loop)
        m=fit(S,V,P,useX,m0,1500); m=phi_ifm(m,tr,k[4]); m=fit(S,V,P,useX,m,1500)
    else: m=fit(S,V,P,useX,m0)
    res=compile_eval(Ut,m,tr)
    err=jnp.array([jnp.sqrt(jnp.mean((m['e1']-tr['e1'])**2)),jnp.sqrt(jnp.mean((m['d']-tr['d'])**2))])
    return jnp.concatenate([res,err])
def dft(d): w=np.exp(2j*np.pi/d); return np.array([[w**(i*j) for j in range(d)] for i in range(d)])/np.sqrt(d)
Ut=jnp.array(dft(N),dtype=complex)
npar_red=2*K+NP; npar_full=npar_red+NP*NP
out={}; t0=time.time()
for xt in (0.0,0.04):
  for ratio in (1,4,8,16):
    ns=int(ratio*npar_red) if True else 0
    for method,useX in (('fyr',True),('fyr',False),('int',False),('coh',False)):
        ns_m=max(ns, NP*8+8) if method=='fyr' else max(ns,NP*8+8)  # equal budget incl. phi-IFM cost
        R=np.array(jax.lax.map(lambda kk:run_chip(kk,Ut,xt,ns_m,method,useX),jax.random.split(jax.random.PRNGKey(100+int(xt*100)),NCH)))
        key=f'xt{xt}|r{ratio}|{method}|X{int(useX)}'
        out[key]=dict(samples=ns_m,inf_proc=(1-R[:,0]).tolist(),inf_gauge=(1-R[:,1]).tolist(),inf_amp=(1-R[:,2]).tolist(),eps_rmse=R[:,3].tolist(),d_rmse=R[:,4].tolist())
        print(key,ns_m,'1-Fproc %.2e 1-Fgauge %.2e 1-Famp %.2e epsRMSE %.3f dRMSE %.3f'%tuple(np.median(np.c_[1-R[:,:3],R[:,3:]],0)),f'{time.time()-t0:.0f}s',flush=True)
        json.dump(out,open(f'/workspace/dir13/it2/res_it2_N{N}.json','w'))
