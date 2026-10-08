"""Iter6: apples-to-apples AO vs EO at identical optics, incl. Shao-2019-measured Q for design B, + RF detuning."""
import numpy as np, json, sys
sys.path.insert(0,'paper')
from iter5_aomolecule import simulate, ring_dw_per_V, tp, cases
import importlib.util
spec=importlib.util.spec_from_file_location('eo','paper/eo_baseline.py')
src=open('paper/eo_baseline.py').read().split('res={}')[0]; ns={}; exec(src,ns); sim_pp=ns['sim_pp']
def opt(fun,wm,ke,ki,T,scale):
    best=None
    for x in np.linspace(0.5,1.6,23):
        d=x*scale; r=fun(wm/2,tp*ke,tp*ki,wm,d,T); s=max(r[1],r[-1]); tot=sum(r.values())
        if best is None or s/tot>best[1]: best=(d,s/tot,s,-10*np.log10(tot))
    return best
out={}
pB=cases['B_suspended_Shao2019']; wm=tp*3.33e9; gAO=ring_dw_per_V(pB['VpiL'],pB['La'],pB['Lring']); gEO=tp*0.5e9
# Shao 2019 Table S2: kappa/2pi=95 MHz, 2kappa_e/kappa=0.3 -> kappa_i=0.85*95 MHz
for tag,ki in [('B_Qi_design_60MHz',0.06e9),('B_Qi_Shao2019_80.75MHz',0.85*0.095e9)]:
    rows=[]
    for ke in [0.4e9,0.6e9,0.8e9,1.0e9]:
        a=opt(simulate,wm,ke,ki,40e-9,tp*(ke+ki)); e=opt(sim_pp,wm,ke,ki,40e-9,tp*ke/2)
        rows.append(dict(ke_GHz=ke/1e9,AO_eta=a[1],AO_abs=a[2],AO_IL=a[3],AO_P_W=(a[0]/gAO)**2/100,EO_eta=e[1],EO_abs=e[2],EO_P_W=(e[0]/gEO)**2/100))
    for r in rows: r['ratio_EO_over_AO']=r['EO_P_W']/r['AO_P_W']
    out[tag]=rows
# RF detuning tolerance, design B at Shao Q, ke=0.6 GHz; acoustic resonator Lorentzian (gamma/2pi=1.28 MHz, Shao 2019) on drive amplitude
ke,ki=0.6e9,0.85*0.095e9; d0=opt(simulate,wm,ke,ki,40e-9,tp*(ke+ki))[0]; det=[]
for df in [0,0.3e6,0.64e6,1e6,2e6,5e6,20e6,100e6]:
    amp=d0/np.sqrt(1+(2*df/1.28e6)**2)
    r=simulate(wm/2,tp*ke,tp*ki,wm+tp*df,amp,40e-9 if df<1e7 else 40e-9); s=max(r[1],r[-1])
    # projection onto q*(wm+df): simulate already uses wm+df
    det.append(dict(df_MHz=df/1e6,eta_shift=s/sum(r.values())))
out['B_RF_detuning_ShaoQ']=det
json.dump(out,open('data/iter6_fair.json','w'),indent=1); print(json.dumps(out,indent=1))
