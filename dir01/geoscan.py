# Round2: for each (w,h) at t=0.6: beta(omega) of pump TE775, sig TE1550, idl TM1550 -> beta1, beta2, dDk/dt, dDk/dw, dDk/dh
import json,os,numpy as np; from geo import neff
f='data/geoscan_raw.json'; R=json.load(open(f)) if os.path.exists(f) else {}
KW=dict(dx=0.02,dy=0.01)
def n(l,w,p,t,h):
    k=f'{l:.4f}_{w:.3f}_{p}_{t:.3f}_{h:.3f}'
    if k not in R: R[k]=neff(l,w,p,t,h,**KW); json.dump(R,open(f,'w'))
    return R[k]
c=0.299792458 # um/fs
def props(w,h,t=0.6):
    out={}
    for name,l0,p in (('p',0.775,'TE'),('s',1.55,'TE'),('i',1.55,'TM')):
        w0=2*np.pi*c/l0; dw=w0*0.01
        bs=[2*np.pi*n(2*np.pi*c/(w0+k*dw),w,p,t,h)/(2*np.pi*c/(w0+k*dw)) for k in (-1,0,1)]  # rad/um
        out[name]=dict(b0=bs[1],b1=(bs[2]-bs[0])/(2*dw),b2=(bs[2]-2*bs[1]+bs[0])/dw**2) # um^-1, fs/um, fs^2/um
    dk=lambda t_,h_,w_: 2*np.pi*(n(0.775,w_,'TE',t_,h_)/0.775-n(1.55,w_,'TE',t_,h_)/1.55-n(1.55,w_,'TM',t_,h_)/1.55)
    out['dDk_dt']=(dk(t+0.01,h+0.01,w)-dk(t-0.01,h-0.01,w))/20*1e3   # film thickness change at fixed etch depth -> slab changes too? see note
    out['dDk_dt_fixedslab']=(dk(t+0.01,h+0.01,w)-dk(t-0.01,h-0.01,w))/20*1e3
    out['dDk_dt']=(dk(t+0.01,h,w)-dk(t-0.01,h,w))/20*1e3
    out['dDk_dh']=(dk(t,h+0.01,w)-dk(t,h-0.01,w))/20*1e3
    out['dDk_dw']=(dk(t,h,w+0.04)-dk(t,h,w-0.04))/80*1e3  # rad/mm per nm
    return out
fo='data/geoscan.json'; G=json.load(open(fo)) if os.path.exists(fo) else {}
for h in (0.3,0.2,0.4,0.5):
  for w in (1.4,1.0,1.8,2.2):
    k=f'{w}_{h}'
    if k in G: continue
    G[k]=props(w,h); json.dump(G,open(fo,'w'),indent=1); print(k,G[k]['dDk_dt'],G[k]['p']['b1'],G[k]['s']['b1'],G[k]['i']['b1'],flush=True)
