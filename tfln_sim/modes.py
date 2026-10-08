import numpy as np, tidy3d as td, json, sys
from tidy3d.plugins.mode import ModeSolver
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
lam=1.55; f0=td.C_0/lam
ne,no,nsio2=2.138,2.211,1.444
LN=td.AnisotropicMedium(xx=td.Medium(permittivity=ne**2),yy=td.Medium(permittivity=no**2),zz=td.Medium(permittivity=no**2))
SiO2=td.Medium(permittivity=nsio2**2)
H,slab=0.6,0.3; etch=H-slab; ang=np.deg2rad(30)  # 60deg sidewall => 30deg from vertical
def build(w,clad):
    bg=SiO2 if clad else td.Medium()
    ridge=td.Structure(geometry=td.PolySlab(vertices=[(-w/2,-50),(w/2,-50),(w/2,50),(-w/2,50)][:0] or [(-w/2,slab),(w/2,slab)],axis=2,slab_bounds=(0,1)),medium=LN) if False else None
    # ridge cross-section in x-y extruded along z
    top=w/2-etch*np.tan(ang)
    verts=[(-w/2,slab),(w/2,slab),(top,H),(-top,H)]
    ridge=td.Structure(geometry=td.PolySlab(vertices=verts,axis=2,slab_bounds=(-td.inf,td.inf)),medium=LN)
    sl=td.Structure(geometry=td.Box(center=(0,slab/2,0),size=(td.inf,slab,td.inf)),medium=LN)
    box=td.Structure(geometry=td.Box(center=(0,-2,0),size=(td.inf,4,td.inf)),medium=SiO2)
    sim=td.Simulation(size=(6,4,1),center=(0,0.3,0),grid_spec=td.GridSpec.auto(min_steps_per_wvl=40,wavelength=lam),
        structures=[box,sl,ridge],medium=bg,run_time=1e-12,boundary_spec=td.BoundarySpec.all_sides(td.PML()))
    ms=ModeSolver(simulation=sim,plane=td.Box(center=(0,0.3,0),size=(6,4,0)),
        mode_spec=td.ModeSpec(num_modes=4,target_neff=2.2),freqs=[f0])
    return ms
res={}
W=np.round(np.array([float(a) for a in sys.argv[1].split(",")]),3) if len(sys.argv)>1 else np.round(np.arange(0.6,2.01,0.05),3)
OUT=sys.argv[2] if len(sys.argv)>2 else "modes.json"
for clad in [True,False]:
    rows=[]
    for w in W:
        d=build(w,clad).solve()
        n=d.n_eff.values[0]; te=d.pol_fraction.te.values[0]
        rows.append(dict(w=float(w),neff=[float(x) for x in n],te=[float(x) for x in te]))
        print(clad,w,np.round(n,4),np.round(te,2),flush=True)
    res["clad" if clad else "air"]=rows
json.dump(res,open(OUT,"w"),indent=1)
