# Head-to-head: standard MZI vs Hamerly 3-splitter MZI (extra 50:50 splitter at MZI input) vs double-MZI couplers (Miller/Suzuki-type),
# known-error calibration (global gradient), same chips. Writes res3_3mzi.json
import json, numpy as np, jax, jax.numpy as jnp
from mesh2 import *
def build3(p, err, N, lay):
    U=jnp.eye(N,dtype=complex)
    for k,m in enumerate(lay):
        P1=jnp.diag(jnp.array([jnp.exp(1j*p['th'][k]),1.])); P2=jnp.diag(jnp.array([jnp.exp(1j*p['ph'][k]),1.]))
        T=dc(err['e2'][k])@P1@dc(err['e1'][k])@P2@dc(err['e0'][k])   # third splitter at the input
        U=U.at[m:m+2,:].set(T@U[m:m+2,:])
    return jnp.exp(1j*p['out'])[:,None]*U
out={}
for nm in ['H2xH2','Toffoli','F4']:
    Ut=targets()[nm]; N=Ut.shape[0]; lay=layout(N,'clements'); K=len(lay)
    best=None
    for r in range(4):
        p,L=adam(lambda p:1-fid(Ut,build3(p,{'e0':jnp.zeros(K),'e1':jnp.zeros(K),'e2':jnp.zeros(K)},N,lay)),init(jax.random.PRNGKey(r),N,K),1500,0.05)
        if best is None or L<best[1]: best=(p,L)
    p0=best[0]
    for sig in [0.05,0.1,0.2,0.3]:
        ch=jax.vmap(lambda k:chip(k,K,sig,0.,0.))(jax.random.split(jax.random.PRNGKey(3),8))  # same seeds as run2 'double'
        E=dict(e0=ch['e1b'],e1=ch['e1'],e2=ch['e2'])
        P=jax.tree.map(lambda a:jnp.stack([a]*8),p0); fc=jax.vmap(lambda p,e:fid(Ut,build3(p,e,N,lay)))
        P,_=adam(lambda P:(1-fc(P,E)).sum(),P,1500,0.02); F=np.array(fc(P,E))
        out[f'{nm}|3MZI|{sig}']=dict(F=float(F.mean()),Fmin=float(F.min())); print(nm,sig,out[f'{nm}|3MZI|{sig}'],flush=True)
json.dump(out,open('res3_3mzi.json','w'),indent=1)
