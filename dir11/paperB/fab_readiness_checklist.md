# Fab readiness checklist — Dir1 / paperB

**Device:** suspended-IDT, dual-ring TFLN photonic-molecule frequency shifter (forward single-bus, fixed 3.33 GHz).  
**Date:** 2026-10-14.  
**Package:** design + measurement plan. Every performance number below is a **prediction** until a column marked measured is filled from this chip. Measured columns stay empty in this note.

## Recommendation

**Tape out the current v2 layout.** Send the mask with the heater-isolated coupler drawn and with the step-1 witnesses on the same reticle. A further coupler redesign before this tape-out is not required.

The device concept stays as locked: a suspended IDT drives one ring of the dual-ring molecule; the bus is forward and single-sided; the shift is the acoustic resonance, 3.33 GHz.

v2 is already the isolation layout. Relative to v1 the Monte Carlo changed only the heater-crosstalk assumption (`dT_cm@Pπ` 10 → 3 mK, `dT_diff@Pπ` 5 → 2 mK). κi×2, the 5 mK lock residual, the MZI law, and the Maeder Pπ assumption were left alone. Those 3 mK and 2 mK figures are **ASSUMED**. No published same-geometry value exists to design a tighter coupler against, and they do not belong in the verified-parameter table.

Simulation-side gates under that assumption (heater ON, κi×2, N=1000, master seed `20261114`):

| Gate | Prediction | Simulation-side result |
|---|---|---|
| ① ≥90% of samples with η_shift ≥ 0.90 | frac = 94.0%; η_shift p10 / median = 0.917 / 0.964 | PASS **if** the crosstalk assumption holds |
| ② conservative RF ≪ Shao 2020 1 W | ξ=0.5 × IDT 10% × Qm=1570 ≈ 172 µW | PASS (prediction; independent of the mK assumption) |
| ③ largest spurious order | q=−1 in 100% of the heater-ON κi×2 suite | PASS (prediction) |
| **ALL_PASS** | conjunction of ①–③ | **Simulation-side only, under the assumed 3/2 mK crosstalk.** Step 1 has to support that assumption before anyone treats ALL_PASS as the yield story. |

v1 (looser crosstalk, master seed `20261014`) is the fallback narrative: gate ① **FAIL**, frac(η_shift ≥ 0.90) = 81.9%.

Thermal-phonon bounds (`n_th/N_coh` and `n_th·C_0`) do not choose this fork. They are not a reason to hold the mask, and they are not a reason to prefer the v1 path.

## What the fab package must contain

- [ ] Functional shifter on the **current v2 layout**: dual rings, forward single bus coupled only to ring 1, suspended acoustic section only on ring 1, IDT at 3.33 GHz, heater on one arm of the ring–ring MZI coupler, heater arm isolated and pulled away from both rings.
- [ ] Step-1 witnesses in the **same heater-to-ring geometry** as that device (coupler MZI for on-chip Pπ; dual-ring readout for common-mode and differential crosstalk).
- [ ] Step-2 IDT cell: same suspension, aperture, and finger pitch as the device IDT, with GSG pads, for S11 and acoustic Q.
- [ ] Step-3 path: the functional shifter, plus one single-ring resonator with the same 100 µm suspended coverage, so ξ is read from a sideband ratio.
- [ ] Step-4 reference: a straight waveguide with the same facets and a comparable path length, so on-chip insertion loss is separated from facet loss.
- [ ] Tape-out log shipped with the GDS: drawn heater-to-ring distances in micrometres, cell list, and this checklist. Distances are layout dimensions. They are not a measured temperature.
- [ ] Prediction sheet with the v2 and v1 rows below. The measured column is blank.

## What stays gated by step 1

Step 1 of the measurement plan runs before any v2 yield claim. It sweeps heater power, reads the doublet splitting (target 2µ = Ω/2π = 3.33 GHz), and extracts common-mode and differential resonance pulls at the operating heater power.

Stay on the v2 story only when all three of the following hold:

- [ ] |2µ − Ω| is brought inside the RF retune window used in the suite (about ±1 MHz in the main case).
- [ ] The heater-on residual is consistent with the predicted hit rate of |2µ − Ω| (100% in the heater-ON κi×2 suite).
- [ ] The extracted crosstalk at equivalent Pπ **supports** the assumed `dT_diff@Pπ = 2 mK` and `dT_cm@Pπ = 3 mK`.

