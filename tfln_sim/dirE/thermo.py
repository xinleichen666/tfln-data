import numpy as np, sys, json
sys.path.insert(0,'/workspace/tfln_sim/iterations')
# Jundt 1997 Opt Lett 22,1553 congruent LN extraordinary, T in C, lam um
a=[5.35583,0.100473,0.20692,100,11.34927,1.5334e-2]; b=[4.629e-7,3.862e-8,-0.89e-8,2.657e-5]
def ne(l,T):
    f=(T-24.5)*(T+570.82)
    return np.sqrt(a[0]+b[0]*f+(a[1]+b[1]*f)/(l**2-(a[2]+b[2]*f)**2)+(a[3]+b[3]*f)/(l**2-a[4]**2)-a[5]*l**2)
T=26.85  # 300 K
d=lambda l:(ne(l,T+0.5)-ne(l,T-0.5))
ng=lambda l: ne(l,T)-l*(ne(l+1e-4,T)-ne(l-1e-4,T))/2e-4
r=dict(dne_dT_1523=d(1.523),dne_dT_1550=d(1.55),dne_dT_775=d(0.775),ng_775=ng(0.775),ng_1550=ng(1.55),ne_1550=ne(1.55,T))
# modal: d(nSH-nFH)/dT ~ G*(dne775-dne1550) with confinement G (sweep 0.7-0.9; assumption), plus thermal expansion of period alpha_Y
alpha=15.4e-6  # LN thermal expansion along a(Y) axis, /K (literature ~14-15e-6; assumption +-20%)
lamSH=0.775; Lam=4.45  # um (our 600/300 w2 calc)
for G in (0.7,0.8,0.9):
    dDn=G*(r['dne_dT_775']-r['dne_dT_1550'])
    dk_dT=2*np.pi/lamSH*dDn + 2*np.pi/Lam*alpha        # 1/um/K
    # PM wavelength shift: dDk/dlamFH for degenerate SHG = -(4pi/lamFH^2)*(ngSH-ngFH) (bulk group indices; waveguide dispersion neglected)
    dk_dlam=-(4*np.pi/1.55**2)*(r['ng_775']-r['ng_1550'])
    r[f'G{G}']=dict(dDn_dT=dDn,dk_dT_per_um=dk_dT,dlamPM_dT_nm=-dk_dT/dk_dlam*1e3)
print(json.dumps(r,indent=1)); json.dump(r,open('thermo.json','w'),indent=1)
