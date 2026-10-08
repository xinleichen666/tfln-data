import json,os,numpy as np; from geo import neff
f='data/calib.json'; R=json.load(open(f)) if os.path.exists(f) else {}
def run(k,*a):
    if k not in R: R[k]=neff(*a); json.dump(R,open(f,'w'),indent=0); print(k,R[k],flush=True)
    return R[k]
# C2: Lu et al 2307.06619 SHG: t=303, h=154, w=0.85, pump 1580 TE, SH 790 TE
def dbeta(t,h,w,lp):
    a=run(f'L_{t}_{h}_{w}_{lp}',lp,w,'TE',t,h); b=run(f'L_{t}_{h}_{w}_{lp/2}',lp/2,w,'TE',t,h)
    return 2*np.pi*(b/(lp/2)-2*a/lp)  # rad/um
d=0.01
r={}
r['dt']=(dbeta(0.303+d,0.154,0.85,1.58)-dbeta(0.303-d,0.154,0.85,1.58))/(2*d)
r['dh']=(dbeta(0.303,0.154+d,0.85,1.58)-dbeta(0.303,0.154-d,0.85,1.58))/(2*d)
r['dw']=(dbeta(0.303,0.154,0.85+0.04,1.58)-dbeta(0.303,0.154,0.85-0.04,1.58))/(0.08)
print('Lu2023 geometry, um^-2: dt',r['dt'],'(paper -4.018) dh',r['dh'],'(paper 1.842) dw',r['dw'],'(paper -0.485)')
# C1: Chen 2023: t=0.6,h=0.35,w=1.8 SHG 1550: dlam_QPM/dt
dl=0.01
db_dl=(dbeta(0.6,0.35,1.8,1.55+dl)-dbeta(0.6,0.35,1.8,1.55-dl))/(2*dl)
db_dt=(dbeta(0.61,0.35,1.8,1.55)-dbeta(0.59,0.35,1.8,1.55))/0.02
r['chen_dlam_dt_nm_per_nm']=-db_dt/db_dl
print('Chen geometry dlam/dt =',r['chen_dlam_dt_nm_per_nm'],'(paper: >70 nm per 10 nm)')
json.dump(r,open('data/calib_result.json','w'),indent=1)
