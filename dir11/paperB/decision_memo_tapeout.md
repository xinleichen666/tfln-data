# Decision memo · Dir1 resonant AO photonic-molecule frequency shifter

**Date:** 2026-10-14  
**Device:** forward, single-bus dual-ring acousto-optic frequency shifter on TFLN (paper B design study). Concept unchanged.  
**Decision:** **GO** for tape-out, under a hard Step-1 gate.  
**Not this decision:** a coupler redesign before the first mask, a methods-only paper, or a measured performance claim.

Locked inputs: heater-ON Monte Carlo v2, seed master `20261114`, N=1000 (`summary_heater_xi.json`); v1 archive seed `20261014`; fab criteria; five-step measurement plan; literature table. This checkout’s `paper/main.tex` still reports the earlier realistic Monte Carlo and still says an inter-ring heater was not modeled. This memo does not rewrite that manuscript.

## Verdict

**GO.** Send the mask with the cells below. Simulation gate ① is **PASS only inside the v2 crosstalk assumption** (heater ON, κi×2, IDT 10%: η≥0.90 in **94.0%** of samples; η p10/median **0.917 / 0.964**). The same suite with the looser v1 assumption fails gate ① (**81.9%**, η p10 **0.874**). Gates ② and ③ do not depend on that assumption: conservative RF ξ=0.5 × IDT 10% × Qm=1570 is **172 µW** (② PASS against the Shao 2020 1 W AO drive), and the worst spur remains q=−1 in the v2 suite (③ PASS). Those two gates stay simulation results until Steps 2–4 measure them, and they do not keep an ALL_PASS label if Step 1 fails.

The 3 mK / 2 mK figures are layout assumptions. The literature table has **no same-geometry published crosstalk**. They stay out of the published-number column and out of the abstract.

A pre-fab isolation redesign is the wrong hold. Nothing in the literature table calibrates a thermal model to this coupler–ring geometry, so another simulation round would not retire the assumption. The first chip is the measurement. Isolation features go on **this** mask as design intent. If they miss ~3/2 mK, the rollback below is the redesign trigger for the next mask.

## What the checklist still gets wrong

The written Step-1 sequence (lock the rings, then sweep the coupler) can hide the quantity the gate is about. Lock heaters that servo during the sweep cancel differential detuning and can shrink the apparent common-mode shift. A device with v1-class crosstalk (10 mK common-mode, 5 mK differential at Pπ) could then look consistent with v2. **Step 1 PASS is an open-loop measurement**, with ring heaters off or parked at a recorded fixed bias.

A value between the v1 and v2 assumptions is still a Step-1 **FAIL** for the v2 narrative. Do not interpolate a yield. A later Monte Carlo at the measured crosstalk is a new analysis, not an ALL_PASS on this tape-out.

## Locked rollback (verbatim)

```
If Step 1 FAIL (cannot achieve ~3/2 mK), revert to v1 narrative (gate ① FAIL), Step 4 accept at v1 p10 η≈0.874 — do NOT claim ALL_PASS. If Step 1 PASS, use v2 p10≈0.917.
```

Companion lines already in the measurement plan, used with that rule: Step 4 IL p10 is 3.71 dB on the v2 branch and 3.70 dB on the v1 branch. The Shao-Qi heater-ON column (η≥0.90 in 98.8%) is not the acceptance yield.

## Mask (minimum that makes Steps 1–5 measurable)

Functional layout. Foundry layers follow the process deck. Pad map in the GDS notes and the traveler: H1 ring-1 lock, H2 ring-2 lock, HC MZI coupler heater, IDT GSG, heater return, RF return.

| Cell | On the mask | Step |
|---|---|---|
| **TS1** | Dual ring, single bus to ring 1 only, ring–ring **MZI** (two arms + directional-coupler sections), **HC / H1 / H2 on three electrically independent pads**, heater returns separate from the RF return. Isolation aimed at the v2 assumption: coupler arm pulled off both rings, no continuous metal heat bridge from HC into either ring, lock-heater metal on a separate thermal path, trenches or air slots on the coupler-to-ring path where the deck allows. If the deck has no trench, spacing plus the broken metal bridge still ships, and Step 1 still governs. | 1 |
| **Ref** | One bus-coupled ring, same waveguide cross-section, no local heater and no membrane, on the same die. Drift monitor for Step 1. | 1 |
| **TS2** | IDT into the suspended cavity, GSG, plus an on-reticle GSG open or thru so S11 is not a bare pad artifact. | 2 |
| **TS3** | Full shifter: TS1 optics + ~0.667 mm ring intent, ~100 µm of ring 1 in the suspended cavity (coverage ~0.15), IDT. RF off, this cell may also serve Step 1 if the reticle cannot hold a separate optical twin. | 3, 4 |
| **TS4** | Straight waveguide, same facet process, for on-chip insertion loss. Facet loss is logged on its own and is not copied into the prediction column. | 4 |
| **TS5** | Further full-shifter copies. One of them is reserved for HOM after some copy has passed Step 4. No extra circuit. | 5 |

