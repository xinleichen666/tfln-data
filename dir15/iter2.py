import numpy as np, json, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
# B3 numbers: total homodyne loss 4 dB incl. 1.4 dB coupler -> other loss 2.6 dB; on-chip squeezing ~10 dB (inferred, other waveguide) and 4.7 dB at 38 mW
def meas(S0,eta): return -10*np.log10(eta*10**(-S0/10)+1-eta)
cpl={'B3 SU-8 bilayer (1.4)':1.4,'C5 TPP out-of-plane (1.3)':1.3,'PWB TFLN Vanguard (1.78)':1.78,'Monolithic 3D taper APL Photon. 2024 (0.29)':0.29,'ideal 0':0.0}
other=2.6; res={}
for S0 in (4.7,10.0):
  for k,c in cpl.items():
    eta=10**(-(c+other)/10); res[f'S0={S0}|{k}']=round(meas(S0,eta),2)
# derivative: dB measured squeezing gained per dB coupler loss reduced
cs=np.linspace(0,3,61)
plt.figure(figsize=(5,3.5))
for S0 in (4.7,10,15):
  plt.plot(cs,[meas(S0,10**(-(c+other)/10)) for c in cs],label=f'on-chip {S0} dB')
plt.plot(cs,[-10*np.log10(1-10**(-(c+other)/10)) for c in cs],'k--',label='bound -10log10(1-eta)')
plt.xlabel('coupling loss (dB/facet)'); plt.ylabel('measured squeezing (dB)'); plt.legend(fontsize=7); plt.tight_layout(); plt.savefig('fig/iter2_squeezing.png',dpi=150)
# heralding: eta_h = coupler * filter(0.9) * detector(0.9) * onchip(0.9) assumed
for k,c in cpl.items(): res[f'herald|{k}']=round(10**(-c/10)*0.9*0.9*0.9,3)
json.dump(res,open('data/iter2.json','w'),indent=1,ensure_ascii=False); print(json.dumps(res,indent=0,ensure_ascii=False))
