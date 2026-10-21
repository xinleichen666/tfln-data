from pathlib import Path
import csv, glob
import numpy as np
from scipy.interpolate import LinearNDInterpolator
base=Path(r'D:\comsol_ao_run')
fine=Path(r'D:\comsol_ao_run\convergence')
out=Path(r'C:\Users\Administrator\Documents\Codex\2026-10-20\new-chat\outputs\tfln_ao_preprint\paper\data\mesh_convergence')
p=2.58e-6; hln=500e-9; z0=2e-6
p33=.071; p31=.179; ne=2.138

def read_field(folder, wap, mode):
    files=glob.glob(str(folder/f'Wap_{wap}um_mode_{mode:02d}_*.csv'))
    if len(files)!=1: raise RuntimeError((folder,wap,mode,files))
    a=np.loadtxt(files[0],delimiter=',',comments='%',encoding='utf-8')
    xyz=a[:,3:6]; strain=a[:,6:9]
    m=xyz[:,1] <= hln+1e-12
    pts=xyz[m]; e=strain[m]
    pe=-(ne**3/2)*(p33*e[:,2]+p31*(e[:,0]+e[:,1]))
    freq=float(Path(files[0]).stem.split('_')[-1].replace('GHz',''))
    return pts,pe,freq

def summary(folder,wap):
    a=np.loadtxt(folder/f'Wap_{wap}um_modes_summary.csv',delimiter=',',comments='%',encoding='utf-8',ndmin=2)
    return a[:,0]/1e9

def calc_corr(wap,bmode):
    bpts,bpe,bf=read_field(base,wap,bmode)
    # Common grid across the acoustic aperture, away from z ends to avoid interpolation boundary artifacts.
    xs=np.linspace(0,p,18,endpoint=False)+p/36
    ys=np.linspace(10e-9,hln-10e-9,9)
    zs=np.arange(z0+0.1e-6,z0+wap*1e-6-0.1e-6,0.2e-6)
    X,Y,Z=np.meshgrid(xs,ys,zs,indexing='ij'); q=np.column_stack([X.ravel(),Y.ravel(),Z.ravel()])
    b=LinearNDInterpolator(bpts,bpe,fill_value=np.nan)(q)
    vals=[]
    ffs=summary(fine,wap)
    for j in range(1,13):
        fpts,fpe,ff=read_field(fine,wap,j)
        v=LinearNDInterpolator(fpts,fpe,fill_value=np.nan)(q)
        m=np.isfinite(b)&np.isfinite(v)
        corr=abs(float(np.dot(b[m],v[m])))/(float(np.linalg.norm(b[m])*np.linalg.norm(v[m]))+1e-300)
        vals.append({'aperture_um':wap,'base_mode':bmode,'base_freq_GHz':bf,'fine_mode':j,'fine_freq_GHz':ff,'abs_PE_shape_correlation':corr,'frequency_difference_MHz':(ff-bf)*1000})
        print('corr',wap,bmode,'->',j,round(corr,5),round(ff,6),flush=True)
    return vals
allrows=calc_corr(6,6)+calc_corr(10,5)
with (out/'mode_shape_tracking.csv').open('w',newline='',encoding='utf-8') as f:
 w=csv.DictWriter(f,fieldnames=list(allrows[0]));w.writeheader();w.writerows(allrows)
