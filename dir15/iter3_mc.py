import numpy as np, json, os
from mplc import *
rng=np.random.default_rng(1)
d=3; w=np.exp(2j*np.pi/3); U=np.array([[1,1,1],[1,w,w**2],[1,w**2,w]])/np.sqrt(3)
W=8.0; basis=[LG(-1,0,W),LG(0,0,W),LG(1,0,W)]; K=4; dz=40.0
key='w2.5_p10.0_W8.0_K4_dz40.0'; phq=list(np.load(f'data/mplc_{key}.npy'))
ins=inputs(d,10.0,2.5)
def fshift(A,sx,sy):
    return np.fft.ifft2(np.fft.fft2(A)*np.exp(-2j*np.pi*(FX*sx+FY*sy)))
def run2(lam=1.55,herr=0,scale=1.0,inshift=(0,0),plshift=0,dzerr=0,hcorr=0):
    phs=[]
    for k,p in enumerate(phq):
        t=np.exp(1j*p*scale*1.55/lam)
        if herr: 
            n=rng.normal(0,herr,p.shape)
            if hcorr: # correlated noise (blur) length hcorr px
                n=np.real(np.fft.ifft2(np.fft.fft2(n)*np.exp(-(FX**2+FY**2)*(np.pi*hcorr)**2))); n*=herr/n.std()
            t=t*np.exp(1j*2*np.pi*0.53*n/lam)
        if plshift: t=fshift(t,*rng.normal(0,plshift,2))
        phs.append(t)
    dzs=[dz+(rng.normal(0,dzerr) if dzerr else 0) for _ in range(K+1)]
    outs=[]
    for E in ins:
        E=fshift(E,*inshift) if inshift!=(0,0) else E
        E=prop(E,H(dzs[0],lam))
        for k in range(K): E=prop(E*phs[k],H(dzs[k+1],lam))
        outs.append(E)
    return metrics(Tmat(outs,basis),U)
out='data/iter3_mc.json'; R=json.load(open(out)) if os.path.exists(out) else {}
def rec(name,f,n):
    if name in R: return
    ms=[f() for _ in range(n)]; R[name]={k:[float(np.mean([m[k] for m in ms])),float(np.std([m[k] for m in ms]))] for k in ms[0]}
    print(name,{k:round(v[0],4) for k,v in R[name].items()},flush=True); json.dump(R,open(out,'w'),indent=1)
rec('nominal',lambda:run2(),1)
for s in (0.02,0.05,0.1): rec(f'height_rand_{s}um',lambda:run2(herr=s),10)
for s in (0.05,0.1): rec(f'height_corr3px_{s}um',lambda:run2(herr=s,hcorr=3),10)
for s in (0.02,0.05,0.1): rec(f'scale_{s}',lambda:run2(scale=1+s),1)
for s in (0.25,0.5,1.0,2.0): rec(f'inshift_{s}um',lambda:run2(inshift=(s,0)),1)
for s in (0.25,0.5,1.0): rec(f'inshift_y_{s}um',lambda:run2(inshift=(0,s)),1)
for s in (0.1,0.25,0.5): rec(f'planeshift_{s}um',lambda:run2(plshift=s),10)
for s in (1.0,2.0,5.0): rec(f'dz_{s}um',lambda:run2(dzerr=s),10)
for l in (1.50,1.53,1.57,1.60): rec(f'lam_{l}',lambda:run2(lam=l),1)
rec('combined_realistic',lambda:run2(herr=0.05,hcorr=3,scale=1.02,inshift=(rng.normal(0,0.3),rng.normal(0,0.3)),plshift=0.2,dzerr=1.0),20)
rec('combined_freespace_align',lambda:run2(herr=0.05,hcorr=3,scale=1.02,inshift=(rng.normal(0,2.0),rng.normal(0,2.0)),plshift=0.2,dzerr=1.0),20)
