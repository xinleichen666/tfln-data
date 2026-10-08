# Round2b: noise spectrum with high-frequency cutoff fc (long-range only) + JSI-only purity metric (phase-blind, like experiments)
import json,os,numpy as np, run2 as r
out='data/run2b.json'; R=json.load(open(out)) if os.path.exists(out) else {}
FC=5.0 # 1/mm  (no thickness structure below 0.2 mm) -- assumption
def pinkc(z,rms):
    if rms==0: return 0*z
    n=len(z); f=np.fft.rfftfreq(n,z[1]-z[0]); a=np.zeros(len(f)); m=(f>0)&(f<=FC); a[m]=1/np.sqrt(f[m])
    x=np.fft.irfft(a*np.exp(2j*np.pi*r.rng.random(len(f))),n); x-=x.mean(); return x/x.std()*rms
def PB2(F,Ws,Wi,dW,tau):
    a=(tau**2/np.pi)**0.25*np.exp(-((Ws+Wi)*tau)**2/2); f=a*F; o=[]
    for g in (f,abs(f)):
        sv=np.linalg.svd(g*dW,compute_uv=False)**2; B=sv.sum(); sv/=B; o.append(float((sv**2).sum()))
    return o[0],B,o[1]
def case(spec,L,sig,st,strategy='none',err=0.1,NR=10):
    P=r.setup('1.4_0.3'); z,q=r.weights(L,P['LAM'],sig); Ws,Wi,dW=r.grid(P,L); D=r.dk(P,Ws,Wi)
    gen=pinkc if spec=='cut' else r.pink; res=[]
    for k in range(NR if st else 1):
        dt=gen(z,st); phi=r.ph(z,P['St'],dt)
        if strategy=='adapt': phi=phi-r.ph(z,P['St'],r.mapped(z,dt,err=err))
        F=r.Phi(z,q,phi,D)
        x=r.minimize_scalar(lambda x:-PB2(F,Ws,Wi,dW,np.exp(x))[0],bounds=(np.log(0.02*L),np.log(20*L)),method='bounded').x
        res.append(PB2(F,Ws,Wi,dW,float(np.exp(x))))
    a=np.array(res); return dict(P=float(a[:,0].mean()),Psd=float(a[:,0].std()),B=float(a[:,1].mean()),P_JSI=float(a[:,2].mean()))
def run(k,*a,**kw):
    if k not in R: R[k]=case(*a,**kw); json.dump(R,open(out,'w'),indent=1); print(k,R[k],flush=True)
for spec in ('cut','full'):
  for st in (0.5,1.59):
    run(f'{spec}|t{st}|L5',spec,5,0.25,st)
    run(f'{spec}|t{st}|L5|adapt0.1',spec,5,0.25,st,'adapt',0.1)
    run(f'{spec}|t{st}|L2.5',spec,2.5,0.25,st)
    run(f'{spec}|t{st}|L1.25',spec,1.25,0.25,st)
