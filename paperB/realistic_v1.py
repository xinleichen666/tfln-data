"""Paper B 'realistic' result set. core.py untouched; vectorized RK4 copy of core.run with per-sample
mu, g, ki, Delta, delta_r. AO mode, drive fixed at the make_all optimum dw (power set by calibration)."""
import numpy as np, json, csv, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from core import tp, F, WM, MU, G, KI, NG, P_from_dw
plt.rcParams.update({'font.size':8,'font.family':'serif','mathtext.fontset':'dejavuserif','axes.linewidth':0.6,'lines.linewidth':1.1})
DW=json.load(open('data/results_B.json'))['optimum']['ao']['dw_GHz']*tp*1e9
def runv(mu,g,ki,Delta,dr,wm=WM,dw=DW,T=40e-9):
    mu,g,ki,Delta,dr=np.broadcast_arrays(*(np.atleast_1d(np.asarray(v,float)) for v in (mu,g,ki,Delta,dr)))
    W=wm; dt=1/(W/tp)/80; n=int(T/dt); d0=mu-Delta; sg=np.sqrt(g)
    a1=np.zeros(mu.shape,complex); a2=a1.copy(); tt=np.arange(n)*dt; msk=tt>T-20e-9; Q=range(-3,4); acc={q:0 for q in Q}
    def f(t,a1,a2):
        m=dw*np.cos(W*t); return ((-1j*(d0+m)-(g+ki)/2)*a1-1j*mu*a2-sg, (-1j*(d0+dr)-ki/2)*a2-1j*mu*a1)
    t=0.0
    for i in range(n):
        k1=f(t,a1,a2);k2=f(t+dt/2,a1+dt/2*k1[0],a2+dt/2*k1[1]);k3=f(t+dt/2,a1+dt/2*k2[0],a2+dt/2*k2[1]);k4=f(t+dt,a1+dt*k3[0],a2+dt*k3[1])
        a1=a1+dt/6*(k1[0]+2*k2[0]+2*k3[0]+k4[0]); a2=a2+dt/6*(k1[1]+2*k2[1]+2*k3[1]+k4[1]); t+=dt
        if msk[i]:
            o=1+sg*a1
            for q in Q: acc[q]=acc[q]+o*np.exp(1j*q*W*tt[i])
    N=msk.sum(); p={q:abs(acc[q]/N)**2 for q in Q}; tot=sum(p.values()); ps=np.maximum(p[1],p[-1])
    return ps/tot, -10*np.log10(tot), ps
MHz=tp*1e6; f0=193.4e12
# ---------------- parameters (see data/params_sources.md) ----------------
P=dict(eta_IDT_main=0.10, eta_IDT_ref=0.50, Qa_nom=2000, Qa_min=1570, Qa_max=3600,
       dndT=3.34e-5, alpha=1.54e-5, n_eff=2.14,       # Moretti 2005 (dn_e/dT); LN a-axis expansion
       ki_extra_frac=1.0,          # ASSUMED: extra intrinsic loss (IDT metal + suspended scattering) = +100% of Shao-measured KI
       sigT_lock_mK=5.0,           # ASSUMED residual rms after heater lock
       sig_gap_nm=5.0, gap_decay_nm=150.0,  # ASSUMED gap sigma and evanescent decay length of mu, g
       retune_MHz=35.0,            # RF retune range = half of Shao 2020 3-dB BW 70 MHz
       facet_dB=1.5,               # conservative per facet (lensed fiber, APL 123,263502 (2023): 1.52 dB)
       Qi_spread=(0.7,1.3))        # ASSUMED uniform spread multiplier on ki
