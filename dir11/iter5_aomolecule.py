"""Iter5: acoustically driven photonic-molecule (coupled-ring doublet) frequency shifter.
Hu et al. Nature 599,587 (2021) architecture [arXiv:2005.09621, Eq. S2], but ring 1 is modulated by
an IDT-driven acoustic wave instead of EO electrodes. Full time-domain (no RWA) integration."""
import numpy as np, csv, json
tp=2*np.pi; c=3e8
def ring_dw_per_V(VpiL_single, La, Lring, ng=2.3):
    # single-arm phase per volt over La, converted to ring resonance shift (rad/s per V)
    dphi=np.pi/(VpiL_single/La); return dphi*c/(ng*Lring)
def simulate(mu,ke,ki,wm,dw,T=60e-9,dt=None):
    # rotating frame at laser = S mode (w0-mu); rings at w0 -> detuning +mu; ring1 modulated dw*cos(wm t)
    dt=dt or 1/(wm/tp)/80; n=int(T/dt); a=np.zeros(2,complex); out=np.empty(n,complex); ain=1.0
    def f(t,a):
        m=dw*np.cos(wm*t)
        return np.array([(-1j*(mu+m)-(ke+ki)/2)*a[0]-1j*mu*a[1]-np.sqrt(ke)*ain,
                         (-1j*mu-ki/2)*a[1]-1j*mu*a[0]])
    t=0
    for i in range(n):
        k1=f(t,a);k2=f(t+dt/2,a+dt/2*k1);k3=f(t+dt/2,a+dt/2*k2);k4=f(t+dt,a+dt*k3)
        a=a+dt/6*(k1+2*k2+2*k3+k4); t+=dt; out[i]=ain+np.sqrt(ke)*a[0]
    # analyse last 20 ns, project onto harmonics of wm
    tt=np.arange(n)*dt; m=tt>T-20e-9; res={}
    for q in range(-3,4): res[q]=abs(np.mean(out[m]*np.exp(1j*q*wm*tt[m])))**2
    return res
if __name__!="__main__": pass
rows=[]; R={}
cases={'A_nonsuspended_Ni2026':dict(f=0.842e9,VpiL=2*1.004e-2,La=400e-6,Lring=1.2e-3,ke=tp*0.30e9,ki=tp*0.03e9),
       'B_suspended_Shao2019':dict(f=3.33e9,VpiL=2*0.046e-2,La=100e-6,Lring=0.667e-3,ke=tp*1.6e9,ki=tp*0.17e9)}
# NOTE Shao MZI Vpi=4.6V is single-arm (one arm modulated) -> VpiL_single=0.046 V cm; Ni push-pull -> single-arm 2x.
cases['B_suspended_Shao2019']['VpiL']=0.046e-2
if __name__=="__main__":
    for name,p in cases.items():
        wm=tp*p['f']; mu=wm/2; k=ring_dw_per_V(p['VpiL'],p['La'],p['Lring'])
        best=None
        for dw in np.linspace(0.2,3.0,15)*p['ke']:
            r=simulate(mu,p['ke'],p['ki'],wm,dw); tot=sum(r.values())
            # output at laser + wm (shift up into AS mode)? find dominant shifted line
            sh=max(r[1],r[-1]); eta_abs=sh; eta_rel=sh/tot
            V=dw/k; P=V**2/(2*50)
            rows.append([name,dw/tp,V,P,eta_abs,eta_rel,r[0],r[2]+r[-2]])
            if best is None or eta_rel>best[5]: best=rows[-1]
        R[name]=dict(dw_per_V_GHz=k/tp/1e9,best_dw_GHz=best[1]/1e9,V=best[2],P_W=best[3],eta_abs=best[4],eta_shift=best[5],
                     IL_dB=-10*np.log10(sum([best[4],best[6],best[7]])),carrier=best[6])
    with open('data/iter5_aomolecule.csv','w',newline='') as fh:
        w=csv.writer(fh); w.writerow(['case','dw_Hz','V_peak','P_RF_W','eta_abs','eta_shift','p_carrier','p_2nd']); w.writerows(rows)
    # EO reference: Hu 2021 measured 96 mW (3.1 V) at 28.2 GHz, eta=98.7%
    json.dump(R,open('data/iter5_key.json','w'),indent=1); print(json.dumps(R,indent=1))
    