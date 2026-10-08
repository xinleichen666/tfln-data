import json,numpy as np, run2 as r
import importlib,sys; sys.argv=['x','0']; M=importlib.import_module('run5')
P=M.P; L=5; z,q=r.weights(L,P['LAM'],0.25); Ws,Wi,dW=r.grid(P,L); D=r.dk(P,Ws,Wi); rng=np.random.default_rng(5)
F0=M.Phi(z,q,0*z,D); tau=json.load(open('data/run5.json'))['L5']['tau']
C=M.C; out={}
def mc(chirp=0.25,wn=2.0,err=0.3,step=0.1,N=12):
    v=[]
    for m in range(N):
        z0=rng.uniform(0,C[-1,0]-L); w=(C[:,0]>=z0)&(C[:,0]<=z0+L); dt=np.interp(z,C[w,0]-z0-L/2,C[w,1]-C[w,1].mean())
        phi=r.ph(z,P['St'],dt)+r.ph(z,P['Sw'],r.pink(z,wn))+r.ph(z,P['Sh'],r.pink(z,0.2))
        zs=np.arange(z[0],z[-1]+step,step); phi-=r.ph(z,P['St'],np.interp(z,zs,np.interp(zs,z,dt)+rng.normal(0,err,len(zs))))
        v.append(M.PB(M.Phi(z,q,phi,D),Ws,Wi,dW,tau,rng.uniform(-chirp,chirp)*tau**2)[0])
    return [float(np.median(v)),float(np.percentile(v,10)),float(np.percentile(v,90))]
for c in (0,0.25,0.5,1.0): out[f'chirp{c}']=mc(chirp=c); print('chirp',c,out[f'chirp{c}'],flush=True)
for wn in (0,2,5,10): out[f'w{wn}']=mc(wn=wn); print('w',wn,out[f'w{wn}'],flush=True)
for e in (0.3,0.5,1.0): out[f'err{e}']=mc(err=e); print('err',e,out[f'err{e}'],flush=True)
json.dump(out,open('data/sens_mc.json','w'),indent=1)
