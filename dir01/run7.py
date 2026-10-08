# Round 7: one TM-pump set. Do not import run5 or run6.
# Geometry w=1.4 um, h=0.3 um, t=0.6 um, vertical sidewalls (etch of Kuttner unknown).
# Pump TM 764 nm, signal TE 1528 nm, idler TM 1528 nm.
# St, Sw, Sh, A, B, b2, period all from data/tm_coeff.json (same mode solves).
# Seed 2027. N=64. Checkpoint after every sample. Loss is NOT folded into b.
import json, os, numpy as np, run2 as r
C=json.load(open('data/tm_coeff.json'))
P=dict(A=C['A_ps_per_mm'], B=C['B_ps_per_mm'],
       b2=(C['b2_ps2_per_mm']['pump'], C['b2_ps2_per_mm']['signal'], C['b2_ps2_per_mm']['idler']),
       LAM=C['period_mm'], St=C['St_rad_per_mm_per_nm'], Sw=C['Sw_rad_per_mm_per_nm'], Sh=C['Sh_rad_per_mm_per_nm'])
CHEN=np.loadtxt('data/chen_fig1d_thickness.csv', delimiter=',')
XIN=np.loadtxt('data/xin2024_fig2b.csv', delimiter=',')
NMC=64
SEED=2027
STEPS=((0.2,'a0.2'),(0.1,'a0.1'),(0.04,'a0.04'))
out='data/run7.json'

def Phi(z,q,phi,D):
    o=np.zeros(D.shape, complex); a=q*np.exp(1j*phi)
    for i in range(0,len(z),400):
        o+=np.exp(1j*np.multiply.outer(D, z[i:i+400]))@a[i:i+400]
    return o*(z[1]-z[0])
def PB(F,Ws,Wi,dW,tau,Cc):
    a=(tau**2/np.pi)**0.25*np.exp(-((Ws+Wi)*tau)**2/2+1j*Cc*(Ws+Wi)**2); f=a*F
    sv=np.linalg.svd(f*dW, compute_uv=False)**2; B=float(sv.sum()); sv=sv/B
    return float((sv**2).sum()), B
def pink(rng,z,rms):
    n=len(z); f=np.fft.rfftfreq(n, z[1]-z[0]); a=np.zeros(len(f)); a[1:]=1/np.sqrt(f[1:])
    x=np.fft.irfft(a*np.exp(2j*np.pi*rng.random(len(f))), n); x-=x.mean()
    return x/x.std()*rms
def dump_state(rng):
    s=rng.bit_generator.state
    return {'bit_generator':s['bit_generator'],
            'state':{'state':int(s['state']['state']), 'inc':int(s['state']['inc'])},
            'has_uint32':int(s['has_uint32']), 'uinteger':int(s['uinteger'])}
def load_state(rng,d):
    rng.bit_generator.state=d

def loss_of(L,z,q):
    # Zhao main: signal 0.54 dB/cm, pump 0, facet 10**(-0.7), detect 0.68
    zz=z+L/2; Tp=np.ones_like(z); Ts=10**(-0.54*(L-zz)/100)
    gen=float((q*Tp).sum()/q.sum()); Tph=float((q*Tp*Ts).sum()/(q*Tp).sum())
    return gen, Tph, 10**(-0.7)*0.68*Tph

def main():
    R=json.load(open(out)) if os.path.exists(out) else {}
    R['P']=P; R['seed']=SEED; R['NMC']=NMC
    R['note']='b is raw JSA norm, not multiplied by gen. eta_h uses A_S=0.54, A_P=0, eta_c=10**(-0.7), eta_d=0.68'
    rng=np.random.default_rng(SEED)
    if 'rng_state' in R: load_state(rng, R['rng_state'])
    keys=['none','a0.2_e0.3','a0.1_e0.3','a0.04_e0.3',
          'w10_none','w10_a0.2_e0.3','w10_a0.1_e0.3','w10_a0.04_e0.3',
          'e1_a0.2','e1_a0.1','e1_a0.04']
    for L in (2,5,10,15,20):
        z,q=r.weights(L,P['LAM'],0.25); Ws,Wi,dW=r.grid(P,L); D=r.dk(P,Ws,Wi)
        F0=Phi(z,q,np.zeros_like(z),D)
        x=r.minimize_scalar(lambda x:-PB(F0,Ws,Wi,dW,np.exp(x),0)[0], bounds=(np.log(0.02*L),np.log(20*L)), method='bounded').x
        tau=float(np.exp(x)); Pid,Bid=PB(F0,Ws,Wi,dW,tau,0)
        gen,Tph,eh=loss_of(L,z,q)
        key=f'L{L}'
        if key not in R or 'none' not in R[key]:
            R[key]=dict(ideal=[Pid,Bid], tau=tau, gen=gen, Tph=Tph, eta_h=eh, src=[], **{k:[] for k in keys})
        else:
            R[key]['ideal']=[Pid,Bid]; R[key]['tau']=tau; R[key]['gen']=gen; R[key]['Tph']=Tph; R[key]['eta_h']=eh
        done=len(R[key]['none'])
        print(f'start L{L} tau={tau:.4f} idealP={Pid:.4f} done={done}', flush=True)
        while len(R[key]['none'])<NMC:
            src='xin' if (L<=5 and (len(R[key]['none'])%2==1)) else 'chen'
            D_=XIN if src=='xin' else CHEN
            zmax=float(D_[-1,0]-L); z0=float(rng.uniform(0, max(zmax,0)))
            w=(D_[:,0]>=z0-1e-9)&(D_[:,0]<=z0+L+1e-9)
            tt=D_[w,1]-D_[w,1].mean(); dt=np.interp(z, D_[w,0]-z0-L/2, tt)
            if src=='xin':
                dh=np.interp(z, D_[w,0]-z0-L/2, D_[w,2]-D_[w,2].mean())
            else:
                dh=pink(rng,z,0.2)
            dw=pink(rng,z,2.0); Cc=float(rng.uniform(-0.25,0.25))*tau**2
            phi_t=r.ph(z,P['St'],dt); phi_w=r.ph(z,P['Sw'],dw); phi_h=r.ph(z,P['Sh'],dh)
            phi2=phi_t+phi_w+phi_h
            phi10=phi_t+5*phi_w+phi_h
            def evalp(phi):
                return list(PB(Phi(z,q,phi,D),Ws,Wi,dW,tau,Cc))
            R[key]['none'].append(evalp(phi2))
            R[key]['w10_none'].append(evalp(phi10))
            for step,name in STEPS:
                zs=np.arange(z[0], z[-1]+step, step)
                noise=rng.normal(0,1,len(zs))
                base=np.interp(zs,z,dt)
                m03=np.interp(z,zs,base+0.3*noise)
                m1=np.interp(z,zs,base+1.0*noise)
                sub03=r.ph(z,P['St'],m03); sub1=r.ph(z,P['St'],m1)
                R[key][f'{name}_e0.3'].append(evalp(phi2-sub03))
                R[key][f'w10_{name}_e0.3'].append(evalp(phi10-sub03))
                R[key][f'e1_{name}'].append(evalp(phi2-sub1))
            R[key]['src'].append(src)
            R['rng_state']=dump_state(rng)
            tmp=out+'.tmp'; json.dump(R, open(tmp,'w')); os.replace(tmp, out)
            n=len(R[key]['none'])
            if n%4==0 or n==NMC:
                med=float(np.median(np.array(R[key]['none'])[:,0]))
                print(f'  L{L} {n}/{NMC} none_med {med:.3f}', flush=True)
    print('ALL DONE', flush=True)

if __name__=='__main__':
    main()
