import numpy as np, json, sys
rng=np.random.default_rng(1)
c=2.998e8; lam0=1.55e-6; w0=2*np.pi*c/lam0
def P(**k):
    p=dict(L=1.2e-3, beta2=5e-27,      # s^2/m (5 fs^2/mm) calibrated from Shi NC 78nm @1.2mm
        SH=0.003, kSH=2*np.pi/0.775e-6, # dDn/dH per nm (assump.) ; k-factor
        sig_wedge=0.3, sig_rough=0.3,   # nm thickness wedge over L / random per segment (assump.)
        sig_D=0.10, sig_Lam=0.01e-6, Lam=4.45e-6, dk_dT=66.0,  # dk_dT 1/m/K from thermo.py (G=0.8)
        dn775=4.46e-5, dn1550=3.34e-5, Lpump=3e-3, Lpair=2e-3,    # duty-cycle sigma per period-block, period error (assump.)
        dT=0.05, dndT=3.3e-5, Larm=5e-3, dlamPM_dT=0.1e-9,  # K, /K (LN ne), arm length, PM shift m/K (assump.)
        psr_il=0.5, psr_il_sig=0.1,     # dB worst-corner conservative (dirB sim worst 0.19 dB)
        ratio_cal=0.02, loss_dBcm=0.3,
        eta_pair=1.24e-4, R_chip=2.1e7, Pmw=0.5, dark=100., tau=1e-9)  # Shi NC measured pair eff./on-chip rate per 0.3nm
    p.update(k); return p
Om=np.linspace(-2*np.pi*c*45e-9/lam0**2, 2*np.pi*c*45e-9/lam0**2, 1801)
def arm_jsa(p, dk_off):
    N=60; z=np.linspace(0,p['L'],N+1); dz=np.diff(z)
    dH=p['sig_wedge']*rng.normal()*(z[:-1]/p['L']-0.5)+p['sig_rough']*rng.normal(size=N)
    dk=-(p['beta2'])*Om[None,:]**2 + (p['kSH']*p['SH']*dH)[:,None] + dk_off
    D=np.clip(0.5+p['sig_D']*rng.normal(size=N),0.05,0.95); d=np.sin(np.pi*D)
    ndom=dz/p['Lam']; jit=np.cumsum(2*np.pi*p['sig_Lam']/p['Lam']*np.sqrt(ndom)*rng.normal(size=N))
    ph=np.cumsum(dk*dz[:,None],axis=0)-dk*dz[:,None]+jit[:,None]
    seg=d[:,None]*np.exp(1j*ph)*np.where(abs(dk)>1e-9,(np.exp(1j*dk*dz[:,None])-1)/(1j*dk+1e-30),dz[:,None])
    return seg.sum(0)/p['L']
def run(p, n=200):
    out=[]
    chan=[]  # 100GHz grid pairs: detuning k*100GHz, k=1..40
    dOm=2*np.pi*100e9
    for t in range(n):
        dT=p['dT']*rng.normal()
        dk_drift=2*np.pi*(p['dlamPM_dT']*dT)/lam0**2 * 2.0*1.0/ (1/ (2*np.pi)) *0  # PM drift folded below
        A1=arm_jsa(p,0.0)
        # drift: shift of PM wavelength ~ dlam => dk ~ 2*|beta2|*Om_pm*dOm ; approximate as constant dk offset
        dk_T=p['dk_dT']*dT
        A2=arm_jsa(p,dk_T)
        phi=0.8*(2*np.pi/0.775e-6*p['dn775']*p['Lpump']+2*2*np.pi/1.55e-6*p['dn1550']*p['Lpair'])*dT
        il=10**(-(p['psr_il']+p['psr_il_sig']*rng.normal())/10)  # per photon, V arm
        A2=A2*il*np.exp(1j*phi)
        # static calibration at t=0 on the integrated rate in central channels: balance ratio & phase (with error)
        sel=abs(Om)<dOm*20
        r_cal=np.sqrt(np.sum(abs(A1[sel])**2)/np.sum(abs(A2[sel])**2))*(1+p['ratio_cal']*rng.normal())
        A2c=A2*r_cal
        g=np.sum(np.conj(A1[sel])*A2c[sel]); A2c=A2c*np.exp(-1j*np.angle(g))*np.exp(1j*phi*0)  # phase locked at calibration; drift phi remains
        A2c=A2c*np.exp(1j*phi)
        Fs=[]; Fp=[]; CARs=[]; rates=[]
        for k in range(1,41):
            m=(abs(Om-k*dOm)<dOm*0.3/0.8/2)  # ~0.3nm passband? 100GHz=0.8nm -> 0.3nm band
            if m.sum()==0: continue
            a=A1[m]; b=A2c[m]
            Ia=np.mean(abs(a)**2); Ib=np.mean(abs(b)**2)
            Fpure=(Ia+Ib+2*np.real(np.mean(np.conj(a)*b)))/(2*(Ia+Ib))
            # rates: normalise so ideal arm (|A|=1) gives Shi on-chip rate per 0.3nm channel, total pump split in 2 arms
            Rc_chip=p['R_chip']*p['Pmw']*(Ia+Ib)/2 * 10**(-p['loss_dBcm']*p['L']*100/10)
            Rc=Rc_chip*p['eta_pair']; S=Rc_chip*np.sqrt(p['eta_pair'])+p['dark']
            acc=S*S*p['tau']; CAR=Rc/acc
            Fm=(Fpure*Rc+0.25*acc)/(Rc+acc)
            Fs.append(Fm); Fp.append(Fpure); CARs.append(CAR); rates.append(Rc_chip)
        out.append(dict(Fmed=float(np.median(Fs)),Fmin=float(np.min(Fs)),Fmean=float(np.mean(Fs)),Fpure_min=float(np.min(Fp)),Fpure_mean=float(np.mean(Fp)),CAR=float(np.median(CARs)),Rchip=float(np.median(rates))))
    return out
def summ(o):
    a=lambda k: np.array([x[k] for x in o])
    q=lambda v: [round(float(np.percentile(v,s)),4) for s in (10,50,90)]
    return dict(Fmean_chan=q(a('Fmean')),Fpure_mean=q(a('Fpure_mean')),Fpure_worstchan=q(a('Fpure_min')),Fworst_chan=q(a('Fmin')),CAR=q(a('CAR')),Rchip_per_chan=q(a('Rchip')))
if __name__=='__main__':
    res={}
    base=P()
    res['ideal_upper']=summ(run(P(sig_wedge=0,sig_rough=0,sig_D=0,dT=0,psr_il=0.19,psr_il_sig=0,ratio_cal=0,loss_dBcm=0.2),20))
    res['conservative']=summ(run(base,300))
    sweeps=dict(sig_Lam=[0.002e-6,0.03e-6,0.1e-6],dk_dT=[50.,90.],Pmw=[0.05,0.1,0.2],sig_wedge=[0.1,1.0,2.0],sig_rough=[0.1,1.0],sig_D=[0.05,0.2],dT=[0.01,0.2,0.5],psr_il=[0.19,1.0,2.0],
                loss_dBcm=[0.2,1.0],SH=[0.0015,0.0055],beta2=[2e-27,20e-27],ratio_cal=[0.05,0.1],dark=[1000.])
    for k,vs in sweeps.items():
        for v in vs: res[f'{k}={v}']=summ(run(P(**{k:v}),120))
    for k,v in res.items(): print(k,v,flush=True)
    json.dump(res,open('mc_results.json','w'),indent=1)
