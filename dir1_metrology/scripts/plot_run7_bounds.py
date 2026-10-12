#!/usr/bin/env python3
"""Figures for dir1_metrology: metrology spacing → SPDC purity MC upper bounds.
Numbers from /workspace/dir01/data/run7.json only. Not measured device results.
"""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

ROOT = Path('/workspace/dir1_metrology')
DATA = Path('/workspace/dir01/data/run7.json')
OUT = ROOT / 'paper' / 'fig'
OUT.mkdir(parents=True, exist_ok=True)

R = json.loads(DATA.read_text())
LS = [2, 5, 10, 15, 20]
# baseline: width rms 2 nm, thickness meas err 0.3 nm
KEYS = [
    ('none', 'uncompensated'),
    ('a0.2_e0.3', 'Δz = 0.2 mm'),
    ('a0.1_e0.3', 'Δz = 0.1 mm'),
    ('a0.04_e0.3', 'Δz = 0.04 mm'),
]
COLORS = {
    'none': '#555555',
    'a0.2_e0.3': '#1f77b4',
    'a0.1_e0.3': '#ff7f0e',
    'a0.04_e0.3': '#2ca02c',
}

def stats(arr):
    p = np.asarray(arr, float)[:, 0]
    return dict(
        median=float(np.median(p)),
        p10=float(np.percentile(p, 10)),
        p90=float(np.percentile(p, 90)),
        mean=float(np.mean(p)),
    )

# Collect baseline table
table = {k: [] for k, _ in KEYS}
for L in LS:
    block = R[f'L{L}']
    for k, _ in KEYS:
        table[k].append(stats(block[k]))

# --- Fig 1: median purity vs length, by metrology spacing ---
fig, ax = plt.subplots(figsize=(6.2, 4.0), dpi=150)
ax.axhline(0.90, color='0.4', ls='--', lw=1.0, label='median target 0.90')
for k, lab in KEYS:
    med = [s['median'] for s in table[k]]
    lo = [s['p10'] for s in table[k]]
    hi = [s['p90'] for s in table[k]]
    ax.plot(LS, med, 'o-', color=COLORS[k], lw=1.6, ms=5, label=lab)
    ax.fill_between(LS, lo, hi, color=COLORS[k], alpha=0.15)
ax.set_xlabel('Device length L (mm)')
ax.set_ylabel('Heralded purity (JSI Schmidt)')
ax.set_title('MC purity upper bound vs length\n'
             '(public wafer traces + adapted poling; N=64, seed 2027)')
ax.set_ylim(0.1, 1.02)
ax.set_xticks(LS)
ax.legend(loc='lower left', fontsize=8, framealpha=0.9)
ax.text(0.02, 0.02,
        'MC upper bound under stated assumptions\n'
        '(width rms 2 nm, meas. err. 0.3 nm).\n'
        'Not a measured device result.',
        transform=ax.transAxes, fontsize=7, va='bottom', ha='left',
        color='0.25')
fig.tight_layout()
fig.savefig(OUT / 'purity_vs_L.png')
fig.savefig(OUT / 'purity_vs_L.pdf')
plt.close(fig)

# --- Fig 2: metrology spacing prescription (max L with median≥0.90) ---
# From report_v7 §4
presc = [
    ('uncompensated', 2, 0.941, 0.821, 0.977, False),
    ('Δz = 0.2 mm', 5, 0.916, 0.859, 0.959, False),
    ('Δz = 0.1 mm', 5, 0.950, 0.899, 0.967, False),
    ('Δz = 0.04 mm', 10, 0.906, 0.855, 0.945, False),
]
# Also highlight the only case with p10≥0.90: 5 mm @ 0.04 mm
fig, ax = plt.subplots(figsize=(6.2, 3.8), dpi=150)
xs = np.arange(len(presc))
meds = [p[2] for p in presc]
los = [p[3] for p in presc]
his = [p[4] for p in presc]
ax.bar(xs, meds, color=['#555555', '#1f77b4', '#ff7f0e', '#2ca02c'],
       alpha=0.85, edgecolor='k', lw=0.5)
ax.errorbar(xs, meds, yerr=[np.array(meds)-np.array(los), np.array(his)-np.array(meds)],
            fmt='none', ecolor='k', capsize=4, lw=1.2)
