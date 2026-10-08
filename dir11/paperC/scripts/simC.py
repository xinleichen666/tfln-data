"""Concept paper C: TFLN phononic frequency-bin buffer / mode gate. All results are simulations."""
import numpy as np, json, csv, os
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from params import *
OUT = os.path.dirname(os.path.abspath(__file__)) + '/..'
plt.rcParams.update({'font.size': 9, 'figure.dpi': 200, 'axes.linewidth': 0.8, 'font.family': 'DejaVu Sans'})
def save(fig, name):
    fig.tight_layout(); fig.savefig(f'{OUT}/fig/{name}.png'); fig.savefig(f'{OUT}/fig/{name}.pdf'); plt.close(fig)
def wcsv(name, header, rows):
    with open(f'{OUT}/data/{name}.csv', 'w', newline='') as f:
        w = csv.writer(f); w.writerow(header); w.writerows(rows)
res = {}
# ---------- Fig 1: delay-line loss & footprint per unit delay ----------
tau = np.logspace(-9, -5, 200)  # s
lines = {  # name: dB per second, metres per second of delay
 'TFLN optical, 1.3 dB/m (record ring)': (loss_TFLN_ring*v_o, v_o),
 'TFLN optical, 0.2 dB/m (material limit)': (loss_TFLN_material*v_o, v_o),
 'SMF fibre, 0.2 dB/km (off-chip)': (loss_SMF*c/n_g_SMF, c/n_g_SMF),
 'LN phonon RT, 4.0 dB/mm (Mayor 2021)': (loss_ac_RT*1e3*v_ac, v_ac),
 'LN phonon 4 K, 0.7 dB/mm (Mayor 2021)': (loss_ac_4K*1e3*v_ac, v_ac),
 'TFLN SBS phonon RT, 11.9 MHz linewidth': (10/np.log(10)*Gam_SBS_RT, v_ac),
}
rows = []; res['loss_dB_per_us'] = {}; res['length_m_per_us'] = {}
fig, ax = plt.subplots(1, 2, figsize=(7.0, 2.8))
for k, (dBs, vs) in lines.items():
    ax[0].loglog(tau*1e6, np.maximum(dBs*tau, 1e-4), label=k); ax[1].loglog(tau*1e6, vs*tau, label=k)
    res['loss_dB_per_us'][k] = dBs*1e-6; res['length_m_per_us'][k] = vs*1e-6
    rows.append([k, dBs*1e-6, vs*1e-6])
wcsv('fig1_delay_line_comparison', ['platform', 'loss_dB_per_us', 'length_m_per_us'], rows)
ax[0].axhline(3, ls=':', c='k', lw=0.7); ax[0].set_ylim(1e-3, 1e3)
ax[0].set_xlabel('Delay (µs)'); ax[0].set_ylabel('Propagation loss (dB)'); ax[0].set_title('(a)', loc='left')
ax[1].axhline(1e-2, ls=':', c='k', lw=0.7); ax[1].text(1.2e-3, 1.3e-2, '1 cm chip', fontsize=7)
ax[1].set_xlabel('Delay (µs)'); ax[1].set_ylabel('Physical length (m)'); ax[1].set_title('(b)', loc='left')
ax[0].legend(fontsize=5.5, frameon=False); save(fig, 'fig1_delay_lines')
# ---------- Fig 2: pump power for full photon->phonon swap vs bandwidth ----------
# coupled-mode: g^2 = G_B*Gamma*v_o*P/4 ; counter-propagating overlap time tau_p/2 ; theta = g*tau_p/2 = pi/2
def P_pi(tau_p, GBG=GBGam):
    return 4*np.pi**2/(GBG*v_o*tau_p**2)
B = np.logspace(6, 10, 200); tau_p = 1/B
cases = {'TFLN x-cut, G_B=26.1 /W/m, 11.9 MHz (measured pair)': GBGam,
         'chalcogenide G_B=750 /W/m (Zhu-Stiller input), same linewidth (assumed)': 750*Gam_SBS_RT}
fig, ax = plt.subplots(figsize=(3.4, 2.8)); rows = []
for k, gg in cases.items():
    ax.loglog(B/1e6, P_pi(tau_p, gg), label=k)
