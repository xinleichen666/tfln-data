import numpy as np, json, csv, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from core import *
plt.rcParams.update({'font.size':8,'font.family':'serif','mathtext.fontset':'dejavuserif','axes.linewidth':0.6,'lines.linewidth':1.1})
R={}
# 1) efficiency vs coupling, AO and EO
xs=np.logspace(-1.3,0.6,34)
sw={}
for mode,base in [('ao',G+KI),('eo',G/2)]:
    rows=[]
    for x in xs:
        dw=x*base; m=metrics(run(MU,G,KI,WM,dw,mode)); rows.append([dw,m['eta_shift'],m['eta_abs'],m['IL_dB'],m['carrier_rel_dB']])
    sw[mode]=np.array(rows)
cases_ao=['AO_Shao_IDT(50%)','AO_IDT_100%','AO_IDT_10%']; cases_eo=['EO_unmatched(Vc=V0)','EO_open(Vc=2V0)','EO_LC_Q30','EO_LC_Q100','EO_LC_ideal']
with open('data/eff_vs_power.csv','w',newline='') as fh:
    w=csv.writer(fh); w.writerow(['drive','case','dw_rad_s','P_source_W','eta_shift','eta_abs','IL_dB','carrier_rel_dB'])
    for mode,cs in [('ao',cases_ao),('eo',cases_eo)]:
        for c in cs:
            for r in sw[mode]: w.writerow([mode,c,r[0],P_from_dw(r[0],c)]+list(r[1:]))
opt={}
for mode,cs in [('ao',cases_ao),('eo',cases_eo)]:
    i=np.argmax(sw[mode][:,1]); dw=sw[mode][i,0]
    opt[mode]=dict(dw_GHz=dw/tp/1e9,eta_shift=sw[mode][i,1],eta_abs=sw[mode][i,2],IL_dB=sw[mode][i,3],carrier_rel_dB=sw[mode][i,4],P_W={c:P_from_dw(dw,c) for c in cs})
R['optimum']=opt
# 2) spectrum at AO optimum
dwA=opt['ao']['dw_GHz']*tp*1e9; spec=metrics(run(MU,G,KI,WM,dwA,'ao'))['p']; specE=metrics(run(MU,G,KI,WM,opt['eo']['dw_GHz']*tp*1e9,'eo'))['p']
R['spectrum_dB']={'ao':{q:10*np.log10(v) for q,v in spec.items()},'eo':{q:10*np.log10(v) for q,v in specE.items()}}
# 3) Q tolerance (re-optimize dw for each Qi) and RF detuning (acoustic Lorentzian gamma/2pi = 3.33GHz/2000)
Qrows=[]
for kiH in [0.02e9,0.04e9,0.08075e9,0.15e9,0.3e9]:
    best=None
    for x in np.linspace(0.6,1.4,9):
        dw=x*(G+tp*kiH); m=metrics(run(MU,G,tp*kiH,WM,dw,'ao'))
        if best is None or m['eta_shift']>best[2]: best=[kiH,193.4e12/kiH,m['eta_shift'],m['eta_abs'],m['IL_dB'],P_from_dw(dw,'AO_Shao_IDT(50%)')]
    Qrows.append(best)
gam=F/2000/1e6  # MHz FWHM
Drows=[]
for df in [0,0.2,0.4,0.6,0.8,1.0,1.5,2,3,5]:
    a=dwA/np.sqrt(1+(2*df/gam)**2); m=metrics(run(MU,G,KI,WM,a,'ao',df=df*1e6))
    me=metrics(run(MU,G,KI,WM,opt['eo']['dw_GHz']*tp*1e9,'eo',df=df*1e6))   # EO: flat drive (LC BW ~122 MHz)
    Drows.append([df,m['eta_shift'],me['eta_shift']])
