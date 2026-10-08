# Gate-level validation of thin-element scalar MPLC model with rigorous 2D TE FDFD (per plate) + exact angular spectrum between plates.
import numpy as np, json, sys, time, scipy.sparse.linalg as sla
from fdfd import build, tfsf_solve
from numpy.polynomial.hermite import hermval
from math import factorial
variant=sys.argv[1]; PIX=float(sys.argv[3]); X=float(sys.argv[4]); PITCH=float(sys.argv[5]); WOUT=float(sys.argv[6]); DZ=float(sys.argv[7]); K=int(sys.argv[8]); d=int(sys.argv[9]); WIN=float(sys.argv[10])
lam=1.55; k0=2*np.pi/lam; npl=1.53
n0=1.0 if variant=='air' else 1.37
dn=npl-n0; import os; dxf=float(os.environ.get("DXF","0.05")); Nf=int(X/dxf); xf=(np.arange(Nf)-Nf/2)*dxf

def gauss(x0,w): E=np.exp(-((xf-x0)/w)**2); return E/np.linalg.norm(E)
def HG(m,w):
    c=np.zeros(m+1); c[m]=1; E=hermval(np.sqrt(2)*xf/w,c)*np.exp(-(xf/w)**2); return E/np.linalg.norm(E)
ins=[gauss((j-(d-1)/2)*PITCH,WIN) for j in range(d)]; basis=[HG(m,WOUT) for m in range(d)]
U=np.array([[np.exp(2j*np.pi*j*k/d) for k in range(d)] for j in range(d)])/np.sqrt(d)
fx=np.fft.fftfreq(Nf,dxf)
def P(E,z):
    m=abs(fx)<n0/lam; kz=2*np.pi*np.sqrt(np.where(m,(n0/lam)**2-fx**2,0)); return np.fft.ifft(np.fft.fft(E)*np.exp(1j*kz*z)*m)
# --- design (thin element, 1 um pixels, height quantized 0.1 um) ---
pix=int(PIX/dxf); step=k0*dn*0.1
def expand(pc): return np.repeat(pc,pix)
tg=[sum(U[k,j]*basis[k] for k in range(d)) for j in range(d)]
ph=[np.zeros(Nf//pix) for _ in range(K)]
ap=abs(np.arange(Nf//pix)-Nf//pix/2)*PIX<0.42*X
for it in range(150):
    for k in range(K):
        F=[]
        for E in ins:
            E=P(E,DZ)
            for j in range(k): E=P(E*np.exp(1j*expand(ph[j])),DZ)
            F.append(E)
        B=[]
        for T in tg:
            E=P(T,-DZ)
            for j in range(K-1,k,-1): E=P(E*np.exp(-1j*expand(ph[j])),-DZ)
            B.append(E)
        ov=sum(np.conj(f)*b for f,b in zip(F,B)).reshape(-1,pix).sum(1)
        ph[k]=np.round(np.mod(np.angle(ov),2*np.pi)/step)*step*ap
def metrics(outs):
    T=np.array([[np.vdot(b,o) for o in outs] for b in basis]); Pw=np.trace(T.conj().T@T).real
    return dict(F=float(abs(np.trace(U.conj().T@T))**2/(d*Pw)),F_trim=float(np.sum(abs(np.diag(U.conj().T@T)))**2/(d*Pw)),IL_dB=float(-10*np.log10(Pw/d)))
def thin(): 
    outs=[]
    for E in ins:
        E=P(E,DZ)
        for k in range(K): E=P(E*np.exp(1j*phf[k]),DZ)
        outs.append(E)
    return outs
SM=float(os.environ.get("SMOOTH","0"))
def smooth(p):
    if SM==0: return p
    g=np.exp(-(xf/SM)**2); g/=g.sum(); return np.real(np.fft.ifft(np.fft.fft(p)*np.fft.fft(np.fft.ifftshift(g))))
phf=[smooth(expand(p)) for p in ph]
np.save(f"data/val3_ph_{variant}_d{d}_pix{PIX}_K{K}.npy",np.array(ph)); res={"variant":variant,"thin":metrics(thin())}; print(res,flush=True)
# --- rigorous: each plate = base 1 um + relief h(x) (relief on exit side), background n0 ---
dz=float(sys.argv[2]) if len(sys.argv)>2 else 0.025; base=1.0; gap=1.0; npml=30
outsR=[None]*d; fields=[P(E,DZ-gap) for E in ins]  # field at injection plane (gap before plate)
t0=time.time()
for k in range(K):
    h=np.maximum(phf[k],0)/(k0*dn); hmax=h.max()
    Lz=gap+base+hmax+gap; Nz=int(Lz/dz)+2*npml; z=(np.arange(Nz)-npml)*dz
    eps=np.full((Nf,Nz),n0**2); 
    for i in range(Nf): eps[i,(z>=gap)&(z<gap+base+h[i])]=npl**2
    A=build(eps,dxf,dz,lam,npml); lu=sla.splu(A); iz0=npml+2; izo=int((gap+base+hmax+0.5*gap)/dz)+npml
    for j in range(d):
        E0=fields[j]; kz=2*np.pi*np.sqrt((n0/lam)**2-fx**2+0j); F0=np.fft.fft(E0)
        Einc=np.array([np.fft.ifft(F0*np.exp(1j*kz*(zz-z[iz0]))*(abs(fx)<n0/lam)) for zz in z]).T
        E=tfsf_solve(lu,A,Einc,iz0)
        zout=z[izo]-z[iz0]  # distance travelled from injection plane
        # remove reference: thin model = travel (gap) + plate + rest; rigorous field at zout; continue to next injection plane
        Eo=E[:,izo]*np.exp(-1j*k0*n0*0)  # keep physical phase
        rem=(DZ-gap)-(zout-gap) if k<K-1 else DZ-(zout-gap)
        fields[j]=P(Eo,rem)
    print('plate',k,'done',round(time.time()-t0),'s',flush=True)
res['rigorous']=metrics(fields); res['dz']=dz
# field-level agreement per input
th=thin(); res['field_overlap']=[float(abs(np.vdot(a,b))**2/(np.vdot(a,a).real*np.vdot(b,b).real)) for a,b in zip(th,fields)]
res['power_ratio']=[float(np.vdot(b,b).real/np.vdot(a,a).real) for a,b in zip(th,fields)]
print(res,flush=True); json.dump(res,open(f'data/val3_{variant}_d{d}_pix{PIX}_K{K}_sm{SM}.json','w'),indent=1)
