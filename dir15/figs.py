import json,numpy as np,matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
R=json.load(open('data/iter1_tips.json'))
fig,ax=plt.subplots(1,2,figsize=(9,3.5))
for t in (0.3,0.6):
  for clad,ls in (('oxide','-'),('polymer','--')):
    ks=[k for k in R if f'_{t}_{clad}_' in k]; w=[R[k]['w'] for k in ks]
    ax[0].plot(w,[-10*np.log10(R[k]['eta_SMF28_direct']) for k in ks],ls,marker='o',label=f't={t}um {clad}-clad')
    ax[1].plot(w,[-10*np.log10(R[k]['eta_bestGauss']) for k in ks],ls,marker='o',label=f't={t}um {clad}-clad')
ax[0].axhline(0.29,color='k',lw=0.8); ax[0].text(0.5,0.35,'SOTA monolithic 0.29 dB (APL Photon. 2024)',fontsize=7)
ax[0].set(xlabel='tip width (um)',ylabel='loss to SMF-28 butt (dB)',yscale='log',title='direct butt coupling')
ax[1].set(xlabel='tip width (um)',ylabel='mode-mismatch loss, ideal lens (dB)',title='best-Gaussian bound (freeform lens)')
ax[0].legend(fontsize=7); plt.tight_layout(); plt.savefig('fig/iter1_tip_coupling.png',dpi=150)
M=json.load(open('data/iter3_mc.json'))
groups=[('inshift_','input shift (um)'),('planeshift_','inter-plane shift sigma (um)'),('height_corr3px_','height error sigma (um)'),('dz_','plane spacing error sigma (um)')]
fig,ax=plt.subplots(1,4,figsize=(13,3))
for a,(g,lab) in zip(ax,groups):
    ks=[k for k in M if k.startswith(g) and 'y_' not in k]; xs=[float(k[len(g):].replace('um','')) for k in ks]
    a.errorbar(xs,[M[k]['F'][0] for k in ks],[M[k]['F'][1] for k in ks],marker='o',label='F (fixed)')
    a.errorbar(xs,[M[k]['F_trim'][0] for k in ks],[M[k]['F_trim'][1] for k in ks],marker='s',label='F (on-chip phase trim)')
    b=a.twinx(); b.plot(xs,[M[k]['IL_dB'][0] for k in ks],'r^:'); b.set_ylabel('IL (dB)',color='r')
    a.set(xlabel=lab,ylim=(0.85,1.0)); a.axhline(0.901,color='k',lw=0.7,ls='--')
ax[0].legend(fontsize=7); ax[0].set_ylabel('process fidelity'); plt.tight_layout(); plt.savefig('fig/iter3_tolerance.png',dpi=150)
ph=np.load('data/mplc_w2.5_p10.0_W8.0_K4_dz40.0.npy')
fig,ax=plt.subplots(1,4,figsize=(12,3))
for i in range(4): ax[i].imshow(np.mod(ph[i],2*np.pi)[40:120,40:120],cmap='twilight'); ax[i].set_title(f'plane {i+1}'); ax[i].axis('off')
plt.tight_layout(); plt.savefig('fig/iter3_phase_planes.png',dpi=120)
