import numpy as np, tidy3d as td, warnings, logging
from tidy3d.plugins.mode import ModeSolver
td.config.logging.level="ERROR"
def ln_index(lam):  # Zelmon 1997 congruent LN Sellmeier, lam in um
    l2=lam**2
    no=np.sqrt(1+2.6734*l2/(l2-0.01764)+1.2290*l2/(l2-0.05914)+12.614*l2/(l2-474.6))
    ne=np.sqrt(1+2.9804*l2/(l2-0.02047)+0.5981*l2/(l2-0.0666)+8.9543*l2/(l2-416.08))
    return no,ne
def sio2(lam):
    l2=lam**2
    return np.sqrt(1+0.6961663*l2/(l2-0.0684043**2)+0.4079426*l2/(l2-0.1162414**2)+0.8974794*l2/(l2-9.896161**2))
ORIENT={"XcutY":"exx=ne,eyy=no","XcutZ":"isotropic no","Zcut":"exx=no,eyy=ne"}
def ln_medium(orient,lam):
    no,ne=ln_index(lam)
    nx,ny,nz={"XcutY":(ne,no,no),"XcutZ":(no,no,ne),"Zcut":(no,ne,no)}[orient]
    return td.AnisotropicMedium(xx=td.Medium(permittivity=nx**2),yy=td.Medium(permittivity=ny**2),zz=td.Medium(permittivity=nz**2))
def clad_index(clad,lam):
    return {"air":1.0,"SiO2":sio2(lam),"SiN":1.99,"polymer":1.50,"Al2O3":1.75}[clad]
def build(w,H=0.6,etch=0.3,angle=60,orient="XcutY",clad="air",lam=1.55,nmodes=4,res=40,partial=None):
    """w: ridge bottom width. clad: upper cladding material (fills top). partial=(mat,thickness): conformal-ish top layer box of given thickness over slab level, rest air."""
    slab=H-etch; LN=ln_medium(orient,lam); n_sio2=sio2(lam)
    top=w/2-etch/np.tan(np.deg2rad(angle))
    if top<0.05: return None
    S=[td.Structure(geometry=td.Box(center=(0,-2.5,0),size=(td.inf,5,td.inf)),medium=td.Medium(permittivity=n_sio2**2))]
    if partial is not None:
        mat,t=partial
        S.append(td.Structure(geometry=td.Box(center=(0,slab+t/2,0),size=(td.inf,t,td.inf)),medium=td.Medium(permittivity=clad_index(mat,lam)**2)))
    if slab>0: S.append(td.Structure(geometry=td.Box(center=(0,slab/2,0),size=(td.inf,slab,td.inf)),medium=LN))
    S.append(td.Structure(geometry=td.PolySlab(vertices=[(-w/2,slab),(w/2,slab),(top,H),(-top,H)],axis=2,slab_bounds=(-td.inf,td.inf)),medium=LN))
    bg=td.Medium(permittivity=clad_index(clad,lam)**2)
    X=w+4; Y=3.5; yc=H/2
    sim=td.Simulation(size=(X,Y,1),center=(0,yc,0),grid_spec=td.GridSpec.auto(min_steps_per_wvl=res,wavelength=lam),
        structures=S,medium=bg,run_time=1e-12,boundary_spec=td.BoundarySpec.all_sides(td.PML()))
    nmax=max(ln_index(lam))
    return ModeSolver(simulation=sim,plane=td.Box(center=(0,yc,0),size=(X,Y,0)),
        mode_spec=td.ModeSpec(num_modes=nmodes,target_neff=nmax,precision="double" if False else "single"),freqs=[td.C_0/lam])
def solve(args):
    w,kw=args
    ms=build(w,**kw)
    if ms is None: return None
    d=ms.solve()
    n=d.n_eff.values[0].tolist(); te=d.pol_fraction.te.values[0].tolist()
    return dict(w=float(w),neff=n,te=te)
def sweep(W,kw,pool):
    return [r for r in pool.map(solve,[(w,kw) for w in W]) if r]
def analyze(rows,lam=1.55,ncut=None):
    """find TM0/TE1 anticrossing among modes 1..3: the pair (i,i+1) whose TE fractions cross 0.5;
    returns gap g (min neff difference), width, slope alpha of diabatic dn/dw, LZ length."""
    best=None
    for r in rows:
        n=np.array(r["neff"]);te=np.array(r["te"])
        for i in range(len(n)-1):
            if ncut is not None and n[i+1]<ncut: continue
            mix=min(abs(te[i]-0.5),abs(te[i+1]-0.5))
            # hybrid: both modes strongly mixed, one TE-ish/TM-ish partner
            score=(n[i]-n[i+1]) if (te[i]>0.15 and te[i]<0.85 and te[i+1]>0.15 and te[i+1]<0.85) else None
            if score is not None and (best is None or score<best["g"]):
                best=dict(g=float(score),w=r["w"],i=i)
    return best