Until that third item is measured:

- [ ] v2 yield stays a prediction: η_shift median 0.964, p10 0.917, frac(η ≥ 0.90) = 94.0% (heater ON, κi×2).
- [ ] **ALL_PASS** stays a simulation-side label under the assumption. It is not a device result.
- [ ] 2 mK and 3 mK stay labeled **ASSUMED**.
- [ ] Step-4 acceptance does not use the v2 p10 bar.
- [ ] The abstract does not state ALL_PASS, and it does not state the crosstalk millikelvin figures, as measured achievements.

Gate ② (≈172 µW) and gate ③ (worst spur q=−1) do not depend on the crosstalk knob. They remain predictions either way. They do not by themselves make ALL_PASS a measured result.

The Shao-Qi loss column is not the acceptance column (heater-ON Shao-Qi prediction: IL median 2.48 dB, frac(η ≥ 0.90) = 98.8%). Acceptance stays on heater ON and κi×2.

## Fallback — step-1 crosstalk fails → v1 FAIL path

If the step-1 extraction **cannot support** `dT_diff@Pπ = 2 mK` and `dT_cm@Pπ = 3 mK`:

1. **Drop the v2 yield narrative.** Gate ① is **FAIL**. The archived v1 suite (heater ON, κi×2, master seed `20261014`, crosstalk assumption 5 mK differential / 10 mK common-mode) has frac(η_shift ≥ 0.90) = **81.9%**, below the 90% gate. η_shift p10 / median in that suite are **0.874 / 0.950**.
2. **Step-4 acceptance uses the v1 p10.** The device bar for η_shift is the v1 p10, **0.874**. IL, carrier suppression, and q=−1 suppression use the p10 row of the archived v1 suite `summary_heater_xi_v1.json` (seed master `20261014`). That file is not in this checkout; do not fill those percentiles from the v2 suite.
3. **ALL_PASS is not achieved** on this path. Do not report it as a tape-out result, a measurement, or an abstract claim.
4. A coupler or isolation change is a **later mask** if the goal is to recover the v2 assumption. It does not block spectrum measurements on this chip, and it does not reopen a v2 pass on this chip after step 1 has failed the assumption.
5. Abstract rule is unchanged: ALL_PASS and the crosstalk millikelvin figures are not measured achievements.

Thermal-phonon bounds do not flip this fork. A large or small `n_th/N_coh` or `n_th·C_0` neither rescues a failed step-1 crosstalk check nor blocks tape-out when step 1 has not yet been measured.

## GDS / mask notes

Foundry layer numbers, die size, and drawn gaps in nanometres are set in the layout tool. This note does not assign them.

- [ ] Top cell is the v2 shifter. Hierarchy keeps the suspended release, the IDT, the heater MZI, and the bus as separate, named cells so the witness cells can instance the same geometry.
- [ ] Release window covers the 100 µm acoustic section of ring 1. Ring length on the device is 0.667 mm (acoustic coverage 0.15). Ring 2 and the bus stay outside that release unless the process stack forces otherwise.
- [ ] Heater metal is on the coupler arm only. It does not cross the suspended acoustic cavity and it does not share a net with the IDT.
- [ ] DC heater pads and RF GSG pads are separate. IDT probe pitch matches the step-2 cell.
- [ ] Draw the v2 thermal isolation (pull-back and/or a thermal break between the heated arm and **both** rings). Write the drawn heater-to-ring-1 and heater-to-ring-2 distances, in micrometres, into the tape-out log.
- [ ] Title block and reticle text name the chip as a design tape-out. They do not print ALL_PASS, 94%, or “2 mK / 3 mK measured”.
- [ ] One reticle carries the functional device and the step-1 witnesses, so the crosstalk calibration is the same geometry as the shifter.
- [ ] `data/params_sources.md` is unchanged by this tape-out. The 2 mK / 3 mK pair is an assumption of the heater Monte Carlo only.

## Heater MZI coupler callouts

