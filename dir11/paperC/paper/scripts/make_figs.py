"""Publication figures for paper C. Re-plots the source data (../../data/*.csv) and re-evaluates the
same closed-form models used in ../../scripts/simC.py (no new physics, no fitted numbers).
Also evaluates the derived interaction-length estimate L_int ~ v_o*tau and the backward-SBS
wave-vector mismatch Delta q = 2*Delta*n_g/c (Sec. V of the manuscript)."""
import sys, os, csv, json
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); SRC = os.path.join(HERE, '../..')
sys.path.insert(0, os.path.join(SRC, 'scripts'))
from params import *
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
plt.rcParams.update({'font.size': 8, 'axes.linewidth': 0.7, 'font.family': 'DejaVu Sans',
                     'xtick.direction': 'in', 'ytick.direction': 'in', 'legend.fontsize': 6.5,
                     'axes.labelsize': 8, 'lines.linewidth': 1.3})
FIG = os.path.join(HERE, '../figures')
def save(fig, name):
    fig.savefig(f'{FIG}/{name}.pdf', bbox_inches='tight'); fig.savefig(f'{FIG}/{name}.png', dpi=250, bbox_inches='tight'); plt.close(fig)
def rcsv(name):
    with open(os.path.join(SRC, 'data', name)) as f: return list(csv.DictReader(f))
out = {}
# ---------------- Fig 2: delay-line figures of merit ----------------
d = rcsv('fig1_delay_line_comparison.csv')
labels = ['TFLN optical\n1.3 dB/m (record)', 'TFLN optical\n0.2 dB/m (material)', 'SMF fiber\n0.2 dB/km (off-chip)',
          'LN phonon RT\n4.0 dB/mm', 'LN phonon 4 K\n0.7 dB/mm', 'TFLN SBS phonon\nRT (11.9 MHz)']
loss = np.array([float(r['loss_dB_per_us']) for r in d]); length = np.array([float(r['length_m_per_us']) for r in d])
cols = ['#4c72b0', '#8fa9d6', '#7f7f7f', '#dd8452', '#c44e52', '#e6a5a5']
fig, ax = plt.subplots(1, 2, figsize=(7.0, 2.5))
for a, y, lab in [(ax[0], loss, 'Loss per µs of delay (dB/µs)'), (ax[1], length, 'Length per µs of delay (m)')]:
    a.barh(range(6), y, color=cols); a.set_xscale('log'); a.set_yticks(range(6)); a.set_xlabel(lab); a.invert_yaxis()
    for i, v in enumerate(y):
        a.text(v*1.25, i, (f'{v:.3g}' if v >= 0.01 else f'{v:.2g}'), va='center', fontsize=6.5)
ax[0].set_yticklabels(labels, fontsize=6.5); ax[1].set_yticklabels([])
ax[0].set_xlim(1e-2, 3e3); ax[1].set_xlim(1e-3, 3e4)
ax[0].text(-0.02, 1.04, '(a)', transform=ax[0].transAxes, fontweight='bold'); ax[1].text(-0.02, 1.04, '(b)', transform=ax[1].transAxes, fontweight='bold')
fig.tight_layout(); save(fig, 'fig2_delay_fom')
out['ratios'] = dict(ring_over_4K=loss[0]/loss[4], material_over_4K=loss[1]/loss[4], fiber_better_than_4K=loss[4]/loss[2],
                     fiber_length_over_phonon=length[2]/length[4], TFLN_length_over_phonon=length[0]/length[4])
# ---------------- Fig 3: pump power and interaction length vs bandwidth ----------------
GBGam = G_B*Gam_SBS_RT
def P_pi(tau, GBG=GBGam): return 4*np.pi**2/(GBG*v_o*tau**2)
B = np.logspace(6, 10, 300); tau = 1/B
fig, ax = plt.subplots(1, 2, figsize=(7.0, 2.5))
ax[0].loglog(B/1e6, P_pi(tau), c='#c44e52', label=r'TFLN x-cut, $G_B$=26.1 W$^{-1}$m$^{-1}$, 11.9 MHz')
ax[0].loglog(B/1e6, P_pi(tau, 750*Gam_SBS_RT), c='#4c72b0', ls='--', label=r'$G_B$=750 W$^{-1}$m$^{-1}$, same linewidth (assumed)')
for Bi in [1e7, 1e8]:
    ax[0].plot(Bi/1e6, P_pi(1/Bi), 'o', c='#c44e52', ms=4); ax[0].annotate(f'{P_pi(1/Bi)*1e3:.0f} mW' if Bi < 5e7 else f'{P_pi(1/Bi):.2f} W', (Bi/1e6, P_pi(1/Bi)), xytext=(-34, 6), textcoords='offset points', fontsize=6.5)
