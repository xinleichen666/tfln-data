# map error at 40um sampling (white, assumption 0.1/0.3 nm), truth = raw digitized profile
import json,numpy as np, run2 as r
from run3 import ev,Z,T,z,P,L,R
rng=np.random.default_rng(3); o={}
for err in (0.1,0.3):
  v=[]
  for z0 in np.arange(0,16.01,2.0):
    m=(Z>=z0)&(Z<=z0+L); zz=Z[m]-z0-L/2; tt=T[m]-T[m].mean(); raw=np.interp(z,zz,tt)
    zs=np.arange(z[0],z[-1]+0.04,0.04); mp=np.interp(z,zs,np.interp(zs,z,raw)+rng.normal(0,err,len(zs)))
    v.append(ev(r.ph(z,P['St'],raw-mp))[0])
  o[err]=[float(np.mean(v)),float(np.min(v))]; print(err,o[err],flush=True)
json.dump(o,open('data/run3b.json','w'))