- [ ] Coupler law used in the suite, and the law the layout must implement: `μ = μ_gap · sin(Δφ/2)` with `Δφ ∈ [0, π]`.
- [ ] Cold-gap target: `μ_gap = μ · √2`, where `2μ = Ω = 2π × 3.33 GHz`, so a bias near Pπ/2 lands on the design splitting. `design_mu_factor = √2` is unchanged from v1.
- [ ] Heater on **one** arm of that MZI.
- [ ] Pπ = **44.4 mW** is the **Maeder geometry assumption** (Maeder et al., QST 2024). It is not a calibration of this ring–ring layout, and it is not taken from Zhang, Nat. Photon. 2019 (that work is DC detuning, not a heater-tuned μ(φ)).
- [ ] On-chip Pπ is an output of the step-1 MZI witness, not an input stamped on the mask as a measured number.
- [ ] Crosstalk the layout is **intended** to reach, still **ASSUMED** until step 1: `dT_diff@Pπ = 2 mK`, `dT_cm@Pπ = 3 mK`. v1 assumption was 5 mK / 10 mK. Lock residual `sigT_lock = 5 mK` is a separate assumption and was not tightened.
- [ ] κi×2 stays the acceptance loss. The mask does not “recover” yield by dropping the extra-loss column.

Predicted heater power in the v2 heater-ON κi×2 suite (not a measurement): p10 / median / p90 ≈ 21.1 / 22.2 / 23.5 mW.

## IDT callouts

- [ ] Suspended LN acoustic resonator, IDT-driven, 100 µm interaction on ring 1, Ω/2π = **3.33 GHz** fixed.
- [ ] Geometry family: Shao et al., Optica 6, 1498 (2019), including the 100 µm suspended section. Shao’s 90 µm IDT width was that paper’s 50 Ω match. This chip’s match is whatever step 2 measures.
- [ ] Source-referred calibration used in the model: ξ = 1 ↔ δω/2π = **21.3 GHz/V** (Shao MZI VπL = 0.046 V·cm, source-referred, already including that paper’s ≈50% IDT coupling). ξ on this chip is measured in step 3.
- [ ] Design predictions for the RF budget, not measured powers: main case Qm = 2000 and η_IDT = 10%; conservative case Qm = **1570 (assumed, no literature source)** at the same 10%. Conservative operating point ξ = 0.5 gives ≈ **172 µW**. Suite sweep at IDT 10% and Qm = 1570: ξ = 0.3 / 0.5 / 1 / 2 → 478 / 172 / 43 / 11 µW.
- [ ] Acoustic linewidth predictions (FWHM): 1.67 MHz (Qm 2000), 0.93 MHz (Qm 3600, Shao 2019 upper), 2.12 MHz (Qm 1570, assumed).
- [ ] Step-2 acceptance band to write on the test plan, still a plan and not a result: Qm at or above 2000, or at least the conservative 1570 with the power still far below the Shao 2020 30 dBm (1 W) drive; η_IDT at or above the main-case 10%.

## Test structures for steps 1–4

Step 5 (narrowband HOM) waits until step 4 has passed its p10 bar. It adds no mask cell on this checklist.

