# -*- coding: utf-8 -*-
"""Post-process Step 5 log -> eig_step5.csv, sweep_step5.csv, summary_step5.md."""
import os, re, math

D = r'D:\comsol_ao_run\step5_drive'
LAM = 1550e-9

def read(p):
    raw = open(p, 'rb').read()
    for enc in ('utf-8', 'gb18030'):
        try:
            return raw.decode(enc)
        except Exception:
            pass
    return raw.decode('utf-8', 'replace')

t = read(os.path.join(D, 'step5.log'))

checks = [l.strip() for l in t.splitlines() if l.strip().startswith(('COORD_SYS_SET','GROUND_CHECK','TERMINAL_CHECK','TYPE2D_READBACK','NUMELEM','TENSOR_CHECK','POINT_CHECK','Y_EXPR','EIG_CHECK','EIG_TARGET','EIG_PARTNER','NFREQ','FREQ_SOLVED'))]
eig = []
for l in t.splitlines():
    s = l.strip()
    m = re.match(r'EIG f_GHz=([\d.]+) fi_MHz=(-?[\d.]+) Q=(-?[\d.]+) fracLN=([\d.]+) fracAl=([\d.]+) pu=([\d.]+) pv=([\d.]+) pw=([\d.]+)', s)
    if m:
        eig.append([float(m.group(i)) for i in range(1, 9)])

# eig CSV: target and partner (last two special rows) if present
tgt = par = None
for l in t.splitlines():
    s = l.strip()
    m = re.match(r'EIG_TARGET f_GHz=([\d.]+) fi_MHz=(-?[\d.]+) Q=(-?[\d.]+) fracLN=([\d.]+) fracAl=([\d.]+) pu=([\d.]+) pv=([\d.]+) pw=([\d.]+)', s)
    if m: tgt = [float(m.group(i)) for i in range(1, 9)]
    m = re.match(r'EIG_PARTNER f_GHz=([\d.]+) fi_MHz=(-?[\d.]+) Q=(-?[\d.]+) fracLN=([\d.]+) fracAl=([\d.]+) pu=([\d.]+) pv=([\d.]+) pw=([\d.]+)', s)
    if m: par = [float(m.group(i)) for i in range(1, 9)]
eigrows = [r for r in [tgt, par] if r]
el = ['f_GHz,fi_MHz,Q,fracLN,fracAl,pu,pv,pw']
for r in eigrows:
    el.append(','.join('%.9g' % x for x in r))
open(os.path.join(D, 'eig_step5.csv'), 'w', encoding='utf-8', newline='\n').write('\n'.join(el) + '\n')

# SW lines
names = []
for met in ['PE', 'EO', 'MB', 'Tot']:
    for kind in ['avg', 'K', 'win']:
        for q in ['Re', 'Im', 'Abs']:
            names.append('%s_%s_%s' % (kind, met, q))
names.append('win_x0_um')
header = ['f_GHz','ReY','ImY','int_u2','max_v'] + names
rows = []
for l in t.splitlines():
    s = l.strip()
    if not s.startswith('SW '):
        continue
    m = re.match(r'SW f_GHz=([\d.]+) ReY=(\S+) ImY=(\S+) int_u2=(\S+) max_v=(\S+)', s)
    if not m:
        continue
    base = [float(m.group(1)), float(m.group(2)), float(m.group(3)), float(m.group(4)), float(m.group(5))]
    blocks = re.findall(r'avgRe=(\S+) avgIm=(\S+) avgAbs=(\S+) KRe=(\S+) KIm=(\S+) KAbs=(\S+) winRe=(\S+) winIm=(\S+) winAbs=(\S+)', s)
    if len(blocks) != 4:
        continue
    vals = []
    for b in blocks:
        vals.extend([float(x) for x in b])
    mw = re.search(r'win_x0_um=(\S+)', s)
    vals.append(float(mw.group(1)) if mw else float('nan'))
    rows.append(base + vals)
open(os.path.join(D, 'sweep_step5.csv'), 'w', encoding='utf-8', newline='\n').write(
    ','.join(header) + '\n' + '\n'.join(','.join('%.9g' % x for x in r) for r in rows) + '\n')

# classify coarse / fine
def is_coarse(f):
    k = (f - 3.30) / 0.001
    return abs(k - round(k)) < 1e-4 and 3.30 - 1e-6 <= f <= 3.380 + 1e-6
coarse = [r for r in rows if is_coarse(r[0])]
fine = [r for r in rows if not is_coarse(r[0])]

# find Y = ReY + i ImY
def Yabs(r):
    return math.hypot(r[1], r[2])

def find_peak(rs, lo, hi):
    cand = [r for r in rs if lo <= r[0] <= hi]
    if not cand:
        return None
    return max(cand, key=lambda r: Yabs(r))

def fwhm_q(rs, peak):
    fp = peak[0]; yp = Yabs(peak)
    half = yp / 2.0
    lo = fp; hi = fp
    for r in sorted(rs, key=lambda r: r[0]):
        if r[0] <= fp and Yabs(r) <= half:
            lo = r[0]
    for r in sorted(rs, key=lambda r: r[0]):
        if r[0] >= fp and Yabs(r) <= half:
            hi = r[0]; break
    if hi > lo:
        return fp / (hi - lo)
    return float('nan')

def idx(name):
    return header.index(name)

L = []
L.append('# Step 5：p_new 上的 1 V 频域驱动（光弹 + 电光 + 移动边界）')
L.append('')
L.append('## 1) 检查结果')
L.append('')
L.append('| 项目 | 值 |')
L.append('|---|---|')
for c in checks:
    L.append('| %s |  |' % c)
