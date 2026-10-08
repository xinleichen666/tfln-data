import numpy as np, csv, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from scipy.special import jv
from ao_model import *
plt.rcParams.update({'font.family':'serif','font.size':8,'axes.linewidth':0.6,'lines.linewidth':1.1,
 'xtick.direction':'in','ytick.direction':'in','xtick.top':True,'ytick.right':True,'savefig.dpi':400,
 'legend.frameon':False,'legend.fontsize':6.5,'mathtext.fontset':'cm'})
def save(fig,name): fig.tight_layout(pad=0.3); [fig.savefig(f'fig/{name}.{e}') for e in ('png','pdf')]; plt.close(fig)
def wcsv(name,hdr,rows):
    with open(f'data/{name}.csv','w',newline='') as f: w=csv.writer(f); w.writerow(hdr); w.writerows(rows)
rng=np.random.default_rng(11); R={}

# ===== Iter 0: validate group acoustic MZI model (T=[1+cos(aP+phi0)]/2) =====
P=np.linspace(0,1.6,161); T=np.array([np.abs(acoustic_mzi(p))**2 for p in P])
Tn=T[:,1]/T.max()
ana=(1+np.cos(ALPHA_TA*P))/2
R['mzi_model_max_dev']=float(np.max(abs(Tn-ana)))
wcsv('iter0_acoustic_mzi',['P_H_W','T_port2_norm','analytic'],zip(P,Tn,ana))

# ===== Iter 1: phononic 90deg hybrid -> nested AO IQ SSB-SC =====
# acoustic DC (L=Lc/2) outputs: equal power, intrinsic -pi/2 phase -> quadrature drive
a=dc(LC_FULL/2)@np.array([1,0]); thQ=np.angle(a[1])-np.angle(a[0])
R['dc_quadrature_deg']=float(np.degrees(thQ))
dd=np.linspace(0.01,6,300); rows=[]
for d in dd:
    p=iq_spectrum(d,d,0,thQ,np.pi/2); V,g=hom_vis(p); V20,_=hom_vis(p,filt_db=20)
    rows.append([d,p[1],p[0],p[-1],p[-3],p[3],V,V20])
rows=np.array(rows); wcsv('iter1_ssb_vs_drive',['dphi_rad','p+1','p0','p-1','p-3','p+3','V_nofilter','V_20dBfilter'],rows)
R['ssb_max_eta']=float(rows[:,1].max()); R['ssb_dopt']=float(dd[rows[:,1].argmax()])
R['V_at_max_eta_nofilter']=float(rows[rows[:,1].argmax(),6])
i99=np.where(rows[:,6]>=0.99)[0][-1]; R['eta_at_V0.99_nofilter']=float(rows[i99,1]); R['d_at_V0.99']=float(dd[i99])
# power needed (Ni 2026 calibration, power split 50:50 in DC + acoustic loss over 200um feed)
Ls=np.linspace(0.2e-3,3e-3,57); feed=10**(-LOSS_DB_MM*0.2/10)
Preq=[(R['ssb_dopt']/dphi_pp(1,L))**2*2/feed for L in Ls]
Preq99=[(R['d_at_V0.99']/dphi_pp(1,L))**2*2/feed for L in Ls]
wcsv('iter1_power_vs_length',['L_m','P_RF_W_maxeta','P_RF_W_V099'],zip(Ls,Preq,Preq99))
R['P_req_maxeta_L400um']=float((R['ssb_dopt']/dphi_pp(1,400e-6))**2*2/feed)
R['P_req_maxeta_L2mm']=float((R['ssb_dopt']/dphi_pp(1,2e-3))**2*2/feed)
fig,ax=plt.subplots(1,2,figsize=(6.8,2.4))
for j,(lab,c) in enumerate([('p+1','C0'),('p0','C1'),('p-1','C2'),('p-3','C3')]):
    ax[0].plot(dd,rows[:,j+1],c,label={'p+1':r'$+\Omega$ (signal)','p0':'carrier','p-1':r'$-\Omega$ (image)','p-3':r'$-3\Omega$'}[lab])
