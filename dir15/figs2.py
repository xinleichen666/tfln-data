import json,numpy as np,matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
fig,axs=plt.subplots(2,1,figsize=(11,7),sharex=True)
for ax,d in zip(axs,(3,5)):
    R=json.load(open(f'data/mc2_d{d}.json')); ks=[k for k in R]
    x=np.arange(len(ks))
    for off,key,lab in ((-0.2,'F','fixed phases'),(0.2,'F_trim','EO input-phase trim')):
        m=[R[k][key]['mean'] for k in ks]; lo=[R[k][key]['mean']-R[k][key]['p2_5'] for k in ks]; hi=[R[k][key]['p97_5']-R[k][key]['mean'] for k in ks]
        ax.errorbar(x+off,m,[lo,hi],fmt='o',ms=4,capsize=2,label=lab)
    ax.axhline(0.901,ls='--',c='k',lw=0.8); ax.text(0,0.905,'U2 experiment 0.901 (free-space, d=3)',fontsize=7)
    ax.set_ylim(0.6,1.005); ax.set_ylabel(f'd={d} process fidelity'); ax.legend(fontsize=7,loc='lower left')
axs[1].set_xticks(x); axs[1].set_xticklabels(ks,rotation=60,ha='right',fontsize=7)
plt.tight_layout(); plt.savefig('fig/v2_mc_fidelity.png',dpi=140)
R=json.load(open('data/fresnel_d3.json'))
fig,ax=plt.subplots(1,2,figsize=(10,3.5))
names=['thin_noFresnel_air','air_uncoated','air_AR0.5pct','air_AR0.1pct','embed1.37_exit_uncoated','embed1.37_exit_AR0.5pct']
lams=(1.548,1.549,1.55,1.551,1.552)
for n in names:
    gh='False' if n.startswith('thin') else 'True'
    ax[0].plot(lams,[R[f'{n}|lam{l}|ghost{gh}']['IL_dB'] for l in lams],'o-',label=n)
    ax[1].plot(lams,[R[f'{n}|lam{l}|ghost{gh}']['F'] for l in lams],'o-',label=n)
ax[0].set(xlabel='wavelength (um)',ylabel='IL (dB), incl. Fresnel+ghosts'); ax[1].set(xlabel='wavelength (um)',ylabel='fidelity'); ax[0].legend(fontsize=6)
plt.tight_layout(); plt.savefig('fig/v2_fresnel.png',dpi=140)
