"""Bell-state fidelity of dual-type-0 PPLN + PSR-as-combiner source, per channel pair (lam_s, lam_i) symmetric about 1550.
State per pair: a|HH> + b e^{i phi} sqrt(eta_s eta_i)|VV> + small cross-pol terms; pump ratio |a|=|b| balanced at ONE reference pair
(static), or re-balanced per pair (EO MZI). Cross-pol amplitude eps from reciprocal TE crosstalk of the PSR (combiner mode)."""
import json,numpy as np
lam=np.array([1.45,1.5,1.55,1.6,1.65])
def F_state(r,eps=0.0,dphi=0.0):
    # |psi> = (|HH> + r e^{i dphi}|VV> + eps-terms)/N ; overlap with Phi+
    num=abs(1+r*np.exp(1j*dphi))**2/2; N=1+r**2+2*eps*(1+r**2)
    return num/N
def scen_eta(name):
    if name=='C_uniformADC':  # dirC Y-prop 400/280: ADC g0.2 L=114.5 x taper (eme_c4 nominal L300 TE1 power)
        R=json.load(open('../dirC/adc/adc_W2.6_wn1.27_g0.2.json')); Ls=np.array(R[0]['Ls']); i=np.argmin(abs(Ls-114.5))
        adc=np.array([r['res']['TE1w->TE0n'][i] for r in R])
        tap=np.interp(lam,[1.45,1.55,1.65],[0.986,0.944,0.834]); return adc*tap, 10**(-31/10)
    if name=='B_adiabaticADC_Z':  # dirB Z-prop 600/320 adiabatic ADC: IL_TM worst corner 0.19 dB, cross TE xt <= -46 dB
        il=np.interp(lam,[1.45,1.55,1.65],[0.08,0.12,0.19]); return 10**(-il/10), 10**(-46/10)
    if name=='C_taper+adiabaticADC_Y':  # dirC taper (L300) + adiabatic ADC assumed like B (IL 0.1dB flat) -- projected
        tap=np.interp(lam,[1.45,1.55,1.65],[0.986,0.944,0.834]); return tap*10**(-0.1/10), 10**(-40/10)
out={}
pairs=[(1.55-d,1.55+d) for d in np.linspace(0,0.1,11)]  # approx (energy cons. ~ symmetric in lam for small d)
for sc in ['C_uniformADC','B_adiabaticADC_Z','C_taper+adiabaticADC_Y']:
    eta,eps=scen_eta(sc); f=lambda x: np.interp(x,lam,eta)
    r0=f(1.55)  # static balance at degeneracy: pump ratio chosen so r=1 there
    res=[]
    for ls,li in pairs:
        r_static=np.sqrt(f(ls)*f(li))/r0; res.append(dict(ls=ls,li=li,F_static=F_state(r_static,eps),F_rebal=F_state(1.0,eps),
            loss_dB=-10*np.log10(np.sqrt(f(ls)*f(li)))))
    out[sc]=res
    print(sc,'F_static (d=0..100nm):',[round(x['F_static'],4) for x in res],' min',round(min(x['F_static'] for x in res),4),' V-arm loss',[round(x['loss_dB'],2) for x in res][::5])
json.dump(out,open('fid_psr.json','w'),indent=1)
# imbalance -> fidelity map
print('F vs r:',{r:round(F_state(r),4) for r in (1,0.9,0.8,0.7,0.6)})
print('F vs dphi(rad):',{p:round(F_state(1,0,p),4) for p in (0.05,0.1,0.2,0.3,0.5)})
