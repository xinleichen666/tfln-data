"""Tape-out readiness sims for Paper B: tunable MZI coupler (heater ON/OFF),
partial-coverage xi, dual IL columns, nth*C0 bound, fab gates.
core.py untouched. Does not import realistic.py (that module has side effects).
"""
from __future__ import annotations
import json, csv, os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from core import tp, F, WM, MU, G, KI, NG, P_from_dw

plt.rcParams.update({'font.size': 8, 'font.family': 'serif',
                     'mathtext.fontset': 'dejavuserif', 'axes.linewidth': 0.6,
                     'lines.linewidth': 1.1})

DW = json.load(open('data/results_B.json'))['optimum']['ao']['dw_GHz'] * tp * 1e9
SPEC = json.load(open('data/results_B.json'))['spectrum_dB']['ao']
THERM = json.load(open('data/results_B.json'))['thermal']

def runv(mu, g, ki, Delta, dr, wm=WM, dw=DW, T=40e-9):
    mu, g, ki, Delta, dr = np.broadcast_arrays(
        *(np.atleast_1d(np.asarray(v, float)) for v in (mu, g, ki, Delta, dr)))
    W = wm
    dt = 1 / (W / tp) / 80
    n = int(T / dt)
    d0 = mu - Delta
    sg = np.sqrt(g)
    a1 = np.zeros(mu.shape, complex)
    a2 = a1.copy()
    tt = np.arange(n) * dt
    msk = tt > T - 20e-9
    Q = range(-3, 4)
    acc = {q: 0 for q in Q}

    def f(t, a1, a2):
        m = dw * np.cos(W * t)
        return ((-1j * (d0 + m) - (g + ki) / 2) * a1 - 1j * mu * a2 - sg,
                (-1j * (d0 + dr) - ki / 2) * a2 - 1j * mu * a1)

    t = 0.0
    for i in range(n):
        k1 = f(t, a1, a2)
        k2 = f(t + dt / 2, a1 + dt / 2 * k1[0], a2 + dt / 2 * k1[1])
        k3 = f(t + dt / 2, a1 + dt / 2 * k2[0], a2 + dt / 2 * k2[1])
        k4 = f(t + dt, a1 + dt * k3[0], a2 + dt * k3[1])
        a1 = a1 + dt / 6 * (k1[0] + 2 * k2[0] + 2 * k3[0] + k4[0])
        a2 = a2 + dt / 6 * (k1[1] + 2 * k2[1] + 2 * k3[1] + k4[1])
        t += dt
        if msk[i]:
            o = 1 + sg * a1
            for q in Q:
                acc[q] = acc[q] + o * np.exp(1j * q * W * tt[i])
    N = msk.sum()
    p = {q: abs(acc[q] / N) ** 2 for q in Q}
    tot = sum(p.values())
    ps = np.maximum(p[1], p[-1])
    # also return spur powers relative to shift for gate check on median sample path
    return ps / tot, -10 * np.log10(tot), ps, {q: p[q] for q in Q}, tot


MHz = tp * 1e6
f0 = 193.4e12
hbar = 1.054571817e-34
kB = 1.380649e-23

# ---------------- parameters ----------------
P = dict(
    eta_IDT_main=0.10,
    eta_IDT_ref=0.50,
    Qa_nom=2000,
    Qa_upper=3600,
    Qa_cons=1570,
    dndT=3.34e-5,
    alpha=1.54e-5,
    n_eff=2.14,
    ki_extra_frac=1.0,          # column B: +100% vs Shao Qi
    sigT_lock_mK=5.0,
    sig_gap_nm=5.0,
    gap_decay_nm=150.0,
    retune_MHz=1.0,
    facet_dB=1.5,
    Qi_spread=(0.7, 1.3),
    # Tunable MZI coupler (Zhang et al. Nat. Photonics 2019 architecture; TO heater)
    # Design headroom: fabricate mu_max so nominal 2*mu_max > Omega (r0>1), then
    # heater phase phi in [0, pi/2] sets mu = mu_max * sin(phi).
    coupler_r0=1.20,            # ASSUMED design: 20% coupling headroom at nominal gap
    P_pi_mW=25.0,               # ASSUMED: TFLN TO P_pi for coupler MZI arm.
                                # Order of magnitude from Liu et al. Opt. Lett. 45, 6318 (2020):
                                # 14.9 mW / FSR with trenches (~P_2pi on a ring); geometric factor for
                                # a short coupler MZI arm is ASSUMED → we take 25 mW as P_pi.
    xtalk_K_per_W=0.5,          # ASSUMED: differential two-ring heating from coupler heater (K/W)
    g0_Hz=1.1e3,                # Shao 2019 Table S2: g0/2pi = 1.1 kHz
    gamma_e_over_gamma=0.15,    # Shao 2019 modeling
)

