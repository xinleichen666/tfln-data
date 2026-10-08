import json,numpy as np,matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
T=['F3','F4','H2xH2','Toffoli']
B=json.load(open('res2_bias.json')); plt.figure(figsize=(5,4))
for t in T:
  M=[0,1,2,4,8,16,32]; plt.semilogy(np.array(M)+0.5,[1-B[f'{t}|{m}']['F'] for m in M],'o-',label=t)
plt.xscale('log');plt.xlabel('number of test couplers measured (+0.5)');plt.ylabel('mean 1-F over 64 chips');plt.title('wafer bias b=0.15, random 0.03');plt.legend();plt.grid(alpha=.3);plt.tight_layout();plt.savefig('fig2_bias_vs_ntest.png',dpi=130)
fig,ax=plt.subplots(1,4,figsize=(18,4.2))
for i,t in enumerate(T):
  for tag,mk,lab in (('coh','o-','MAP fit, single+coherent-pair inputs'),('int','s--','MAP fit, single-port intensity only')):
    R=json.load(open(f'res2_fit_{t}_{tag}.json'))
    for nph,c in (('10000','C0'),('1e+06','C1')):
      ks=sorted([k for k in R if k.startswith(f'MAP|{nph}|')],key=lambda k:int(k.split('|')[2]))
      ax[i].semilogy([R[k]['readings'] for k in ks],[1-R[k]['F'] for k in ks],mk,color=c,label=f'{lab}, N_ph={nph}')
    if tag=='coh':
      ks=sorted([k for k in R if k.startswith('SEQ|1e+06|')],key=lambda k:int(k.split('|')[2]))
      ax[i].semilogy([R[k]['readings'] for k in ks],[1-R[k]['F'] for k in ks],'^:',color='C3',label='sequential single-MZI sweeps (phase only)')
      ax[i].axhline(1-R['none'],color='k',ls=':',label='no calibration'); ax[i].axhline(max(1-R['oracle'],1e-7),color='g',ls='-.',label='oracle (true errors)')
  if t in ('F4','Toffoli'):
    R=json.load(open(f'res2_fit_{t}_cohres.json')); ks=sorted([k for k in R if k.startswith('MAP|1e+06|')],key=lambda k:int(k.split('|')[2]))
    ax[i].semilogy([R[k]['readings'] for k in ks],[1-R[k]['F'] for k in ks],'d-',color='C4',label='coh, +unmodeled 0.02 rad coupler phase')
  ax[i].set_xscale('log');ax[i].set_title(f'{t} (sigma=0.1)');ax[i].set_xlabel('number of power readings');ax[i].grid(alpha=.3);ax[i].set_ylim(1e-7,1)
ax[0].set_ylabel('mean 1-F after calibration');ax[3].legend(fontsize=6);plt.tight_layout();plt.savefig('fig2_fidelity_vs_measurements.png',dpi=130)
D=json.load(open('res2_double.json')); plt.figure(figsize=(5,4)); S=[0.05,0.1,0.2,0.3]
for t,c in zip(['F4','H2xH2','Toffoli'],['C0','C1','C2']):
  for dbl,ls in (('False','-'),('True','--')):
    plt.semilogy(S,[max(1-D[f'{t}|{dbl}|{s}']['F'],1e-12) for s in S],ls,marker='o',color=c,label=f'{t} {"double-MZI coupler" if dbl=="True" else "standard MZI"}')
plt.xlabel('coupler error sigma');plt.ylabel('1-F after known-error calibration');plt.legend(fontsize=7);plt.grid(alpha=.3);plt.tight_layout();plt.savefig('fig2_double_mzi.png',dpi=130)