ax[0].axhline(1, ls=':', c='k', lw=0.7); ax[0].set_ylim(1e-5, 1e5)
ax[0].set_xlabel(r'Photon bandwidth $1/\tau$ (MHz)'); ax[0].set_ylabel(r'Peak pump power $P_\pi$ (W)'); ax[0].legend(frameon=False, loc='upper left')
Lmin = v_o*tau/2; Lsym = v_o*tau
ax[1].loglog(B/1e6, Lsym, c='k', label=r'$v_o(\tau_s+\tau_w)/2$, $\tau_s=\tau_w=\tau$')
ax[1].loglog(B/1e6, Lmin, c='k', ls='--', label=r'$v_o\tau_s/2$ (short write pulse)')
ax[1].axhline(0.30, c='#8fa9d6', ls=':', lw=1); ax[1].text(1.15, 0.34, '30 cm TFLN delay line (demonstrated)', fontsize=6.3, color='#4c72b0')
ax[1].axhline(v_ac*1e-6, c='#c44e52', ls=':', lw=1); ax[1].text(1.15, 3.6e-3, 'acoustic travel per µs (3.1 mm)', fontsize=6.3, color='#c44e52')
ax[1].set_ylim(1e-3, 1e3); ax[1].set_xlabel(r'Photon bandwidth $1/\tau$ (MHz)'); ax[1].set_ylabel('Optical interaction length (m)'); ax[1].legend(frameon=False, loc='upper right')
for a, l in zip(ax, 'ab'): a.text(-0.02, 1.04, f'({l})', transform=a.transAxes, fontweight='bold')
fig.tight_layout(); save(fig, 'fig3_power_length')
out['Lint_m'] = {f'{Bi/1e6:.0f}MHz': dict(sym=v_o/Bi, short_write=v_o/Bi/2) for Bi in [1e7, 1e8, 1e9]}
out['P_pi_W'] = {f'{Bi/1e6:.0f}MHz': P_pi(1/Bi) for Bi in [1e7, 1e8, 1e9]}
# ---------------- Fig 4: storage efficiency and noise-limited fidelity ----------------
tau_w = 10e-9; ts = np.logspace(-9, -5, 2000)
scen = [('RT, SBS phonon ($\\Gamma/2\\pi$=11.9 MHz), $n_{th}$=768', Gam_SBS_RT, nth(f_SBS, 295), '#7f7f7f', '-'),
        ('4 K, $\\Gamma$ from 0.7 dB/mm, $n_{th}$=9.9', gam_from_dBmm(loss_ac_4K), nth(f_SBS, 4), '#c44e52', '-'),
        ('20 mK, 4 K loss assumed, $n_{th}\\approx0$', gam_from_dBmm(loss_ac_4K), nth(f_SBS, 0.02), '#4c72b0', '--')]
fig, ax = plt.subplots(1, 2, figsize=(7.0, 2.5)); out['storage'] = {}
for lab, G, n, c_, ls in scen:
    eta = np.exp(-G*(ts+tau_w)); nadd = n*(1-np.exp(-G*(ts+tau_w))); F = (eta+nadd/2)/(eta+nadd)
    ax[0].semilogx(ts*1e6, eta, c=c_, ls=ls, label=lab); ax[1].semilogx(ts*1e6, F, c=c_, ls=ls, label=lab)
    key = lab.split(',')[0]
    t90 = ts[F > 0.9].max() if (F > 0.9).any() else 0.; t23 = ts[F > 2/3].max() if (F > 2/3).any() else 0.
    out['storage'][key] = dict(Gamma_over_2pi_Hz=G/2/np.pi, nth=n, F_first=F[0], t_F090_s=t90, t_F2over3_s=t23,
                               F_10us=F[-1], eta_1us=float(np.exp(-G*(1e-6+tau_w))), t_half_s=np.log(2)/G - tau_w)
ax[0].set_ylabel(r'Storage efficiency $\eta$'); ax[1].set_ylabel('Noise-limited qubit fidelity $F$')
ax[1].axhline(0.9, c='k', ls=':', lw=0.6); ax[1].axhline(2/3, c='k', ls='-.', lw=0.6); ax[1].text(1.2e-3, 0.68, 'classical 2/3', fontsize=6.3)
ax[1].axhline(0.99, c='#4c72b0', ls=':', lw=0.6)
ax[1].plot(0.05, 0.79, 'k*', ms=6); ax[1].annotate('Zhu et al. [chalcogenide,\n1 K, 50 ns, exp.]', (0.05, 0.79), xytext=(0.08, 0.80), fontsize=5.8)
for a, l in zip(ax, 'ab'):
    a.set_xlabel('Storage time (µs)'); a.set_xlim(1e-3, 10); a.text(-0.02, 1.04, f'({l})', transform=a.transAxes, fontweight='bold')
