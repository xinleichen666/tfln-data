import sys,json,numpy as np,tidy3d as td; sys.path.insert(0,'/workspace/tfln_sim/iterations'); import psrlib as P
from tidy3d.plugins.mode import ModeSolver
from multiprocessing import Pool
def eps_rot(lam,th):
    no,ne=P.ln_index(lam); z=np.array([np.cos(th),0,np.sin(th)])  # crystal Z in sim (x,y,z); y_sim = crystal X (film normal)
    return no**2*np.eye(3)+(ne**2-no**2)*np.outer(z,z)
def solve(a):
    w,H,e,thdeg,R,lam=a; th=np.deg2rad(thdeg)
    E=eps_rot(lam,th); LN=td.AnisotropicMedium(xx=td.Medium(permittivity=E[0,0]),yy=td.Medium(permittivity=E[1,1]),zz=td.Medium(permittivity=E[2,2]))  # diagonal approx (off-diag xz dropped; tensorial solver needs tidy3d-extras)
    slab=H-e; top=w/2-e/np.tan(np.deg2rad(60)); s=P.sio2(lam)
    S=[td.Structure(geometry=td.Box(center=(0,-2.5,0),size=(td.inf,5,td.inf)),medium=td.Medium(permittivity=s**2)),
       td.Structure(geometry=td.Box(center=(0,slab/2,0),size=(td.inf,slab,td.inf)),medium=LN),
       td.Structure(geometry=td.PolySlab(vertices=[(-w/2,slab),(w/2,slab),(top,H),(-top,H)],axis=2,slab_bounds=(-td.inf,td.inf)),medium=LN)]
    X=w+6; sim=td.Simulation(size=(X,3.5,1),center=(0,H/2,0),grid_spec=td.GridSpec.auto(min_steps_per_wvl=30,wavelength=lam),
        structures=S,medium=td.Medium(),run_time=1e-12,boundary_spec=td.BoundarySpec.all_sides(td.PML()))
    ms=dict(num_modes=3,target_neff=2.25)
    if R: ms.update(bend_radius=R,bend_axis=1)
    m=ModeSolver(simulation=sim,plane=td.Box(center=(0,H/2,0),size=(X,3.5,0)),mode_spec=td.ModeSpec(**ms),freqs=[td.C_0/lam]).solve()
    n=m.n_eff.values[0]; k=m.k_eff.values[0]; te=m.pol_fraction.te.values[0]
    return dict(a=list(a),n=[float(x) for x in n],k=[float(x) for x in k],te=[float(x) for x in te])
if __name__=='__main__':
    J=[(w,0.6,0.3,t,None,1.55) for w in (1.2,2.0) for t in range(0,91,10)]
    J+=[(1.2,0.6,0.3,t,R,l) for t in (0,45,90) for R in (40,60,80,120) for l in (1.55,)]
    J+=[(1.2,0.6,0.3,t,80,l) for t in (0,45,90) for l in (1.45,1.65)]
    R=[]
    with Pool(8) as p:
        for r in p.imap(solve,J): R.append(r); print(json.dumps(r),flush=True)
    json.dump(R,open('bend.json','w'))
