import numpy as np,json
from iter5_aomolecule import simulate,ring_dw_per_V,tp,cases
out={}
for name,p in cases.items():
    wm=tp*p['f']; k=ring_dw_per_V(p['VpiL'],p['La'],p['Lring']); best=None
    for kr in [0.08,0.12,0.18,0.25]:
        ke=kr*wm; ki=p['ki']*(0.03/0.03)
        for x in np.linspace(0.6,1.6,11):
            dw=x*2*np.sqrt(((ke+ki)/2)**2+0)  # around eta-optimum
            r=simulate(wm/2,ke,ki,wm,dw,T=40e-9 if p['f']>1e9 else 80e-9); tot=sum(r.values()); sh=max(r[1],r[-1])
            e=sh/tot
            if best is None or e>best['eta_shift']: best=dict(ke_GHz=ke/tp/1e9,dw_GHz=dw/tp/1e9,eta_shift=e,eta_abs=sh,carrier_dB=10*np.log10(r[0]/sh),V=dw/k,P_W=(dw/k)**2/100)
    out[name]=best
print(json.dumps(out,indent=1)); json.dump(out,open('data/iter5b_key.json','w'),indent=1)
