# Round3: discriminating criteria. (1) g2-purity vs applied pump chirp C (scan). (2) CW-SFG |PMF|^2 shape metrics.
import json,numpy as np, run2 as r
from run3 import Z,T,z,q,P,L,Ws,Wi,dW,D
def Pc(F,tau,C):
    a=(tau**2/np.pi)**0.25*np.exp(-((Ws+Wi)*tau)**2/2+1j*C*(Ws+Wi)**2); f=a*F
    sv=np.linalg.svd(f*dW,compute_uv=False)**2; sv/=sv.sum(); g=abs(f); s2=np.linalg.svd(g*dW,compute_uv=False)**2; s2/=s2.sum()
    return float((sv**2).sum()),float((s2**2).sum())
def win(z0):
    m=(Z>=z0)&(Z<=z0+L); zz=Z[m]-z0-L/2; tt=T[m]-T[m].mean(); return np.interp(z,zz,tt)
F0=r.Phi(z,q,0*z,D); tau0=None
from run2b import PB2
x=r.minimize_scalar(lambda x:-PB2(F0,Ws,Wi,dW,np.exp(x))[0],bounds=(np.log(0.1),np.log(100)),method='bounded').x; tau=float(np.exp(x))
cases={'pump_chirp_0.5tau2':(F0,0.5*tau**2),'pump_chirp_1tau2':(F0,1.0*tau**2)}
for z0 in (4.0,10.0): cases[f'thick_chen_win{z0:.0f}']=(r.Phi(z,q,r.ph(z,P['St'],win(z0)),D),0.0)
Cs=np.linspace(-1.5,1.5,13)*tau**2; out={'tau_ps':tau,'C_applied_tau2':list(Cs/tau**2)}
for k,(F,Cint) in cases.items():
    v=[Pc(F,tau,Cint+C) for C in Cs]; out[k]={'P':[a for a,b in v],'P_JSI':[b for a,b in v]}
    i=int(np.argmax([a for a,b in v])); print(k,'P(C=0)=%.3f JSI(C=0)=%.3f  maxP=%.3f at C=%.2f tau^2'%(v[6][0],v[6][1],v[i][0],Cs[i]/tau**2))
# (2) PMF from CW SFG: |Phi(dk)|^2 along dk; metrics: overlap with design, peak-normalised max sidelobe
dk=np.linspace(-6,6,1201)*2*np.pi/L
def pm(phi): return abs(np.exp(1j*np.outer(dk,z))@(q*np.exp(1j*phi)))**2
p0=pm(0*z); out['pmf']={}
for z0 in np.arange(0,16.01,2.0):
    p=pm(r.ph(z,P['St'],win(z0))); ov=float((np.sqrt(p*p0).sum())**2/(p.sum()*p0.sum()))
    w=float(np.sqrt(((dk-(dk*p).sum()/p.sum())**2*p).sum()/p.sum())/np.sqrt(((dk)**2*p0).sum()/p0.sum()))
    out['pmf'][f'{z0:.0f}']=dict(overlap=ov,width_ratio=w,peak_ratio=float(p.max()/p0.max())); print('win',z0,out['pmf'][f'{z0:.0f}'])
json.dump(out,open('data/crit.json','w'),indent=1)
