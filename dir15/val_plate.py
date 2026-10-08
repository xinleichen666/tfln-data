# single-plate check: thin-element vs FDFD field after 1 plate + 40 um; cases: vacuum plate (sanity), real plate, smoothed heights
import numpy as np, json, sys, scipy.sparse.linalg as sla
from fdfd import build, build_tm, tfsf_solve
lam=1.55; k0=2*np.pi/lam; dxf=0.05; X=96.0; Nf=int(X/dxf); xf=(np.arange(Nf)-Nf/2)*dxf; fx=np.fft.fftfreq(Nf,dxf)
case=sys.argv[1]; pix=float(sys.argv[2]); pol=sys.argv[3] if len(sys.argv)>3 else "TE"; dz=0.025; gap=1.0; base=1.0; npml=30
npl=1.0 if case=='vacuum' else 1.53
def P(E,z):
    m=abs(fx)<1/lam; kz=2*np.pi*np.sqrt(np.where(m,(1/lam)**2-fx**2,0)); return np.fft.ifft(np.fft.fft(E)*np.exp(1j*kz*z)*m)
rng=np.random.default_rng(3)
npx=int(X/pix); phc=rng.uniform(0,2*np.pi,npx)
# smooth-ish random phase like MPLC plate: low-pass then quantize 0.1um height
phc=np.angle(np.fft.ifft(np.fft.fft(np.exp(1j*phc))*np.exp(-(np.fft.fftfreq(npx,pix)*np.pi*4)**2)))%(2*np.pi)
h=np.repeat(np.round(phc/(k0*0.53)/0.1)*0.1,int(pix/dxf)); 
if case=='vacuum': pass
E0=np.exp(-((xf)/6.0)**2)*np.exp(1j*0)  # broad beam
# thin model: phase at plate front plane
th=P(P(E0,gap)*np.exp(1j*k0*(npl-1)*(h+base)),40.0)
hmax=h.max(); Nz=int((gap+base+hmax+gap)/dz)+2*npml; z=(np.arange(Nz)-npml)*dz
eps=np.ones((Nf,Nz))
for i in range(Nf): eps[i,(z>=gap)&(z<gap+base+h[i])]=npl**2
A=(build if pol=="TE" else build_tm)(eps,dxf,dz,lam,npml); lu=sla.splu(A); iz0=npml
m=abs(fx)<1/lam; kz=2*np.pi*np.sqrt(np.where(m,(1/lam)**2-fx**2,0)); F0=np.fft.fft(E0)
Einc=np.array([np.fft.ifft(F0*np.exp(1j*kz*(zz-z[iz0]))*m) for zz in z]).T
E=tfsf_solve(lu,A,Einc,iz0); izo=Nz-npml-5
rg=P(E[:,izo],40.0+gap-(z[izo]-z[iz0]))
ov=abs(np.vdot(th,rg))**2/(np.vdot(th,th).real*np.vdot(rg,rg).real); pr=np.vdot(rg,rg).real/np.vdot(th,th).real
r=dict(case=case,pix=pix,pol=pol,overlap=float(ov),power_ratio=float(pr)); print(r,flush=True)
json.dump(r,open(f'data/val_plate_{case}_pix{pix}_{pol}.json','w'))
