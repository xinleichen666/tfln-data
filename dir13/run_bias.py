# systematic (wafer-level) coupler bias b plus random sigma: (a) ideal-programmed, (b') bias-aware trained (b known from test DCs), (b) error-aware with unknown symmetric bias
from mesh import *
R={}
for name in ('F3','Toffoli'):
  Ut=targets()[name]; N=Ut.shape[0]; lay=layout(N,'clements'); K=len(lay)
  f=lambda p,e: fid(Ut,build(p,e,N,lay)); fb=jax.jit(jax.vmap(f,in_axes=(None,0)))
  best=min([adam(lambda p:1-f(p,zero_err(K)),init(jax.random.PRNGKey(r),N,K),1500,0.05) for r in range(6)],key=lambda x:x[1]); p0=best[0]
  for b in (0.05,0.1,0.2):
    s=0.02
    def samp(k,n,bb=b):
      e=sample_err(k,n,K,s); e['e1']=e['e1']+bb; e['e2']=e['e2']+bb; return e
    te=samp(jax.random.PRNGKey(999),200)
    Fa=np.array(fb(p0,te))
    pb,_=adam(lambda p,e:1-fb(p,e).mean(),p0,800,0.02,key=jax.random.PRNGKey(3),resample=lambda k:samp(k,32))
    Fb=np.array(fb(pb,te))
    R[f'{name}|b={b}|s={s}']=dict(ideal=float(Fa.mean()),bias_aware=float(Fb.mean()),bias_aware_p5=float(np.percentile(Fb,5)))
    print(name,b,R[f'{name}|b={b}|s={s}'],flush=True)
json.dump(R,open('res_bias.json','w'),indent=1)
