from pathlib import Path
import pandas as pd,numpy as np,glob
base=Path(r'D:\comsol_ao_run\convergence\mode_match')
out=Path(r'C:\Users\Administrator\Documents\Codex\2026-10-20\new-chat\outputs\tfln_ao_preprint\paper\data\coupled_drive')
def mode(p):
 d=pd.read_csv(p,comment='%');a=d.to_numpy(float);x=a[:,:3];m=(x[:,1]>=-1e-12)&(x[:,1]<=500e-9+1e-12);return x[m],a[m,6:9]
xe,phi=mode(base/'fine_mode02_3.305664GHz.csv');norm=np.sum(phi**2);rows=[]
for pat in ['driven_coarse_*.csv','driven_target_*.csv']:
 for p in sorted(base.glob(pat)):
  d=pd.read_csv(p,comment='%');a=d.to_numpy(float);x=a[:,:3];m=(x[:,1]>=-1e-12)&(x[:,1]<=500e-9+1e-12);delta=x[m]-xe;assert np.max(np.abs(delta))==0
  z=a[m,6:12];u=z[:,0]+1j*z[:,1];v=z[:,2]+1j*z[:,3];w=z[:,4]+1j*z[:,5];q=(np.sum(phi[:,0]*u)+np.sum(phi[:,1]*v)+np.sum(phi[:,2]*w))/norm
  name=p.name.split('_')[-1].replace('GHz.csv','');f=float(name)
  rows.append({'frequency_GHz':f,'detuning_MHz':(f-3.305664)*1000,'projection_real':q.real,'projection_imag':q.imag,'projection_abs':abs(q),'phase_deg':np.angle(q,deg=True)})
df=pd.DataFrame(rows).sort_values('frequency_GHz').drop_duplicates('frequency_GHz');df['normalized_projection_abs']=df.projection_abs/df.projection_abs.max();df.to_csv(out/'mode_projected_drive_response.csv',index=False,float_format='%.10g')
print(df[['frequency_GHz','detuning_MHz','normalized_projection_abs','phase_deg']].to_string(index=False))
