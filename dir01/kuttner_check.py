# Round 5: Kuttner's actual process = TM pump (764) -> TE signal + TM idler, 600 nm x-cut.
# Group indices from disp.json (w=1.0 um, nearest to the ~0.9 um read off their Fig.2d SEM).
# Thickness sensitivity from the w=1.4 thickness sweep (dt.json), pump TM: -3.16 rad/mm/nm.
import json, numpy as np, run2 as r
from run2b import PB2
D=json.load(open('data/disp.json'))
def ng(w,l,p): return D[f'0.6_{w}_{l}_{p}'][1]
c=0.299792458
w=1.0
A=(ng(w,0.775,'TM')-ng(w,1.55,'TE'))/c
B=(ng(w,0.775,'TM')-ng(w,1.55,'TM'))/c
# neff for period
ne=lambda l,p: D[f'0.6_{w}_{l}_{p}'][0]
DK=2*np.pi*(ne(0.775,'TM')/0.775 - ne(1.55,'TE')/1.55 - ne(1.55,'TM')/1.55)  # rad/um
LAM=2*np.pi/abs(DK)*1e-3  # mm
S=-3.16  # rad/mm/nm  (w=1.4 TM pump, see report)
P=dict(A=A,B=B,b2=(0,0,0),LAM=LAM,St=S)
print('A,B ps/mm',A,B,'|A/B|',abs(A/B),'period um',LAM*1e3)
C=np.loadtxt('data/chen_fig1d_thickness.csv',delimiter=','); Z,T=C[:,0],C[:,1]
def FWHM_nm(tau, lam=0.764):
    dOdl=2*np.pi*c/lam**2/1000.0   # rad/fs per nm
    sigO=1.0/(tau*1000.0)
    return 2*np.sqrt(np.log(2))*sigO/dOdl
def tau_of(fwhm, lam=0.764):
    dOdl=2*np.pi*c/lam**2/1000.0
    sigO=fwhm*dOdl/(2*np.sqrt(np.log(2)))
    return 1.0/(sigO*1000.0)
out={}
for L in (1.0,2.0,3.0,5.0,7.0):
    z,q=r.weights(L,LAM,0.25); Ws,Wi,dW=r.grid(P,L,96); Dk=r.dk(P,Ws,Wi)
    F0=r.Phi(z,q,0*z,Dk)
    x=r.minimize_scalar(lambda x:-PB2(F0,Ws,Wi,dW,np.exp(x))[0],bounds=(np.log(0.02*L),np.log(40*L)),method='bounded').x
    tau=float(np.exp(x)); p0=PB2(F0,Ws,Wi,dW,tau)
    rec={'ideal_P':p0[0],'ideal_JSI':p0[2],'tau':tau,'pump_FWHM_nm':FWHM_nm(tau)}
    # Kuttner pump ~1.75 nm fixed
    tK=tau_of(1.75); rec['P_at_1.75nm']=PB2(F0,Ws,Wi,dW,tK)[0]
    wins={}
    for z0 in np.arange(0,21-L+1e-9,max(3.0,L)):
        m=(Z>=z0)&(Z<=z0+L); zz=Z[m]-z0-L/2; dt=np.interp(z,zz,T[m]-T[m].mean())
        F=r.Phi(z,q,r.ph(z,S,dt),Dk); v=PB2(F,Ws,Wi,dW,tau)
        wins[f'{z0:.0f}']={'P':v[0],'JSI':v[2],'rms_nm':float(dt.std())}
    rec['chen']=wins
    out[f'L{L}']=rec
    js=[v['JSI'] for v in wins.values()]
    print(f'L={L} ideal {p0[0]:.3f}/{p0[2]:.3f} pumpFWHM {FWHM_nm(tau):.2f} nm | Chen windows JSI',
          [round(j,3) for j in js],'true',[round(v['P'],3) for v in wins.values()], flush=True)
# scale Chen deviation at L=5
L=5.0; z,q=r.weights(L,LAM,0.25); Ws,Wi,dW=r.grid(P,L,96); Dk=r.dk(P,Ws,Wi)
tau=out['L5.0']['tau']; sc={}
for f in (0.25,0.5,0.75,1.0):
    vv=[]
    for z0 in np.arange(0,21-L+1e-9,4.0):
        m=(Z>=z0)&(Z<=z0+L); zz=Z[m]-z0-L/2; dt=f*np.interp(z,zz,T[m]-T[m].mean())
        F=r.Phi(z,q,r.ph(z,S,dt),Dk); vv.append(PB2(F,Ws,Wi,dW,tau)[2])
    sc[f]=[float(np.median(vv)),float(np.min(vv))]; print('scale',f,'JSI median/min',sc[f],flush=True)
out['scale_L5']=sc
json.dump(out,open('data/kuttner_check.json','w'),indent=1)
