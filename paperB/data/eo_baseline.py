"""Matched EO baseline for the manuscript (added during write-up, not part of iterations 0-5).
Same Eq. S2 time-domain model as iter5_aomolecule.simulate, but push-pull EO drive on BOTH rings
(Hu et al. Eq. S1/S2: +Omega cos on ring 1, -Omega cos on ring 2) with Hu's EO coefficient
~0.5 GHz/V (Supp. Sec. V; on the capacitor). Optical parameters identical to AO design A/B.
Assumption: V_c = V_0 (voltage on electrode = probe peak voltage), P = V0^2/(2*50 ohm)."""
import numpy as np, json
tp=2*np.pi
def sim_pp(mu,ke,ki,wm,Om,T,dt=None):
    dt=dt or 1/(wm/tp)/80; n=int(T/dt); a=np.zeros(2,complex); out=np.empty(n,complex)
    def f(t,a):
        m=Om*np.cos(wm*t)
        return np.array([(-1j*(mu+m)-(ke+ki)/2)*a[0]-1j*mu*a[1]-np.sqrt(ke),
                         (-1j*(mu-m)-ki/2)*a[1]-1j*mu*a[0]])
    t=0
    for i in range(n):
        k1=f(t,a);k2=f(t+dt/2,a+dt/2*k1);k3=f(t+dt/2,a+dt/2*k2);k4=f(t+dt,a+dt*k3)
        a=a+dt/6*(k1+2*k2+2*k3+k4); t+=dt; out[i]=1+np.sqrt(ke)*a[0]
    tt=np.arange(n)*dt; m=tt>T-20e-9
    return {q:abs(np.mean(out[m]*np.exp(1j*q*wm*tt[m])))**2 for q in range(-3,4)}
res={}
for name,f,ke,ki,T in [('A_matched',0.842e9,0.10e9,0.01e9,80e-9),('B_matched',3.33e9,0.60e9,0.06e9,40e-9)]:
    wm=tp*f; best=None
    for x in np.linspace(0.6,1.4,33):
        Om=x*tp*ke/2; r=sim_pp(wm/2,tp*ke,tp*ki,wm,Om,T); s=max(r[1],r[-1]); tot=sum(r.values())
        if best is None or s/tot>best['eta_shift']:
            V=Om/tp/0.5e9; best=dict(Omega_GHz=Om/tp/1e9,eta_shift=s/tot,eta_abs=s,V_peak=V,P_W_Vc_eq_V0=V**2/100)
    res[name]=best
print(json.dumps(res,indent=1)); json.dump(res,open('eo_baseline.json','w'),indent=1)
