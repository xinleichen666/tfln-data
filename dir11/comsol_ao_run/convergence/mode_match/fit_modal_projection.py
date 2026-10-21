from pathlib import Path
import pandas as pd,numpy as np,matplotlib.pyplot as plt
from scipy.optimize import minimize
root=Path(r'C:\Users\Administrator\Documents\Codex\2026-10-20\new-chat\outputs\tfln_ao_preprint\paper')
p=root/'data'/'coupled_drive'/'mode_projected_drive_response.csv';d=pd.read_csv(p);x=d.detuning_MHz.to_numpy();y=d.projection_real.to_numpy()+1j*d.projection_imag.to_numpy();ys=max(abs(y));yn=y/ys
def profile(par, yy=yn):
 f0,g=par;z=1/(x-f0-1j*g/2);c=np.vdot(z,yy)/np.vdot(z,z);return np.sum(np.abs(yy-c*z)**2)
r=minimize(profile,[0,1.13],method='Nelder-Mead',options={'xatol':1e-12,'fatol':1e-12,'maxiter':10000});f0,g=r.x
z=1/(x-f0-1j*g/2);c=np.vdot(z,yn)/np.vdot(z,z);fit=c*z
rms=np.sqrt(np.mean(abs(yn-fit)**2));f0GHz=3.305664+f0/1000;Q=f0GHz*1000/g
summary=pd.DataFrame([{'model':'single-pole complex Lorentzian, free center and width','n_points':len(x),'center_GHz':f0GHz,'center_offset_kHz':f0*1000,'FWHM_MHz':g,'Q_estimate':Q,'normalized_RMS_residual':rms,'assumed_eta_s':5e-4,'interpretation':'preliminary simulated Q under assumed LN structural loss; not measured'}])
summary.to_csv(root/'data'/'coupled_drive'/'modal_projection_fit_summary.csv',index=False,float_format='%.10g')
# Plot modal projected response with fitted linewidth, plus mean displacement panel.
av=pd.read_csv(root/'data'/'coupled_drive'/'drive_sweep_3p304664_3p306664GHz.csv')
fig,ax=plt.subplots(1,2,figsize=(10.2,4.0),constrained_layout=True)
ax[0].plot(x,d.normalized_projection_abs,'o',color='#184e77',label='COMSOL projection')
xx=np.linspace(-2,6.5,600);zz=c/(xx-f0-1j*g/2);ax[0].plot(xx,abs(zz)/abs(zz).max(),'-',lw=2,color='#e76f51',label=f'Lorentzian fit, FWHM={g:.2f} MHz')
ax[0].axvline(f0,color='0.5',ls='--',lw=1);ax[0].set(xlabel='Detuning from 3.305664 GHz (MHz)',ylabel='Normalized modal projection amplitude',xlim=(-2,6.5),ylim=(0,1.08),title='Driven field projected onto target eigenmode');ax[0].grid(alpha=.25);ax[0].legend(frameon=False)
for key,label,color in [('mean_abs_u_pm','mean |u|','#e76f51'),('mean_abs_v_pm','mean |v|','#2a9d8f'),('mean_abs_w_pm','mean |w|','#e9c46a')]:ax[1].plot((av.frequency_GHz-3.305664)*1000,av[key]/av.loc[2,key],'o-',lw=1.7,label=label,color=color)
ax[1].axvline(0,color='0.5',ls='--',lw=1);ax[1].set(xlabel='Detuning from 3.305664 GHz (MHz)',ylabel='LN-average component amplitude (normalized)',title='Volume-average displacement components');ax[1].grid(alpha=.25);ax[1].legend(frameon=False)
fig.suptitle('6 µm suspended TFLN IDT: coupled 1 V frequency response',fontsize=12)
fig.savefig(root/'images'/'coupled_drive_projection.png',dpi=220,bbox_inches='tight');plt.close(fig)
print(summary.to_string(index=False))