ax[0].plot(dd,(jv(1,dd/2))**2,'k:',lw=0.8,label=r'$J_1^2(\Delta\phi/2)$')
ax2=ax[0].twinx(); ax2.plot(dd,rows[:,6],'m--',lw=0.9); ax2.set_ylabel('HOM visibility (no filter)',color='m'); ax2.set_ylim(0.9,1.001)
ax[0].set_xlabel(r'push-pull phase $\Delta\phi$ (rad)'); ax[0].set_ylabel('sideband power fraction'); ax[0].legend(loc='center left'); ax[0].text(0.02,0.93,'(a)',transform=ax[0].transAxes)
ax[1].semilogy(Ls*1e3,Preq,label=r'max $\eta$ (33.9%)'); ax[1].semilogy(Ls*1e3,Preq99,label=r'$V=0.99$')
ax[1].set_xlabel('AO interaction length $L$ (mm)'); ax[1].set_ylabel('RF power (W)'); ax[1].legend(); ax[1].text(0.02,0.93,'(b)',transform=ax[1].transAxes)
save(fig,'fig1_ssb_iq')

# ===== Iter 2: fabrication tolerance + thermo-acoustic trim =====
def build(sigL,sig_th,ext_db,trim,d0=None):
    d0=d0 or R['ssb_dopt']
    L1=LC_FULL/2*(1+sigL*rng.standard_normal()); M=dc(L1)@np.array([1,0])
    th_err=sig_th*rng.standard_normal()
    PI,PQ=abs(M[0])**2,abs(M[1])**2; dI=d0*np.sqrt(2*PI); dQ=d0*np.sqrt(2*PQ)
    th=np.angle(M[1])-np.angle(M[0])+th_err
    if trim:   # heater on Q feed: P_H chosen so phase -> -pi/2 exactly (alpha=4.03 rad/W)
        dth=(-np.pi/2-th+np.pi)%(2*np.pi)-np.pi; PH=(dth%(2*np.pi))/ALPHA_TA; th=th+ALPHA_TA*PH
    p=iq_spectrum(dI,dQ,0,th,np.pi/2,ext_db=ext_db)
    return p
sig=np.linspace(0,0.10,11); rows=[]
for s in sig:
    for trim in (0,1):
        out=[]
        for _ in range(300):
            p=build(s,0.05,30,trim,d0=R['d_at_V0.99']); bad=p[-1]+p[0]+1e-3*sum(v for n,v in p.items() if n not in(1,-1,0)); V=p[1]/(p[1]+bad); out.append([p[1]/max(p[-1],1e-30),p[1]/max(p[0],1e-30),V])
        out=np.array(out); rows.append([s,trim,10*np.log10(np.median(out[:,0])),10*np.log10(np.median(out[:,1])),np.median(out[:,2]),np.percentile(out[:,2],5)])
rows=np.array(rows); wcsv('iter2_tolerance_mc',['sigma_Lc_rel','trim','image_rej_dB_med','carrier_supp_dB_med','V_med','V_p5'],rows)
R['iter2']=rows.tolist()
# extinction sweep
ex=np.linspace(15,50,36); er=[]
for e in ex:
    p=iq_spectrum(R['ssb_dopt'],R['ssb_dopt'],0,-np.pi/2,np.pi/2,ext_db=e); er.append([e,10*np.log10(p[1]/p[0]),hom_vis(p)[0]])
er=np.array(er); wcsv('iter2_extinction',['subMZI_ext_dB','carrier_supp_dB','V'],er)
fig,ax=plt.subplots(1,2,figsize=(6.8,2.4))
for trim,ls in ((0,'--'),(1,'-')):
    m=rows[:,1]==trim; ax[0].plot(rows[m,0]*100,rows[m,2],'C0'+ls); ax[0].plot(rows[m,0]*100,rows[m,3],'C1'+ls)
