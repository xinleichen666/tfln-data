"""Plots data/iter6_fair.json (no new simulation). Output: figures/fig6_fair.{pdf,png}."""
import json, numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
plt.rcParams.update({'font.size':8,'font.family':'serif','mathtext.fontset':'dejavuserif','axes.linewidth':0.6,'lines.linewidth':1.1})
J=json.load(open('../data/iter6_fair.json'))
fig,ax=plt.subplots(1,2,figsize=(7.0,2.4))
for k,lab,c in [('B_Qi_Shao2019_80.75MHz',r'$\kappa_i/2\pi=80.75$ MHz (Shao 2019)','C1'),('B_Qi_design_60MHz',r'$\kappa_i/2\pi=60$ MHz','C0')]:
    R=J[k]; ke=[r['ke_GHz'] for r in R]
    ax[0].semilogy(ke,[r['AO_P_W']*1e3 for r in R],c+'o-',ms=4,label='AO, '+lab)
    ax[0].semilogy(ke,[r['EO_P_W']*1e3 for r in R],c+'s--',ms=4,label='EO, '+lab)
ax[0].axhline(96,color='k',ls=':',lw=0.8); ax[0].text(0.55,125,'Hu 2021 EO, measured (96 mW)',fontsize=6)
ax[0].set_xlabel(r'waveguide coupling $\gamma/2\pi$ (GHz)'); ax[0].set_ylabel(r'RF power at max $\eta_{\rm shift}$ (mW)'); ax[0].set_ylim(1e-3,400); ax[0].legend(fontsize=5.2,loc='center right')
D=J['B_RF_detuning_ShaoQ']; df=np.array([d['df_MHz'] for d in D]); e=np.array([d['eta_shift'] for d in D])
ax[1].semilogx(df[1:],e[1:],'C1o-'); ax[1].axhline(e[0],color='C1',ls=':',lw=0.8); ax[1].text(3,e[0]-0.09,r'$\delta f=0$: %.1f%%'%(100*e[0]),fontsize=6,color='C1')
ax[1].set_xlabel(r'RF detuning $\delta f$ (MHz)'); ax[1].set_ylabel(r'$\eta_{\rm shift}$ (design B)'); ax[1].set_ylim(0,1.08)
for i,a in enumerate(ax): a.text(0.03 if i==0 else 0.9,0.92 if i==0 else 0.8,'(%s)'%'ab'[i],transform=a.transAxes)
fig.tight_layout(); fig.savefig('figures/fig6_fair.pdf'); fig.savefig('figures/fig6_fair.png',dpi=300)
