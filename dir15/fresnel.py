# Fresnel + etalon + first-order inter-element ghost model on top of thin-element MPLC (3D scalar).
import numpy as np, json, os, sys
import mplc as Mp
from mplc import *
npl=1.53; base=1.0
def slab(T,lam,n0,ni,Rsurf=None):
    """symmetric slab index ni in n0, thickness map T -> (t,r) per pixel, t referenced to background path n0*T.
       Rsurf: override surface power reflectance (AR coated), else Fresnel."""
    k0=2*np.pi/lam; r12=(n0-ni)/(n0+ni) if Rsurf is None else -np.sqrt(Rsurf)
    dl=k0*ni*T; e=np.exp(2j*dl); den=1-r12**2*e
    t=(1-r12**2)*np.exp(1j*dl)/den*np.exp(-1j*k0*n0*T); r=r12*(1-e)/den
    return t,r
def evaluate(ph,ins,basis,U,dz,lam,n0,dn,Rsurf=None,Rexit=None,ghosts=True,lam0=1.55,perturb=None):
    """ph: design phases (for lam0); heights h=ph/(k0 dn). elements: 0=base block exit face (single interface resin->n0), 1..K plates.
       final: output in n0 (if n0!=1 last face n0->air with Rexit counted as power factor)."""
    K=len(ph); lm=lam/n0  # wavelength in medium for AS
    k0=2*np.pi/lam0; hs=[np.mod(p,2*np.pi)/(k0*dn) for p in ph]
    if perturb: hs,dzs,shift=perturb(hs)
    else: dzs=[dz]*(K+1); shift=None
    ts=[];rs=[]
    for h in hs:
        t,r=slab(base+h,lam,n0,npl,Rsurf); ts.append(t); rs.append(r)
    # base exit face: resin (npl) -> n0 single interface
    if Rsurf is None: rb=(npl-n0)/(npl+n0)
    else: rb=np.sqrt(Rsurf)
    tb=np.sqrt(1-rb**2); rb_back=-rb  # reflection seen from n0 side going back
    # chip/resin interface ~ (1.6-1.53) negligible (5e-4): include as power factor
    outs=[]
    Hs=[H(z,lm) for z in dzs]
    for E in ins:
        E=E*tb*np.sqrt(1-5e-4)
        if shift is not None: E=shift(E)
        # forward fields at each element (before applying element)
        fw=[]; F=prop(E,Hs[0])
        for k in range(K):
            fw.append(F); F=prop(F*ts[k],Hs[k+1])
        main=F
        if ghosts:
            # pair (i,j): element j reflects backward, element i reflects forward. i=-1 is base face.
            for j in range(K):
                B=fw[j]*rs[j]  # backward-going at plate j
                for i in range(j-1,-2,-1):
                    B=prop(B,Hs[i+1])  # back to element i
                    if i>=0:
                        G=B*rs[i]; B=B*ts[i]
                    else: G=B*rb_back
                    # forward again from element i to output
                    for k in range(i+1,K): G=prop(G,Hs[k]) if False else G
                    Gf=G
                    if i>=0: Gf=prop(Gf,Hs[i+1])
                    else: Gf=prop(Gf,Hs[0])
                    for k in range(i+1,K): Gf=prop(Gf*ts[k],Hs[k+1])
                    main=main+Gf
        outs.append(main)
    m=metrics(Tmat(outs,basis),U)
    if n0!=1.0:
        Rx=((n0-1)/(n0+1))**2 if Rexit is None else Rexit
        m['eta']*= (1-Rx); m['IL_dB']=float(-10*np.log10(m['eta']))
    return m
