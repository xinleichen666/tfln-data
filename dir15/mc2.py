# Hardened Monte Carlo: n=200 per item, d=3 (K4) and d=5 (K7); mean, std, 95% CI (of mean) and 2.5-97.5 percentile
import numpy as np, json, os, sys
from mplc import *
d=int(sys.argv[1]); NS=int(sys.argv[2]) if len(sys.argv)>2 else 200
VAR=sys.argv[3] if len(sys.argv)>3 else 'air'
n0=1.37 if VAR=='embed' else 1.0; dn=1.53-n0
rng=np.random.default_rng(100+d)
if d==3:
    ph=list(np.load('data/mplc_w2.5_p10.0_W8.0_K4_dz40.0.npy')); W=8.0
else:
    ph=list(np.load('data/mplc_d5_K7_plain.npy')); W=9.0
if VAR=='embed': ph=list(np.load(f'data/mplc_embed_d{d}.npy'))
if VAR=='pix4':
    ph=list(np.load(f'data/mplc_pix4_d{d}_K{3 if False else (5 if d==3 else 7)}.npy')); W=16.0 if d==3 else 18.0
K=len(ph); dz=150.0 if VAR=='pix4' else 40.0; ls=list(range(-(d//2),d//2+1)); basis=[LG(l,0,W) for l in ls]
U=np.array([[np.exp(2j*np.pi*j*k/d) for k in range(d)] for j in range(d)])/np.sqrt(d)
ins=inputs(d,20.0,5.0) if VAR=='pix4' else inputs(d,10.0,2.5)
def fshift(A,sx,sy): return np.fft.ifft2(np.fft.fft2(A)*np.exp(-2j*np.pi*(FX*sx+FY*sy)))
Hc={}
def Hd(z,lam):
    k=(round(z,3),lam)
    if k not in Hc:
        if len(Hc)>64: Hc.clear()
        Hc[k]=H(z,lam/n0)
    return Hc[k]
def sample(lam=1.55,herr=0,hcorr=0,scale=0,inshift=0,plshift=0,dzerr=0):
    ts=[]
    s=1+(rng.normal(0,scale) if scale else 0)
    for p in ph:
        t=np.exp(1j*p*s*1.55/lam)
        if herr:
            n=rng.normal(0,1,p.shape)
            if hcorr: n=np.real(np.fft.ifft2(np.fft.fft2(n)*np.exp(-(FX**2+FY**2)*(np.pi*hcorr)**2)))
            n*=herr/n.std(); t=t*np.exp(1j*2*np.pi*dn*n/lam)
        if plshift: t=fshift(t,*rng.normal(0,plshift,2))
        ts.append(t)
    dzs=[dz+(rng.normal(0,dzerr) if dzerr else 0) for _ in range(K+1)]
    sh=rng.normal(0,inshift,2) if inshift else None
    outs=[]
    for E in ins:
        if sh is not None: E=fshift(E,*sh)
        E=prop(E,Hd(dzs[0],lam))
        for k,t in enumerate(ts): E=prop(E*t,Hd(dzs[k+1],lam))
        outs.append(E)
    return metrics(Tmat(outs,basis),U)
items={'nominal':{},'height_rand_50nm':dict(herr=0.05),'height_corr3um_50nm':dict(herr=0.05,hcorr=3),'height_corr3um_100nm':dict(herr=0.1,hcorr=3),
 'shrink_sigma2pct':dict(scale=0.02),'shrink_sigma5pct':dict(scale=0.05),'inshift_sigma0.3um':dict(inshift=0.3),'inshift_sigma1um':dict(inshift=1.0),
 'planeshift_sigma0.1um':dict(plshift=0.1),'planeshift_sigma0.2um':dict(plshift=0.2),'planeshift_sigma0.25um':dict(plshift=0.25),
 'dz_sigma1um':dict(dzerr=1.0),'dz_sigma2um':dict(dzerr=2.0),
 'lam_1.53':dict(lam=1.53),'lam_1.57':dict(lam=1.57),
 'combined_chip':dict(herr=0.05,hcorr=3,scale=0.02,inshift=0.3,plshift=0.2,dzerr=1.0),
 'combined_freespace':dict(herr=0.05,hcorr=3,scale=0.02,inshift=2.0,plshift=0.2,dzerr=1.0)}
out=f'data/mc2_d{d}.json' if VAR=='air' else f'data/mc2_d{d}_{VAR}.json'; R=json.load(open(out)) if os.path.exists(out) else {}
for name,kw in items.items():
    if name in R: continue
    n=1 if name in ('nominal','lam_1.53','lam_1.57') else NS
    ms=[sample(**kw) for _ in range(n)]; r={}
    for k in ms[0]:
        a=np.array([m[k] for m in ms]); r[k]=dict(mean=float(a.mean()),std=float(a.std(ddof=1)) if n>1 else 0.0,
          ci95=float(1.96*a.std(ddof=1)/np.sqrt(n)) if n>1 else 0.0,p2_5=float(np.percentile(a,2.5)),p97_5=float(np.percentile(a,97.5)),n=n)
    R[name]=r; json.dump(R,open(out,'w'),indent=1)
    print(name,'F',round(r['F']['mean'],4),'+-',round(r['F']['std'],4),'Ftrim',round(r['F_trim']['mean'],4),'IL',round(r['IL_dB']['mean'],2),flush=True)
