"""HOM after shift with group-delay compensation (a reference photon can always be delay-matched)."""
import numpy as np, json
d=np.loadtxt('data/H_shift.csv',delims:=',',skiprows=1) if False else np.loadtxt('data/H_shift.csv',delimiter=',',skiprows=1)
eta=json.load(open('data/results_B.json'))['optimum']['ao']['eta_shift']; out=[]
for sig in np.unique(d[:,0]):
    m=d[:,0]==sig; D=d[m,1]; H=d[m,2]+1j*d[m,3]; psi=np.exp(-D**2/(4*sig**2))
    best=0
    for tau in np.linspace(-20e-9,20e-9,4001):
        A=H*psi*np.exp(-2j*np.pi*D*tau); ov=abs(np.sum(psi*A))**2/(np.sum(psi**2)*np.sum(abs(A)**2))
        if ov>best: best,tb=ov,tau
    out.append([sig,tb,best,best*eta])
out=np.array(out); np.savetxt('data/HOM.csv',out,delimiter=',',header='photon_rms_bw_Hz,delay_s,V_filtered_delaymatched,V_unfiltered(=V*eta_shift)',comments='')
print(out)
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
plt.rcParams.update({'font.size':8,'font.family':'serif','mathtext.fontset':'dejavuserif'})
fig,ax=plt.subplots(figsize=(3.4,2.4)); ax.semilogx(out[:,0]/1e6,1-out[:,2],'C2o-',label='target bin filtered, delay-matched'); ax.semilogx(out[:,0]/1e6,1-out[:,3],'C3s--',label='unfiltered')
ax.set_yscale('log'); ax.set_xlabel('photon rms bandwidth (MHz)'); ax.set_ylabel(r'$1-V_{\rm HOM}$'); ax.legend(fontsize=6); fig.tight_layout(); fig.savefig('fig/figB3_HOM.png',dpi=300); fig.savefig('fig/figB3_HOM.pdf')
