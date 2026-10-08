import numpy as np, json, csv, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from iter5_aomolecule import simulate, ring_dw_per_V, tp, cases
plt.rcParams.update({'font.size':8,'font.family':'serif','mathtext.fontset':'dejavuserif','axes.linewidth':0.6,'lines.linewidth':1.1})
des={'A':dict(c='A_nonsuspended_Ni2026',ke=0.10e9,ki=0.01e9,T=80e-9),'B':dict(c='B_suspended_Shao2019',ke=0.60e9,ki=0.06e9,T=40e-9)}
out={}; sweep=[]
for k,d in des.items():
    p=cases[d['c']]; wm=tp*p['f']; g=ring_dw_per_V(p['VpiL'],p['La'],p['Lring'])
    Ps=np.logspace(-6.5,-2.5,36) if k=='A' else np.logspace(-8,-4,36); R=[]
    for P in Ps:
        dw=g*np.sqrt(2*50*P); r=simulate(wm/2,tp*d['ke'],tp*d['ki'],wm,dw,T=d['T']); s=max(r[1],r[-1]); tot=sum(r.values())
        R.append([P,s/tot,s,r[0],tot]); sweep.append([k,P,s/tot,s,r[0],tot])
    R=np.array(R); i=np.argmax(R[:,1]); dwb=g*np.sqrt(100*R[i,0])
    spec=simulate(wm/2,tp*d['ke'],tp*d['ki'],wm,dwb,T=d['T'])
    out[k]=dict(R=R,spec=spec,best=dict(P_W=R[i,0],eta_shift=R[i,1],eta_abs=R[i,2],IL_dB=-10*np.log10(R[i,4]),carrier_rel_dB=10*np.log10(R[i,3]/R[i,2]),f_GHz=p['f']/1e9,ke_GHz=d['ke']/1e9,ki_GHz=d['ki']/1e9))
# Q dependence (design A)
p=cases[des['A']['c']]; wm=tp*p['f']; g=ring_dw_per_V(p['VpiL'],p['La'],p['Lring']); Qrows=[]
for ki in [0.003e9,0.01e9,0.03e9,0.1e9]:
    best=None
    for ke in [0.08e9,0.10e9,0.13e9]:
        for x in np.linspace(0.7,1.2,7):
            dw=x*tp*(ke+ki); r=simulate(wm/2,tp*ke,tp*ki,wm,dw,T=80e-9); s=max(r[1],r[-1]); tot=sum(r.values())
            if best is None or s/tot>best[2]: best=[ki,ke,s/tot,s,-10*np.log10(tot),(dw/g)**2/100]
    Qrows.append(best)
Qrows=np.array(Qrows); Qi=193.4e12/Qrows[:,0]
with open('data/iter5_power_sweep.csv','w',newline='') as f: w=csv.writer(f); w.writerow(['design','P_RF_W','eta_shift','eta_abs','p_carrier','p_total']); w.writerows(sweep)
with open('data/iter5_Q_sweep.csv','w',newline='') as f: w=csv.writer(f); w.writerow(['ki_Hz','ke_Hz','Q_i','eta_shift','eta_abs','IL_dB','P_RF_W']); w.writerows([list(r[:2])+[q]+list(r[2:]) for r,q in zip(Qrows,Qi)])
json.dump({k:v['best'] for k,v in out.items()},open('data/iter5_final.json','w'),indent=1)
fig,ax=plt.subplots(1,3,figsize=(7.0,2.3))
for k,cl in [('A','C0'),('B','C1')]:
    R=out[k]['R']; ax[0].semilogx(R[:,0]*1e3,R[:,1],cl,label=f'AO design {k} ($\\eta_{{\\rm shift}}$)'); ax[0].semilogx(R[:,0]*1e3,R[:,2],cl+'--',label=f'{k} absolute')
ax[0].axvline(96,color='k',ls=':'); ax[0].plot(96,0.987,'k*',ms=7,label='Hu 2021 EO (meas.)'); ax[0].axvline(10,color='gray',ls='-.',lw=0.8); ax[0].text(11,0.05,'Hu proj.\n1 V',fontsize=6,color='gray')
ax[0].set_xlabel('RF power (mW)'); ax[0].set_ylabel('efficiency'); ax[0].set_ylim(0,1.02); ax[0].legend(fontsize=5.2,loc='center left'); ax[0].set_xlim(1e-5,300)
qs=np.arange(-3,4)
for k,off,cl in [('A',-0.18,'C0'),('B',0.18,'C1')]:
    s=out[k]['spec']; v=np.array([s[q] for q in qs]); ax[1].bar(qs+off,10*np.log10(v+1e-12)+80,0.34,bottom=-80,color=cl,label=k)
ax[1].set_ylim(-80,2); ax[1].set_xlabel(r'output order $q$ ($\omega_L+q\Omega_m$)'); ax[1].set_ylabel('power (dB, rel. input)'); ax[1].legend(fontsize=6)
a2=ax[2]; a2.semilogx(Qi,Qrows[:,2],'C0o-',label=r'$\eta_{\rm shift}$'); a2.semilogx(Qi,Qrows[:,3],'C0s--',label='absolute'); a2.axhline(0.987,color='k',ls=':',lw=0.8)
a2.set_xlabel(r'intrinsic $Q_i$'); a2.set_ylabel('efficiency (design A)'); a2.set_ylim(0,1.02); a2.set_xticks([1e6,1e7,1e8]); a2.minorticks_off(); b_dummy=None
b=a2.twinx(); b.semilogx(Qi,Qrows[:,5]*1e6,'C3^-'); b.minorticks_off(); b.set_ylabel(r'RF power ($\mu$W)',color='C3'); a2.legend(fontsize=6,loc='center right')
from matplotlib.ticker import LogLocator,LogFormatterMathtext,NullLocator
a2.set_xlim(1e6,1e8); a2.xaxis.set_major_locator(LogLocator(base=10,numticks=5)); a2.xaxis.set_major_formatter(LogFormatterMathtext()); a2.xaxis.set_minor_locator(LogLocator(base=10,subs=np.arange(2,10)*0.1,numticks=20)); a2.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
for i,a in enumerate(ax): a.text(0.03 if i<2 else 0.45,0.92 if i<2 else 0.05,'(%s)'%'abc'[i],transform=a.transAxes)
fig.tight_layout(); fig.savefig('fig/fig5_ao_molecule.png',dpi=300); fig.savefig('fig/fig5_ao_molecule.pdf')
print(json.dumps({k:v['best'] for k,v in out.items()},indent=1)); print(Qrows)
