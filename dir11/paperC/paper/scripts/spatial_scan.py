"""diag=True keeps only the resonant (n=m) pump-signal beats (rotating-wave approximation for the phonon).
Rationale: with kappa>0 the off-resonant n!=m terms re-radiate bin-m light into the bin-n envelope (double counting),
an artefact of the per-bin envelope basis; for kappa=0 the full model (diag=False) is also reported for reference.
Extension of spatial_check.py: (i) scale the backward-SBS spatial phase by kappa (kappa=0: local model,
kappa=1: physical backward SBS, Delta q = 2 Delta n_g/c); (ii) bin-selective write with a single pump line."""
import numpy as np, json, os
import spatial_check as sc
v, Delta = sc.v, sc.Delta
def run_k(N, w, inp, tau_s, tau_w, theta, kappa, dt=2e-3, diag=True):
    # same integrator as sc.run, with the spatial phase multiplied by kappa
    n = np.arange(N) - (N-1)/2; dz = v*dt; T = 3*tau_s + 3*tau_w; M = int(round(T/dt)); L = M
    z = np.arange(L)*dz; sig = lambda x, c, fw: np.exp(-4*np.log(2)*((x-c)/(v*fw))**2)
    A = np.array([inp[k]*sig(z, z[L//4], tau_s) for k in range(N)], complex); norm_in = np.sum(np.abs(A)**2)*dz
    B = np.zeros(L, complex); zp0 = z[3*L//4]; gpk = theta/(0.5*tau_w*np.sqrt(np.pi/(4*np.log(2))))
    ph_z = np.exp(1j*kappa*np.add.outer(n, n)[:, :, None]*Delta/v*z[None, None, :])
    D = np.eye(N)[:, :, None] if diag else np.ones((N, N, 1))
    for s in range(M):
        t = s*dt; p = gpk*sig(z, zp0 - v*t, tau_w)
        Cn = D*np.conj(w)[None, :, None]*ph_z*np.exp(-1j*np.subtract.outer(n, n)*Delta*t)[:, :, None]
        sA = np.einsum('nmz->nz', np.conj(Cn))
        dB1 = -1j*p*np.einsum('nmz,nz->z', Cn, A); dA1 = -1j*p[None, :]*sA*B[None, :]
        Bm = B + 0.5*dt*dB1; Am = A + 0.5*dt*dA1
        B = B + dt*(-1j*p*np.einsum('nmz,nz->z', Cn, Am)); A = A + dt*(-1j*p[None, :]*sA*Bm[None, :])
        A = np.roll(A, 1, axis=1); A[:, 0] = 0
    return np.sum(np.abs(B)**2)*dz/norm_in
tau_s, tau_w, th = 3.0, 1.0, 1.2
w = np.array([1, 1])/np.sqrt(2); plus = np.array([1, 1])/np.sqrt(2); minus = np.array([1, -1])/np.sqrt(2)
dq = 2*Delta/v                     # rad/m per bin (n+m runs over -1..1 for N=2 -> neighbouring pairs differ by dq)
Lsig = v*(tau_s + tau_w)/2         # collision-region length scale (m)
full = dict(local_full=(run_k(2, w, plus, tau_s, tau_w, th, 0, diag=False), run_k(2, w, minus, tau_s, tau_w, th, 0, diag=False)))
print(full, flush=True)
out = dict(full_model_kappa0_target_orth=full['local_full'], tau_s_ns=tau_s, tau_w_ns=tau_w, theta=th, dq_rad_per_m=dq, L_collision_m=Lsig, scan=[])
for kappa in [0, 3e-4, 1e-3, 3e-3, 1e-2, 3e-2, 1e-1, 1.0]:
    et = run_k(2, w, plus, tau_s, tau_w, th, kappa); eo = run_k(2, w, minus, tau_s, tau_w, th, kappa)
    out['scan'].append(dict(kappa=kappa, dqL=kappa*dq*Lsig, eta_target=et, eta_orth=eo, sel=et/(et+eo))); print(out['scan'][-1], flush=True)
w0 = np.array([1, 0.])
e0 = run_k(2, w0, np.array([1, 0.]), tau_s, tau_w, th, 1.0); e1 = run_k(2, w0, np.array([0, 1.]), tau_s, tau_w, th, 1.0)
e0l = run_k(2, w0, np.array([1, 0.]), tau_s, tau_w, th, 0.0)
out['bin_selective_single_line'] = dict(eta_bin0=e0, eta_bin1=e1, eta_bin0_local=e0l); print(out['bin_selective_single_line'])
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data_spatial_scan.json'), 'w'), indent=1)
