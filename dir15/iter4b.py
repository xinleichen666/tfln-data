import numpy as np, json
from mplc import *
rng=np.random.default_rng(11)
exec(open('iter4.py').read().split("step=2*np.pi")[0].split("rng=np.random")[1].split('\n',1)[1])  # reuse fshift/evalmc
step=2*np.pi*0.53*0.1/1.55; ap=(XX**2+YY**2)<2500; R={}
d=3; basis=[LG(l,0,8.0) for l in (-1,0,1)]; Uf=np.array([[np.exp(2j*np.pi*j*k/d) for k in range(d)] for j in range(d)])/np.sqrt(d)
ins=inputs(d,10.0,2.5); K=4; dz=40.0
for sig in (1.0,2.0,3.0):
    ph=[quant(p,step)*ap for p in design(ins,targets(basis,Uf),K,[dz]*5,iters=120,sig=sig)]
    key=f'd3_K4_inloop_sig{sig}'; R[key]={'nominal':evalmc(ph,ins,basis,Uf,K,dz)}
    for s in (0.1,0.25,0.5): R[key][f'plshift_{s}']=evalmc(ph,ins,basis,Uf,K,dz,plshift=s,n=10)
    R[key]['realistic']=evalmc(ph,ins,basis,Uf,K,dz,plshift=0.2,herr=0.05,n=20,inshift=0.3)
    print(key,{a:(round(b['F'][0],4),round(b['F_trim'][0],4),round(b['IL_dB'][0],2)) for a,b in R[key].items()},flush=True)
    json.dump(R,open('data/iter4b.json','w'),indent=1)
