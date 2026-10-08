import jax, jax.numpy as jnp, numpy as np
jax.config.update("jax_enable_x64", True)
from mesh import layout, fid, targets, adam, init, dc
def tdc(e, a=None, cph=0.):
    """coupler; if a is given: tunable coupler DC(e[1]) P(a) DC(e[0]) (double-MZI design). cph: unmodeled coupler phase residual"""
    R=jnp.diag(jnp.array([jnp.exp(1j*cph),1.]))
    if a is None: return R@dc(e)
    return R@dc(e[1])@jnp.diag(jnp.array([jnp.exp(1j*a),1.]))@dc(e[0])
def build2(p, err, N, lay, double=False):
    U=jnp.eye(N,dtype=complex)
    for k,m in enumerate(lay):
        P1=jnp.diag(jnp.array([jnp.exp(1j*(p['th'][k]+err['dth'][k])),1.]))
        P2=jnp.diag(jnp.array([jnp.exp(1j*(p['ph'][k]+err['dph'][k])),1.]))
        A=jnp.diag(jnp.array([jnp.exp(-err['loss'][k]),1.]))
        if double:
            c1=tdc((err['e1'][k],err['e1b'][k]),p['a1'][k],err['c1'][k]); c2=tdc((err['e2'][k],err['e2b'][k]),p['a2'][k],err['c2'][k])
        else:
            c1=tdc(err['e1'][k],None,err['c1'][k]); c2=tdc(err['e2'][k],None,err['c2'][k])
        U=U.at[m:m+2,:].set(c2@A@P1@c1@P2@U[m:m+2,:])
    return jnp.exp(1j*p['out'])[:,None]*U
KEYS=('e1','e2','e1b','e2b','dth','dph','loss','c1','c2')
def zeros(K): return {k:jnp.zeros(K) for k in KEYS}
def chip(key,K,sig,b=0.,soff=0.2,sres=0.,sl=0.):
    ks=jax.random.split(key,9); g=lambda i,s:s*jax.random.normal(ks[i],(K,))
    return dict(e1=b+g(0,sig),e2=b+g(1,sig),e1b=b+g(2,sig),e2b=b+g(3,sig),dth=g(4,soff),dph=g(5,soff),
                loss=sl*jnp.abs(g(6,1.)),c1=g(7,sres),c2=g(8,sres))
