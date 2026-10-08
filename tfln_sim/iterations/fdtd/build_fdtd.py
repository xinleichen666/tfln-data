"""Final cascaded PSR, 3D FDTD model (NOT run). X-cut LN, propagation along crystal Z (sim z).
Sections: CA taper 1.2->2.6 (101 um) | ADC1 (gap .3, 80 um, narrow 1.21 -> cross port, S-bend) |
ADC2 dump (80 um, other side) | 5 um down-taper 2.6->1.0 (through port)."""
import json,sys,numpy as np,tidy3d as td
sys.path.insert(0,".."); import psrlib as P
lam0=1.55; f0=td.C_0/lam0; fw=td.C_0/1.45-td.C_0/1.65
H,etch,ang=0.6,0.3,60; slab=H-etch; swa=np.deg2rad(90-ang)
LN=P.ln_medium("XcutZ",lam0); SiO2=td.Medium(permittivity=P.sio2(lam0)**2)
prof=json.load(open("../round4/eme_results.json")); Wp=np.array(prof["W"]); zp=np.array(prof["ca_profile"])
Lt,La,Lb,Ls=101.2,79.5,15.0,5.0; gap,wn,W=0.3,1.21,2.6; zin=3.0
z_t0=zin; z_a1=z_t0+Lt; z_b1=z_a1+La; z_a2=z_b1+Lb; z_b2=z_a2+La; z_d=z_b2+Lb; z_end=z_d+Ls+4
def strip(xc_fun,w_fun,z):
    z=np.asarray(z); xl=xc_fun(z)-w_fun(z)/2; xr=xc_fun(z)+w_fun(z)/2
    return list(zip(xl,z))+list(zip(xr[::-1],z[::-1]))
def ps(verts):  # verts in (x,z); PolySlab axis=1 (y) uses (z,x)? -> tidy3d plane coords for axis=1 are (x,z)
    return td.Structure(geometry=td.PolySlab(vertices=verts,axis=1,slab_bounds=(slab,H),sidewall_angle=swa,reference_plane="bottom"),medium=LN)
# main (wide) arm: x=0 centre
zt=np.linspace(z_t0,z_a1,80); wt=np.interp((zt-z_t0)/Lt,zp,Wp)
zz=np.concatenate([[ -2.0],zt,[z_d],np.linspace(z_d,z_d+Ls,6),[z_end+2]])
ww=np.concatenate([[1.2],wt,[W],np.linspace(W,1.0,6),[1.0]])
o=np.argsort(zz,kind="stable"); zz,ww=zz[o],ww[o]
main=ps(strip(lambda z:0*z,lambda z:np.interp(z,zz,ww),zz))
def sbend_arm(side,za,zb):
    xc0=side*(W/2+gap+wn/2); dx=side*3.0
    z=np.concatenate([np.linspace(za-Lb,zb+Lb,120),[z_end+2]])
    def xc(z):
        z=np.asarray(z); x=np.full_like(z,xc0,dtype=float)
        a=z<za; x[a]=xc0+dx*(1-np.cos(np.pi*np.clip((za-z[a])/Lb,0,1)))/2
        b=z>zb; x[b]=xc0+dx*(1-np.cos(np.pi*np.clip((z[b]-zb)/Lb,0,1)))/2
        return x
    return ps(strip(xc,lambda z:0*z+wn,z)),xc
cross,xc1=sbend_arm(+1,z_a1,z_b1); dump,xc2=sbend_arm(-1,z_a2,z_b2)
structs=[td.Structure(geometry=td.Box(center=(0,-1.5,0),size=(td.inf,3,td.inf)),medium=SiO2),
         td.Structure(geometry=td.Box(center=(0,slab/2,0),size=(td.inf,slab,td.inf)),medium=LN),main,cross,dump]
X=2*(W/2+gap+wn+3.0+1.5); Y=3.2; Z=z_end
src=td.ModeSource(center=(0,H/2,1.0),size=(4,2.5,0),source_time=td.GaussianPulse(freq0=f0,fwidth=fw),
    mode_spec=td.ModeSpec(num_modes=3,target_neff=2.0),mode_index=1,direction="+",name="TM0_in")
freqs=list(np.linspace(td.C_0/1.65,td.C_0/1.45,41))
mons=[td.ModeMonitor(center=(xc1(np.array([z_end-2]))[0],H/2,z_end-2),size=(3.5,2.5,0),freqs=freqs,mode_spec=td.ModeSpec(num_modes=3),name="cross"),
      td.ModeMonitor(center=(0,H/2,z_end-2),size=(3.5,2.5,0),freqs=freqs,mode_spec=td.ModeSpec(num_modes=3),name="through"),
      td.FieldMonitor(center=(0,H/2,Z/2),size=(td.inf,0,td.inf),freqs=[f0],name="top_view")]
sim=td.Simulation(size=(X,Y,Z),center=(0,0.3,Z/2),structures=structs,sources=[src],monitors=mons,medium=td.Medium(),
    grid_spec=td.GridSpec.auto(min_steps_per_wvl=15,wavelength=1.45),run_time=5e-12,
    boundary_spec=td.BoundarySpec.all_sides(td.PML()))
sim.to_file("psr_final_3d.hdf5")
print("size",sim.size,"cells %.3e"%sim.num_cells,"time steps",sim.num_time_steps)