L.append('')
L.append('（上一表逐行给出：坐标系、接地、端口实体数、Type2D、单元数、张量检查、点值检查、Y 变量、本征复核、频点数。）')
L.append('')
L.append('## 2) 本征复核')
L.append('')
L.append('| 模 | f_GHz | fi_MHz | Q | fracLN | fracAl | pu | pv | pw |')
L.append('|---|---|---|---|---|---|---|---|---|')
for nm, r in [('目标竖模', tgt), ('配对模', par)]:
    if r:
        L.append('| %s | %.9f | %.6f | %.3f | %.4f | %.4f | %.3f | %.3f | %.3f |' % (nm, r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7]))
L.append('')
L.append('## 3) 频率响应曲线')
L.append('')
L.append('| f_GHz | |Y| (S) | int_u2 | |avg_Tot| | |K_Tot| |')
L.append('|---|---|---|---|---|')
for r in coarse:
    L.append('| %.6f | %.6e | %.6e | %.6e | %.6e |' % (r[0], Yabs(r), r[idx('int_u2')], abs(r[idx('avg_Tot_Abs')]), abs(r[idx('K_Tot_Abs')])))
L.append('')
L.append('### 细扫')
L.append('')
L.append('| f_GHz | |Y| (S) | int_u2 | |avg_Tot| | |K_Tot| |')
L.append('|---|---|---|---|---|')
for r in fine:
    L.append('| %.6f | %.6e | %.6e | %.6e | %.6e |' % (r[0], Yabs(r), r[idx('int_u2')], abs(r[idx('avg_Tot_Abs')]), abs(r[idx('K_Tot_Abs')])))
L.append('')
L.append('## 4) 共振峰')
L.append('')
peaks = [p for p in [find_peak(fine, tgt[0]-0.01, tgt[0]+0.01) if tgt else None,
                     find_peak(fine, par[0]-0.01, par[0]+0.01) if par else None] if p]
# peaks CSV
pl = ['f_peak_GHz,Y_abs,Q_FWHM,int_u2,avg_Tot_Abs,K_Tot_Abs,phi_avg_rad_per_mm_V,phi_K_rad_per_mm_V']
for p in peaks:
    phi1 = (2*math.pi/LAM) * p[idx('avg_Tot_Abs')] * 1e-3
    phi2 = (2*math.pi/LAM) * p[idx('K_Tot_Abs')] * 1e-3
    pl.append('%.6f,%.9e,%.6f,%.9e,%.9e,%.9e,%.9e,%.9e' % (p[0], Yabs(p), fwhm_q(fine, p), p[idx('int_u2')],
        p[idx('avg_Tot_Abs')], p[idx('K_Tot_Abs')], phi1, phi2))
open(os.path.join(D, 'peaks_step5.csv'), 'w', encoding='utf-8', newline='\n').write('\n'.join(pl) + '\n')

L.append('| 峰 | f_peak_GHz | |Y|_peak | Q(FWHM from |Y|) | int_u2_peak |')
L.append('|---|---|---|---|---|')
for p in peaks:
    L.append('|  | %.6f | %.6e | %.3f | %.6e |' % (p[0], Yabs(p), fwhm_q(fine, p), p[idx('int_u2')]))
L.append('')
for p in peaks:
    L.append('### f = %.6f GHz 处 Δn（每伏）' % p[0])
    L.append('')
    L.append('| 指标 | 实部 | 虚部 | 模 |')
    L.append('|---|---|---|---|')
    for kind in ['avg', 'K', 'win']:
        for met in ['PE', 'EO', 'MB', 'Tot']:
            re_, im_, ab = p[idx('%s_%s_Re' % (kind, met))], p[idx('%s_%s_Im' % (kind, met))], p[idx('%s_%s_Abs' % (kind, met))]
            L.append('| %s_%s | %.6e | %.6e | %.6e |' % (kind, met, re_, im_, ab))
    L.append('')
L.append('## 5) 相位调制换算 φ/L = (2π/λ)|δn|')
L.append('')
L.append('| 峰 f (GHz) | (2π/λ)|avg_Tot| (rad/(mm·V)) | (2π/λ)|K_Tot| (rad/(mm·V)) |')
L.append('|---|---|---|')
for p in peaks:
    f1 = (2*math.pi/LAM) * p[idx('avg_Tot_Abs')] * 1e-3
    f2 = (2*math.pi/LAM) * p[idx('K_Tot_Abs')] * 1e-3
    L.append('| %.6f | %.6e | %.6e |' % (p[0], f1, f2))
L.append('')
L.append('## 6) 说明')
L.append('')
L.append('- Δn 指标：2D 域积分实现（y 方向乘 E(y)^2 权重，x 方向用 exp(-i2πnx/p) 权重直接做二维积分）；窗口平均由傅里叶级数（N=%d 阶）解析重建后取 0.5 µm 窗。' % 16)
L.append('- 光模式：500 nm 空气平板 TE0，neff=1.88978，κ=4.052926e6 1/m，λ=1550 nm；晶体 Z=全局 z，走 ne。')
L.append('- 常数：ne=2.138，p31=0.179，p33=0.071，r13=8.6e-12 m/V，r33=30.8e-12 m/V。')
L.append('- Q（FWHM）用细扫 |Y| 半高宽估算，未插值。')
L.append('')
open(os.path.join(D, 'summary_step5.md'), 'w', encoding='utf-8', newline='\n').write('\n'.join(L) + '\n')
print('rows sweep', len(rows), 'coarse', len(coarse), 'fine', len(fine), 'eig', len(eigrows), 'peaks', len(peaks))
print('header cols', len(header))