np.savetxt('data/Q_tolerance.csv',np.array(Qrows),delimiter=',',header='kappa_i_Hz,Q_i,eta_shift,eta_abs,IL_dB,P_source_W_ShaoIDT',comments='')
np.savetxt('data/RF_detuning.csv',np.array(Drows),delimiter=',',header='df_MHz,eta_shift_AO(acoustic Lorentzian),eta_shift_EO(flat drive)',comments='')
# 4) IDT efficiency sensitivity
eff=np.logspace(-2,0,30); P_ao=[P_from_dw(dwA,'AO_Shao_IDT(50%)')*0.5/e for e in eff]
np.savetxt('data/IDT_sensitivity.csv',np.c_[eff,P_ao],delimiter=',',header='IDT_efficiency,P_source_W',comments='')
# 5) HOM: optical transfer function H(Delta) of shifted amplitude, AO optimum
hom=[]; Hall=[]
for sig in [5e6,10e6,25e6,50e6,100e6,200e6]:   # Gaussian photon amplitude, rms spectral width of |psi|^2 = sig
    Ds=np.linspace(-4,4,41)*sig; H=[]
    for D in Ds:
        c=run(MU,G,KI,WM,dwA,'ao',Delta=tp*D); H.append(c[1] if abs(c[1])>abs(c[-1]) else c[-1])
    H=np.array(H); Hall+= [[sig,D_,h.real,h.imag] for D_,h in zip(Ds,H)]
    psi=np.exp(-Ds**2/(4*sig**2)); A=H*psi
    ov=abs(np.sum(np.conj(psi)*A))**2/(np.sum(abs(psi)**2)*np.sum(abs(A)**2))
    hom.append([sig,ov,ov*opt['ao']['eta_shift'],np.sum(abs(A)**2)/np.sum(abs(psi)**2)])
np.savetxt('data/H_shift.csv',np.array(Hall),delimiter=',',header='photon_bw_Hz,Delta_Hz,ReH,ImH',comments='')
np.savetxt('data/HOM.csv',np.array(hom),delimiter=',',header='photon_rms_bw_Hz,V_filtered(target bin),V_unfiltered(=V*eta_shift),eta_abs_spectral',comments='')
R['HOM']=hom
# 6) thermal phonons
hb=1.0546e-34;kB=1.380649e-23; gamma=WM/2000; ge=0.15*gamma
Pac=P_from_dw(dwA,'AO_Shao_IDT(50%)'); Ncoh=4*ge/gamma**2*Pac/(hb*WM)
th={}
for T in [300,4,0.01]:
    nth=1/np.expm1(hb*WM/(kB*T)); th[str(T)]=dict(n_th=nth,ratio_nth_over_Ncoh=nth/Ncoh)
R['thermal']=dict(N_coh=Ncoh,cases=th,note='Pump-free, number-conserving beam-splitter process: no noise photons are generated without an input photon; thermal phonons only add incoherent coupling noise of order n_th/N_coh.')
json.dump(R,open('data/results_B.json','w'),indent=1,default=float)
# ---------- figures
fig,ax=plt.subplots(1,2,figsize=(7.0,2.5),gridspec_kw=dict(width_ratios=[1.25,1]))
sty={'AO_Shao_IDT(50%)':('C0','-'),'AO_IDT_100%':('C0','--'),'AO_IDT_10%':('C0',':'),'EO_unmatched(Vc=V0)':('C3','-'),'EO_open(Vc=2V0)':('C3','-.'),'EO_LC_Q30':('C1','--'),'EO_LC_Q100':('C1','-'),'EO_LC_ideal':('C1',':')}
lab={'AO_Shao_IDT(50%)':'AO, Shao IDT (50%)','AO_IDT_100%':'AO, ideal IDT','AO_IDT_10%':'AO, 10% IDT','EO_unmatched(Vc=V0)':'EO unmatched ($V_c$=$V_0$)','EO_open(Vc=2V0)':'EO open ($V_c$=2$V_0$)','EO_LC_Q30':'EO LC-matched, $Q_L$=30','EO_LC_Q100':'EO LC-matched, $Q_L$=100','EO_LC_ideal':'EO LC, ideal $L$'}
for mode,cs in [('ao',cases_ao),('eo',cases_eo)]:
    for c in cs:
        P=[P_from_dw(r[0],c) for r in sw[mode]]; ax[0].semilogx(np.array(P)*1e3,sw[mode][:,1],color=sty[c][0],ls=sty[c][1],label=lab[c])
ax[0].plot(96,0.987,'k*',ms=7,label='Hu 2021 EO meas. (28.2 GHz)'); ax[0].plot(1000,0.035,'kv',ms=5,label='Shao 2020 AO, meas. (abs.)')
ax[0].set_xlabel('source RF power (mW)'); ax[0].set_ylabel(r'$\eta_{\rm shift}$'); ax[0].set_ylim(0,1.03); ax[0].set_xlim(1e-6,3e3); ax[0].legend(fontsize=4.6,loc='center left',bbox_to_anchor=(1.0,0.5),frameon=False)
qs=np.arange(-3,4)
for k,off,cl in [('ao',-0.18,'C0'),('eo',0.18,'C1')]:
    v=np.array([R['spectrum_dB'][k][q] for q in qs]); ax[1].bar(qs+off,v+80,0.34,bottom=-80,color=cl,label=k.upper())