ax[0].legend(frameon=False, loc='lower left', fontsize=6); ax[1].set_ylim(0.45, 1.01)
fig.tight_layout(); save(fig, 'fig4_storage')
# ---------------- Fig 5: local (single-phonon-mode) multimode model ----------------
d = rcsv('fig4_multimode.csv'); M = np.loadtxt(os.path.join(SRC, 'data/fig4b_N8_matrix.csv'), delimiter=',')
fig, ax = plt.subplots(1, 2, figsize=(7.0, 2.6), gridspec_kw=dict(width_ratios=[1.3, 1]))
for N, c_ in [(2, '#4c72b0'), (4, '#dd8452'), (8, '#c44e52')]:
    x = [float(r['Delta_Tw_over_2pi']) for r in d if int(r['N_bins']) == N]; y = [1-float(r['mean_selectivity']) for r in d if int(r['N_bins']) == N]
    ax[0].loglog(x, y, 'o-', c=c_, ms=3, label=f'N = {N}')
ax[0].set_xlabel(r'$\Delta\tau_w/2\pi$'); ax[0].set_ylabel(r'$1-$selectivity (local model)'); ax[0].legend(frameon=False)
im = ax[1].imshow(np.log10(np.maximum(M, 1e-6)), cmap='magma', vmin=-6, vmax=0)
ax[1].set_xlabel('stored-mode index j'); ax[1].set_ylabel('input DFT mode k'); cb = fig.colorbar(im, ax=ax[1], fraction=0.046); cb.set_label(r'$\log_{10}E_{kj}$')

for a, l in zip(ax, 'ab'): a.text(-0.02, 1.04, f'({l})', transform=a.transAxes, fontweight='bold')
fig.tight_layout(); save(fig, 'fig5_local_multimode')
# ---------------- wave-vector mismatch numbers ----------------
Delta = 2*np.pi*10e9; dq = 2*Delta*n_g_TFLN/c
out['phase_mismatch'] = dict(dq_per_bin_rad_per_m=dq, spatial_period_m=2*np.pi/dq,
                             dqL_for_L_vo_1ns=dq*v_o*1e-9, dqL_for_L_vo_10ns=dq*v_o*10e-9,
                             report_estimate_dk_l_with_l_vac_1ns=dq*v_ac*1e-9)
json.dump(out, open(os.path.join(HERE, '../derived_numbers.json'), 'w'), indent=1, default=float)
print(json.dumps(out, indent=1, default=float))
# ---------------- Fig 6: space-time check of the mode-selective write ----------------
S = json.load(open(os.path.join(HERE, '../data_spatial_scan.json')))
sc_ = S['scan']; x = np.array([max(r['dqL'], 0.01) for r in sc_]); 
et = np.array([r['eta_target'] for r in sc_]); eo = np.array([r['eta_orth'] for r in sc_]); se = np.array([r['sel'] for r in sc_])
fig, ax = plt.subplots(1, 2, figsize=(7.0, 2.5))
ax[0].semilogx(x[1:], et[1:], 'o-', c='#c44e52', ms=3.5, label=r'$\eta$, target $(a_0+a_1)/\sqrt{2}$')
ax[0].semilogx(x[1:], eo[1:], 's--', c='#4c72b0', ms=3.5, label=r'$\eta$, orthogonal $(a_0-a_1)/\sqrt{2}$')
ax[0].plot([x[0]], [et[0]], 'o', c='#c44e52', mfc='w', ms=5); ax[0].plot([x[0]], [eo[0]], 's', c='#4c72b0', mfc='w', ms=5)
ax[0].annotate('local model ($\\kappa$=0)', (x[0]*1.3, 0.9), fontsize=6.3, ha='left', va='center')
ax[0].axvline(S['dq_rad_per_m']*S['L_collision_m'], c='k', ls=':', lw=0.8); ax[0].text(230, 0.97, 'backward SBS', fontsize=6.3, ha='right', va='top')
ax[0].set_xlabel(r'wave-vector mismatch $\kappa\,\Delta q\,L_c$ (rad)'); ax[0].set_ylabel('stored fraction'); ax[0].legend(frameon=False, fontsize=6, loc='lower right', bbox_to_anchor=(0.97, 0.0))
ax[1].semilogx(x[1:], se[1:], 'o-', c='k', ms=3.5); ax[1].plot([x[0]], [se[0]], 'o', c='k', mfc='w', ms=5)
ax[1].axhline(0.5, c='gray', ls=':', lw=0.8); ax[1].axvline(S['dq_rad_per_m']*S['L_collision_m'], c='k', ls=':', lw=0.8)
ax[1].set_xlabel(r'wave-vector mismatch $\kappa\,\Delta q\,L_c$ (rad)'); ax[1].set_ylabel('selectivity $\\eta_t/(\\eta_t+\\eta_o)$'); ax[1].set_ylim(0, 1.05)
for a, l in zip(ax, 'ab'): a.text(-0.02, 1.04, f'({l})', transform=a.transAxes, fontweight='bold')
fig.tight_layout(); save(fig, 'fig6_spatial_check')
