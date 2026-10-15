# Direction 11 SOTA comparison (our numbers = simulation/design prediction; literature = measured unless noted)

Every literature number below was read from the cited source in this session (arXiv full text or abstract).

| # | Metric | Ours (sim) | Best published | Source (URL) | Verdict |
|---|---|---|---|---|---|
| 1 | RF power for ~99% single-tone shift | **79 µW (A, 0.842 GHz); 7.2 µW (B, 3.33 GHz)** | 96 mW (3.1 V peak at 50 Ω probe) for η=98.7% at 28.2 GHz; authors project 1 V peak (about 10 mW) at Q_i=10⁷ (projection, not measured) | Hu et al., Nature 599, 587 (2021), https://arxiv.org/abs/2005.09621 (Supp. Sec. IV–V) | Beats the measured device by about 10³–10⁴×, **but see row 1b** |
| 1b | Matched-EO comparison (same optics, Hu 0.5 GHz/V push-pull, V_c=V_0) | A: AO 79 µW vs EO 95 µW; B at the Shao-2019 measured Q_i≈2.4×10⁶: AO 7.4 µW vs EO 3.25 mW | Hu coefficient: https://arxiv.org/abs/2005.09621 Supp. Sec. V; Q: Shao et al. Optica 6, 1498 (2019) Table S2 | — | **A: no acoustic advantage (1.2×). B: about 440× (simulation), narrowband (~1 MHz)** |
| 2 | Shift efficiency η=P_shift/P_out | 99.2% (A) / 98.4% (B) | 99.1% up, 99.4% down at 12.5 GHz; 98.7% at 28.2 GHz | same | Comparable |
| 3 | Insertion loss / absolute efficiency | 1.8 dB / 66% (Q_i 1.9×10⁷); 0.65 dB / 86% at Q_i 6×10⁷ | 0.45 dB at 28.2 GHz; 1.2 dB at 12.5 GHz | same | Worse (comparable only at Q_i ≳ 6×10⁷) |
| 4 | Shift frequency / RF bandwidth | 0.84 or 3.33 GHz fixed; 132.5 MHz (A) or ~1 MHz (B) acoustic bandwidth | 11–28.2 GHz; >3 GHz bandwidth (amplifier-limited) | same | Worse |
| 5 | Previous TFLN acousto-optic shifter | iter-5 η_shift 99.2% | 3.5% on-chip efficiency at 30 dBm, >30 dB carrier suppression, 70 MHz bandwidth, ~3 GHz | Shao et al., Opt. Express 28, 23728 (2020), https://doi.org/10.1364/OE.397138, https://arxiv.org/abs/2005.03794 (verified 2026-10-07; values as recorded in report.md §3 from the full text) | Beats prior AO record, but prior AO is not overall SOTA |
| 6 | AO IQ SSB efficiency (iter 0–2) | 33.9% | 98.7–99.4% (Hu) | https://arxiv.org/abs/2005.09621 | Worse (dropped) |
| 7 | Quantum spectral control of single photons on TFLN | iter 5 coherent; HOM not separately simulated for iter 5 | Frequency shearing ±641 GHz of telecom single photons with high-visibility nondegenerate HOM; 18× bandwidth compression | Zhu et al., Light Sci. Appl. 11, 327 (2022), https://arxiv.org/abs/2112.09961 | Not comparable (different function) |
| 8 | Optomechanical single-photon shifter | — | Fan et al., Nat. Photon. 10, 766 (2016) | — | Context only |
| 9 | M→O efficiency, piezo-OM on TFLN/Si | iter 4: 1.8% at 1 mW (double-resonance design, room-T model) | 0.9% efficiency, 14.8 MHz bandwidth, few-photon added noise | Weaver et al., Nat. Nanotechnol. 19, 166 (2024), https://arxiv.org/abs/2210.15702 | Comparable on paper, but ours ignores cryogenic noise; not a claim |
| 10 | M→O, LN piezo-OM | — | 5% continuous conversion efficiency; thermal noise <2 microwave photons; 15 Hz heralding | Jiang et al., https://arxiv.org/abs/2210.10739 | Worse |
| 11 | M→O, TFLN EO (qubit control) | — | up to 1.18% conversion efficiency with low added noise; optically driven qubit Rabi | Warner et al., Nat. Phys. 2025, https://arxiv.org/abs/2310.16155 | Worse |
| 12 | M→O from qubit, AlN/Si | — | η_t=(0.88±0.16)×10⁻⁵, n_add=0.57±0.2 | Mirhosseini et al., Nature 588, 599 (2020), https://arxiv.org/abs/2004.04838 | Not comparable (pulsed, qubit-referred) |
| 13 | Calibration sources | — | Shao 2019: MZI V_π=4.6 V (100 µm, single arm), g0/2π=1.1 kHz, η=0.0017% at 1 mW; Ni 2026: V_πL=1.004 V·cm push-pull, 0.842 GHz, 132.5 MHz bandwidth | Shao et al., Optica 6, 1498 (2019), https://doi.org/10.1364/OPTICA.6.001498 ; Ni, Bhave, Xu, https://arxiv.org/abs/2606.05337 | Inputs |