ax.axhline(0.90, color='0.35', ls='--', lw=1.0)
for i, p in enumerate(presc):
    ax.text(i, his[i] + 0.02, f'L≤{p[1]} mm', ha='center', fontsize=8)
ax.set_xticks(xs)
ax.set_xticklabels([p[0] for p in presc], fontsize=9)
ax.set_ylabel('Purity at longest L with median ≥ 0.90')
ax.set_ylim(0.7, 1.05)
ax.set_title('Metrology prescription (run7 baseline assumptions)\n'
             'None of these hold 10th-percentile ≥ 0.90 — not design points')
ax.text(0.98, 0.05,
        'Only L=5 mm @ Δz=0.04 mm has\n'
        '10th–90th = 0.932–0.982 (both ≥0.90).\n'
        '10 mm @ 0.04 mm: median 0.906 but\n'
        '10th = 0.855 — do NOT sell as design point.',
        transform=ax.transAxes, fontsize=7, va='bottom', ha='right',
        color='0.2',
        bbox=dict(boxstyle='round,pad=0.3', fc='white', ec='0.7', alpha=0.9))
fig.tight_layout()
fig.savefig(OUT / 'metrology_prescription.png')
fig.savefig(OUT / 'metrology_prescription.pdf')
plt.close(fig)

# --- Fig 3: sensitivity — width 10 nm and meas err 1 nm kill the 10 mm story ---
# At L=10, compare baseline a0.04 vs w10 and e1
fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.6), dpi=150, sharey=True)
# left: L=5
# right: L=10
for ax, L in zip(axes, [5, 10]):
    block = R[f'L{L}']
    rows = [
        ('baseline\nΔz=0.04, ε=0.3 nm\nw_rms=2 nm', 'a0.04_e0.3'),
        ('w_rms=10 nm\n(ε=0.3 nm)', 'w10_a0.04_e0.3'),
        ('ε=1 nm\n(w_rms=2 nm)', 'e1_a0.04'),
    ]
    xs = np.arange(len(rows))
    meds, los, his = [], [], []
    for _, key in rows:
        s = stats(block[key])
        meds.append(s['median']); los.append(s['p10']); his.append(s['p90'])
    ax.bar(xs, meds, color=['#2ca02c', '#d62728', '#9467bd'], alpha=0.85,
           edgecolor='k', lw=0.5)
    ax.errorbar(xs, meds,
                yerr=[np.array(meds)-np.array(los), np.array(his)-np.array(meds)],
                fmt='none', ecolor='k', capsize=3, lw=1.0)
    ax.axhline(0.90, color='0.35', ls='--', lw=1.0)
    ax.set_xticks(xs)
    ax.set_xticklabels([r[0] for r in rows], fontsize=7)
    ax.set_title(f'L = {L} mm')
    ax.set_ylim(0.2, 1.05)
axes[0].set_ylabel('Purity (median ± 10–90%)')
fig.suptitle('Assumption stress test at Δz = 0.04 mm (run7)\n'
             'MC upper bounds — not measured devices', fontsize=10, y=1.02)
fig.tight_layout()
fig.savefig(OUT / 'assumption_stress.png', bbox_inches='tight')
fig.savefig(OUT / 'assumption_stress.pdf', bbox_inches='tight')
plt.close(fig)

# Write a small summary JSON for the paper pack
summary = {
    'source': str(DATA),
    'seed': R['seed'],
    'NMC': R['NMC'],
    'note': R['note'],
    'P': R['P'],
    'baseline_by_L': {
        str(L): {k: table[k][i] for k, _ in KEYS}
        for i, L in enumerate(LS)
    },
    'prescription_median_ge_0.90': [
        {'spacing': p[0], 'max_L_mm': p[1], 'median': p[2],
         'p10': p[3], 'p90': p[4], 'p10_ge_0.90': p[5]}
        for p in presc
    ],
    'only_p10_ge_0.90_in_main_table': {
        'L_mm': 5, 'spacing_mm': 0.04, 'median': 0.969, 'p10': 0.932, 'p90': 0.982
    },
}
(ROOT / 'paper' / 'run7_summary.json').write_text(json.dumps(summary, indent=2))
print('Wrote figures to', OUT)
for f in sorted(OUT.iterdir()):
    print(' ', f.name, f.stat().st_size)
