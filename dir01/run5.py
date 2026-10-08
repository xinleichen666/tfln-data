# Round4 main (conservative MC). Truth thickness = measured profiles (Chen 2023 Fig1d; Xin 2024 Fig2b for L<=5).
# Per realization: random window, map error (white, per sample), residual pump chirp C~U(-0.25,0.25)tau^2,
# width noise 1/f rms 2 nm (assumption), etch-depth noise = Xin measured 'film etched' profile (rms~0.2nm) scaled by our dh.
# Pump bandwidth fixed at ideal optimum (not re-optimized per device). Loss/coupling/detection applied analytically.
import json,os,sys,numpy as np, run2 as r
P=r.setup('1.4_0.3'); rng=np.random.default_rng(2026)
C=np.loadtxt('data/chen_fig1d_thickness.csv',delimiter=','); X=np.loadtxt('data/xin2024_fig2b.csv',delimiter=',')
NMC=int(sys.argv[1]) if len(sys.argv)>1 else 16
A_S,A_P=0.3,0.6   # dB/cm signal/idler, pump  (assumptions, conservative)
ETA_C,ETA_D=0.5,0.8  # per-facet coupling, detector efficiency (assumptions)
def Phi(z,q,phi,D):
    o=np.zeros(D.shape,complex); a=q*np.exp(1j*phi)
    for i in range(0,len(z),400): o+=np.exp(1j*np.multiply.outer(D,z[i:i+400]))@a[i:i+400]
    return o*(z[1]-z[0])
def PB(F,Ws,Wi,dW,tau,Cc):
    a=(tau**2/np.pi)**0.25*np.exp(-((Ws+Wi)*tau)**2/2+1j*Cc*(Ws+Wi)**2); f=a*F
    sv=np.linalg.svd(f*dW,compute_uv=False)**2; B=sv.sum(); sv/=B; return float((sv**2).sum()),float(B)
STRAT=(('none',None,0),('a0.2_e0.3',0.2,0.3),('a0.1_e0.3',0.1,0.3),('a0.1_e0.5',0.1,0.5),('a0.04_e0.3',0.04,0.3))
out='data/run5.json'; R=json.load(open(out)) if os.path.exists(out) else {}
for L in (() if __name__!='__main__' else (2,5,10,15,20)):
  pass
for L in ((2,5,10,15,20) if __name__=='__main__' else ()):
    if f'L{L}' in R and len(R[f'L{L}']['none'])>=NMC: continue
    z,q=r.weights(L,P['LAM'],0.25); Ws,Wi,dW=r.grid(P,L); D=r.dk(P,Ws,Wi)
    F0=Phi(z,q,0*z,D)
    x=r.minimize_scalar(lambda x:-PB(F0,Ws,Wi,dW,np.exp(x),0)[0],bounds=(np.log(0.02*L),np.log(20*L)),method='bounded').x; tau=float(np.exp(x))
    Pid,Bid=PB(F0,Ws,Wi,dW,tau,0)
    # loss: pump power at z, photons exit at +L/2
    zz=z+L/2; Tp=10**(-A_P*zz/100); Ts=10**(-A_S*(L-zz)/100)   # dB/cm, z in mm
    gen=(q*Tp).sum()/q.sum(); Tph=(q*Tp*Ts).sum()/(q*Tp).sum()
    eh=ETA_C*ETA_D*Tph
    res={k:[] for k,_,_ in STRAT}; srcs=[]
    for m in range(NMC):
        src='xin' if (L<=5 and m%2==1) else 'chen'; D_=X if src=='xin' else C
        zmax=D_[-1,0]-L; z0=rng.uniform(0,max(zmax,0)); w=(D_[:,0]>=z0-1e-9)&(D_[:,0]<=z0+L+1e-9)
        tt=D_[w,1]-D_[w,1].mean(); dt=np.interp(z,D_[w,0]-z0-L/2,tt)
        if src=='xin': dh=np.interp(z,D_[w,0]-z0-L/2,D_[w,2]-D_[w,2].mean())
        else: dh=0*z+r.pink(z,0.2)
        dw=r.pink(z,2.0); Cc=rng.uniform(-0.25,0.25)*tau**2
        phi0=r.ph(z,P['St'],dt)+r.ph(z,P['Sw'],dw)+r.ph(z,P['Sh'],dh)
        for k,step,err in STRAT:
            phi=phi0.copy()
            if step:
                zs=np.arange(z[0],z[-1]+step,step); mp=np.interp(z,zs,np.interp(zs,z,dt)+rng.normal(0,err,len(zs)))
                phi=phi-r.ph(z,P['St'],mp)
            p,b=PB(Phi(z,q,phi,D),Ws,Wi,dW,tau,Cc)
            res[k].append([p,b*gen])
        srcs.append(src)
    R[f'L{L}']=dict(ideal=[Pid,Bid],tau=tau,gen=gen,Tph=Tph,eta_h=eh,src=srcs,**res)
    json.dump(R,open(out,'w'),indent=1)
    print(L,'ideal',round(Pid,3),'eta_h',round(eh,3),{k:np.round(np.median(np.array(v)[:,0]),3) for k,v in res.items()},flush=True)
