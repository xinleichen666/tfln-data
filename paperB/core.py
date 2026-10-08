"""Paper B core model: Hu et al. Nature 599, 587 (2021) Eq. S2, full time domain (no RWA).
Ring 1 (bus-coupled) is modulated. mode='ao': ring-1 only, d(w1)=dw cos; mode='eo': push-pull +dw/-dw."""
import numpy as np
tp=2*np.pi
def run(mu,g,ki,wm,dw,mode='ao',Delta=0.0,T=40e-9,df=0.0):
    W=wm+tp*df; dt=1/(W/tp)/80; n=int(T/dt); a=np.zeros(2,complex); out=np.empty(n,complex)
    d0=mu-Delta  # ring detuning from laser (laser = S mode + Delta)
    s2=-1.0 if mode=='eo' else 0.0
    def f(t,a):
        m=dw*np.cos(W*t)
        return np.array([(-1j*(d0+m)-(g+ki)/2)*a[0]-1j*mu*a[1]-np.sqrt(g),
                         (-1j*(d0+s2*m)-ki/2)*a[1]-1j*mu*a[0]])
    t=0.0
    for i in range(n):
        k1=f(t,a);k2=f(t+dt/2,a+dt/2*k1);k3=f(t+dt/2,a+dt/2*k2);k4=f(t+dt,a+dt*k3)
        a=a+dt/6*(k1+2*k2+2*k3+k4); t+=dt; out[i]=1+np.sqrt(g)*a[0]
    tt=np.arange(n)*dt; m=tt>T-20e-9
    return {q:np.mean(out[m]*np.exp(1j*q*W*tt[m])) for q in range(-3,4)}
def metrics(c):
    p={q:abs(v)**2 for q,v in c.items()}; tot=sum(p.values()); qs=max((1,-1),key=lambda q:p[q])
    return dict(eta_shift=p[qs]/tot,eta_abs=p[qs],IL_dB=-10*np.log10(tot),carrier_rel_dB=10*np.log10(p[0]/p[qs]),q=qs,p=p)
# Design B (suspended, 3.33 GHz) with Shao 2019 measured optical Q
F=3.33e9; WM=tp*F; MU=WM/2; G=tp*0.6e9; KI=tp*0.85*0.095e9
# drive calibrations (rad/s per volt of source amplitude, P=V^2/(2*50))
VPIL_SHAO=0.046e-2; LA=100e-6; LRING=0.667e-3; NG=2.3; C0=3e8
K_AO=(np.pi/(VPIL_SHAO/LA))*C0/(NG*LRING)   # Shao Vpi is source-referred (Supp. Eq. S8), incl. ~50% IDT coupling
K_EO=tp*0.5e9                                # Hu: 0.5 GHz/V on the capacitor
CAP=0.11e-12; REL=1.5; XC=1/(WM*CAP)
def P_from_dw(dw,case):
    if case=='AO_Shao_IDT(50%)': return (dw/K_AO)**2/100
    if case.startswith('AO_IDT'):  e=float(case.split('_')[2].rstrip('%'))/100; return (dw/K_AO)**2/100*0.5/e
    Vc=dw/K_EO
    if case=='EO_unmatched(Vc=V0)': return Vc**2/100
    if case=='EO_open(Vc=2V0)': return (Vc/2)**2/100
    if case.startswith('EO_LC_Q'): Q=float(case[7:]); return Vc**2*(REL+XC/Q)/(2*XC**2)
    if case=='EO_LC_ideal': return Vc**2*REL/(2*XC**2)