ax[0].plot([],[],'C0',label='image rejection'); ax[0].plot([],[],'C1',label='carrier suppression'); ax[0].plot([],[],'k--',label='untrimmed'); ax[0].plot([],[],'k-',label='heater-trimmed')
ax[0].set_ylim(20,60); ax[0].axhline(30,color='gray',lw=0.5,ls=':'); ax[0].set_xlabel(r'DC length error $\sigma_L/L$ (%)'); ax[0].set_ylabel('suppression (dB)'); ax[0].legend(); ax[0].text(0.02,0.93,'(a)',transform=ax[0].transAxes)
for trim,ls in ((0,'--'),(1,'-')):
    m=rows[:,1]==trim; ax[1].plot(rows[m,0]*100,1-rows[m,4],'C2'+ls); ax[1].fill_between(rows[m,0]*100,1-rows[m,4],1-rows[m,5],color='C2',alpha=0.15)
ax[1].set_xlabel(r'DC length error $\sigma_L/L$ (%)'); ax[1].set_ylabel(r'$1-V$ (median, 95th pct)'); ax[1].set_yscale('log'); ax[1].text(0.02,0.93,'(b)',transform=ax[1].transAxes)
save(fig,'fig2_tolerance')

# ===== Iter 3: phase-matched intermodal shifter (beyond Bessel limit) =====
# calibration: Shao et al. OE 28,23728 (2020): 3.5% at 30 dBm (1 W) -> Gamma^2 = 0.035 per W (weak-conversion)
G1W=np.sqrt(0.035)
Pw=np.logspace(-1,2.3,200); rows=[]
for loss in (0.0,1.0,2.4):     # dB/mm acoustic loss over L=1 mm normalized device
    an=loss*np.log(10)/10*1e3   # 1/m intensity
    for p in Pw:
        G=G1W*np.sqrt(p); eta=intermodal(G,an,1e-3,nz=200) if loss>0 else np.sin(G)**2
        rows.append([loss,p,eta])
rows=np.array(rows); wcsv('iter3_intermodal_vs_power',['acoustic_loss_dB_per_mm','P_RF_W','eta'],rows)
R['P_full_lossless_W']=float((np.pi/2/G1W)**2)
# HOM vs residual carrier & mode-filter extinction
etas=np.linspace(0.5,1,51); Xs=[10,20,30]; hv=[]
for X in Xs:
    for e in etas: bad=(1-e)*10**(-X/10); hv.append([X,e,e/(e+bad)])
hv=np.array(hv); wcsv('iter3_hom_intermodal',['modefilter_dB','eta','V'],hv)
# phase mismatch bandwidth
db=np.linspace(-15,15,121)/1e-3; bw=[intermodal(np.pi/2,0,1e-3,dbeta=x,nz=200) for x in db]
wcsv('iter3_dbeta',['dbeta_per_m','eta'],zip(db,bw))
fig,ax=plt.subplots(1,2,figsize=(6.8,2.4))
for loss,c in zip((0.0,1.0,2.4),('C0','C1','C3')):
    m=rows[:,0]==loss; ax[0].semilogx(rows[m,1],rows[m,2],c,label=f'{loss} dB/mm')
ax[0].axhline(0.339,color='k',ls=':',lw=0.8); ax[0].text(0.12,0.36,'IQ-SSB Bessel limit 33.9%',fontsize=6)
ax[0].plot([1],[0.035],'ks',ms=3); ax[0].text(1.2,0.02,'Shao 2020',fontsize=6)
ax[0].set_xlabel('RF power (W)'); ax[0].set_ylabel(r'conversion $\eta$'); ax[0].legend(title='acoustic loss',title_fontsize=6); ax[0].text(0.02,0.93,'(a)',transform=ax[0].transAxes)
for X,c in zip(Xs,('C0','C1','C2')):
    m=hv[:,0]==X; ax[1].plot(hv[m,1],hv[m,2],c,label=f'mode filter {X} dB')
ax[1].set_xlabel(r'conversion $\eta$'); ax[1].set_ylabel('HOM visibility'); ax[1].legend(); ax[1].text(0.02,0.93,'(b)',transform=ax[1].transAxes)
save(fig,'fig3_intermodal')

