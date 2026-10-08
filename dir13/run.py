import sys
from mesh import *
SIG=[0.0,0.02,0.05,0.1,0.15,0.2]; NT=200; NB=32; NCAL=16
tg=targets(); R={}
names=sys.argv[1].split(',') ; sph=float(sys.argv[2]) if len(sys.argv)>2 else 0.; sl=float(sys.argv[3]) if len(sys.argv)>3 else 0.
tag=sys.argv[4] if len(sys.argv)>4 else 'split'
for name in names:
  Ut=tg[name]; N=Ut.shape[0]
  for arch in ('clements','reck'):
    lay=layout(N,arch); K=len(lay); t0=time.time()
    f=lambda p,e: fid(Ut,build(p,e,N,lay))
    fb=jax.jit(jax.vmap(f,in_axes=(None,0)))
    # (a) ideal programming, best of restarts
    best=None
    for r in range(6):
      p,L=adam(lambda p:1-f(p,zero_err(K)),init(jax.random.PRNGKey(r),N,K),1500,0.05)
      if best is None or L<best[1]: best=(p,L)
    p0=best[0]; print(name,arch,'ideal infid',best[1],flush=True)
    for s in SIG:
      te=sample_err(jax.random.PRNGKey(999),NT,K,s,sph,sl)
      Fa=np.array(fb(p0,te))
      # (b) error-aware training
      pb,_=adam(lambda p,e:1-fb(p,e).mean(),p0,600,0.02,key=jax.random.PRNGKey(7),resample=lambda k:sample_err(k,NB,K,s,sph,sl))
      Fb=np.array(fb(pb,te))
      # (c) known-error calibration: per instance re-optimization (vmapped)
      ce=jax.tree.map(lambda a:a[:NCAL],te)
      P=jax.tree.map(lambda a:jnp.stack([a]*NCAL),p0)
      fc=jax.vmap(f,in_axes=(0,0))
      Pc,_=adam(lambda P:(1-fc(P,ce)).sum(),P,800,0.02)
      Fc=np.array(fc(Pc,ce))
      R[f'{name}|{arch}|{s}']=dict(a=[Fa.mean(),np.percentile(Fa,5)],b=[Fb.mean(),np.percentile(Fb,5)],c=[Fc.mean(),Fc.min()])
      print(name,arch,s,{k:np.round(v,5).tolist() for k,v in R[f'{name}|{arch}|{s}'].items()},round(time.time()-t0),flush=True)
    json.dump({k:{kk:[float(x) for x in vv] for kk,vv in v.items()} for k,v in R.items()},open(f'res_{tag}_{"_".join(names)}.json','w'),indent=1)
