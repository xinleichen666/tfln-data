"""Iter7: source-referred RF power incl. IDT / electrode matching, design B (3.33 GHz, Shao-2019 Q).
AO: Shao 2019 V_pi=4.6 V is extracted from S21 with P_in=V_p^2/(2*50ohm) of the VNA source (Supp. Eq. S8),
    i.e. it already includes their IDT's measured ~50% electrical-to-acoustic coupling (-3 dB S11 dip).
EO: Hu 2021 electrode C=0.11 pF, L=0.12 nH, R=1.5 ohm; 0.5 GHz/V referred to capacitor voltage V_c."""
import numpy as np, json
J=json.load(open('data/iter6_fair.json'))['B_Qi_Shao2019_80.75MHz'][1]   # gamma/2pi=0.6 GHz row
P_AO=J['AO_P_W']; P_EO_hu=J['EO_P_W']; Vc=np.sqrt(P_EO_hu*100)       # baseline used V_c=V_0, P=V^2/100
f=3.33e9; w=2*np.pi*f; C=0.11e-12; X=1/(w*C); Rel=1.5
cases={}
cases['AO_ShaoIDT_as_measured(~50% coupling)']=P_AO
cases['AO_perfectly_matched_IDT(100%)']=P_AO*0.5
cases['AO_poor_IDT(10% RF->acoustic, Xu 2025 LNOS level)']=P_AO*0.5/0.10
# independent non-resonant cross-check: Xu 2025 G^2=alpha*P_a, alpha=1774 GHz^2/W; coupling needed = dw/2 (single ring) -> AO optimum dw from iter6
dw_GHz=np.sqrt(P_AO*100)*21.2559/1  # dw/2pi in GHz at AO optimum (21.26 GHz/V)
G=dw_GHz/2; Pa=G**2/1774; cases['AO_travelling_wave_Xu_alpha(acoustic)']=Pa; cases['AO_travelling_wave_Xu_alpha(RF, 10%)']=Pa/0.10
cases['EO_Hu_convention_Vc=V0']=P_EO_hu
cases['EO_open_capacitor_Vc=2V0']=(Vc/2)**2/100
for QL in [30,100]:
    Rtot=Rel+X/QL; cases[f'EO_LC_matched_inductorQ{QL}']=Vc**2*Rtot/(2*X**2)
cases['EO_LC_matched_ideal_inductor(R=1.5ohm)']=Vc**2*Rel/(2*X**2)
cases['EO_LC_bandwidth_MHz_Q30']=f/(X/(Rel+X/30))/1e6
out=dict(Vc_needed_V=Vc,X_ohm=X,dw_GHz=dw_GHz,G_GHz=G,P_W=cases)
json.dump(out,open('data/iter7_matching.json','w'),indent=1); print(json.dumps(out,indent=1))
