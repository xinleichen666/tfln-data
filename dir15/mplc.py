# Thin-element MPLC (phase planes in air) via angular spectrum + wavefront matching (Fontaine-style)
import numpy as np, json, os, sys
from math import factorial
N=160; dx=1.0; L=N*dx
x=(np.arange(N)-N/2)*dx; XX,YY=np.meshgrid(x,x,indexing='ij')
fx=np.fft.fftfreq(N,dx); FX,FY=np.meshgrid(fx,fx,indexing='ij')
def H(dz,lam,n=1.0):
    kz=2*np.pi*np.sqrt(np.maximum((n/lam)**2-FX**2-FY**2,0)+0j)
    return np.exp(1j*kz*dz)*(((n/lam)**2-FX**2-FY**2)>0)
def prop(E,h): return np.fft.ifft2(np.fft.fft2(E)*h)
def gauss(w,x0=0,y0=0): E=np.exp(-((XX-x0)**2+(YY-y0)**2)/w**2); return E/np.sqrt((abs(E)**2).sum())
def LG(l,p,w):
    from scipy.special import genlaguerre
    r2=(XX**2+YY**2)/w**2; E=(np.sqrt(2*r2))**abs(l)*genlaguerre(p,abs(l))(2*r2)*np.exp(-r2)*np.exp(1j*l*np.arctan2(YY,XX))
    return E/np.sqrt((abs(E)**2).sum())
def inputs(d,pitch,w_in):
    xs=(np.arange(d)-(d-1)/2)*pitch; return [gauss(w_in,xi,0) for xi in xs]
def targets(basis,U):  # output for input j = sum_k U[k,j] basis_k
    return [sum(U[k,j]*basis[k] for k in range(len(basis))) for j in range(U.shape[1])]
def run(phis,ins,lam,dzs,herr=None,shift=(0,0),scale=1.0,dlam=None):
    """forward through planes; phis designed phases at lam0; errors: per-plane height noise (phase rad), global scale, lateral shift of inputs"""
    out=[]
    for E in ins:
        if shift!=(0,0): E=np.roll(np.roll(E,int(round(shift[0]/dx)),0),int(round(shift[1]/dx)),1)
        E=prop(E,H(dzs[0],lam))
        for k,ph in enumerate(phis):
            p=ph*scale*(1.55/lam)  # phase from height: dispersion of polymer neglected
            if herr is not None: p=p+herr[k]
            E=E*np.exp(1j*p)
            E=prop(E,H(dzs[k+1],lam))
        out.append(E)
    return out
def Tmat(outs,basis): return np.array([[np.sum(np.conj(b)*o) for o in outs] for b in basis])
def metrics(T,U):
    d=U.shape[0]; P=np.trace(T.conj().T@T).real
    F=abs(np.trace(U.conj().T@T))**2/(d*P); eta=P/d
    Ft=np.sum(abs(np.diag(U.conj().T@T)))**2/(d*P)
    s=np.linalg.svd(T,compute_uv=False)**2; mdl=10*np.log10(s.max()/s.min())
    return dict(F=float(F),F_trim=float(Ft),eta=float(eta),IL_dB=float(-10*np.log10(eta)),MDL_dB=float(mdl))
def quant(ph,step):  # height quantization step -> phase step
    ph=np.mod(ph,2*np.pi); return np.round(ph/step)*step
def design(ins,tgs,K,dzs,lam=1.55,iters=200,step=None,aperture=40.0,phasefree=False,sig=0):
    phis=[np.zeros((N,N)) for _ in range(K)]; hf=[H(dz,lam) for dz in dzs]; hb=[np.conj(h) for h in hf]
    ap=(XX**2+YY**2)<aperture**2
    for it in range(iters):
        for k in range(K):
            # forward fields to just before plane k
            F=[]
            for E in ins:
                E=prop(E,hf[0])
                for j in range(k): E=prop(E*np.exp(1j*phis[j]),hf[j+1])
                F.append(E)
            B=[]
            for T in tgs:
                E=prop(T,hb[K])
                for j in range(K-1,k,-1): E=prop(E*np.exp(-1j*phis[j]),hb[j])
                B.append(E)
            ov=sum(np.conj(f)*b*(np.exp(-1j*np.angle(np.sum(np.conj(f*np.exp(1j*phis[k]))*b))) if phasefree else 1) for f,b in zip(F,B))
            if sig: ov=np.fft.ifft2(np.fft.fft2(ov)*np.exp(-(FX**2+FY**2)*(np.pi*sig)**2))
            phis[k]=np.angle(ov)*ap
            if step: phis[k]=quant(phis[k],step)*ap
    return phis