ax[1].set_ylim(-80,2); ax[1].set_xlabel(r'order $q$ ($\omega_L+q\Omega_m$)'); ax[1].set_ylabel('output (dB rel. input)'); ax[1].legend(fontsize=6)
for i,a in enumerate(ax): a.text(0.93,0.92,'(%s)'%'ab'[i],transform=a.transAxes)
fig.tight_layout(); fig.subplots_adjust(wspace=0.75); fig.savefig('fig/figB1_eff_power_spectrum.png',dpi=300); fig.savefig('fig/figB1_eff_power_spectrum.pdf')
from matplotlib.ticker import LogFormatterMathtext
fig,ax=plt.subplots(1,3,figsize=(7.0,2.3)); Q=np.array(Qrows); D=np.array(Drows); h=np.array(hom)
ax[0].semilogx(Q[:,1],Q[:,2],'C0o-',label=r'$\eta_{\rm shift}$'); ax[0].semilogx(Q[:,1],Q[:,3],'C0s--',label='absolute'); ax[0].axvline(193.4e12/0.08075e9,color='gray',ls=':'); ax[0].text(2.5e6,0.62,'Shao 2019',fontsize=6,color='gray')
ax[0].set_xlabel(r'intrinsic $Q_i$'); ax[0].set_ylabel('efficiency'); ax[0].set_ylim(0,1.02); ax[0].legend(fontsize=6,loc='center right'); ax[0].xaxis.set_major_formatter(LogFormatterMathtext())
ax[1].plot(D[:,0],D[:,1],'C0o-',label='AO'); ax[1].plot(D[:,0],D[:,2],'C1s-',ms=3,label='EO (LC, 122 MHz BW)'); ax[1].set_xlabel('RF detuning (MHz)'); ax[1].set_ylabel(r'$\eta_{\rm shift}$'); ax[1].set_ylim(0,1.08); ax[1].legend(fontsize=6,loc='center right')
ax[2].loglog(eff*100,np.array(P_ao)*1e6,'C0',label='AO vs IDT eff.')
for c,cl,ls in [('EO_LC_Q30','C1','--'),('EO_LC_Q100','C1','-'),('EO_LC_ideal','C1',':')]: ax[2].axhline(opt['eo']['P_W'][c]*1e6,color=cl,ls=ls,lw=0.9,label=lab[c])
ax[2].axvline(50,color='gray',ls=':',lw=0.8); ax[2].axvline(10,color='gray',ls=':',lw=0.8)
ax[2].set_xlabel('IDT RF→acoustic efficiency (%)'); ax[2].set_ylabel(r'source power ($\mu$W)'); ax[2].legend(fontsize=5,loc='upper right',bbox_to_anchor=(1,0.86)); ax[2].xaxis.set_major_formatter(LogFormatterMathtext())
for i,a in enumerate(ax): a.text(0.04 if i<2 else 0.88,0.04 if i<2 else 0.9,'(%s)'%'abc'[i],transform=a.transAxes)
fig.tight_layout(); fig.savefig('fig/figB2_tolerance_IDT.png',dpi=300); fig.savefig('fig/figB2_tolerance_IDT.pdf')
fig,ax=plt.subplots(1,1,figsize=(3.4,2.4)); ax.semilogx(h[:,0]/1e6,1-h[:,1],'C2o-',label='filtered target bin'); ax.semilogx(h[:,0]/1e6,1-h[:,2],'C3s--',label='unfiltered')
ax.set_yscale('log'); ax.set_xlabel('photon rms bandwidth (MHz)'); ax.set_ylabel(r'$1-V_{\rm HOM}$'); ax.legend(fontsize=6); fig.tight_layout(); fig.savefig('fig/figB3_HOM.png',dpi=300); fig.savefig('fig/figB3_HOM.pdf')
print(json.dumps({k:R[k] for k in ['optimum','HOM','thermal']},indent=1,default=float)); print(Qrows); print(Drows)
