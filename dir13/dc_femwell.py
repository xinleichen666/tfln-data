# Supermode solve of TFLN rib directional coupler with femwell (isotropic n_e approx for TE in X-cut, y-propagation)
import numpy as np, json, sys
from collections import OrderedDict
import shapely
from shapely.geometry import box
from skfem import Basis, ElementTriP0
from skfem.io.meshio import from_meshio
from femwell.mesh import mesh_from_OrderedDict
from femwell.maxwell.waveguide import compute_modes
lam=1.55; nLN=2.138; nSiO2=1.444
H=0.6; etch=0.3; slab=H-etch
def neffs(w,g,swa=0.0):
    x1=-(g/2+w/2); x2=g/2+w/2
    core=shapely.union_all([box(x1-w/2,slab,x1+w/2,H),box(x2-w/2,slab,x2+w/2,H)])
    polys=OrderedDict(core=core, slab=box(-5,0,5,slab), clad=box(-5,-2,5,2.6))
    res=dict(core=0.06,slab=0.08,clad=0.4)
    mesh=from_meshio(mesh_from_OrderedDict(polys,{k:{"resolution":v,"distance":0.5} for k,v in res.items()},default_resolution_max=0.4))
    b0=Basis(mesh,ElementTriP0()); eps=b0.zeros()
    for k,n in dict(core=nLN,slab=nLN,clad=nSiO2).items(): eps[b0.get_dofs(elements=k)]=n**2
    modes=compute_modes(b0,eps,wavelength=lam,num_modes=4,order=2)
    te=[m for m in modes if m.te_fraction>0.7][:2]
    return sorted([float(np.real(m.n_eff)) for m in te],reverse=True)
out=[]
for w in [1.1,1.2,1.3]:
    for g in [0.5,0.6,0.7,0.8,0.9,1.0]:
        ne,no=neffs(w,g); Lc=lam/(2*(ne-no))
        out.append(dict(w=w,g=g,ne=ne,no=no,Lc_um=Lc)); print(out[-1],flush=True)
json.dump(out,open('dc_supermodes.json','w'),indent=1)
