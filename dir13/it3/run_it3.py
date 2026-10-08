# Iteration 3 pilot: tracking slow phase drift (TFLN DC drift modelled as random walk of passive phases) with warm-start MAP updates
import sys,json,numpy as np,jax,jax.numpy as jnp
sys.path.insert(0,'/workspace/dir13/it2'); sys.argv=['x','4','1']
src=open('/workspace/dir13/it2/run_it2.py').read().split('def dft(d)')[0]; exec(src)
from lib4 import adam_scan
def fit_prior(S,V,P,m0,sd,steps=800):
    def loss(m):
        r=pred(m,S,V)-P
        return (r**2).sum()*NPH*N/2+(((m['d']-m0['d'])/sd)**2).sum()/2+(((m['e1']-m0['e1'])/0.01)**2).sum()/2+(((m['e2']-m0['e2'])/0.01)**2).sum()/2
    return adam_scan(loss,m0,steps,0.005)[0]
def dft(d): w=np.exp(2j*np.pi/d); return np.array([[w**(i*j) for j in range(d)] for i in range(d)])/np.sqrt(d)
Ut=jnp.array(dft(N),dtype=complex)
@partial(jax.jit,static_argnums=(1,2))
def track(key,b,T,q):
    k=jax.random.split(key,4); tr=truth(k[0],0.)
    S=jax.random.uniform(k[1],(200,NP))*2*np.pi; V=INS[jax.random.randint(k[2],(200,),0,N)]
    m=fit(S,V,meas(tr,S,V,k[3]),False,dict(e1=jnp.zeros(K),e2=jnp.zeros(K),d=jnp.zeros(NP),X=jnp.zeros((NP,NP))),3000)
    def step(c,i):
        tr,m,key=c; key,a,b1,b2,b3=jax.random.split(key,5)
        tr=dict(tr); tr['d']=tr['d']+q*jax.random.normal(a,(NP,))
        Fstale=compile_eval(Ut,m,tr)[1]
        if b>0:
            S=jax.random.uniform(b1,(b,NP))*2*np.pi; V=INS[jax.random.randint(b2,(b,),0,N)]
            m=fit_prior(S,V,meas(tr,S,V,b3),m,jnp.sqrt(q**2+0.01**2))
        F=compile_eval(Ut,m,tr)[1]
        return (tr,m,key),jnp.array([Fstale,F])
    _,Fs=jax.lax.scan(step,(tr,m,k[3]),jnp.arange(T)); return Fs
out={}
for q in (0.02,0.05):
  for b in (0,2,4,8,16):
    R=np.array(jax.lax.map(lambda kk:track(kk,b,20,q),jax.random.split(jax.random.PRNGKey(5),10)))
    out[f'q{q}|b{b}']=R.tolist(); print(q,b,'final 1-Fgauge median %.2e (stale-before-update %.2e)'%(np.median(1-R[:,-5:,1]),np.median(1-R[:,-5:,0])),flush=True)
    json.dump(out,open('res_it3.json','w'))
