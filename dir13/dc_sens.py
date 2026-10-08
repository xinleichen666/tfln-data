import numpy as np, json, dc_fd as F
lam=1.55; w=1.2; g=0.7
def Lc(dw=0,dslab=0,dH=0):
    F.slab=0.3+dslab; F.H=0.6+dH
    ne,no=F.solve(F.eps_map(w,g,dw)); F.slab=0.3; F.H=0.6; return lam/(2*(ne-no))
L0=Lc(); res={'L0':L0}
for name,kw in [('dw',dict(dw=0.04)),('dslab',dict(dslab=0.02)),('dH',dict(dH=0.02))]:
    k=lambda s:{kk:s*v for kk,v in kw.items()}
    Lp,Lm=Lc(**k(1)),Lc(**k(-1))
    dlnk=-(np.log(Lp)-np.log(Lm))/2*0.01/list(kw.values())[0]   # dln(kappa) per +10 nm
    res[name]=dict(Lp=Lp,Lm=Lm,dlnkappa_per10nm=dlnk,
        dtheta_rad_per10nm=np.pi/4*dlnk, dsplit_per10nm=0.5*np.sin(np.pi/2*(1+dlnk))-0.5) 
print(json.dumps(res,indent=1)); json.dump(res,open('dc_sens.json','w'),indent=1)
