"""Paper B tolerance scan: ring-ring mismatch delta_r, coupling deviation 2mu-Omega, common-mode laser detuning Delta.
Vectorized copy of core.run (core.py untouched). AO mode, operating drive dw from make_all optimum."""
import numpy as np, json, csv, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from core import tp, F, WM, MU, G, KI, NG
plt.rcParams.update({'font.size':8,'font.family':'serif','mathtext.fontset':'dejavuserif','axes.linewidth':0.6,'lines.linewidth':1.1})
DW=json.load(open('data/results_B.json'))['optimum']['ao']['dw_GHz']*tp*1e9
def runv(mu,Delta,dr,g=G,ki=KI,wm=WM,dw=DW,T=40e-9):
    """mu,Delta,dr: arrays (rad/s). ring2 resonance offset +dr relative to ring1. Laser referenced to S mode of *design* MU... 
    we keep core convention d0=mu-Delta (laser tracks the actual lower supermode of the symmetric molecule)."""
    mu,Delta,dr=np.broadcast_arrays(*(np.atleast_1d(np.asarray(x,float)) for x in (mu,Delta,dr)))
    W=wm; dt=1/(W/tp)/80; n=int(T/dt); d0=mu-Delta; sg=np.sqrt(g)
    a1=np.zeros(mu.shape,complex); a2=a1.copy()
    tt=np.arange(n)*dt; msk=tt>T-20e-9; Q=range(-3,4); acc={q:0 for q in Q}; ph={q:np.exp(1j*q*W*tt) for q in Q}
    def f(t,a1,a2):
        m=dw*np.cos(W*t)
        return ((-1j*(d0+m)-(g+ki)/2)*a1-1j*mu*a2-sg, (-1j*(d0+dr)-ki/2)*a2-1j*mu*a1)
    t=0.0
    for i in range(n):
        k1=f(t,a1,a2);k2=f(t+dt/2,a1+dt/2*k1[0],a2+dt/2*k1[1]);k3=f(t+dt/2,a1+dt/2*k2[0],a2+dt/2*k2[1]);k4=f(t+dt,a1+dt*k3[0],a2+dt*k3[1])
        a1=a1+dt/6*(k1[0]+2*k2[0]+2*k3[0]+k4[0]); a2=a2+dt/6*(k1[1]+2*k2[1]+2*k3[1]+k4[1]); t+=dt
        if msk[i]:
            o=1+sg*a1
            for q in Q: acc[q]=acc[q]+o*ph[q][i]
    N=msk.sum(); p={q:abs(acc[q]/N)**2 for q in Q}; tot=sum(p.values()); ps=np.maximum(p[1],p[-1])
    return ps/tot, -10*np.log10(tot), ps
MHz=tp*1e6
x=np.linspace(-300,300,61)
e0,il0,_=runv(MU,0,0); print('zero point eta=%.4f IL=%.3f dB'%(e0[0],il0[0]))
res={}
res['dr']=runv(MU,0,x*MHz); res['Delta']=runv(MU,x*MHz,0); res['eps']=runv(MU+x*MHz/2,0,0)   # eps = 2mu-Omega
# 2D map
xd=np.linspace(-300,300,41); yd=np.linspace(-300,300,41); XX,YY=np.meshgrid(xd,yd)
E2,IL2,_=runv(MU,YY.ravel()*MHz,XX.ravel()*MHz); E2=E2.reshape(XX.shape); IL2=IL2.reshape(XX.shape)
def hw(e,thr):
    ok=e>=thr; i0=len(x)//2
    if not ok[i0]: return (0,0)
    l=i0
    while l>0 and ok[l-1]: l-=1
    r=i0
    while r<len(x)-1 and ok[r+1]: r+=1
    fi=lambda j,k: x[j]+(thr-e[j])*(x[k]-x[j])/(e[k]-e[j])
    lo=fi(l,l-1) if l>0 else x[0]; hi=fi(r,r+1) if r<len(x)-1 else x[-1]
    return (lo,hi)