dfdT = f0 * (P['dndT'] + P['n_eff'] * P['alpha']) / NG  # Hz/K
dfdT_TO = f0 * P['dndT'] / NG


def pct(v):
    return [float(np.percentile(v, q)) for q in (10, 50, 90)]


def summarize(eta, IL, ea, fac, extra=None):
    out = dict(
        eta_shift_p10_50_90=pct(eta),
        IL_dB_p10_50_90=pct(IL),
        eta_abs_onchip_p10_50_90=pct(ea),
        eta_abs_fiber_to_fiber_p10_50_90=pct(ea * fac),
        frac_eta_ge_095=float(np.mean(eta >= 0.95)),
        frac_eta_ge_090=float(np.mean(eta >= 0.90)),
        N=int(len(eta)),
    )
    if extra:
        out.update(extra)
    return out


def sample(N, rng, p, heater_on=True, ki_extra_frac=None):
    """Draw gaps first; if heater_on, minimize |2mu-Omega| within MZI heater range."""
    kef = p['ki_extra_frac'] if ki_extra_frac is None else ki_extra_frac
    ki = KI * (1 + kef) * rng.uniform(*p['Qi_spread'], N)
    dgap = rng.normal(0, p['sig_gap_nm'], N)
    dgap_b = rng.normal(0, p['sig_gap_nm'], N)
    mu_max = MU * p['coupler_r0'] * np.exp(-dgap / p['gap_decay_nm'])
    g = G * np.exp(-dgap_b / p['gap_decay_nm'])
    eps_raw = 2 * mu_max - WM  # at full-on coupler (phi=pi/2), before heater trim

    if heater_on:
        # mu = mu_max * sin(phi), phi in [0, pi/2] → 2mu in [0, 2 mu_max]
        # choose phi to hit WM/2 when possible
        target = MU
        ratio = np.clip(target / np.maximum(mu_max, 1e-30), 0.0, 1.0)
        # if mu_max < MU, best is phi=pi/2 (full on)
        phi = np.arcsin(ratio)
        mu = mu_max * np.sin(phi)
        P_heater_W = (phi / (np.pi / 2.0)) * (0.5 * p['P_pi_mW'] * 1e-3)  # pi/2 phase = half P_pi
        # heater-induced differential ring temperature → delta_r; common half into Delta bias
        dT_diff = p['xtalk_K_per_W'] * P_heater_W
        dr_heat = dT_diff * dfdT * tp
        Delta_heat = 0.5 * dT_diff * dfdT * tp  # ASSUMED: half of differential also as common offset
        can_reach = mu_max >= MU - 1e-12
    else:
        # fixed coupler at design bias sin(phi0)=1/r0 so nominal mu=MU when dgap=0
        phi0 = np.arcsin(1.0 / p['coupler_r0'])
        mu = mu_max * np.sin(phi0)  # = MU * exp(-dgap/L)
        P_heater_W = np.zeros(N)
        dr_heat = np.zeros(N)
        Delta_heat = np.zeros(N)
        phi = np.full(N, phi0)
        can_reach = np.zeros(N, dtype=bool)

    eps = 2 * mu - WM
    # RF retune residual
    eps_res = np.sign(eps) * np.maximum(np.abs(eps) - p['retune_MHz'] * MHz, 0.0)
    mu_eff = (WM + eps_res) / 2.0

    sT = p['sigT_lock_mK'] * 1e-3
    Delta = rng.normal(0, sT, N) * dfdT * tp + Delta_heat
    dr = rng.normal(0, np.sqrt(2) * sT, N) * dfdT * tp + dr_heat
    return dict(
        mu=mu_eff, g=g, ki=ki, Delta=Delta, dr=dr,
        mu_max=mu_max, mu_after_heater=mu, phi=phi,
        P_heater_mW=P_heater_W * 1e3,
        eps_raw_MHz=eps_raw / MHz, eps_after_heater_MHz=eps / MHz,
        eps_res_MHz=eps_res / MHz, can_reach=can_reach,
        dgap_nm=dgap,
    )


