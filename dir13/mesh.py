import jax, jax.numpy as jnp, numpy as np, json, time
jax.config.update("jax_enable_x64", True)
def layout(N, arch):
    """list of (top mode index) for each MZI in order"""
    if arch=='clements':
        return [m for c in range(N) for m in range(c%2, N-1, 2)]
    ms=[]  # reck: triangular
    for k in range(N-1):
        for m in range(k,-1,-1): ms.append(m)
    return ms
def dc(eps):  # directional coupler, nominal 50:50 => t=pi/4
    t=jnp.pi/4+eps; c,s=jnp.cos(t),jnp.sin(t)
    return jnp.array([[c,1j*s],[1j*s,c]])
def build(params, err, N, lay):
    th,ph,out=params['th'],params['ph'],params['out']
    U=jnp.eye(N,dtype=complex)
    for k,m in enumerate(lay):
        P1=jnp.diag(jnp.array([jnp.exp(1j*(th[k]+err['dth'][k])),1.]))
        P2=jnp.diag(jnp.array([jnp.exp(1j*(ph[k]+err['dph'][k])),1.]))
        A=jnp.diag(jnp.array([jnp.exp(-err['loss'][k]),1.]))  # differential loss on internal arm (amplitude)
        T=dc(err['e2'][k])@A@P1@dc(err['e1'][k])@P2
        U=U.at[m:m+2,:].set(T@U[m:m+2,:])
    return jnp.exp(1j*out)[:,None]*U
def fid(Ut,M):  # normalized (post-selected) process fidelity = |Tr(Ut^+ M)|^2/(d Tr(M^+M))
    d=Ut.shape[0]; return jnp.abs(jnp.trace(Ut.conj().T@M))**2/(d*jnp.real(jnp.trace(M.conj().T@M)))
def sample_err(key,n,K,sig,sph=0.,sl=0.):
    k=jax.random.split(key,4)
    return dict(e1=sig*jax.random.normal(k[0],(n,K)),e2=sig*jax.random.normal(k[1],(n,K)),
                dth=sph*jax.random.normal(k[2],(n,K)),dph=jnp.zeros((n,K)),
                loss=sl*jnp.abs(jax.random.normal(k[3],(n,K))))
def zero_err(K): z=jnp.zeros(K); return dict(e1=z,e2=z,dth=z,dph=z,loss=z)
def adam(lossf, p, steps, lr=0.05, key=None, resample=None):
    g=jax.jit(jax.value_and_grad(lossf)); m=jax.tree.map(jnp.zeros_like,p); v=jax.tree.map(jnp.zeros_like,p)
    for i in range(1,steps+1):
        args=() if resample is None else (resample(jax.random.fold_in(key,i)),)
        L,gr=g(p,*args)
        m=jax.tree.map(lambda a,b:0.9*a+0.1*b,m,gr); v=jax.tree.map(lambda a,b:0.999*a+0.001*b*b,v,gr)
        p=jax.tree.map(lambda a,b,c:a-lr*(b/(1-0.9**i))/(jnp.sqrt(c/(1-0.999**i))+1e-9),p,m,v)
    return p,float(L)
def init(key,N,K): k=jax.random.split(key,3); return dict(th=jax.random.uniform(k[0],(K,))*2*np.pi,ph=jax.random.uniform(k[1],(K,))*2*np.pi,out=jax.random.uniform(k[2],(N,))*2*np.pi)
def targets():
    T={}
    for d in (3,4):
        w=np.exp(2j*np.pi/d); T[f'F{d}']=np.array([[w**(i*j) for j in range(d)] for i in range(d)])/np.sqrt(d)
    H=np.array([[1,1],[1,-1]])/np.sqrt(2); T['H2xH2']=np.kron(H,H)
    P=np.eye(8); P[[6,7]]=P[[7,6]]; T['Toffoli']=P
    return {k:jnp.array(v,dtype=complex) for k,v in T.items()}