# thermal conversion
f0=193.4e12; dndT=3.3e-5; dfdT=f0/NG*dndT/1e6  # MHz/K (magnitude; shift is red, negative)
out={'zero':[e0[0],il0[0]],'dfdT_MHz_per_K':dfdT}
for k in res:
    out[k]={}
    for thr in (0.95,0.90):
        lo,hi=hw(res[k][0],thr); out[k][thr]=(lo,hi)
    out[k]['IL_at_edges95']=[float(np.interp(v,x,res[k][1])) for v in out[k][0.95]]
for k,lab in [('Delta','common-mode Delta'),('dr','ring mismatch delta_r'),('eps','2mu-Omega')]:
    for thr in (0.95,0.90):
        lo,hi=out[k][thr]; hwv=min(-lo,hi)
        s='%s eta>=%.2f: [%.1f, %.1f] MHz, half-width %.1f MHz'%(lab,thr,lo,hi,hwv)
        if k!='eps': s+=' -> dT = +/-%.1f mK'%(hwv/dfdT*1e3)
        print(s)
    print('   IL at eta=0.95 edges:',out[k]['IL_at_edges95'],' IL min/max in scan: %.2f/%.2f'%(res[k][1].min(),res[k][1].max()))
json.dump({k:(v if not isinstance(v,dict) else {str(a):b for a,b in v.items()}) for k,v in out.items()},open('data/tol_scan_summary.json','w'),indent=1)
with open('data/tol_scan.csv','w',newline='') as fh:
    w=csv.writer(fh); w.writerow(['scan','offset_MHz','Delta_MHz','delta_r_MHz','eps_2mu_minus_Omega_MHz','eta_shift','IL_dB'])
    for k in ('Delta','dr','eps'):
        for xi,e,il in zip(x,res[k][0],res[k][1]):
            w.writerow([k,xi,xi if k=='Delta' else 0,xi if k=='dr' else 0,xi if k=='eps' else 0,e,il])
    for d,r_,e,il in zip(YY.ravel(),XX.ravel(),E2.ravel(),IL2.ravel()): w.writerow(['2D',np.nan,d,r_,0,e,il])
fig,ax=plt.subplots(1,3,figsize=(7.0,2.3))
for k,c,lab in [('Delta','C0',r'$\Delta$ (common mode)'),('dr','C3',r'$\delta_r$ (ring mismatch)'),('eps','C2',r'$2\mu-\Omega$')]:
    ax[0].plot(x,res[k][0],c,label=lab); ax[1].plot(x,res[k][1],c)
for a in ax[:2]: a.set_xlabel('offset (MHz)')
for th in (0.95,0.90): ax[0].axhline(th,color='0.6',lw=0.5,ls='--')
ax[0].set_ylabel(r'$\eta_{\rm shift}$'); ax[0].set_ylim(0.5,1.0); ax[0].legend(fontsize=5.5,loc='lower center')
ax[1].set_ylabel('insertion loss (dB)')
sec=ax[0].secondary_xaxis('top',functions=(lambda v:v/dfdT*1e3,lambda v:v*dfdT/1e3)); sec.set_xlabel(r'$\Delta T$ (mK)',fontsize=7)
cs=ax[2].contourf(xd,yd,E2,levels=[0.5,0.7,0.8,0.9,0.95,0.97,1.0],cmap='viridis'); ax[2].contour(xd,yd,E2,levels=[0.90,0.95],colors='w',linewidths=0.6)
ax[2].set_xlabel(r'$\delta_r$ (MHz)'); ax[2].set_ylabel(r'$\Delta$ (MHz)'); fig.colorbar(cs,ax=ax[2],label=r'$\eta_{\rm shift}$')
for a,l in zip(ax,'abc'): a.text(-0.3,1.02,'(%s)'%l,transform=a.transAxes,fontsize=8)
fig.tight_layout(); fig.savefig('fig/figB4_thermal_tolerance.png',dpi=300); fig.savefig('fig/figB4_thermal_tolerance.pdf')