def mc(N, p, heater_on=True, ki_extra_frac=None, seed=1, batch=50):
    rng = np.random.default_rng(seed)
    s = sample(N, rng, p, heater_on=heater_on, ki_extra_frac=ki_extra_frac)
    eta = np.empty(N); IL = np.empty(N); ea = np.empty(N)
    for i0 in range(0, N, batch):
        i1 = min(i0 + batch, N)
        e, il, a, _, _ = runv(s['mu'][i0:i1], s['g'][i0:i1], s['ki'][i0:i1],
                             s['Delta'][i0:i1], s['dr'][i0:i1])
        eta[i0:i1] = e; IL[i0:i1] = il; ea[i0:i1] = a
    s.update(eta=eta, IL=IL, eta_abs=ea)
    return s


def main():
    os.makedirs('data', exist_ok=True)
    os.makedirs('fig', exist_ok=True)
    fac = 10 ** (-2 * P['facet_dB'] / 10)
    S = {}

    # Ideal / nominal
    e, il, ea, pmap, tot = runv(MU, G, KI, 0, 0)
    S['ideal'] = dict(eta_shift=float(e[0]), IL_dB=float(il[0]), eta_abs=float(ea[0]),
                      eta_abs_fiber_to_fiber=float(ea[0]) * fac)
    e2, il2, ea2, _, _ = runv(MU, G, KI * (1 + P['ki_extra_frac']), 0, 0)
    S['nominal_extra_loss'] = dict(eta_shift=float(e2[0]), IL_dB=float(il2[0]), eta_abs=float(ea2[0]))

    # Power & xi
    P50 = P_from_dw(DW, 'AO_Shao_IDT(50%)')
    P10 = P_from_dw(DW, 'AO_IDT_10%')
    # xi=1 corresponds to current calibration (Shao 2019 VpiL extrapolation, acoustic Q~2000 modeling)
    xi_list = [0.3, 0.5, 1.0, 2.0]
    S['xi_definition'] = dict(
        xi_equals_1='delta_omega/2pi = 21.3 GHz/V extrapolated from Shao 2019 straight-waveguide '
                    'VpiL=0.046 V cm (source-referred, incl ~50% IDT); acoustic Q used in that '
                    'modeling typically 2000 (measured up to 3600).',
        power_scales_as='1/xi^2 at fixed delta_omega',
    )
    S['power_uW'] = dict(
        IDT50_Qa2000_xi1=P50 * 1e6,
        IDT10_Qa2000_xi1=P10 * 1e6,
        IDT10_Qa1570_xi1=P10 * 2000 / 1570 * 1e6,
    )
    S['power_vs_xi_uW'] = {
        f'xi_{xi:g}': dict(
            IDT10_Qa2000=P10 / xi**2 * 1e6,
            IDT10_Qa1570=P10 * 2000 / 1570 / xi**2 * 1e6,
            IDT50_Qa2000=P50 / xi**2 * 1e6,
        ) for xi in xi_list
    }
    # Conservative lab source margin
    P_cons = P10 * 2000 / 1570 / (0.5 ** 2)  # xi=0.5, IDT 10%, Qm=1570
    S['conservative_power'] = dict(
        xi=0.5, eta_IDT=0.10, Qm=1570,
        P_RF_uW=P_cons * 1e6,
        P_dissipated_uW=(1 - 0.10) * P_cons * 1e6,
        Shao2019_heating_note='Shao 2019 Fig.5: optical resonance red-shift observed with '
                              'increasing microwave power at ~1–5 mW class; compare dissipated '
                              '(1-eta_IDT)*P_RF qualitatively to that scale.',
        Shao2019_ref_mW_range=[1.0, 5.0],
    )

    S['RF_FWHM_MHz'] = dict(Qa2000=F / 2000 / 1e6, Qa1570=F / 1570 / 1e6, Qa3600=F / 3600 / 1e6)
    S['dfdT_GHz_per_K'] = dict(thermo_optic_only=dfdT_TO / 1e9, with_expansion=dfdT / 1e9)
    S['params'] = {k: (list(v) if isinstance(v, tuple) else v) for k, v in P.items()}

    # Thermal phonon: drive jitter + spontaneous upper bound n_th * C0
    # C0 = 4 g0^2 / (kappa * gamma_m); kappa = gamma + kappa_i (loaded ring-1 rate)
    g0 = 2 * np.pi * P['g0_Hz']
    kappa = G + KI
    gamma_m = WM / 2000.0
    C0 = 4 * g0**2 / (kappa * gamma_m)
    n_th_300 = 1.0 / np.expm1(hbar * WM / (kB * 300.0))
    nth_C0 = n_th_300 * C0
    unfiltered_sideband_err = 1.0 - S['ideal']['eta_shift']
    S['thermal_phonon'] = dict(
        n_th_over_Ncoh_300K=THERM['cases']['300']['ratio_nth_over_Ncoh'],
        N_coh=THERM['N_coh'],
        n_th_300K=float(n_th_300),
        g0_Hz=P['g0_Hz'],
        kappa_over_2pi_Hz=float(kappa / tp),
        gamma_m_over_2pi_Hz=float(gamma_m / tp),
        C0=float(C0),
        C0_definition='C0 = 4 g0^2 / (kappa * gamma_m) with kappa=gamma+kappa_i (bus+intrinsic of ring 1), '
                      'gamma_m=Omega_m/Q_m (Q_m=2000), g0/2pi=1.1 kHz (Shao 2019 Table S2). '
                      'n_th*C0 is an upper bound on spontaneous scattering into the same acoustic mode '
                      'relative to a single intracavity photon; compare to unfiltered sideband error 1-eta_shift.',
        n_th_C0_300K=float(nth_C0),
        unfiltered_1_minus_eta=float(unfiltered_sideband_err),
        non_dominant=bool(nth_C0 < unfiltered_sideband_err),
    )

    # Spectrum spur gate
    spur_order = max([q for q in SPEC if int(q) != 1], key=lambda q: SPEC[q])
    # spectrum_dB values are power relative to input (negative dB); shifted is q=1
    # "largest spurious" among q!=1: least negative relative to shift, or highest absolute power among q!=1
    spur_abs = {int(q): SPEC[q] for q in SPEC if int(q) != 1}
    largest_spur_q = max(spur_abs, key=lambda q: spur_abs[q])  # least negative = largest power
    S['spectrum_gate'] = dict(
        spectrum_dB_vs_input=SPEC,
        largest_spurious_order=int(largest_spur_q),
        largest_spur_is_qm1=bool(largest_spur_q == -1),
        q_m1_rel_to_shift_dB=float(SPEC['-1'] - SPEC['1']),
    )

    N = 1000
    print('Running heater-OFF / ki as-is ...', flush=True)
    s_off_A = mc(N, P, heater_on=False, ki_extra_frac=0.0, seed=1)
    print('Running heater-OFF / ki×2 ...', flush=True)
    s_off_B = mc(N, P, heater_on=False, ki_extra_frac=1.0, seed=1)
    print('Running heater-ON / ki as-is ...', flush=True)
    s_on_A = mc(N, P, heater_on=True, ki_extra_frac=0.0, seed=1)
    print('Running heater-ON / ki×2 (main) ...', flush=True)
    s_on_B = mc(N, P, heater_on=True, ki_extra_frac=1.0, seed=1)

    def pack(s, label):
        extra = dict(
            eps_raw_MHz_std=float(np.std(s['eps_raw_MHz'])),
            eps_after_heater_MHz_p10_50_90=pct(s['eps_after_heater_MHz']),
            eps_res_MHz_p10_50_90=pct(s['eps_res_MHz']),
            frac_can_reach_Omega=float(np.mean(s['can_reach'])) if label.startswith('heater_ON') else None,
            frac_eps_beyond_retune=float(np.mean(s['eps_res_MHz'] != 0)),
            P_heater_mW_p10_50_90=pct(s['P_heater_mW']),
            coupler_r0=P['coupler_r0'],
        )
        return summarize(s['eta'], s['IL'], s['eta_abs'], fac, extra)

    S['MC_heater_OFF_IL_ShaoQi'] = pack(s_off_A, 'heater_OFF_A')  # comparison / old-style
    S['MC_heater_OFF_IL_extra'] = pack(s_off_B, 'heater_OFF_B')
    S['MC_heater_ON_IL_ShaoQi'] = pack(s_on_A, 'heater_ON_A')
    S['MC_heater_ON_IL_extra'] = pack(s_on_B, 'heater_ON_B')  # MAIN prediction (conservative IL)

    # Dual IL columns at heater ON (already in packs); also ideal-point columns
    S['IL_two_columns'] = dict(
        A_Shao2019_Qi_as_is=dict(
            note='Uses measured Qi of suspended racetrack with IDT (Shao 2019); no extra kappa_i.',
            ideal_IL_dB=S['ideal']['IL_dB'],
            heater_ON_IL_dB_p10_50_90=S['MC_heater_ON_IL_ShaoQi']['IL_dB_p10_50_90'],
            heater_ON_eta_abs_onchip_p10_50_90=S['MC_heater_ON_IL_ShaoQi']['eta_abs_onchip_p10_50_90'],
        ),
        B_extra_kappa_i_x2=dict(
            note='Adds assumed extra kappa_i x2 on top of Shao Qi (possible double-count).',
            ideal_IL_dB=S['nominal_extra_loss']['IL_dB'],
            heater_ON_IL_dB_p10_50_90=S['MC_heater_ON_IL_extra']['IL_dB_p10_50_90'],
            heater_ON_eta_abs_onchip_p10_50_90=S['MC_heater_ON_IL_extra']['eta_abs_onchip_p10_50_90'],
        ),
    )

    # Coverage of gap scatter by heater
    frac_reach = S['MC_heater_ON_IL_extra']['frac_can_reach_Omega']
    S['heater_coverage'] = dict(
        frac_samples_2mu_max_ge_Omega=frac_reach,
        covers_100MHz_gap_scatter=bool(frac_reach >= 0.90),
        design_note='coupler_r0=1.20 gives ~20% headroom; if frac_reach<0.9, redesign coupler '
                    '(do not fab fixed-gap dual-ring).',
    )

    # Tape-out gates
    main = S['MC_heater_ON_IL_extra']  # conservative loss + heater ON
    gate1 = main['frac_eta_ge_090'] >= 0.90
    P_diss_uW = S['conservative_power']['P_dissipated_uW']
    gate2 = P_diss_uW < 500.0  # far below 1–5 mW Shao heating class
    gate3 = S['spectrum_gate']['largest_spur_is_qm1']
    S['tapeout_gates'] = dict(
        gate1_yield=dict(
            require='heater ON + conservative loss (kappa_i x2) + 10% IDT: >=90% samples eta_shift>=90%',
            frac_eta_ge_090=main['frac_eta_ge_090'],
            eta_p10_50_90=main['eta_shift_p10_50_90'],
            pass_=gate1,
        ),
        gate2_power=dict(
            require='conservative RF (xi=0.5, Qm=1570, eta_IDT=10%) dissipated (1-eta_IDT)P_RF '
                    'still far below Shao 2019 thermal-redshift drive (~1–5 mW)',
            P_RF_uW=S['conservative_power']['P_RF_uW'],
            P_dissipated_uW=P_diss_uW,
            Shao_ref_mW=[1, 5],
            pass_=gate2,
        ),
        gate3_spur=dict(
            require='largest spurious sideband is still q=-1 (spectrometer-visible)',
            largest_spurious_order=S['spectrum_gate']['largest_spurious_order'],
            pass_=gate3,
        ),
        all_pass=bool(gate1 and gate2 and gate3 and S['heater_coverage']['covers_100MHz_gap_scatter']),
        fab_verdict=('PASS: tunable-coupler layout may proceed to fab under stated assumptions'
                     if (gate1 and gate2 and gate3 and S['heater_coverage']['covers_100MHz_gap_scatter'])
                     else 'FAIL: change coupler headroom/coverage length; do not fab fixed-gap layout'),
    )

    # Save MC samples (heater ON, conservative IL = main)
    with open('data/mc_samples_tapeout.csv', 'w', newline='') as fh:
        w = csv.writer(fh)
        w.writerow(['heater', 'IL_col', 'dgap_nm', 'mu_max', 'phi', 'P_heater_mW',
                    'eps_after_heater_MHz', 'eps_res_MHz', 'can_reach',
                    'ki', 'Delta_MHz', 'dr_MHz', 'eta_shift', 'IL_dB', 'eta_abs_onchip'])
        for tag, s, kef in [('OFF', s_off_B, 1.0), ('ON', s_on_B, 1.0),
                            ('ON', s_on_A, 0.0)]:
            for i in range(N):
                w.writerow([tag, 'extra' if kef else 'ShaoQi', s['dgap_nm'][i], s['mu_max'][i],
                            s['phi'][i], s['P_heater_mW'][i], s['eps_after_heater_MHz'][i],
                            s['eps_res_MHz'][i], int(s['can_reach'][i]),
                            s['ki'][i], s['Delta'][i] / MHz, s['dr'][i] / MHz,
                            s['eta'][i], s['IL'][i], s['eta_abs'][i]])

    json.dump(S, open('data/tapeout_summary.json', 'w'), indent=1)
    # keep realistic_summary.json pointing at heater-ON main for downstream
    legacy = dict(S)
    legacy['MC'] = S['MC_heater_ON_IL_extra']
    legacy['MC_heater_OFF_comparison'] = S['MC_heater_OFF_IL_extra']
    json.dump(legacy, open('data/realistic_summary.json', 'w'), indent=1)

    # Figure: heater ON vs OFF
    fig, ax = plt.subplots(1, 3, figsize=(7.2, 2.4))
    ax[0].hist(s_off_B['eta'], bins=40, alpha=0.55, color='0.5', label='heater OFF')
    ax[0].hist(s_on_B['eta'], bins=40, alpha=0.65, color='C0', label='heater ON')
    ax[0].axvline(S['ideal']['eta_shift'], color='k', ls='--', lw=0.8)
    ax[0].set_xlabel(r'$\eta_{\rm shift}$'); ax[0].set_ylabel('count'); ax[0].legend(fontsize=6)
    ax[1].hist(s_on_A['IL'], bins=30, alpha=0.65, color='C2', label='Shao $Q_i$')
    ax[1].hist(s_on_B['IL'], bins=30, alpha=0.65, color='C1', label=r'extra $\kappa_i\times2$')
    ax[1].set_xlabel('on-chip IL (dB)'); ax[1].legend(fontsize=6)
    xs = np.array(xi_list)
    ax[2].plot(xs, [S['power_vs_xi_uW'][f'xi_{x:g}']['IDT10_Qa1570'] for x in xs], 'o-', color='C3')
    ax[2].axhline(S['conservative_power']['P_RF_uW'], color='C3', ls='--', lw=0.7)
    ax[2].set_xlabel(r'partial-coverage $\xi$')
    ax[2].set_ylabel(r'conservative $P_{\rm RF}$ ($\mu$W)')
    ax[2].set_yscale('log')
    for a, lab in zip(ax, 'abc'):
        a.text(-0.28, 1.02, '(%s)' % lab, transform=a.transAxes, fontsize=8)
    fig.tight_layout()
    fig.savefig('fig/figB5_tapeout_MC.png', dpi=300)
    fig.savefig('fig/figB5_tapeout_MC.pdf')
    fig.savefig('paper/figures/figB5_realistic_MC.pdf')  # replace paper fig

    print(json.dumps({
        'heater_ON_extra_eta': S['MC_heater_ON_IL_extra']['eta_shift_p10_50_90'],
        'heater_ON_extra_frac90': S['MC_heater_ON_IL_extra']['frac_eta_ge_090'],
        'heater_OFF_extra_eta': S['MC_heater_OFF_IL_extra']['eta_shift_p10_50_90'],
        'frac_reach': frac_reach,
        'P_cons_uW': S['conservative_power']['P_RF_uW'],
        'nth_C0': S['thermal_phonon']['n_th_C0_300K'],
        'gates': S['tapeout_gates'],
    }, indent=1))


if __name__ == '__main__':
    main()