def find_cross(kw,wmin=0.8,wmax=6.0,step=0.2,tol=0.005):
    """Sequential (for use inside a pool over configs). Tracks the TM-like mode (min TE fraction among
    modes 1..) and finds the first width where it swaps with the TE mode just above it (i.e. TE fraction
    of mode i crosses 0.5 for i>=1). Returns dict with gap g, width wx, slope alpha, LZ L99 etc."""
    lam=kw.get("lam",1.55)
    W=np.arange(wmin,wmax+1e-9,step); rows=[]; cands=[]
    prev=None
    for w in W:
        r=solve((w,kw))
        if r is None: continue
        rows.append(r)
        if prev is not None:
            for i in (1,2):
                a,b=prev["te"][i],r["te"][i]
                if (a-0.5)*(b-0.5)<0 and min(prev["te"][i+1],r["te"][i+1])<1.01:
                    # bisect for te_i = 0.5
                    lo,hi,tlo=prev["w"],r["w"],a
                    while hi-lo>tol:
                        m=solve(((lo+hi)/2,kw)); rows.append(m)
                        if (m["te"][i]-0.5)*(tlo-0.5)>0: lo,tlo=m["w"],m["te"][i]
                        else: hi=m["w"]
                    mid=solve(((lo+hi)/2,kw)); rows.append(mid)
                    g=mid["neff"][i]-mid["neff"][i+1]; wx=mid["w"]
                    # slope from +-d
                    d=max(0.15,8*g/1.0) ; d=min(d,0.4)
                    rp=solve((wx+d,kw)); rm=solve((wx-d,kw)); rows+= [x for x in (rp,rm) if x]
                    def dn(x): 
                        v=(x["neff"][i]-x["neff"][i+1])**2-g**2; return np.sqrt(max(v,0))
                    alpha=(dn(rp)+dn(rm))/(2*d) if rp and rm else np.nan
                    cands.append(dict(found=True,g=float(g),wx=float(wx),alpha=float(alpha),i=i,
                                neff_x=float((mid["neff"][i]+mid["neff"][i+1])/2),te_x=[mid["te"][i],mid["te"][i+1]]))
        prev=r
    return dict(found=bool(cands),cands=cands,rows=rows)
def lz_length(g,alpha,lam=1.55,span_min=0.4,target=0.99):
    """Linear taper spanning S across the anticrossing; LZ conversion P=1-exp(-pi^2 g^2 L/(lam alpha S))."""
    S=max(10*g/alpha,span_min)
    L=-np.log(1-target)*lam*alpha*S/(np.pi**2*g**2)
    return L,S

def slab_neff(H=0.6,etch=0.3,orient="XcutY",clad="air",lam=1.55,partial=None,**k):
    """effective indices (TE0,TM0) of the remaining slab (x-invariant) -> lateral leakage threshold."""
    slab=H-etch
    if slab<=1e-6: return (clad_index(clad,lam),clad_index(clad,lam))
    LN=ln_medium(orient,lam); n_sio2=sio2(lam)
    S=[td.Structure(geometry=td.Box(center=(0,-2.5,0),size=(td.inf,5,td.inf)),medium=td.Medium(permittivity=n_sio2**2))]
    if partial is not None:
        mat,t=partial; S.append(td.Structure(geometry=td.Box(center=(0,slab+t/2,0),size=(td.inf,t,td.inf)),medium=td.Medium(permittivity=clad_index(mat,lam)**2)))
    S.append(td.Structure(geometry=td.Box(center=(0,slab/2,0),size=(td.inf,slab,td.inf)),medium=LN))
    sim=td.Simulation(size=(0.2,4,1),center=(0,0.3,0),grid_spec=td.GridSpec.auto(min_steps_per_wvl=60,wavelength=lam),
        structures=S,medium=td.Medium(permittivity=clad_index(clad,lam)**2),run_time=1e-12,
        boundary_spec=td.BoundarySpec(x=td.Boundary.periodic(),y=td.Boundary.pml(),z=td.Boundary.pml()))
    ms=ModeSolver(simulation=sim,plane=td.Box(center=(0,0.3,0),size=(0.2,4,0)),mode_spec=td.ModeSpec(num_modes=2,target_neff=2.3),freqs=[td.C_0/lam])
    d=ms.solve(); n=d.n_eff.values[0]; te=d.pol_fraction.te.values[0]
    nte=max([a for a,b in zip(n,te) if b>0.5],default=np.nan); ntm=max([a for a,b in zip(n,te) if b<=0.5],default=np.nan)
    return float(nte),float(ntm)

def build2(w1,w2,gap,H=0.6,etch=0.3,angle=60,orient="XcutZ",clad="air",lam=1.55,nmodes=4,res=40,target=None,only=None):
    """two ridges (bottom widths w1 left, w2 right) separated by bottom gap."""
    slab=H-etch; LN=ln_medium(orient,lam); n_sio2=sio2(lam); dx=etch/np.tan(np.deg2rad(angle))
    x1=-(gap/2+w1/2); x2=gap/2+w2/2
    S=[td.Structure(geometry=td.Box(center=(0,-2.5,0),size=(td.inf,5,td.inf)),medium=td.Medium(permittivity=n_sio2**2))]
    if slab>0: S.append(td.Structure(geometry=td.Box(center=(0,slab/2,0),size=(td.inf,slab,td.inf)),medium=LN))
    for j,(xc,w) in enumerate([(x1,w1),(x2,w2)]):
        if only is not None and j!=only: continue
        S.append(td.Structure(geometry=td.PolySlab(vertices=[(xc-w/2,slab),(xc+w/2,slab),(xc+w/2-dx,H),(xc-w/2+dx,H)],axis=2,slab_bounds=(-td.inf,td.inf)),medium=LN))
    X=w1+w2+gap+4; xc0=(x1+x2)/2
    sim=td.Simulation(size=(X,3.5,1),center=(xc0,H/2,0),grid_spec=td.GridSpec.auto(min_steps_per_wvl=res,wavelength=lam),
        structures=S,medium=td.Medium(permittivity=clad_index(clad,lam)**2),run_time=1e-12,boundary_spec=td.BoundarySpec.all_sides(td.PML()))
    return ModeSolver(simulation=sim,plane=td.Box(center=(xc0,H/2,0),size=(X,3.5,0)),
        mode_spec=td.ModeSpec(num_modes=nmodes,target_neff=target or max(ln_index(lam))),freqs=[td.C_0/lam])
