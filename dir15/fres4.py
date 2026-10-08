import numpy as np, json
from mplc import *
from fresnel import evaluate
R={}
for d,K,W in ((3,5,16.0),(5,7,18.0)):
    ls=list(range(-(d//2),d//2+1)); basis=[LG(l,0,W) for l in ls]
    U=np.array([[np.exp(2j*np.pi*j*k/d) for k in range(d)] for j in range(d)])/np.sqrt(d)
    ph=list(np.load(f'data/mplc_pix4_d{d}_K{K}.npy')); ins=inputs(d,20.0,5.0)
    for name,Rs in (('uncoated',None),('AR0.5pct',0.005),('AR0.1pct',0.001)):
        m=evaluate(ph,ins,basis,U,150.0,1.55,1.0,0.53,Rsurf=Rs,ghosts=True); R[f'd{d}_{name}']=m; print(d,name,{k:round(v,4) for k,v in m.items()},flush=True)
        json.dump(R,open('data/fresnel_pix4.json','w'),indent=1)
