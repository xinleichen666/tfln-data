# Round4: purity, brightness vs L (2-20mm) on Chen Fig1d measured profile (raw as truth). Chunked PMF to save memory.
import json,os,numpy as np, run2 as r
from run2b import PB2
d=np.loadtxt('data/chen_fig1d_thickness.csv',delimiter=','); Z,T=d[:,0],d[:,1]
P=r.setup('1.4_0.3'); rng=np.random.default_rng(11)
def Phi(z,q,phi,D):
    o=np.zeros(D.shape,complex); a=q*np.exp(1j*phi)
    for i in range(0,len(z),400): o+=np.exp(1j*np.multiply.outer(D,z[i:i+400]))@a[i:i+400]
    return o*(z[1]-z[0])
out='data/run4.json'; R=json.load(open(out)) if os.path.exists(out) else {}
strat=(('none',None,0),('a0.2e0',0.2,0),('a0.2e0.1',0.2,0.1),('a0.04e0.1',0.04,0.1),('a0.04e0.3',0.04,0.3))
for L in (2,3.5,5,10,15,20):
    z,q=r.weights(L,P['LAM'],0.25); Ws,Wi,dW=r.grid(P,L); D=r.dk(P,Ws,Wi)
    def ev(phi):
        F=Phi(z,q,phi,D); x=r.minimize_scalar(lambda x:-PB2(F,Ws,Wi,dW,np.exp(x))[0],bounds=(np.log(0.02*L),np.log(20*L)),method='bounded').x
        return PB2(F,Ws,Wi,dW,float(np.exp(x)))[:2]
    k0=f'L{L}|ideal'
    if k0 not in R: R[k0]=ev(0*z); json.dump(R,open(out,'w'),indent=1)
    for z0 in np.arange(0,21-L+1e-9,2.0):
        k=f'L{L}|z{z0:.0f}'
        if k in R: continue
        m=(Z>=z0)&(Z<=z0+L); zz=Z[m]-z0-L/2; tt=T[m]-T[m].mean(); dt=np.interp(z,zz,tt); res={}
        for nm,step,err in strat:
            if step is None: e=dt
            else:
                zs=np.arange(z[0],z[-1]+step,step); e=dt-np.interp(z,zs,np.interp(zs,z,dt)+rng.normal(0,err,len(zs)))
            res[nm]=ev(r.ph(z,P['St'],e))
        R[k]=res; json.dump(R,open(out,'w'),indent=1); print(k,{a:round(b[0],3) for a,b in res.items()},flush=True)
