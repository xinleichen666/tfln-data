import numpy as np, json, os, sys
from mplc import *
from fresnel import evaluate
LAMS=(1.548,1.549,1.55,1.551,1.552) if sys.argv[1]=='3' else (1.55,)
d=int(sys.argv[1]); out=f'data/fresnel_d{d}.json'; R=json.load(open(out)) if os.path.exists(out) else {}
ls=list(range(-(d//2),d//2+1)); W=8.0 if d==3 else 9.0; basis=[LG(l,0,W) for l in ls]
U=np.array([[np.exp(2j*np.pi*j*k/d) for k in range(d)] for j in range(d)])/np.sqrt(d)
ins=inputs(d,10.0,2.5); dz=40.0
phA=list(np.load('data/mplc_w2.5_p10.0_W8.0_K4_dz40.0.npy') if d==3 else np.load('data/mplc_d5_K7_plain.npy'))
K=len(phA)
# embedded design: background n0=1.37, propagate with lam/n0; heights quantized 0.1um -> phase step k0*dn*0.1
n0e=1.37; dne=1.53-n0e
fe=f'data/mplc_embed_d{d}.npy'
if os.path.exists(fe): phE=list(np.load(fe))
else:
    ap=(XX**2+YY**2)<2500; step=2*np.pi*dne*0.1/1.55
    phE=[quant(p,step)*ap for p in design(ins,targets(basis,U),K,[dz]*(K+1),lam=1.55/n0e,iters=120,aperture=50)]
    np.save(fe,np.array(phE))
cases={'thin_noFresnel_air':(phA,1.0,0.53,'none',None,None),
 'air_uncoated':(phA,1.0,0.53,None,None,None),
 'air_AR0.5pct':(phA,1.0,0.53,0.005,None,None),
 'air_AR0.1pct':(phA,1.0,0.53,0.001,None,None),
 'embed1.37_exit_uncoated':(phE,n0e,dne,None,None,None),
 'embed1.37_exit_AR0.5pct':(phE,n0e,dne,None,0.005,None),
 'thin_noFresnel_embed':(phE,n0e,dne,'none',None,None)}
for name,(ph,n0,dn,Rs,Rx,_) in cases.items():
  for lam in LAMS:
    for gh in (False,True):
      key=f'{name}|lam{lam}|ghost{gh}'
      if key in R: continue
      if Rs=='none':
        if gh: continue
        Rsurf=1e-12
      else: Rsurf=Rs
      m=evaluate(ph,ins,basis,U,dz,lam,n0,dn,Rsurf=Rsurf,Rexit=(1e-12 if Rs=='none' else Rx),ghosts=gh)
      R[key]=m; json.dump(R,open(out,'w'),indent=1)
      if lam==1.55: print(key,{k:round(v,4) for k,v in m.items()},flush=True)
