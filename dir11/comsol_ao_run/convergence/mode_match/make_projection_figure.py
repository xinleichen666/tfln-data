from pathlib import Path
import numpy as np,pandas as pd,glob,os
import matplotlib.pyplot as plt
base=Path(r'D:\comsol_ao_run\convergence\mode_match')
out=Path(r'C:\Users\Administrator\Documents\Codex\2026-10-20\new-chat\outputs\tfln_ao_preprint\paper\data\coupled_drive')
def load(p):
 d=pd.read_csv(p,comment='%');a=d.to_numpy(float);xyz=a[:,:3];mask=(xyz[:,1]>=-1e-12)&(xyz[:,1]<=500e-9+1e-12);return xyz[mask],a[mask,6:9]
xe,phi=load(base/'fine_mode02_3.305664GHz.csv');den=np.sum(phi**2)
rows=[]
for p in sorted(glob.glob(str(base/'driven_target_*.csv'))):
 d=pd.read_csv(p,comment='%');a=d.to_numpy(float);xyz=a[:,:3];mask=(xyz[:,1]>=-1e-12)&(xyz[:,1]<=500e-9+1e-12);freq=float(p.split('_')[-1].replace('GHz.csv',''));z=a[mask,6:12];u=z[:,0]+1j*z[:,1];v=z[:,2]+1j*z[:,3];w=z[:,4]+1j*z[:,5];q=(np.sum(phi[:,0]*u)+np.sum(phi[:,1]*v)+np.sum(phi[:,2]*w))/den
 rows.append({'frequency_GHz':freq,'detuning_MHz':(freq-3.305664)*1000,'projection_real':q.real,'projection_imag':q.imag,'projection_abs':abs(q),'phase_deg':np.angle(q,deg=True)})
proj=pd.DataFrame(rows);proj['normalized_projection_abs']=proj.projection_abs/proj.projection_abs.max();proj.to_csv(out/'mode_projected_drive_response.csv',index=False,float_format='%.10g')
# Join the average absolute component data for side-by-side interpretation.
av=pd.read_csv(out/'drive_sweep_3p304664_3p306664GHz.csv')
fig,ax=plt.subplots(1,2,figsize=(10.2,4.0),constrained_layout=True)
ax[0].plot(proj.detuning_MHz,proj.normalized_projection_abs,'o-',lw=2,color='#184e77')
ax[0].axvline(0,color='0.5',ls='--',lw=1);ax[0].set(xlabel='Detuning from 3.305664 GHz (MHz)',ylabel='Normalized modal projection amplitude',ylim=(0,1.08),title='Driven field projected onto target eigenmode');ax[0].grid(alpha=.25)
for key,label,color in [('mean_abs_u_pm','mean |u|','#e76f51'),('mean_abs_v_pm','mean |v|','#2a9d8f'),('mean_abs_w_pm','mean |w|','#e9c46a')]:
 ax[1].plot((av.frequency_GHz-3.305664)*1000,av[key]/av.loc[2,key], 'o-',lw=1.7,label=label,color=color)
ax[1].axvline(0,color='0.5',ls='--',lw=1);ax[1].set(xlabel='Detuning from 3.305664 GHz (MHz)',ylabel='LN-average component amplitude (normalized)',title='Volume-average displacement components');ax[1].grid(alpha=.25);ax[1].legend(frameon=False)
fig.suptitle('6 µm suspended TFLN IDT: coupled 1 V frequency response',fontsize=12)
img=Path(r'C:\Users\Administrator\Documents\Codex\2026-10-20\new-chat\outputs\tfln_ao_preprint\paper\images\coupled_drive_projection.png');fig.savefig(img,dpi=220,bbox_inches='tight');plt.close(fig)
print(proj[['frequency_GHz','detuning_MHz','normalized_projection_abs','phase_deg']].to_string(index=False));print(img)