| Step | Cell on this mask | What it is for | Prediction it is allowed to be compared against | Leave blank until measured |
|---|---|---|---|---|
| 1 | Coupler MZI witness | Same heater length, width, metal, and cladding as the device coupler arm. Optical readout of phase vs electrical power → on-chip Pπ. | Maeder 44.4 mW is the **assumption**, replaced by this measurement for the real arm. | Pπ, tuning curve |
| 1 | Crosstalk witness | Same heater and the same drawn isolation as the device. **Each ring has its own readout bus** so the two resonance shifts separate common-mode pull from differential pull. This cell is a witness, not a second shifter; the functional device stays single-bus. | Supports or fails the **assumed** 2 mK differential and 3 mK common-mode at equivalent Pπ. Also checks \|2µ − Ω\| against the ±1 MHz retune window and the predicted heater-on hit of 100%. | dT_diff, dT_cm, 2µ(P), heater-off baseline |
| 1 | Functional device, heater off and on | Heater-off spectrum is the control. Heater-on spectrum is the splitting measurement on the real single-bus device. | Heater-OFF κi×2 suite is a control only (predicted frac(η ≥ 0.90) = 74.2%, not the acceptance column). | spectra vs heater power |
| 2 | IDT S11 cell + de-embed | Same suspension, aperture, and finger pitch as the device IDT; GSG pads; an open or thru in the same pad frame. VNA S11 and the acoustic linewidth. | Qm 2000 main, 3600 literature upper, 1570 assumed conservative. η_IDT 10% main case. Shao’s S11 ≈ −3 dB is that paper’s ≈50% device, not a curve for this chip. | S11, Qm, η_IDT |
| 3 | Functional device + single-ring AO reference | Known RF voltage or power in, optical sideband out. The single ring has the same 100 µm suspended coverage so δω is not mixed with molecule dynamics. ξ = 1 means 21.3 GHz/V in the model. | ξ ∈ {0.3, 0.5, 1, 2} at IDT 10% and Qm 1570: 478 / 172 / 43 / 11 µW. Plan floor: ξ ≥ 0.5, power still ≪ 1 W. | ξ, RF power at the operating point |
| 4 | Functional device + straight reference waveguide | Spectrum of the q=+1 line, the carrier, and spurious orders; on-chip IL from the straight reference, not from the 1.5 dB/facet literature figure. | **Only after step 1.** v2 bar if crosstalk is supported: heater-ON κi×2 p10 (η_shift p10 ≈ 0.917; the measurement-plan IL figure at that percentile is ≈ 3.71 dB; worst spur still q=−1). v1 bar if crosstalk is not supported: η_shift p10 = **0.874**, plus the v1 archive p10 row. | η_shift, IL, carrier, spur order and level |

Predicted v2 heater-ON κi×2 spectrum figures for the step-4 sheet (suite percentiles, not measurements): η_shift p10 / median / p90 = 0.917 / 0.964 / 0.983; IL = 3.71 / 4.72 / 5.72 dB; carrier relative to the shifted line ≈ −25.8 / −16.7 / −11.3 dB; q=−1 relative ≈ −20.2 / −19.4 / −18.8 dB; fraction whose worst spur is q=−1 = 100%.

## Prediction table (do not treat as data from a device)

| Quantity | v2 (current layout assumption) | v1 (fallback) | Status |
|---|---|---|---|
| Crosstalk at Pπ | 2 mK differential, 3 mK common-mode | 5 mK differential, 10 mK common-mode | **ASSUMED** both columns |
| η_shift p10 / median | 0.917 / 0.964 | 0.874 / 0.950 | prediction, heater ON, κi×2 |
| frac(η_shift ≥ 0.90) | 94.0% | 81.9% | prediction |
| Gate ① | PASS under the assumption | **FAIL** | simulation label |
| Conservative RF | ≈172 µW | ≈172 µW (unchanged) | prediction |
| Worst spur | q=−1 | q=−1 | prediction |
| ALL_PASS | simulation-side true **only** under 3/2 mK | not achieved | not a measurement |

## Manuscript rules for this tape-out

- [ ] The abstract describes a design and a measurement plan. Predicted performance stays labeled as predicted.
- [ ] The abstract does not contain ALL_PASS, and it does not contain the crosstalk millikelvin figures, as measured achievements.
- [ ] The five-step measurement plan keeps an empty measured column. Literature Pπ, Zhang’s splitting, and Shao’s Q are not copied into that column.
- [ ] The verified-parameter table does not gain a 2 mK or 3 mK row marked measured or verified.

## Thermal phonons — not a fab gate

At the ideal operating point the design study predicts `N_coh ≈ 1.75×10^11` (Qm = 2000, γ_e/γ = 0.15) and `n_th/N_coh ≈ 1×10^−8` at 300 K. That ratio, and `n_th·C_0`, do not block tape-out and do not select the v1 fallback. No value of `n_th·C_0` is assigned here.

## Sources for the numbers in this note

- v2 suite: heater-ON, κi×2, N=1000, master seed `20261114` (lab summary `summary_heater_xi`, 2026-10-14). Predictions.
- v1 archive: master seed `20261014`. Gate ① FAIL at 81.9%; η_shift p10 / median 0.874 / 0.950. Predictions.
- Device geometry and the ξ = 1 calibration: paperB design notes (ring 0.667 mm, 100 µm suspended section, coverage 0.15, 21.3 GHz/V). Design inputs, not results from this chip.
- This checkout’s `paper/main.tex` is the earlier realistic Monte Carlo (heater not yet in that file). It is not a measured-device paper, and it is not the v2 yield claim.