# ===== Iter 4: microwave-to-optical transducer (Shao 2019 parameters, Optica 6,1498) =====
tp=2*np.pi
kap=tp*95e6; kape=0.15*kap; gam=tp*1.28e6; game=0.17*gam; Om=tp*2.007e9; g0=tp*1.1e3
C0=4*g0**2/(gam*kap); R['C0_shao']=float(C0)
n1=ncav(1e-3,kap,kape,Om); eta1=C0*n1*(2*game/gam)*(2*kape/kap); R['ncav_1mW_single']=float(n1); R['eta_1mW_single_validate']=float(eta1)
Pp=np.logspace(-5,-1,200); rows=[]
cases={'A: Shao2019 single-res':(kape,game,False),'B: + double resonance':(kape,game,True),
       'C: B + critical IDT/optics (design)':(kap/2,gam/2,True),'D: C + overcoupled (design)':(0.9*kap,0.9*gam,True)}
for name,(ke,ge,dbl) in cases.items():
    for p in Pp:
        n=ncav(p,kap,ke,0 if dbl else Om); G=g0*np.sqrt(n); e,s=transducer(0,G,kap,ke,gam,ge)
        C=4*G**2/(kap*gam); rows.append([name,p,n,C,e[0],(gam-ge)/ge])
wcsv('iter4_transducer_vs_pump',['case','P_pump_W','n_cav','C','eta','Nadd_per_nth'],rows)
for name in cases:
    r=[x for x in rows if x[0]==name]; i=np.argmin(abs(np.array([x[1] for x in r])-1e-3)); R['eta_1mW_'+name]=float(r[i][4]); R['C_1mW_'+name]=float(r[i][3])
    R['eta_max_'+name]=float(max(x[4] for x in r))
# bandwidth vs C (case D)
bws=[]
for C in np.logspace(-2,2,41):
    G=np.sqrt(C*kap*gam/4); w=np.linspace(-1,1,40001)*max(20*gam,6*G); e,_=transducer(w,G,kap,0.9*kap,gam,0.9*gam); m=w[e>=e.max()/2]; bws.append([C,e.max(),(m.max()-m.min())/tp])
bws=np.array(bws); wcsv('iter4_bandwidth_caseD',['C','eta_peak','BW3dB_Hz'],bws)
temps={'300 K':300,'4 K':4,'0.1 K':0.1,'10 mK':0.01}; R['nth']={k:float(nth(2.007e9,T)) for k,T in temps.items()}
R['Nadd_caseD']={k:float(nth(2.007e9,T)*(0.1/0.9)) for k,T in temps.items()}
fig,ax=plt.subplots(1,2,figsize=(6.8,2.4))
for (name,_),c in zip(cases.items(),('C0','C1','C2','C3')):
    r=np.array([[x[1],x[4]] for x in rows if x[0]==name]); ax[0].loglog(r[:,0]*1e3,r[:,1],c,label=name)
ax[0].plot([1],[1.7e-5],'ko',ms=3); ax[0].text(1.3,8e-6,'Shao 2019 (0.0017%)',fontsize=6)
ax[0].plot([3.3e-3],[1e-5],'k^',ms=3); ax[0].text(4.5e-3,4e-6,'Jiang 2020 (red, OMC)',fontsize=6)
ax[0].set_xlabel('optical pump power (mW)'); ax[0].set_ylabel(r'photon conversion $\eta$'); ax[0].legend(fontsize=5.5,loc='lower right'); ax[0].set_ylim(1e-8,1.2); ax[0].text(0.02,0.93,'(a)',transform=ax[0].transAxes)
ax[1].semilogx(bws[:,0],bws[:,1],'C3'); ax[1].set_xlabel('cooperativity $C$'); ax[1].set_ylabel(r'peak $\eta$ (case D)',color='C3')
a2=ax[1].twinx(); a2.loglog(bws[:,0],bws[:,2]/1e6,'C0--'); a2.set_ylabel('3-dB bandwidth (MHz)',color='C0'); ax[1].text(0.02,0.93,'(b)',transform=ax[1].transAxes)
save(fig,'fig4_transducer')
import json; json.dump(R,open('data/key_results.json','w'),indent=1,default=float); print(json.dumps(R,indent=1,default=float))