for Bi in [1e7, 1e8, 1e9]:
    rows.append([Bi, P_pi(1/Bi), P_pi(1/Bi, 750*Gam_SBS_RT)])
wcsv('fig2_pump_power', ['bandwidth_Hz', 'P_pi_TFLN_W', 'P_pi_chalc_W'], rows)
res['P_pi_W_TFLN'] = {f'{Bi/1e6:.0f}MHz': P_pi(1/Bi) for Bi in [1e7, 1e8, 1e9]}
ax.axhline(1, ls=':', c='k', lw=0.7); ax.text(1.2, 1.3, '1 W on-chip peak', fontsize=7)
ax.set_xlabel('Photon bandwidth 1/τ_p (MHz)'); ax.set_ylabel('Peak pump power for π-swap (W)')
ax.legend(fontsize=5.5, frameon=False); save(fig, 'fig2_pump_power')
# ---------- Fig 3: storage efficiency & noise-limited qubit fidelity ----------
tau_w = 10e-9   # 10 ns write pulse (100 MHz class) -> P_pi from above
scen = {'RT, SBS phonon (Γ/2π=11.9 MHz), n_th=%.0f' % nth(f_SBS, 295): (Gam_SBS_RT, nth(f_SBS, 295)),
        '4 K, Γ from 0.7 dB/mm, n_th=%.1f' % nth(f_SBS, 4): (gam_from_dBmm(loss_ac_4K), nth(f_SBS, 4)),
        '20 mK, Γ from 0.7 dB/mm (assumed), n_th≈0': (gam_from_dBmm(loss_ac_4K), nth(f_SBS, 0.02))}
ts = np.logspace(-9, -5, 300)
fig, ax = plt.subplots(1, 2, figsize=(7.0, 2.8)); rows = []; res['storage'] = {}
for k, (G, n) in scen.items():
    eta = np.exp(-G*(ts + tau_w))           # write & read pi-swaps assumed ideal otherwise
    nadd = n*(1 - np.exp(-G*(ts + tau_w)))  # reheating of the stored acoustic mode
    F = (eta + nadd/2)/(eta + nadd)
    ax[0].semilogx(ts*1e6, eta, label=k); ax[1].semilogx(ts*1e6, F, label=k)
    i = np.argmin(abs(ts - 1e-6)); t_half = np.log(2)/G - tau_w
    Fi = np.where(F > 0.99)[0]; t99 = ts[Fi[-1]] if len(Fi) and Fi[0] == 0 else 0
    res['storage'][k] = dict(Gamma_over_2pi_Hz=G/2/np.pi, n_th=n, t_half_s=t_half, DBP_half=t_half/tau_w,
                             eta_at_1us=eta[i], F_at_1us=F[i], t_F99_s=float(t99))
    for t, e, f_ in zip(ts[::10], eta[::10], F[::10]): rows.append([k, t, e, f_])
wcsv('fig3_storage', ['scenario', 'storage_time_s', 'efficiency', 'qubit_fidelity'], rows)
ax[1].axhline(2/3, ls=':', c='k', lw=0.7); ax[1].text(1.2e-3, 0.68, 'classical 2/3', fontsize=7)
ax[0].set_xlabel('Storage time (µs)'); ax[0].set_ylabel('Retrieval efficiency'); ax[0].set_title('(a)', loc='left')
ax[1].set_xlabel('Storage time (µs)'); ax[1].set_ylabel('Noise-limited qubit fidelity'); ax[1].set_title('(b)', loc='left')
ax[0].legend(fontsize=5.5, frameon=False); save(fig, 'fig3_storage')
# ---------- Fig 4: multimode frequency-bin mode-selective write (pump comb) ----------
eps = 2*n_g_TFLN*v_ac/c      # dOmega_B/domega (backward SBS), uses n_g as proxy for n_eff (ASSUMPTION)
def write_matrix(N, Delta, Tw, w, G=0.0, steps=None):
    """rotating-frame ODE for N signal bins + 1 phonon; pump comb weights w (sum|w|^2=1), theta=pi/2"""
    g = (np.pi/2)/Tw
    n = np.arange(N) - (N-1)/2
    det = (n[:, None] - n[None, :])*Delta + n[:, None]*eps*Delta   # delta_{n m}
    steps = steps or int(max(2000, 30*(N-1)*Delta*Tw/(2*np.pi)))
    dt = Tw/steps; U = np.eye(N+1, dtype=complex)
    def M(t):
        Gnm = g*w[None, :]*np.exp(1j*det*t); s = Gnm.sum(1)   # coupling of b to a_n
        A = np.zeros((N+1, N+1), complex); A[:N, N] = -1j*np.conj(s); A[N, :N] = -1j*s; A[N, N] = -G/2
        return A
    t = 0.0
    for _ in range(steps):   # RK4 on the propagator
        k1 = M(t)@U; k2 = M(t+dt/2)@(U+dt/2*k1); k3 = M(t+dt/2)@(U+dt/2*k2); k4 = M(t+dt)@(U+dt*k3)
        U = U + dt/6*(k1+2*k2+2*k3+k4); t += dt
    return U