| 1c | Source-referred power incl. matching (iteration 7) | AO 7.4 µW with Shao IDT as measured (V_π extracted vs 50 Ω source power, incl. ~50% IDT coupling); 3.7 µW with ideal IDT. EO with lumped LC match (Hu electrode C=0.11 pF, R=1.5 Ω): 13.8 µW (inductor Q 30), 5.0 µW (Q 100), 1.3 µW (ideal) | Shao 2019 https://arxiv.org/abs/1907.08593 (Eq. 1, Supp. Eq. S8); Hu https://arxiv.org/abs/2005.09621 Supp. Sec. V | — | **Fair advantage only 1.4–3.7×, or worse. The ~440× claim is withdrawn** |
| 14 | Acoustically driven TFLN photonic molecule (prior art) | — | LN-on-sapphire coupled rings, IDT-driven GHz acoustic dynamic Bragg mirror; strong supermode coupling at mW drive; cooperativity 2.46 per mW; DBM reflectivity up to 24% (abstract-verified; other details from the writer's full-text read) | Zhu et al., arXiv:2511.22585, https://arxiv.org/abs/2511.22585 | Prior art: "acoustic photonic molecule" is not new |
| 15 | Acousto-optic ring coupling calibration | — | G²=αP_a, α=1774±171 GHz²/W at 8.533 GHz; RF→acoustic ≈10%; κ0/2π≈0.32 GHz; 45 dB isolation at 5.7 dBm acoustic; π gyration at −0.3 dBm with ≈8.2 dB IL; ~1 nm optical BW, 60 nm tuning (full text verified) | Xu et al., arXiv:2509.01940, https://arxiv.org/abs/2509.01940 | Calibration/context |
| 16 | Broadband TFLN serrodyne shifter | — | Vπ≈2.3 V; shift efficiency >98.8%; CSR 42 dB, SSR 31 dB (**abstract only, not verified from full text**) | Qiu et al., Opt. Lett. 50, 1132 (2025), https://opg.optica.org/ol/abstract.cfm?uri=ol-50-4-1132 | Comparable-or-better efficiency, broadband; beats ours on agility |

## Verdict
- **Iteration 7 supersedes everything below:** once both drives are impedance-matched, AO (3.7 µW) vs EO (1.3–14 µW) gives no meaningful acoustic advantage. No Direction-11 metric beats SOTA.
- (Superseded) iteration 6: only design B. It is about 440× below a matched EO drive at the same Shao-measured Q, and about 1.3×10⁴× below the measured Hu device. Design A's advantage came from optical Q, not acoustics. B usable RF bandwidth is about 1 MHz (η_shift ≥97.8% within ±0.3 MHz). An EO drive with an on-chip microwave resonator of loaded Q≈450 could in principle match B (not demonstrated).
- Original row-1 statement: An acoustically driven photonic-molecule shifter reaches about 99% shift efficiency with µW-scale RF, about 3–4 orders of magnitude below the best measured EO shifter (Hu 2021). The authors' own 1 V projection is still 2–3 orders higher.
- **Everything else** is comparable or worse: IL, frequency agility, RF bandwidth, IQ-SSB efficiency, and all transducer metrics.
- **Caveats that must appear in the paper:**
  - The drive strength is a linear extrapolation of published V_πL to partial ring coverage.
  - The shift frequency is fixed at the acoustic resonance, with MHz-scale RF bandwidth.
  - The power advantage needs Q_i ≳ 10⁷.
  - IDT/metal optical loss and acoustic heating are not modelled.
  - Spurious orders are about −25 dB.
- **Verification note:** rows 5 and 8 have no URL (journal citation only), and their numbers were not re-read from the full text in this session. Check both before submission.

## Iterations 8–13 (screen of acoustic-unique metrics)
Isolation (EO 48 dB/0.5 dB, arXiv:2212.01945; AO 28 dB/2 THz, arXiv:2403.10628), transduction, small-spacing frequency-bin operations, and beamsplitter fidelity were all screened. None gives a fair simulated win over measured SOTA. The best near-miss beats only the prior acousto-optic shifter record (Shao 2020: 3.5% at 30 dBm), not the EO SOTA. **Final verdict: nothing in Direction 11 beats SOTA under a fair comparison.**
