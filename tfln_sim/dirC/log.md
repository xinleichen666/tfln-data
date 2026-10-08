Wed Oct  7 21:58:18 CST 2026 round1 scans launched (dirC/scan.py C, dirD/scan.py D)
Wed Oct  7 22:22:59 CST 2026 relaunched with 1 thread/proc, Pool(4) (load issue)
## Round C1 (scan_C.json, scan.log) — 400nm film, etch 200-360, XcutY/XcutZ, air/SiO2
- Best: H400 e280 XcutY air: g=0.029/0.036/0.042 @1.45/1.55/1.65, wx~1.65um (wavelength-independent!), linear-LZ L99 ~185-230um.
- e240/e320 much worse (g<=0.015 or erratic); SiO2 clad kills gap (<=0.011). Z-prop 400nm not better (erratic).
- Note slab TM NaN => residual slab has no guided TM (slab TE leakage check pending).
## Round C2 (r2_C.json): fab corners on 400/280 Y-prop air
- All corners e260-300, H390-410, angle 55-65: g=0.025-0.045 over 1450-1650; wx 1.59-1.81 um; mode neff exceeds slab TE by >0.12 (no leakage). LZ L99 172-272 um.
- => robust. Next C3: EME linear taper 1.1->2.4 um at all corners (eme_c.py -> eme_c.json)
## Round C3 done (eme_c.log/json, figs/eme_taper_corners.png)
- L=200um linear taper: 1450-1600 conv 95-99.5% at all corners; 1650 saturates 0.84-0.95 independent of L (end-width/mode-identity issue, not adiabaticity). EME power-conservation error ~±3% (tot 0.96-1.06) -> PER >15 dB not resolvable with this EME.
## final_summary written
## Round C4 started: EME 1.1->2.9um, 73 pts, nm=8, res40, dx15nm (eme_c4.py). D stopped per user.
## Novelty search (C4)
- Li C. et al., APL Photonics 10, 016111 (2025), doi 10.1063/5.0240402: SAME platform: 400nm X-cut, Y-prop, 200nm etch (slab 200), 60deg; 3-seg taper 10+100+250um (w3=2.16um) + STIRAP 700um => ~1.06mm; IL<0.5dB, ER>20dB/130nm, fab-tolerant.
- Chen Y. et al., OL 50(10) 3433 (2025): TFLN PRS adiabatic tapers + 2x2 MMI, 228um total.
- Chen G. arXiv 2407.04995: 400nm platform crossing at 0.4um top width.
=> "400nm Y-prop PSR" not novel; only differentiator possible = deeper etch (280) -> larger g -> shorter taper.
## C5 ADC: phase match TE1(W2.6)=1.752 ~ TE0(wn1.27); running adc_exact W2.6 wn1.27 g0.3/0.4 -> adc/
## C4 done (eme_c4.json): taper 1.1->2.9um, nm8, dx15nm
- Residual TM0 at output: L=300um: 1.45 -25dB, 1.55 -30dB, 1.65 <-30dB nominal; corners @1.65: H390 -21.5dB, e260 <-30, a55 -27; e300@1.65 numerically divergent (PML modes).
- "1650 saturation" in C3 = power going to PML/leaky modes in EME (non-unitary), NOT residual TM0. TE1 power 0.76-0.94 at 1.65 -> either EME artifact or 0.3-1.2 dB real loss; unresolved locally.
## C5 done: uniform ADC W2.6/wn1.27 (Y-prop 400/280), g=0.2/0.3/0.4
- phase-matched at 1.6um; mismatch 0.0025 @1.45. g0.2: Lc 88-137um across band; common L=114.5um gives TE1->TE0 0.76-0.92 => cross residual -6..-11 dB. g0.3/0.4 too weak (<0.55 @1.45 within 150um). TE0 crosstalk -31..-40 dB.
- => uniform ADC cannot reach 20 dB over 200nm; needs adiabatic/tapered ADC (dirB: >=50dB but ~250-300um) -> total ~550-650um.
## Conclusion: full-device PER>20dB not demonstrated -> no 3D FDTD built. Novelty negated by Li 2025 APL Photonics (same 400nm Y-prop platform).
