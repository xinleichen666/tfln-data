import numpy as np, json, sys, os
from mplc import *
d=int(sys.argv[1]); K=int(sys.argv[2]); pix=4; dz=150.0; pitch=20.0; win=5.0; W=16.0 if d==3 else 18.0
ls=list(range(-(d//2),d//2+1)); U=np.array([[np.exp(2j*np.pi*j*k/d) for k in range(d)] for j in range(d)])/np.sqrt(d)
basis=[LG(l,0,W) for l in ls]; ins=inputs(d,pitch,win); tg=targets(basis,U); dzs=[dz]*(K+1)
hf=[H(z,1.55) for z in dzs]; ph=[np.zeros((N,N)) for _ in range(K)]; step=2*np.pi*0.53*0.1/1.55
for it in range(80):
    for k in range(K):
        F=[];B=[]
        for E in ins:
            E=prop(E,hf[0])
            for j in range(k): E=prop(E*np.exp(1j*ph[j]),hf[j+1])
            F.append(E)
        for T in tg:
            E=prop(T,np.conj(hf[K]))
            for j in range(K-1,k,-1): E=prop(E*np.exp(-1j*ph[j]),np.conj(hf[j]))
            B.append(E)
        ob=sum(np.conj(f)*b for f,b in zip(F,B)).reshape(N//pix,pix,N//pix,pix).sum((1,3))
        ph[k]=np.kron(quant(np.angle(ob),step),np.ones((pix,pix)))
m=metrics(Tmat(run(ph,ins,1.55,dzs),basis),U); print(d,K,m,flush=True)
np.save(f'data/mplc_pix4_d{d}_K{K}.npy',np.array(ph)); json.dump(m,open(f'data/mplc_pix4_d{d}_K{K}.json','w'))
