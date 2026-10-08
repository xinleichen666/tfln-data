# Round2 JSA with GVD, 1/f fabrication noise (t,w,h), strategies compared at equal noise; purity & brightness.
import json,os,sys,numpy as np
from scipy.optimize import minimize_scalar
G=json.load(open('data/geoscan.json'))
out='data/run2.json'; R=json.load(open(out)) if os.path.exists(out) else {}
def save(): json.dump(R,open(out,'w'),indent=1)
NR=10
def setup(geo):
    g=G[geo]; p,s,i=g['p'],g['s'],g['i']
    LAM=2*np.pi/abs(p['b0']-s['b0']-i['b0'])*1e-3  # mm
    return dict(A=p['b1']-s['b1'],B=p['b1']-i['b1'],b2=(p['b2']*1e-3,s['b2']*1e-3,i['b2']*1e-3),LAM=LAM,St=g['dDk_dt'],Sw=g['dDk_dw'],Sh=g['dDk_dh'])
def weights(L,LAM,sig):
    n=int(L/LAM); z=(np.arange(n)+0.5)*LAM-L/2
    tgt=np.exp(-z**2/(2*(sig*L)**2)); q=np.zeros(n); acc=0.
    for j in range(n):
        acc+=tgt[j]
        if acc>=0.5: q[j]=1; acc-=1
    return z,q
def grid(P,L,N=120):
    span=16*2*np.pi/(max(abs(P['A']),abs(P['B']))*L)*1.0
    span=max(span,16*2*np.pi/(min(abs(P['A']),abs(P['B']))*L)/3)
    W=np.linspace(-span/2,span/2,N); Ws,Wi=np.meshgrid(W,W,indexing='ij'); return Ws,Wi,W[1]-W[0]
def dk(P,Ws,Wi):
    bp,bs,bi=P['b2']; return P['A']*Ws+P['B']*Wi+0.5*(bp*(Ws+Wi)**2-bs*Ws**2-bi*Wi**2)
def Phi(z,q,phi,D):
    E=np.exp(1j*np.multiply.outer(D,z)); return (E*(q*np.exp(1j*phi))).sum(-1)*(z[1]-z[0])
def PB(F,Ws,Wi,dW,tau):
    a=(tau**2/np.pi)**0.25*np.exp(-((Ws+Wi)*tau)**2/2); f=a*F
    sv=np.linalg.svd(f*dW,compute_uv=False)**2; B=sv.sum(); sv/=B; return float((sv**2).sum()),float(B)
def best(F,Ws,Wi,dW,L):
    r=minimize_scalar(lambda x:-PB(F,Ws,Wi,dW,np.exp(x))[0],bounds=(np.log(0.02*L),np.log(20*L)),method='bounded')
    return PB(F,Ws,Wi,dW,float(np.exp(r.x)))
rng=np.random.default_rng(7)
def pink(z,rms):
    if rms==0: return 0*z
    n=len(z); f=np.fft.rfftfreq(n,z[1]-z[0]); a=np.zeros(len(f)); a[1:]=1/np.sqrt(f[1:])
    x=np.fft.irfft(a*np.exp(2j*np.pi*rng.random(len(f))),n); x-=x.mean(); return x/x.std()*rms
def ph(z,S,dx): return np.cumsum(S*dx)*(z[1]-z[0])
def mapped(z,dt,step=0.2,err=0.1):  # thickness map sampled every 0.2 mm (Lu Filmetrics step) + white error
    zs=np.arange(z[0],z[-1]+step,step); m=np.interp(zs,z,dt)+rng.normal(0,err,len(zs)); return np.interp(z,zs,m)
def case(geo,L,sig,st,sw,sh,strategy='none',err=0.1):
    P=setup(geo); z,q=weights(L,P['LAM'],sig); Ws,Wi,dW=grid(P,L); D=dk(P,Ws,Wi)
    res=[]
    for r in range(NR):
        dt,dw,dh=pink(z,st),pink(z,sw),pink(z,sh)
        phi=ph(z,P['St'],dt)+ph(z,P['Sw'],dw)+ph(z,P['Sh'],dh)
        if strategy=='adapt': phi=phi-ph(z,P['St'],mapped(z,dt,err=err))
        res.append(best(Phi(z,q,phi,D),Ws,Wi,dW,L))
        if st==sw==sh==0: break
    a=np.array(res); return [float(a[:,0].mean()),float(a[:,0].std()),float(a[:,1].mean())]
def run(k,*a,**kw):
    if k not in R: R[k]=case(*a,**kw); save(); print(k,R[k],flush=True)
    return R[k]
if __name__=="__main__":
    geo=sys.argv[1] if len(sys.argv)>1 else '1.4_0.3'
    print(setup(geo))
    run(f'{geo}|ideal|L5',geo,5,0.25,0,0,0)

    for st in (0.25,0.5,1.0,1.59):
        run(f'{geo}|t{st}|L5',geo,5,0.25,st,0,0)
    run(f'{geo}|t1.59w13h3.5|L5',geo,5,0.25,1.59,13.16,3.47)
    run(f'{geo}|t0w13h3.5|L5',geo,5,0.25,0,13.16,3.47)
    # strategies at realistic noise (Lu 5mm estimates: t1.59, w,h upper bounds) and t-only 1.59
    for nm,(st,sw,sh) in (('t',(1.59,0,0)),('twh',(1.59,13.16,3.47))):
        run(f'{geo}|{nm}|L5|adapt_e0.1',geo,5,0.25,st,sw,sh,strategy='adapt',err=0.1)
        run(f'{geo}|{nm}|L5|adapt_e0.3',geo,5,0.25,st,sw,sh,strategy='adapt',err=0.3)
        run(f'{geo}|{nm}|L2.5',geo,2.5,0.25,st,sw,sh)
        run(f'{geo}|{nm}|L1.25',geo,1.25,0.25,st,sw,sh)
        run(f'{geo}|{nm}|L5sig0.15',geo,5,0.15,st,sw,sh)
    run(f'{geo}|ideal|L2.5',geo,2.5,0.25,0,0,0); run(f'{geo}|ideal|L1.25',geo,1.25,0.25,0,0,0); run(f'{geo}|ideal|L5sig0.15',geo,5,0.15,0,0,0)
