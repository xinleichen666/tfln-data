from pathlib import Path
import csv
base=Path(r'C:\Users\Administrator\Documents\Codex\2026-10-20\new-chat\outputs\tfln_ao_preprint\paper\data\mesh_convergence')
rows=[
{'aperture_um':6,'base_best_mode':6,'base_best_freq_GHz':3.304065579,'base_best_g_int_Jmhalf':39.54255,'base_edge_Jmhalf':66.76953,'fine_best_mode':6,'fine_best_freq_GHz':3.311762107,'fine_best_g_int_Jmhalf':42.69595,'fine_edge_Jmhalf':62.18085,'matched_fine_mode':2,'matched_fine_freq_GHz':3.291194264,'abs_PE_shape_correlation':0.915372082897313,'matched_fine_g_int_Jmhalf':35.41651,'matched_fine_edge_Jmhalf':63.01581,'matched_fine_edge_to_int':1.77928},
{'aperture_um':10,'base_best_mode':5,'base_best_freq_GHz':3.302075401,'base_best_g_int_Jmhalf':34.05262,'base_edge_Jmhalf':59.34961,'fine_best_mode':11,'fine_best_freq_GHz':3.364041514,'fine_best_g_int_Jmhalf':111.8192,'fine_edge_Jmhalf':55.18075,'matched_fine_mode':6,'matched_fine_freq_GHz':3.291775731,'abs_PE_shape_correlation':0.419696835375,'matched_fine_g_int_Jmhalf':38.18433,'matched_fine_edge_Jmhalf':46.13422,'matched_fine_edge_to_int':1.20820},
]
with (base/'mesh_comparison.csv').open('w',newline='',encoding='utf-8') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
# Spot-size sensitivity on the original full aperture sweep, TE only, within 3.28-3.38 GHz.
source=Path(r'D:\tfln\tfln-data-pr17-work\dir11\idt_3d_sus\analysis\aperture_sweep_overlap.csv')
with source.open(encoding='utf-8') as f: allrows=list(csv.DictReader(f))
out=[]
for width in ['0.5','1.0','1.5']:
 c=[r for r in allrows if r['pol']=='TE' and r['waveguide_FWHM_um']==width and 3.28<=float(r['freq_GHz'])<=3.38 and r['g_interior_2um']]
 best=max(c,key=lambda r:float(r['g_interior_2um']))
 out.append({'pol':'TE','waveguide_FWHM_um':width,'best_aperture_um':best['aperture_um'],'mode':best['mode'],'freq_GHz':best['freq_GHz'],'g_interior_Jmhalf':best['g_interior_2um'],'g_edge_same_mode_Jmhalf':best['g_edge_1um'],'edge_to_interior':best['edge_to_interior']})
with (base/'baseline_spot_width_sensitivity.csv').open('w',newline='',encoding='utf-8') as f:
 w=csv.DictWriter(f,fieldnames=list(out[0]));w.writeheader();w.writerows(out)
