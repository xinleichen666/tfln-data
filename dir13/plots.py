import json,glob,numpy as np,matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
R={};[R.update(json.load(open(f))) for f in glob.glob('res_split_*.json')]
SIG=[0.0,0.02,0.05,0.1,0.15,0.2]
fig,ax=plt.subplots(1,4,figsize=(18,4.2))
for i,t in enumerate(['F3','F4','H2xH2','Toffoli']):
  for arch,ls in (('clements','-'),('reck','--')):
    for k,c,lab in (('a','C0','ideal-programmed'),('b','C1','error-aware trained'),('c','C2','known-error calibrated')):
      ax[i].plot(SIG,[1-R[f'{t}|{arch}|{s}'][k][0] for s in SIG],ls,color=c,marker='o',label=f'{lab} ({arch})')
  ax[i].set_yscale('log'); ax[i].set_ylim(1e-6,1); ax[i].set_title(t); ax[i].set_xlabel('coupler error sigma (rad, t=pi/4+eps)'); ax[i].grid(alpha=.3)
ax[0].set_ylabel('mean infidelity 1-F'); ax[3].legend(fontsize=7); plt.tight_layout(); plt.savefig('fig_infidelity_vs_sigma.png',dpi=130)
# scaling
plt.figure(figsize=(5,4))
K={'F3':3,'F4':6,'H2xH2':6,'Toffoli':28}
for t in K: plt.plot(SIG[1:],[(1-R[f'{t}|clements|{s}']['a'][0])/K[t] for s in SIG[1:]],'o-',label=t)
s=np.array(SIG[1:]); plt.plot(s,s**2,'k:',label='sigma^2'); plt.xscale('log');plt.yscale('log');plt.xlabel('sigma');plt.ylabel('(1-F)/N_MZI, ideal-programmed');plt.legend();plt.grid(alpha=.3);plt.tight_layout();plt.savefig('fig_scaling.png',dpi=130)
# DC
D=json.load(open('dc_supermodes.json')); plt.figure(figsize=(5,4))
for w in (1.1,1.2,1.3):
  g=[d['g'] for d in D if d['w']==w]; L=[d['Lc_um'] for d in D if d['w']==w]; plt.semilogy(g,L,'o-',label=f'w={w} um')
plt.xlabel('gap (um)');plt.ylabel('coupling length Lc (100% transfer), um');plt.title('X-cut 600nm TFLN, 300nm etch, SiO2 clad, 1550nm (FD quasi-TE)');plt.legend();plt.grid(alpha=.3);plt.tight_layout();plt.savefig('fig_dc_Lc_vs_gap.png',dpi=130)
B=json.load(open('res_bias.json')); plt.figure(figsize=(5,4))
for t in ('F3','Toffoli'):
  b=[0.05,0.1,0.2]; plt.semilogy(b,[1-B[f'{t}|b={x}|s=0.02']['ideal'] for x in b],'o-',label=f'{t} ideal-programmed'); plt.semilogy(b,[1-B[f'{t}|b={x}|s=0.02']['bias_aware'] for x in b],'s--',label=f'{t} bias-aware trained')
plt.xlabel('systematic coupler bias b (rad), +random sigma=0.02');plt.ylabel('1-F');plt.legend(fontsize=8);plt.grid(alpha=.3);plt.tight_layout();plt.savefig('fig_systematic_bias.png',dpi=130)
