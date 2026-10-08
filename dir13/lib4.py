import jax, jax.numpy as jnp, numpy as np
jax.config.update("jax_enable_x64", True)
from mesh import layout, fid
def dc(e):
    t=jnp.pi/4+e; c,s=jnp.cos(t),jnp.sin(t); return jnp.array([[c,1j*s],[1j*s,c]])
def ph(x): return jnp.diag(jnp.array([jnp.exp(1j*x),1.+0j]))
SW=jnp.array([[0,1],[1,0]],dtype=complex)
def coupler(e,eb,a,h):  # h=1 -> tunable double-MZI coupler
    return jnp.where(h>0, dc(eb)@ph(a)@dc(e), dc(e))
def build(p,E,N,lay,arch,H):
    """arch: 'std','3mzi','mzix','dbl' (H mask selects doubled couplers; 'dbl'=all)"""
    U=jnp.eye(N,dtype=complex)
    for k,m in enumerate(lay):
        if arch=='3mzi':
            T=dc(E['e2'][k])@ph(p['th'][k]+E['dth'][k])@dc(E['e1'][k])@ph(p['ph'][k]+E['dph'][k])@dc(E['e0'][k])
        else:
            c1=coupler(E['e1'][k],E['e1b'][k],p['a1'][k],H[k]); c2=coupler(E['e2'][k],E['e2b'][k],p['a2'][k],H[k])
            T=c2@ph(p['th'][k]+E['dth'][k])@c1@ph(p['ph'][k]+E['dph'][k])
            if arch=='mzix': T=SW@T
        U=U.at[m:m+2,:].set(T@U[m:m+2,:])
    return jnp.exp(1j*p['out'])[:,None]*U
def adam_scan(lossf,p,steps,lr):
    g=jax.value_and_grad(lossf)
    def step(c,i):
        p,m,v=c; L,gr=g(p)
        m=jax.tree.map(lambda a,b:0.9*a+0.1*b,m,gr); v=jax.tree.map(lambda a,b:0.999*a+0.001*b*b,v,gr)
        p=jax.tree.map(lambda a,b,c:a-lr*(b/(1-0.9**i))/(jnp.sqrt(c/(1-0.999**i))+1e-10),p,m,v)
        return (p,m,v),L
    z=jax.tree.map(jnp.zeros_like,p)
    (p,_,_),Ls=jax.lax.scan(step,(p,z,z),jnp.arange(1,steps+1,dtype=float))
    return p,Ls[-1]
def zeroE(K): z=jnp.zeros(K); return dict(e0=z,e1=z,e2=z,e1b=z,e2b=z,dth=z,dph=z)
def chips(key,n,K,sig,b=0.):
    ks=jax.random.split(key,5); g=lambda i:b+sig*jax.random.normal(ks[i],(n,K))
    z=jnp.zeros((n,K)); return dict(e0=g(0),e1=g(1),e2=g(2),e1b=g(3),e2b=g(4),dth=z,dph=z)
def initp(key,N,K):
    k=jax.random.split(key,3); u=lambda i,s:jax.random.uniform(k[i],s)*2*jnp.pi
    return dict(th=u(0,(K,)),ph=u(1,(K,)),out=u(2,(N,)),a1=jnp.full(K,jnp.pi/2),a2=jnp.full(K,jnp.pi/2))
