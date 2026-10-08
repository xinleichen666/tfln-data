# verify Tr(chi_exp chi_th) == |Tr(Ut^+U)|^2/d^2 for unitary channels; and normalized version for lossy maps
import numpy as np
from mesh import *
def choi(M):  # Choi of map rho->M rho M^+, normalized (trace 1) => equals chi in a unitary-equivalent basis
    d=M.shape[0]; v=np.array(M).reshape(-1)  # vec(M) row-major
    C=np.outer(v,v.conj()); return C/np.trace(C).real
rng=np.random.default_rng(0); Ut=np.array(targets()['F3'])
from scipy.stats import unitary_group
U=unitary_group.rvs(3,random_state=1)
print('unitary:', np.trace(choi(U)@choi(Ut)).real, abs(np.trace(Ut.conj().T@U))**2/9)
M=U@np.diag([1,0.9,0.8])
print('lossy normalized:', np.trace(choi(M)@choi(Ut)).real, float(fid(jnp.array(Ut),jnp.array(M))))