dfdT=f0*(P['dndT']+P['n_eff']*P['alpha'])/NG     # Hz/K magnitude, incl. expansion
dfdT_TO=f0*P['dndT']/NG
def sample(N,rng,p):
    ki=KI*(1+p['ki_extra_frac'])*rng.uniform(*p['Qi_spread'],N)
    dgap=rng.normal(0,p['sig_gap_nm'],N); dgap_b=rng.normal(0,p['sig_gap_nm'],N)
    mu=MU*np.exp(-dgap/p['gap_decay_nm']); g=G*np.exp(-dgap_b/p['gap_decay_nm'])
    eps=2*mu-WM                                      # rad/s
    # RF retuning: Omega can follow 2mu only within +/-retune; implement as residual eps on mu (W fixed)
    eps_res=np.sign(eps)*np.maximum(abs(eps)-p['retune_MHz']*MHz,0); mu=(WM+eps_res)/2
    sT=p['sigT_lock_mK']*1e-3
    Delta=rng.normal(0,sT,N)*dfdT*tp                 # common-mode residual
    dr=rng.normal(0,np.sqrt(2)*sT,N)*dfdT*tp         # two independent ring locks; static fab mismatch removed by heaters
    Qa=rng.uniform(p['Qa_min'],p['Qa_max'],N)
    return dict(mu=mu,g=g,ki=ki,Delta=Delta,dr=dr,eps_MHz=eps/MHz,eps_res_MHz=eps_res/MHz,Qa=Qa)
def mc(N,p,seed=1):
    s=sample(N,np.random.default_rng(seed),p); e,il,ea=runv(s['mu'],s['g'],s['ki'],s['Delta'],s['dr'])
    s.update(eta=e,IL=il,eta_abs=ea); return s
pct=lambda v:[float(np.percentile(v,q)) for q in (10,50,90)]
S={}
e,il,ea=runv(MU,G,KI,0,0); S['ideal']=dict(eta_shift=float(e[0]),IL_dB=float(il[0]),eta_abs=float(ea[0]))
e,il,ea=runv(MU,G,KI*(1+P['ki_extra_frac']),0,0); S['nominal_extra_loss']=dict(eta_shift=float(e[0]),IL_dB=float(il[0]),eta_abs=float(ea[0]))
# power: drive calibration via Shao S21 includes ~50% IDT; acoustic resonant enhancement ∝ Qa (assumed P ∝ 1/Qa)
P50=P_from_dw(DW,'AO_Shao_IDT(50%)'); P10=P_from_dw(DW,'AO_IDT_10%')
S['power_uW']=dict(IDT50_Qa2000=P50*1e6,IDT10_Qa2000=P10*1e6,check_10pct_equals_5x_50pct=bool(abs(P10/P50-5)<1e-9),
    IDT50_Qa1570=P50*2000/1570*1e6,IDT10_Qa1570=P10*2000/1570*1e6,IDT10_Qa3600=P10*2000/3600*1e6)
S['RF_FWHM_MHz']=dict(Qa2000=F/2000/1e6,Qa1570=F/1570/1e6,Qa3600=F/3600/1e6)
S['dfdT_GHz_per_K']=dict(thermo_optic_only=dfdT_TO/1e9,with_expansion=dfdT/1e9)
tol=json.load(open('data/tol_scan_summary.json'))
S['thermal_windows_mK_with_expansion']={k:{thr:min(-tol[k][thr][0],tol[k][thr][1])*1e6/dfdT*1e3 for thr in ('0.95','0.9')} for k in ('Delta','dr')}
N=1000; s=mc(N,P); fac=10**(-2*P['facet_dB']/10)
S['MC']=dict(N=N,eta_shift_p10_50_90=pct(s['eta']),IL_dB_p10_50_90=pct(s['IL']),eta_abs_onchip_p10_50_90=pct(s['eta_abs']),
   eta_abs_fiber_to_fiber_p10_50_90=pct(s['eta_abs']*fac),frac_eta_ge_095=float(np.mean(s['eta']>=0.95)),frac_eta_ge_090=float(np.mean(s['eta']>=0.90)),
   eps_raw_MHz_std=float(np.std(s['eps_MHz'])),frac_eps_beyond_retune=float(np.mean(s['eps_res_MHz']!=0)),
   P_uW_IDT10_p10_50_90=pct(P10*2000/s['Qa']*1e6))