def dft(N): j = np.arange(N); return np.exp(2j*np.pi*np.outer(j, j)/N)/np.sqrt(N)
def selectivity(N, Delta, Tw):
    D = dft(N); E = np.zeros((N, N))
    for k in range(N):
        w = np.conj(D[:, k])      # pump comb shaped to target DFT mode k
        U = write_matrix(N, Delta, Tw, w); t = U[N, :N]
        E[k] = abs(D.T @ t)**2    # efficiency for each DFT input mode j
    eta = np.diag(E); sel = eta/E.sum(1)
    return E, eta.mean(), sel.mean()
Delta = 2*np.pi*10e9   # 10 GHz bin spacing (ASSUMPTION; within EO-comb range)
rows = []; res['multimode'] = {}
DT = np.array([1, 2, 4, 8, 16, 32, 64])   # Delta*Tw/(2 pi) = number of beat periods in write window
fig, ax = plt.subplots(1, 2, figsize=(7.0, 2.8))
for N in [2, 4, 8]:
    S = []; H = []
    for d in DT:
        Tw = d/(Delta/2/np.pi); E, eta, sel = selectivity(N, Delta, Tw); S.append(sel); H.append(eta)
        rows.append([N, d, Tw, eta, sel])
    ax[0].semilogx(DT, 1-np.array(S), 'o-', ms=3, label=f'N={N} selectivity'); ax[0].semilogx(DT, 1-np.array(H), 's--', ms=3, label=f'N={N} efficiency')
    res['multimode'][f'N{N}'] = dict(zip([int(x) for x in DT], [dict(eta=h_, sel=s_) for h_, s_ in zip(H, S)]))
wcsv('fig4_multimode', ['N_bins', 'Delta_Tw_over_2pi', 'Tw_s', 'mean_target_efficiency', 'mean_selectivity'], rows)
ax[0].set_yscale('log'); ax[0].set_xlabel('Δ·τ_w/2π (bin-spacing beats in write window)'); ax[0].set_ylabel('1 − metric'); ax[0].set_title('(a)', loc='left')
ax[0].legend(fontsize=5.5, frameon=False)
E, eta, sel = selectivity(8, Delta, 1e-9)    # 1 ns write at 10 GHz spacing
im = ax[1].imshow(E, cmap='viridis', vmin=0, vmax=1); plt.colorbar(im, ax=ax[1], fraction=0.046)
ax[1].set_xlabel('input DFT mode j'); ax[1].set_ylabel('target (pump-comb) mode k'); ax[1].set_title('(b) N=8, τ_w=1 ns', loc='left')
res['multimode']['N8_1ns_matrix_eta_sel'] = dict(eta=eta, sel=sel)
np.savetxt(f'{OUT}/data/fig4b_N8_matrix.csv', E, delimiter=',', fmt='%.6f')
save(fig, 'fig4_multimode')
res['eps_dOmegaB_domega'] = eps; res['P_pi_tau_w_10ns_W'] = P_pi(tau_w); res['P_pi_1ns_W'] = P_pi(1e-9)
json.dump(res, open(f'{OUT}/data/key_results_C.json', 'w'), indent=1, default=float)
print(json.dumps(res, indent=1, default=float))
