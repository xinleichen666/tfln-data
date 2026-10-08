import numpy as np, json, os
import mplc as P
from mplc import *
rng=np.random.default_rng(7); R={}
out='data/iter4.json'
def fshift(A,sx,sy): return np.fft.ifft2(np.fft.fft2(A)*np.exp(-2j*np.pi*(FX*sx+FY*sy)))
def evalmc(phq,ins,basis,U,K,dz,plshift=0,herr=0,dzerr=0,n=1,inshift=0):
    ms=[]
    for _ in range(n):
        ts=[]
        for p in phq:
            t=np.exp(1j*p)
            if herr:
                nn=np.real(np.fft.ifft2(np.fft.fft2(rng.normal(0,1,p.shape))*np.exp(-(FX**2+FY**2)*(np.pi*3)**2))); nn*=herr/nn.std(); t=t*np.exp(1j*2*np.pi*0.53*nn/1.55)
            if plshift: t=fshift(t,*rng.normal(0,plshift,2))
            ts.append(t)
        dzs=[dz+(rng.normal(0,dzerr) if dzerr else 0) for _ in range(K+1)]; outs=[]
        s=rng.normal(0,inshift,2) if inshift else (0,0)
        for E in ins:
            E=fshift(E,*s); E=prop(E,H(dzs[0],1.55))
            for t in ts: E=prop(E*t,H(dzs[ts.index(t)+1] if False else dz,1.55))
            outs.append(E)
        ms.append(metrics(Tmat(outs,basis),U))
    return {k:[float(np.mean([m[k] for m in ms])),float(np.std([m[k] for m in ms]))] for k in ms[0]}
def smooth_design(ins,tg,K,dzs,sig,iters=120):
    # WFM with low-pass on transmission each sweep (smoothness -> shift tolerance)
    phis=design(ins,tg,K,dzs,iters=iters//2)
    for _ in range(3):
        phis=[np.angle(np.fft.ifft2(np.fft.fft2(np.exp(1j*p))*np.exp(-(FX**2+FY**2)*(np.pi*sig)**2))) for p in phis]
    return phis
step=2*np.pi*0.53*0.1/1.55; ap=(XX**2+YY**2)<2500
for d in (3,5):
    ls=list(range(-(d//2),d//2+1)); W=8.0 if d==3 else 9.0
    basis=[LG(l,0,W) for l in ls]; Uf=np.array([[np.exp(2j*np.pi*j*k/d) for k in range(d)] for j in range(d)])/np.sqrt(d)
    pitch=10.0; ins=inputs(d,pitch,2.5)
    for K in ((4,) if d==3 else (5,7)):
        dz=40.0; dzs=[dz]*(K+1)
        for name,f in (('plain',lambda: design(ins,targets(basis,Uf),K,dzs,iters=120)),('smooth2px',lambda: smooth_design(ins,targets(basis,Uf),K,dzs,2.0))):
            if d==3 and name=='plain': continue
            ph=[quant(p,step)*ap for p in f()]
            key=f'd{d}_K{K}_{name}'; R[key]={'nominal':evalmc(ph,ins,basis,Uf,K,dz)}
            for s in (0.1,0.25): R[key][f'plshift_{s}']=evalmc(ph,ins,basis,Uf,K,dz,plshift=s,n=10)
            R[key]['realistic']=evalmc(ph,ins,basis,Uf,K,dz,plshift=0.2,herr=0.05,n=20,inshift=0.3)
            print(key,{a:(round(b['F'][0],4),round(b['F_trim'][0],4),round(b['IL_dB'][0],2)) for a,b in R[key].items()},flush=True)
            json.dump(R,open(out,'w'),indent=1); np.save(f'data/mplc_{key}.npy',np.array(ph))
