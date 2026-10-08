# Part 1 (wafer bias), Part 2 (per-chip characterization methods), Part 3 (double-MZI fix)
import sys, json, time
from mesh2 import *
part=sys.argv[1]; tg=targets(); out={}
def p_ideal(Ut,N,lay,double=False):
    K=len(lay); best=None
    for r in range(4):
        p=init(jax.random.PRNGKey(r),N,K)
        if double: p['a1']=jnp.full(K,jnp.pi/2); p['a2']=jnp.full(K,jnp.pi/2)
        p,L=adam(lambda p:1-fid(Ut,build2(p,zeros(K),N,lay,double)),p,1500,0.05)
        if best is None or L<best[1]: best=(p,L)
    return best[0]
def calibrate(Ut,N,lay,p0,errs,steps=800,double=False):  # errs batched (n,K); returns per-chip params
    n=errs['e1'].shape[0]; P=jax.tree.map(lambda a:jnp.stack([a]*n),p0)
    fc=jax.vmap(lambda p,e:fid(Ut,build2(p,e,N,lay,double)))
    P,_=adam(lambda P:(1-fc(P,errs)).sum(),P,steps,0.02); return P,fc
NAMES=['F3','F4','H2xH2','Toffoli']
if part=='bias':
    b,sr,sm=0.15,0.03,0.01; NCH=64
    for nm in NAMES:
        Ut=tg[nm]; N=Ut.shape[0]; lay=layout(N,'clements'); K=len(lay); p0=p_ideal(Ut,N,lay)
        chips=jax.vmap(lambda k:chip(k,K,sr,b,soff=0.))(jax.random.split(jax.random.PRNGKey(5),NCH))
        fb=jax.jit(jax.vmap(lambda e,p=None:0.))
        for M in [0,1,2,4,8,16,32]:
            rng=np.random.default_rng(M); bh=0. if M==0 else b+rng.normal(0,np.sqrt(sr**2+sm**2)/np.sqrt(M))
            e=zeros(K); e['e1']=e['e1']+bh; e['e2']=e['e2']+bh
            pb,_=adam(lambda p:1-fid(Ut,build2(p,e,N,lay)),p0,600,0.02)
            F=np.array(jax.vmap(lambda c:fid(Ut,build2(pb,c,N,lay)))(chips))
            out[f'{nm}|{M}']=dict(bhat=float(bh),F=float(F.mean()),F5=float(np.percentile(F,5))); print(nm,M,out[f'{nm}|{M}'],flush=True)
