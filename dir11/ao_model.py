"""Direction 11: TFLN acousto-optic MZI for single-photon frequency shifting and
microwave-to-optical transduction.  Extends the group's acoustic (phononic) MZI model
(slides tfln_review/user_materials/report.txt "3.声学MZI阵列": DC 50:50 + thermal phase tuning;
parameters/equation from Xu et al. arXiv:2510.26596 = pnic.txt:
  T_MZI = [1+cos(alpha*P_H+phi0)]/2, alpha=4.03 rad/W, DC coupling length 79.14 um,
  acoustic loss 2.4 dB/mm, Y-splitter IL 0.5 dB, f~1.5 GHz).
"""
import numpy as np
hbar=1.054571817e-34; kB=1.380649e-23; h=2*np.pi*hbar

# ---------------- group acoustic MZI model (reconstructed) ----------------
LC_FULL=79.14e-6      # full power-transfer length of phononic DC [pnic]
ALPHA_TA=4.03         # thermo-acoustic phase efficiency rad/W [pnic / review U3]
LOSS_DB_MM=2.4        # acoustic intensity loss dB/mm [pnic]

def dc(L):
    """2x2 field transfer matrix of acoustic directional coupler of length L."""
    th=np.pi/2*L/LC_FULL; c,s=np.cos(th),np.sin(th)
    return np.array([[c,-1j*s],[-1j*s,c]])

def arm(Larm,P_H=0.0,phi0=0.0,loss_db_mm=LOSS_DB_MM):
    a=10**(-loss_db_mm*Larm*1e3/20)
    return a*np.exp(1j*(ALPHA_TA*P_H+phi0))

def acoustic_mzi(P_H,L1=LC_FULL/2,L2=LC_FULL/2,Larm=200e-6,phi0=0.0):
    M=dc(L2)@np.diag([arm(Larm,P_H,phi0),arm(Larm)])@dc(L1)
    return M@np.array([1,0])     # output field amplitudes (port1, port2)

# ---------------- AO phase modulation calibration ----------------
# Ni, Bhave, Xu arXiv:2606.05337: push-pull AO-MZI, VpiL=1.004 V cm, L=400um, 0.842 GHz, BW 132.5 MHz,
# 50 ohm.  Differential phase  dphi = pi*V/Vpi,  P=V^2/(2R).
VPIL_NI=1.004e-2  # V m
def dphi_pp(P,L):  # differential (push-pull) phase amplitude for RF power P [W] delivered, length L
    Vpi=VPIL_NI/L; V=np.sqrt(2*50*P); return np.pi*V/Vpi

# ---------------- nested IQ SSB-SC acousto-optic shifter ----------------
def iq_spectrum(dI,dQ,thI,thQ,phiIQ,ext_db=np.inf,nmax=7,N=1024):
    """Sub-MZIs push-pull at null with differential phase amplitudes dI,dQ and acoustic
    phases thI,thQ; outer MZI phase phiIQ. Finite sub-MZI extinction ext_db.
    Returns dict n->power fraction (relative to input)."""
    t=np.arange(N)/N*2*np.pi
    r=10**(-ext_db/20) if np.isfinite(ext_db) else 0.0
    def sub(d,th):
        x=d/2*np.sin(t+th)
        return 0.5*(np.exp(1j*x)-(1-r)*np.exp(-1j*x))
    E=0.5*(sub(dI,thI)+np.exp(1j*phiIQ)*sub(dQ,thQ))
    c=np.fft.fft(E)/N
    return {n:abs(c[n%N])**2 for n in range(-nmax,nmax+1)}

def hom_vis(p,target=1,filt_db=0.0):
    """HOM visibility of shifted photon vs ideal reference at target sideband, after
    a spectral filter that suppresses all other sidebands by filt_db (post-selected)."""
    f=10**(-filt_db/10); good=p[target]; bad=sum(v for n,v in p.items() if n!=target)*f
    return good/(good+bad), good

# ---------------- phase-matched intermodal (Bragg) shifter ----------------
def intermodal(Gamma0,alpha_np,L,dbeta=0.0,nz=400):
    """Coupled-mode TE0(w)->TE1(w+W): da0=-i k a1 e^{-i db z}, da1=-i k a0 e^{i db z},
    k(z)=k0 exp(-alpha z/2), k0=Gamma0/L. Returns conversion efficiency."""
    z=np.linspace(0,L,nz); dz=z[1]-z[0]; a=np.array([1+0j,0j]); k0=Gamma0/L
    for zi in z[:-1]:
        zm=zi+dz/2; k=k0*np.exp(-alpha_np*zm/2)
        H=np.array([[0,k*np.exp(-1j*dbeta*zm)],[k*np.exp(1j*dbeta*zm),0]])
        w,V=np.linalg.eigh(H); a=V@(np.exp(-1j*w*dz)*(V.conj().T@a))
    return abs(a[1])**2

# ---------------- cavity piezo-opto-mechanical transducer ----------------
def nth(f,T): return 1/np.expm1(h*f/(kB*T))

def transducer(w,G,kappa,kappa_e,gamma,gamma_e):
    """Resolved-sideband red-detuned beam-splitter, frame of resonances. w: detuning array (rad/s).
    Returns eta(w) (mw->opt photon efficiency) and noise transfer |S_bath->opt|^2."""
    w=np.atleast_1d(w)
    A=-1j*w+kappa/2; B=-1j*w+gamma/2; D=A*B+G**2
    S_mw=np.sqrt(kappa_e)*(-1j*G)*np.sqrt(gamma_e)/D
    S_th=np.sqrt(kappa_e)*(-1j*G)*np.sqrt(gamma-gamma_e)/D
    return abs(S_mw)**2,abs(S_th)**2

def ncav(P,kappa,kappa_e,Delta,f_opt=193.4e12):
    return kappa_e*P/(h*f_opt)/(Delta**2+kappa**2/4)