Repeated full shifters are for a later yield count. One Step-4 device is not the 94% Monte Carlo yield.

Coupler law on the traveler: self-scaled MZI, µ = µ_gap sin(Δφ/2), design µ_max = √2 · (Ω/2). That is a textbook model. It is not a Zhang 2019 µ(φ). Heater-arm Pπ in the Monte Carlo is **44.4 mW, Maeder geometric assumption** (≈1 mm Au arm), not a calibration of this ring–ring coupler.

## What is measured before any performance claim

**Step 1, before Steps 2–5 are treated as the v2 device.**

1. Heaters off. Step the stage temperature. Record df/dT on both molecule resonances and on the reference ring. That slope is the on-chip conversion. The simulation df/dT is not the measurement.
2. Park H1 and H2 (off, or a fixed recorded bias). Do not servo them. Sweep **only HC**. Record dissipated power from a source-measure unit on HC’s own pads. Do not infer power from the Maeder resistance or from 44.4 mW.
3. From the bus spectrum record the doublet center, the splitting 2µ, and the differential asymmetry. Common-mode crosstalk is the molecule center **relative to the reference ring**. Differential crosstalk is the relative motion of the two rings.
4. Pπ is the dissipated HC power that produces a π phase on this arm, read from the splitting swing. Evaluate dT_cm and dT_diff at **that** Pπ. If the arm cannot reach that phase, extrapolate the open-loop slope linearly in power, label the comparison extrapolated, and apply the same ~3/2 mK test. If the sweep cannot put |2µ−Ω| inside the ±1 MHz RF window, Step 1 is FAIL regardless of slope.
5. PASS only when the open-loop result is compatible with **~3 mK common-mode and ~2 mK differential at that Pπ**, and the ±1 MHz window is reachable. Then the lock heaters may be closed, as a separate check that the residual stays in the window. The closed-loop residual is not the crosstalk result.
6. Write the measured slopes into the lab book as measurements. Leave the literature table’s published-number column empty for this crosstalk.

**After the branch is chosen**

| Step | Claim allowed only if |
|---|---|
| 2 | IDT S11 and acoustic Q on TS2. Acceptance intent: Qa at or above the conservative 1570 and consistent with the power budget; η_IDT at the 10% main-column floor, or measured RF power still far below the Shao 1 W drive. |
| 3 | ξ from sideband strength versus RF voltage on TS3. ξ=1 means δω/2π = 21.3 GHz/V. Floor used for gate ②: ξ≥0.5. |
| 4 | Spectrum on a device that took the Step-1 branch above. Acceptance is that branch’s p10 (v2 **0.917** or v1 **0.874**), on-chip IL from TS4 subtraction, worst spur still q=−1. |
| 5 | HOM only after Step 4 meets the active p10. Same device class. No HOM if Step 4 misses. |

Gate ② is a comparison with the Shao 1 W acousto-optic drive. This tape-out adds **no** claim that the AO shifter beats a matched electro-optic drive on source power. That comparison stays the one already in the design study.

## HOLD triggers

Hold the GDS if any of these is missing:

- three electrically independent heaters (H1, H2, HC), or
- a ring–ring MZI whose phase is set by HC, or
- a bus spectrum that shows both the doublet center and the splitting with H1/H2 frozen, or
- the isolation intent (arm spacing, no metal heat bridge, separate lock-heater path), or
- this Step-1 rollback written into the traveler.

Missing trenches alone are not a hold. A redesign of µ, of the single-bus molecule, or of the IDT is not a hold on this mask.

## GDS release checks

- [ ] Dual ring, single bus, splitting target aligned to 3.33 GHz
- [ ] MZI coupler; HC independent; Maeder 44.4 mW marked as a geometric assumption
- [ ] Isolation intent drawn toward the 3/2 mK assumption
- [ ] H1, H2, HC on separate pads; pad map on the GDS
- [ ] Reference ring; GSG open or thru; straight waveguide; repeated full shifters
- [ ] Traveler states open-loop Step 1 and the verbatim rollback
- [ ] Literature table still has no published mK crosstalk; abstract has no ALL_PASS