if part=='fit':
    nm=sys.argv[2]; COH=int(sys.argv[5]); sig=0.1; sres=float(sys.argv[3]); NCH=4; tag=sys.argv[4]
    Ut=tg[nm]; N=Ut.shape[0]; lay=layout(N,'clements'); K=len(lay); p0=p_ideal(Ut,N,lay)
    chips=jax.vmap(lambda k:chip(k,K,sig,0.,0.2,sres))(jax.random.split(jax.random.PRNGKey(11),NCH))
    est_keys=('e1','e2','dth','dph')
    def fill(est): e=zeros(K); e.update(est); return e
    def eval_est(ests):  # ests batched; calibrate on estimate, evaluate on truth
        E=jax.vmap(fill)(ests); P,_=calibrate(Ut,N,lay,p0,E,600)
        return np.array(jax.vmap(lambda p,c:fid(Ut,build2(p,c,N,lay)))(P,chips))
    F_none=np.array(jax.vmap(lambda c:fid(Ut,build2(p0,c,N,lay)))(chips))
    F_oracle=eval_est({k:chips[k] for k in est_keys})
    out['none']=float(F_none.mean()); out['oracle']=float(F_oracle.mean()); print(nm,'none',out['none'],'oracle',out['oracle'],flush=True)
    for nph in [1e4,1e6]:
      # --- method A/C: global model fit to classical-light intensity data at S random phase settings
      for S in [1,2,4,8,16]:
        key=jax.random.PRNGKey(S)
        sets=init(key,N,K); sets={k:jax.random.uniform(jax.random.fold_in(key,i),(S,)+v.shape)*2*np.pi for i,(k,v) in enumerate(sets.items())}
        V=[np.eye(N)[i] for i in range(N)]
        if COH: V+= [(np.eye(N)[i]+np.eye(N)[i+1])/np.sqrt(2) for i in range(N-1)]+[(np.eye(N)[i]+1j*np.eye(N)[i+1])/np.sqrt(2) for i in range(N-1)]
        V=jnp.array(np.array(V).T,dtype=complex); NIN=V.shape[1]
        def inten(e1):  # (S,N,NIN) output powers for chip errors e1, input vectors V (single-port + coherent pairs)
            return jax.vmap(lambda p:jnp.abs(build2(p,e1,N,lay)@V)**2)(sets)
        D=jax.vmap(inten)(chips)
        D=D+jax.random.normal(jax.random.PRNGKey(77+S),D.shape)*jnp.sqrt(jnp.maximum(D,1e-12)/nph)  # shot noise, nph photons per injection
        for meth,lam in (('MAP',1.),):
            def loss(est,Dc):
                r=inten(fill(est))-Dc; pri=sum(((est[k]/(sig if k in('e1','e2') else 0.2))**2).sum() for k in est_keys)
                return (r**2).sum()*nph/2 + lam*pri/2   # ~ neg log-likelihood (Gaussian shot noise approx, var~D/nph ~ 1/(N nph))
            def fit1(Dc):
                g=jax.value_and_grad(loss); est={k:jnp.zeros(K) for k in est_keys}
                m=jax.tree.map(jnp.zeros_like,est); v=jax.tree.map(jnp.zeros_like,est)
                def step(c,i):
                    est,m,v=c; L,gr=g(est,Dc); m=jax.tree.map(lambda a,b:0.9*a+0.1*b,m,gr); v=jax.tree.map(lambda a,b:0.999*a+0.001*b*b,v,gr)
                    est=jax.tree.map(lambda a,b,cc:a-0.01*(b/(1-0.9**i))/(jnp.sqrt(cc/(1-0.999**i))+1e-12),est,m,v); return (est,m,v),L
                (est,_,_),_=jax.lax.scan(step,(est,m,v),jnp.arange(1,2001)); return est
            ests=jax.jit(jax.vmap(fit1))(D)
            F=eval_est(ests); err=float(np.sqrt(np.mean([(np.array(ests[k])-np.array(chips[k]))**2 for k in ('e1','e2')])))
            out[f'{meth}|{nph:g}|{S}']=dict(readings=S*N*NIN,ph_rmse=float(np.sqrt(np.mean([(np.array(ests[k])-np.array(chips[k]))**2 for k in ('dth','dph')]))),F=float(F.mean()),Fmin=float(F.min()),eps_rmse=err); print(nm,meth,nph,S,out[f'{meth}|{nph:g}|{S}'],flush=True)
      # --- method B: sequential per-MZI sweeps (assumes each MZI can be isolated; optimistic)
      for Pn in [4,8,16,32]:
        th=jnp.linspace(0,2*np.pi,Pn,endpoint=False)
        def Tbar(e1,e2,d,t): c1,s1,c2,s2=jnp.cos(np.pi/4+e1),jnp.sin(np.pi/4+e1),jnp.cos(np.pi/4+e2),jnp.sin(np.pi/4+e2); return jnp.abs(c2*c1*jnp.exp(1j*(t+d))-s2*s1)**2
        def fitB(e1,e2,d,key):
            y=Tbar(e1,e2,d,th); y=y+jax.random.normal(key,y.shape)*jnp.sqrt(jnp.maximum(y,1e-12)/nph)
            L=lambda q:((Tbar(q[0],q[1],q[2],th)-y)**2).sum()
            q=jnp.array([0.01,-0.01,0.]); m=jnp.zeros(3); v=jnp.zeros(3); gL=jax.grad(L)
            def st(c,i):
                q,m,v=c; g=gL(q); m=0.9*m+0.1*g; v=0.999*v+0.001*g*g; return (q-0.01*(m/(1-0.9**i))/(jnp.sqrt(v/(1-0.999**i))+1e-12),m,v),0
            (q,_,_),_=jax.lax.scan(st,(q,m,v),jnp.arange(1,2001))
            # swap ambiguity: pick ordering e1>=e2 (no information); phase dph from 2nd sweep of same quality
            return q
        ests={k:[] for k in est_keys}
        keys=jax.random.split(jax.random.PRNGKey(1000+Pn),NCH*K*2).reshape(NCH,K,2,2)
        fB=jax.jit(jax.vmap(jax.vmap(fitB)))
        q=fB(chips['e1'],chips['e2'],chips['dth'],keys[:,:,0])
        q2=fB(chips['e2'],chips['e1'],chips['dph'],keys[:,:,1])  # 2nd sweep (external phase via neighbour), same model
        est=dict(e1=0*q[...,0],e2=0*q[...,1],dth=q[...,2],dph=q2[...,2])
        F=eval_est(est); err=float(np.sqrt(np.mean([(np.array(est[k])-np.array(chips[k]))**2 for k in ('e1','e2')])))
        out[f'SEQ|{nph:g}|{Pn}']=dict(readings=2*K*Pn,F=float(F.mean()),Fmin=float(F.min()),eps_rmse=err); print(nm,'SEQ',nph,Pn,out[f'SEQ|{nph:g}|{Pn}'],flush=True)
    part=f'fit_{nm}_{tag}'
if part=='double':
    for nm in ['H2xH2','Toffoli','F4']:
        Ut=tg[nm]; N=Ut.shape[0]; lay=layout(N,'clements'); K=len(lay)
        for dbl in (False,True):
            p0=p_ideal(Ut,N,lay,dbl)
            for sig in [0.05,0.1,0.2,0.3]:
                chips=jax.vmap(lambda k:chip(k,K,sig,0.,0.))(jax.random.split(jax.random.PRNGKey(3),8))
                P,fc=calibrate(Ut,N,lay,p0,chips,1500,dbl); F=np.array(fc(P,chips))
                out[f'{nm}|{dbl}|{sig}']=dict(F=float(F.mean()),Fmin=float(F.min())); print(nm,dbl,sig,out[f'{nm}|{dbl}|{sig}'],flush=True)
json.dump(out,open(f'res2_{part}.json','w'),indent=1)