S['ideal']['eta_abs_fiber_to_fiber']=S['ideal']['eta_abs']*fac
S['Shao2020_onchip_eff']=0.035; S['params']={k:v for k,v in P.items()}
with open('data/mc_samples.csv','w',newline='') as fh:
    w=csv.writer(fh); w.writerow(['mu_rad_s','g_rad_s','ki_rad_s','Delta_MHz','delta_r_MHz','eps_raw_MHz','eps_resid_MHz','Qa','P_uW_IDT10','eta_shift','IL_dB','eta_abs_onchip','eta_abs_fiber'])
    for i in range(N): w.writerow([s['mu'][i],s['g'][i],s['ki'][i],s['Delta'][i]/MHz,s['dr'][i]/MHz,s['eps_MHz'][i],s['eps_res_MHz'][i],s['Qa'][i],P10*2000/s['Qa'][i]*1e6,s['eta'][i],s['IL'][i],s['eta_abs'][i],s['eta_abs'][i]*fac])
# ---------------- 1D sensitivity of assumed params (N=300 each) ----------------
scans={'ki_extra_frac':[0,0.5,1,2,4],'sigT_lock_mK':[1,2,5,10,20],'sig_gap_nm':[1,2,5,10,20],'retune_MHz':[0,10,35,100,300]}
sens={}
for k,vals in scans.items():
    sens[k]=[]
    for v in vals:
        q=dict(P); q[k]=v; r=mc(300,q,seed=2); sens[k].append([v]+pct(r['eta'])+pct(r['IL'])+[float(np.median(r['eta_abs']))])
sens['facet_dB']=[[d,S['MC']['eta_abs_onchip_p10_50_90'][1]*10**(-2*d/10)] for d in (0.5,1.0,1.5,2.0,3.0)]
S['sensitivity']=sens
json.dump(S,open('data/realistic_summary.json','w'),indent=1)
print(json.dumps({k:S[k] for k in S if k not in ('sensitivity','params')},indent=1)); print(json.dumps(sens,indent=0))
# ---------------- figure ----------------
fig,ax=plt.subplots(1,3,figsize=(7.0,2.3))
ax[0].hist(s['eta'],bins=40,color='C0'); ax[0].axvline(S['ideal']['eta_shift'],color='k',ls='--',lw=0.8,label='ideal')
ax[0].axvline(np.median(s['eta']),color='C3',lw=0.8,label='MC median'); ax[0].set_xlabel(r'$\eta_{\rm shift}$'); ax[0].set_ylabel('count'); ax[0].legend(fontsize=6)
ax[1].hist(s['IL'],bins=40,color='C2'); ax[1].axvline(S['ideal']['IL_dB'],color='k',ls='--',lw=0.8); ax[1].set_xlabel('on-chip IL (dB)')
lab=['ideal\nchip','real.\nchip','real.\nfiber','Shao\n2020']
val=[S['ideal']['eta_abs'],S['MC']['eta_abs_onchip_p10_50_90'][1],S['MC']['eta_abs_fiber_to_fiber_p10_50_90'][1],0.035]
lo=[0,val[1]-S['MC']['eta_abs_onchip_p10_50_90'][0],val[2]-S['MC']['eta_abs_fiber_to_fiber_p10_50_90'][0],0]
hi=[0,S['MC']['eta_abs_onchip_p10_50_90'][2]-val[1],S['MC']['eta_abs_fiber_to_fiber_p10_50_90'][2]-val[2],0]
ax[2].bar(range(4),val,yerr=[lo,hi],color=['0.6','C0','C1','C3'],capsize=2); ax[2].set_xticks(range(4)); ax[2].set_xticklabels(lab,fontsize=6)
ax[2].set_ylabel('absolute shifted power')
for a,l in zip(ax,'abc'): a.text(-0.3,1.02,'(%s)'%l,transform=a.transAxes,fontsize=8)
fig.tight_layout(); fig.savefig('fig/figB5_realistic_MC.png',dpi=300); fig.savefig('fig/figB5_realistic_MC.pdf')
