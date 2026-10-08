import numpy as np, json, os, time
from mplc import *
d=3; w=np.exp(2j*np.pi/3); U=np.array([[1,1,1],[1,w,w**2],[1,w**2,w]])/np.sqrt(3)
res={}
step=2*np.pi*0.53*0.1/1.55
for win,pitch,W in ((2.5,10.0,8.0),):
  basis=[LG(-1,0,W),LG(0,0,W),LG(1,0,W)]
  for K in (3,4,5):
    for dz in (25.0,40.0):
      t=time.time(); ins=inputs(d,pitch,win); tg=targets(basis,U); dzs=[dz]*(K+1)
      ph=design(ins,tg,K,dzs,iters=150,aperture=50)
      phq=[quant(p,step)*((XX**2+YY**2)<2500) for p in ph]
      m=metrics(Tmat(run(ph,ins,1.55,dzs),basis),U); mq=metrics(Tmat(run(phq,ins,1.55,dzs),basis),U)
      key=f'w{win}_p{pitch}_W{W}_K{K}_dz{dz}'; res[key]=dict(cont=m,quant=mq); print(key,mq,round(time.time()-t),flush=True)
      np.save(f'data/mplc_{key}.npy',np.array(phq)); json.dump(res,open('data/iter3_design.json','w'),indent=1)
