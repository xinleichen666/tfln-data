# Round3: purity with REAL thickness profile (Chen 2023 Fig1d digitized), 5mm windows, type-II design 1.4_0.3
import json,os,numpy as np, run2 as r
from run2b import PB2
d=np.loadtxt('data/chen_fig1d_thickness.csv',delimiter=','); Z,T=d[:,0],d[:,1]
P=r.setup('1.4_0.3'); L=5.0; z,q=r.weights(L,P['LAM'],0.25); Ws,Wi,dW=r.grid(P,L); D=r.dk(P,Ws,Wi)
def smooth(x,k): return np.convolve(np.pad(x,k,mode='edge'),np.ones(k)/k,'same')[k:-k]
out='data/run3.json'; R=json.load(open(out)) if os.path.exists(out) else {}
def ev(phi):
    F=r.Phi(z,q,phi,D); x=r.minimize_scalar(lambda x:-PB2(F,Ws,Wi,dW,np.exp(x))[0],bounds=(np.log(0.02*L),np.log(20*L)),method='bounded').x
    return PB2(F,Ws,Wi,dW,float(np.exp(x)))
for z0 in np.arange(0,16.01,2.0):
    k=f'{z0:.0f}'
    if k in R: continue
    m=(Z>=z0)&(Z<=z0+L); zz=Z[m]-z0-L/2; tt=T[m]-T[m].mean()
    raw=np.interp(z,zz,tt); sm=np.interp(z,zz,smooth(tt,5))  # 5 pts*40um=0.2mm
    res={}
    for truth,dt in (('raw',raw),('smooth',sm)):
        res[truth+'|none']=ev(r.ph(z,P['St'],dt))
        for step in (0.2,0.04):
            mp=np.interp(z,np.arange(z[0],z[-1]+step,step),np.interp(np.arange(z[0],z[-1]+step,step),z,dt))
            res[truth+f'|adapt{step}']=ev(r.ph(z,P['St'],dt-mp))
    R[k]=res; json.dump(R,open(out,'w'),indent=1); print(k,{a:round(b[0],3) for a,b in res.items()},flush=True)
