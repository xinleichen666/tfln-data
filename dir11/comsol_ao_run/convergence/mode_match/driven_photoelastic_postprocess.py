from pathlib import Path
import numpy as np,pandas as pd,glob
from scipy.interpolate import LinearNDInterpolator
from scipy.spatial import Delaunay
from scipy.optimize import brentq
root=Path(r'C:\Users\Administrator\Documents\Codex\2026-10-20\new-chat\outputs\tfln_ao_preprint\paper')
base=Path(r'D:\comsol_ao_run\convergence\mode_match')
P=2.58e-6; H=500e-9; Z0=2e-6; WAP=6e-6; LAM=1.55e-6; NE=2.138; P31=.179; P33=.071
k0=2*np.pi/LAM
fn=lambda k:k*np.tan(k*H/2)-np.sqrt((NE**2-1)*k0**2-k**2)
kte=brentq(fn,1e-3*k0,min(k0*np.sqrt(NE**2-1)*.9999,np.pi/H*.9999))
x=np.linspace(0,P,130,endpoint=False)+P/260
y=np.linspace(.5*H/25,H-.5*H/25,25)
z=np.linspace(0,WAP+4e-6,int(round((WAP+4e-6)/.1e-6))+1)
X,Y,Z=np.meshgrid(x,y,z,indexing='ij'); Q=np.c_[X.ravel(),Y.ravel(),Z.ravel()]
wy=np.cos(kte*(y-H/2))**2; wy/=wy.sum(); wx=np.full((len(x),len(y)),1/len(x))*wy[None,:]; dz=z[1]-z[0]
# LN-node coordinates, complex strain data from COMSOL exports on the driven 100/50 nm mesh.
files=sorted(base.glob('driven_strain_[0-9][0-9]_*GHz.csv'))
first=pd.read_csv(files[0],comment='%',header=None).to_numpy(float); xyz=first[:,:3];mask=(xyz[:,1]>=-1e-12)&(xyz[:,1]<=H+1e-12);pts=xyz[mask];tri=Delaunay(pts)
zcandidates=np.arange(Z0,Z0+WAP+0.01e-6,0.1e-6)
sigma=1e-6/2.355
rows=[];profiles=[]
for f in files:
 d=pd.read_csv(f,comment='%',header=None).to_numpy(float); xyz=d[:,:3];m=(xyz[:,1]>=-1e-12)&(xyz[:,1]<=H+1e-12)
 assert np.max(np.abs(xyz[m]-pts))==0
 eXX=d[m,6]+1j*d[m,7];eYY=d[m,8]+1j*d[m,9];eZZ=d[m,10]+1j*d[m,11]
 pe=-(NE**3/2)*(P33*eZZ+P31*(eXX+eYY))
 vals=LinearNDInterpolator(tri,pe,fill_value=np.nan)(Q).reshape(len(x),len(y),len(z))
 line=np.einsum('xy,xyz->z',wx,vals)
 for zc in zcandidates:
  wz=np.exp(-.5*((z-zc)/sigma)**2)*(z>=Z0)*(z<=Z0+WAP); norm=np.nansum(wz)*dz
  dn=np.nansum(line*wz)*dz/norm
  freq=float(f.stem.split('_')[-1].replace('GHz',''))
  profiles.append({'frequency_GHz':freq,'waveguide_center_um':zc*1e6,'delta_neff_re_per_V':dn.real,'delta_neff_im_per_V':dn.imag,'delta_neff_abs_per_V':abs(dn),'phase_rad_per_mm_per_V':abs(2*np.pi/LAM*dn)*1e-3})
# Write complete frequency-location profile and per-frequency interior peak summaries.
profile=pd.DataFrame(profiles);profile.to_csv(root/'data'/'coupled_drive'/'driven_photoelastic_profile_1V.csv',index=False,float_format='%.10g')
summary=[]
for freq,g in profile.groupby('frequency_GHz'):
 c=g.iloc[np.argmin(abs(g.waveguide_center_um-5.5))]
 interior=g[(g.waveguide_center_um>=4-1e-8)&(g.waveguide_center_um<=6+1e-8)]
 edge=g[(g.waveguide_center_um<=3+1e-8)|(g.waveguide_center_um>=7-1e-8)]
 bi=interior.loc[interior.delta_neff_abs_per_V.idxmax()]
 be=edge.loc[edge.delta_neff_abs_per_V.idxmax()]
 summary.append({'frequency_GHz':freq,'best_interior_z_um':bi.waveguide_center_um,'delta_neff_abs_interior_per_V':bi.delta_neff_abs_per_V,'phase_rad_per_mm_per_V_interior':bi.phase_rad_per_mm_per_V,'max_edge_z_um':be.waveguide_center_um,'delta_neff_abs_edge_per_V':be.delta_neff_abs_per_V,'edge_to_interior_ratio':be.delta_neff_abs_per_V/bi.delta_neff_abs_per_V,'delta_neff_abs_at_5p5um_per_V':c.delta_neff_abs_per_V,'phase_rad_per_mm_per_V_at_5p5um':c.phase_rad_per_mm_per_V})
pd.DataFrame(summary).to_csv(root/'data'/'coupled_drive'/'driven_photoelastic_summary_1V.csv',index=False,float_format='%.10g')

