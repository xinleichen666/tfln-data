import numpy as np,matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from mplc import *
ph=list(np.load('data/mplc_w2.5_p10.0_W8.0_K4_dz40.0.npy')); ins=inputs(3,10.0,2.5)
outs=run(ph,ins,1.55,[40.0]*5)
basis=[LG(-1,0,8.0),LG(0,0,8.0),LG(1,0,8.0)]; T=Tmat(outs,basis)
fig,ax=plt.subplots(2,4,figsize=(11,5.5))
ax[0,0].imshow(sum(abs(e)**2 for e in ins)[50:110,50:110]); ax[0,0].set_title('chip facet: 3 waveguides')
for j in range(3):
  ax[0,j+1].imshow(abs(outs[j][50:110,50:110])**2); ax[0,j+1].set_title(f'input {j}: |E|^2')
  ax[1,j+1].imshow(np.angle(outs[j][50:110,50:110]),cmap='twilight'); ax[1,j+1].set_title('phase')
ax[1,0].imshow(abs(T)**2/np.max(abs(T)**2),vmin=0,vmax=1); ax[1,0].set_title('|T|^2 (LG -1,0,+1)')
for a in ax.ravel(): a.set_xticks([]); a.set_yticks([])
plt.tight_layout(); plt.savefig('fig/iter3_fields.png',dpi=120); print(np.round(abs(T)**2,3))
