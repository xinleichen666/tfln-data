import sys,json,time,numpy as np,jax,jax.numpy as jnp
sys.path.insert(0,'/workspace/dir13'); from lib4 import *
from functools import partial
from scipy.stats import unitary_group
rng=np.random.default_rng(7)
def dft(d): w=np.exp(2j*np.pi/d); return np.array([[w**(i*j) for j in range(d)] for i in range(d)])/np.sqrt(d)
H=np.array([[1,1],[1,-1]])/np.sqrt(2)
T={}
for d in range(3,9): T[f'DFT{d}']=dft(d)
for d in (4,6,8):
    for i in range(8): T[f'Haar{d}_{i}']=unitary_group.rvs(d,random_state=int(rng.integers(1e9)))
    for i in range(8): P=np.eye(d)[rng.permutation(d)]; T[f'Perm{d}_{i}']=np.diag(np.exp(2j*np.pi*rng.random(d)))@P
T['HxH']=np.kron(H,H); T['HxHxH']=np.kron(T['HxH'],H)
P=np.eye(8); P[[6,7]]=P[[7,6]]; T['Toffoli']=P
T['DFT2xDFT2xI2']=np.kron(np.kron(H,H),np.eye(2)); T['CNOTxH']=np.kron(np.eye(4)[[0,1,3,2]],H)
ARCH=['std','3mzi','mzix','dbl','hyb']
SC={'rand0.05':(0.05,0.),'rand0.10':(0.10,0.),'bias0.08':(0.03,0.08)}
NCH=50
@partial(jax.jit,static_argnums=(2,3))
def ideal(Ut,keys,N,arch,Hm):
    lay=layout(N,'clements'); K=len(lay)
    def one(k):
        return adam_scan(lambda p:1-fid(Ut,build(p,zeroE(K),N,lay,arch,Hm)),initp(k,N,K),2500,0.05)
    return jax.vmap(one)(keys)
@partial(jax.jit,static_argnums=(3,4))
def calib(Ut,p0,E,N,arch,Hm):
    lay=layout(N,'clements')
    def one(e):
        p,L=adam_scan(lambda p:1-fid(Ut,build(p,e,N,lay,arch,Hm)),p0,1500,0.01)
        return 1-L
    return jax.vmap(one)(E)
def splits(p,N):  # internal bar power |s|^2 of each MZI in ideal std setting: (1+cos th)/2 for 50:50 DCs -> bar=sin^2(th/2)
    return np.sin(np.array(p['th'])/2)**2
out={}; t0=time.time()
for nm,U in T.items():
    Ut=jnp.array(U,dtype=complex); N=U.shape[0]; K=len(layout(N,'clements'))
    keys=jax.random.split(jax.random.PRNGKey(1),8); P0={}
    for a in ['std','3mzi','mzix']:
        Hm=jnp.zeros(K) if a!='dbl' else jnp.ones(K)
        ps,Ls=ideal(Ut,keys,N,a,Hm); i=int(jnp.argmin(Ls)); P0[a]=(jax.tree.map(lambda x:x[i],ps),float(Ls[i]))
    bar=splits(P0['std'][0],N)
    hmask=jnp.array(((bar<0.1)|(bar>0.9)).astype(float))
    P0['dbl']=P0['std']; P0['hyb']=P0['std']
    rec=dict(N=N,K=K,bar=bar.tolist(),nhyb=int(hmask.sum()),ideal_inf={a:P0[a][1] for a in P0})
    for sn,(s,b) in SC.items():
        E=chips(jax.random.PRNGKey(hash(sn)%1000+11),NCH,K,s,b)
        for a in ARCH:
            Hm={'dbl':jnp.ones(K),'hyb':hmask}.get(a,jnp.zeros(K)); aa='std' if a in('dbl','hyb') else a
            F=np.array(calib(Ut,P0[a][0],E,N,aa,Hm)); rec[f'{sn}|{a}']=F.tolist()
    out[nm]=rec
    print(nm,f'{time.time()-t0:.0f}s',{k:float(np.mean(1-np.array(v))) for k,v in rec.items() if '|' in k and k.startswith('rand0.10')},flush=True)
    json.dump(out,open('/workspace/dir13/it1/res_it1.json','w'))
