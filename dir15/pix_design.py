import numpy as np, json
import mplc as Mp
from mplc import *
d=3; U=np.array([[np.exp(2j*np.pi*j*k/d) for k in range(d)] for j in range(d)])/np.sqrt(d)
R={}
for pix,win,pitch,W,dz,K in ((4,5.0,20.0,16.0,150.0,4),(4,5.0,20.0,16.0,150.0,5)):
    basis=[LG(l,0,W) for l in (-1,0,1)]; ins=inputs(d,pitch,win); tg=targets(basis,U); dzs=[dz]*(K+1)
    hf=[H(z,1.55) for z in dzs]; ph=[np.zeros((N,N)) for _ in range(K)]
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
            ov=sum(np.conj(f)*b for f,b in zip(F,B))
            ob=ov.reshape(N//pix,pix,N//pix,pix).sum((1,3))
            ph[k]=np.kron(np.angle(ob),np.ones((pix,pix)))
    m=metrics(Tmat(run(ph,ins,1.55,dzs),basis),U); key=f'pix{pix}_K{K}_dz{dz}_W{W}'; R[key]=m; print(key,m,flush=True)
    json.dump(R,open('data/pix_design.json','w'),indent=1)
