"""Independent 1D space-time check of the mode-selective write (added during manuscript preparation).
Counter-propagating backward SBS: N signal bins move +z at v, pump comb (classical, undepleted) moves -z at v,
phonon is local (v_ac ~ 0 on ns scales, no damping). Envelope phases Phi_nm = (n+m)(Delta/v) z - (n-m) Delta t.
Flag `spatial`: if False the spatial phase (n+m)Delta z/v is dropped -> reproduces the single-acoustic-mode (local) model.
Exact advection: dz = v dt, fields shift one cell per step. Units: ns, m."""
import numpy as np, json, sys, os
v = 2.998e8/2.3*1e-9          # m/ns (n_g = 2.3, same assumption as params.py)
Delta = 2*np.pi*10.0          # rad/ns (10 GHz bins)
def run(N, w, inp, tau_s, tau_w, theta, spatial=True, dt=2e-3):
    n = np.arange(N) - (N-1)/2
    dz = v*dt
    T = 3*tau_s + 3*tau_w          # collision window
    M = int(round(T/dt)); L = M    # cells
    z = np.arange(L)*dz
    # signal: gaussian (FWHM tau_s) centred at cell L/4 initially moving +z; pump centred at 3L/4 moving -z
    sig = lambda x, c, fw: np.exp(-4*np.log(2)*((x-c)/(v*fw))**2)
    A = np.array([inp[k]*sig(z, z[L//4], tau_s) for k in range(N)], complex)   # A_n(z)
    norm_in = np.sum(np.abs(A)**2)*dz
    B = np.zeros(L, complex)
    zp0 = z[3*L//4]
    # pump peak coupling g0*|p|: choose so that a signal slice accumulates swap angle theta: g*tau_w_eff/2 = theta
    gpk = theta/(0.5*tau_w*np.sqrt(np.pi/(4*np.log(2))))   # integral of gaussian FWHM tau_w = tau_w*sqrt(pi/4ln2)
    if spatial:
        ph_z = np.exp(1j*np.add.outer(n, n)[:, :, None]*Delta/v*z[None, None, :])
    else:
        ph_z = np.ones((N, N, 1))
    for s in range(M):
        t = s*dt
        p = gpk*sig(z, zp0 - v*t, tau_w)               # pump envelope (common), weights w_m
        ph_t = np.exp(-1j*np.subtract.outer(n, n)*Delta*t)            # (n-m)
        Phi = ph_z*ph_t[:, :, None]            # e^{i Phi_nm}
        C = w[None, :, None]*Phi               # coupling of A_n to B via pump line m (conj appropriately)
        # dB/dt = -i sum_nm p w_m^* A_n e^{iPhi}; dA_n/dt = -i sum_m p w_m B e^{-iPhi}
        Cn = np.conj(w)[None, :, None]*Phi
        sB = np.einsum('nmz,nz->z', Cn, A)
        sA = np.einsum('nmz->nz', np.conj(Cn))  # sum_m w_m e^{-iPhi}
        # midpoint (RK2) local update of the 2-way coupling
        dB1 = -1j*p*sB; dA1 = -1j*p[None, :]*sA*B[None, :]
        Bm = B + 0.5*dt*dB1; Am = A + 0.5*dt*dA1
        dB2 = -1j*p*np.einsum('nmz,nz->z', Cn, Am); dA2 = -1j*p[None, :]*sA*Bm[None, :]
        B = B + dt*dB2; A = A + dt*dA2
        A = np.roll(A, 1, axis=1); A[:, 0] = 0      # advect signal +z
    return np.sum(np.abs(B)**2)*dz/norm_in
if __name__ == '__main__':
    out = {}
    N = 2; tau_s = 3.0; tau_w = 1.0
    w = np.array([1, 1])/np.sqrt(2)                   # pump comb targets mode (a0+a1)/sqrt2 (local model)
    for spatial in [False, True]:
        best = None
        for theta in [1.2, np.pi/2, 2.0]:
            e_t = run(N, w, np.array([1, 1])/np.sqrt(2), tau_s, tau_w, theta, spatial)
            e_o = run(N, w, np.array([1, -1])/np.sqrt(2), tau_s, tau_w, theta, spatial)
            if best is None or e_t > best[1]: best = (theta, e_t, e_o)
        out['spatial' if spatial else 'local'] = dict(theta=best[0], eta_target=best[1], eta_orth=best[2], sel=best[1]/(best[1]+best[2]))
        print(out, flush=True)
    json.dump(out, open(os.path.join(os.path.dirname(__file__), '..', 'data_spatial_check.json'), 'w'), indent=1)
