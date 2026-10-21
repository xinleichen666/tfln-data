from pathlib import Path
import importlib.util,glob,csv
import numpy as np
from scipy.interpolate import LinearNDInterpolator
script=Path(r'D:\tfln\tfln-data-pr17-work\dir11\idt_3d_sus\analysis\aperture_sweep.py')
spec=importlib.util.spec_from_file_location('sweep',script); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
def high_grid(wap):
 stack=(wap+4)*1e-6
 x=np.linspace(0,m.P,195,endpoint=False)+m.P/390
 y=np.linspace(0.5*m.H_LN/38,m.H_LN-0.5*m.H_LN/38,38)
 z=np.linspace(0,stack,int(round(stack/0.05e-6))+1)
 return x,y,z
rows=[]
for wap,mode,freq,base_gi,base_ge in [(6,6,3.304065579,39.54255,66.76953),(10,5,3.302075401,34.05262,59.34961)]:
 m.regular_grid=high_grid
 f=glob.glob(str(Path(r'D:\comsol_ao_run')/f'Wap_{wap}um_mode_{mode:02d}_*.csv'))[0]
 x,y,z,g=m.interpolate_fields(Path(f),wap)
 zp,gv,U=m.coupling_profile(x,y,z,g,'TE',1.0)
 valid=np.isfinite(gv); z1=2+wap
 edge=(zp<=3e-6)|(zp>=(z1-1)*1e-6)
 interior=(zp>=4e-6)&(zp<=(z1-2)*1e-6)
 gi=float(np.max(gv[valid&interior])); ge=float(np.max(gv[valid&edge]))
 rows.append({'aperture_um':wap,'mode':mode,'freq_GHz':freq,'baseline_grid_g_int':base_gi,'refined_grid_g_int':gi,'interior_change_percent':100*(gi/base_gi-1),'baseline_grid_g_edge':base_ge,'refined_grid_g_edge':ge,'edge_change_percent':100*(ge/base_ge-1)})
 print(rows[-1],flush=True)
out=Path(r'C:\Users\Administrator\Documents\Codex\2026-10-20\new-chat\outputs\tfln_ao_preprint\paper\data\mesh_convergence')
with (out/'postprocess_grid_sensitivity.csv').open('w',newline='',encoding='utf-8') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
