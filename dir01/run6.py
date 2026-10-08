# Same MC as run5 (seed 2026, Chen/Xin, width 2 nm, etch, chirp +-0.25 tau^2, pump fixed at ideal).
# Only change: film-thickness phase coefficient St = -3.1614231863126006 rad/mm/nm
# (TM pump, w=1.4 um, h=0.3 um, centered difference of neff at 0.56 and 0.64 um, dt.json).
# Dispersion A,B,b2,LAM and Sw,Sh stay the run5 TE-pump geoscan values so the comparison is one coefficient.
import json, numpy as np, run2 as r
P=r.setup('1.4_0.3')
P['St']=-3.1614231863126006
assert abs(r.setup('1.4_0.3')['St']+3.687420864052382)<1e-6
rng=np.random.default_rng(2026)
C=np.loadtxt('data/chen_fig1d_thickness.csv',delimiter=','); X=np.loadtxt('data/xin2024_fig2b.csv',delimiter=',')
NMC=16
def Phi(z,q,phi,D):
    o=np.zeros(D.shape,complex); a=q*np.exp(1j*phi)
    for i in range(0,len(z),400): o+=np.exp(1j*np.multiply.outer(D,z[i:i+400]))@a[i:i+400]
    return o*(z[1]-z[0])
def PB(F,Ws,Wi,dW,tau,Cc):
    a=(tau**2/np.pi)**0.25*np.exp(-((Ws+Wi)*tau)**2/2+1j*Cc*(Ws+Wi)**2); f=a*F
    sv=np.linalg.svd(f*dW,compute_uv=False)**2; B=sv.sum(); sv/=B; return float((sv**2).sum()),float(B)
STRAT=(('none',None,0),('a0.2_e0.3',0.2,0.3),('a0.1_e0.3',0.1,0.3),('a0.04_e0.3',0.04,0.3))
out='data/run6.json'; R=json.load(open(out)) if __import__('os').path.exists(out) else {}
R['St']=P['St']; R['St_old']=r.setup('1.4_0.3')['St']
for L in (2,5,10,15,20):
    if f'L{L}' in R and len(R[f'L{L}']['none'])>=NMC: continue
    z,q=r.weights(L,P['LAM'],0.25); Ws,Wi,dW=r.grid(P,L); D=r.dk(P,Ws,Wi)
    F0=Phi(z,q,0*z,D)
    x=r.minimize_scalar(lambda x:-PB(F0,Ws,Wi,dW,np.exp(x),0)[0],bounds=(np.log(0.02*L),np.log(20*L)),method='bounded').x
    tau=float(np.exp(x)); Pid,Bid=PB(F0,Ws,Wi,dW,tau,0)
    res={k:[] for k,_,_ in STRAT}; srcs=[]
    for m in range(NMC):
        src='xin' if (L<=5 and m%2==1) else 'chen'; D_=X if src=='xin' else C
        zmax=D_[-1,0]-L; z0=rng.uniform(0,max(zmax,0))
        w=(D_[:,0]>=z0-1e-9)&(D_[:,0]<=z0+L+1e-9)
        tt=D_[w,1]-D_[w,1].mean(); dt=np.interp(z,D_[w,0]-z0-L/2,tt)
        dh=np.interp(z,D_[w,0]-z0-L/2,D_[w,2]-D_[w,2].mean()) if src=='xin' else r.pink(z,0.2)
        dw=r.pink(z,2.0); Cc=rng.uniform(-0.25,0.25)*tau**2
        phi0=r.ph(z,P['St'],dt)+r.ph(z,P['Sw'],dw)+r.ph(z,P['Sh'],dh)
        for k,step,err in STRAT:
            phi=phi0.copy()
            if step:
                zs=np.arange(z[0],z[-1]+step,step)
                mp=np.interp(z,zs,np.interp(zs,z,dt)+rng.normal(0,err,len(zs)))
                phi=phi-r.ph(z,P['St'],mp)
            p,b=PB(Phi(z,q,phi,D),Ws,Wi,dW,tau,Cc)
            res[k].append([p,b])
        srcs.append(src)
    R[f'L{L}']=dict(ideal=[Pid,Bid],tau=tau,src=srcs,**res)
    json.dump(R,open(out,'w'))
    print(L,{k:round(float(np.median(np.array(v)[:,0])),3) for k,v in res.items()},flush=True)
