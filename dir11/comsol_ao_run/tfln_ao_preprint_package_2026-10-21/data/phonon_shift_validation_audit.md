# Phonon-driven optical frequency-shift validation audit

## Scope

This audit checks what the current suspended 3D finite-aperture IDT eigenmode study can support about phonon-driven optical frequency shifting. It also compares it with older driven data found in the workspace. The older data are from a different 2D geometry and are not substituted for the current 3D result.

## Findings

1. **The 3.3 GHz acoustic eigenfrequency sets a possible sideband spacing, not the amount of optical power shifted.** At a 1550 nm optical carrier, a 3.304 GHz sideband is approximately 26.4 pm away from the carrier. Actual conversion efficiency depends on the voltage-normalized acoustic amplitude, photoelastic and moving-boundary perturbations, acoustic loss, and optical interaction length.
2. **The original aperture comparison is eigenmode-based.** Its exported eigenvectors have arbitrary normalization, so the original photoelastic overlap proxy cannot be converted into volts, phase modulation index, or sideband efficiency. A separate coupled 6 µm model includes a 1 V drive and a mode-projected resonance. A first-order photoelastic-only `delta n_eff/V` has now been estimated using the assumed TE slab-mode and Gaussian optical weighting; it is not based on an actual waveguide eigenmode, omits moving-boundary effects, and does not establish conversion efficiency.
3. **An older 2D driven calculation exists, but it is not the current geometry.** `dir11/photoelastic_p283` uses a 500 nm flat suspended slab, a 2D periodic cell with `p = 2.8326 um`, and a 1 V frequency-domain piezoelectric drive. Its recorded TE photoelastic ring-frequency perturbation is about 1.648 MHz at 3.330092 GHz. The current 3D aperture model uses `p = 2.58 um`, a finite aperture, and a different post-processing model.
4. **The drive calibration is unresolved.** A separate photonic-molecule frequency-shift model uses about 21.256 GHz/V for its ring detuning coefficient, based on a measured MZI `Vpi` from a different suspended device. Comparing that coefficient with the older 2D calculation's 1.648 MHz per 1 V gives a numerical gap of about 1.29 x 10^4. Because the structures and reported quantities are not yet shown to be equivalent, this is a warning that requires a like-for-like calibration; it is not evidence by itself that either result is wrong.
5. **Frequency shifting must be named precisely.** A driven acoustic mode at frequency `fa` can create optical sidebands at `fopt +/- fa`. A standing-wave eigenmode plus sinusoidal phase modulation generally gives both Stokes and anti-Stokes sidebands. A one-way frequency shifter additionally needs a mechanism for selecting one sideband and suppressing the carrier, such as phase-matched traveling-wave scattering or an interferometric/cavity scheme.

## Current conclusion

The current data support a candidate acoustic resonance near 3.3 GHz, a photoelastic spatial-overlap comparison, a simulated 1 V electromechanical resonance in a separate 6 µm model, and a first-order photoelastic-only optical perturbation estimate per volt under assumed optical weighting. They do **not** yet establish a phonon-driven optical frequency shifter, a conversion efficiency, or a source-power advantage. The sideband spacing is a plausible application target; optical conversion performance remains unverified.

## Required next numerical checks

1. Confirm the electrical drive and short-circuit eigenmode boundary equivalence, then repeat the mode-projected response on a second mesh and verify the resonance shape.
2. Refine the mode-projected complex response around the resonance, establish mass/energy normalization and the model linewidth under a justified loss factor, and report voltage-normalized displacement and strain.
3. Replace the assumed slab/Gaussian weighting with the actual waveguide optical eigenmode and include both photoelastic and moving-boundary terms where applicable. The current derived data are only a photoelastic-only estimate per applied volt.
4. Convert the complex perturbation into phase-modulation index or a coupled-mode coefficient; then calculate Stokes/anti-Stokes sidebands, carrier suppression, and conversion efficiency with an explicitly stated optical architecture.
5. Repeat the mode-projected driven response on a second mesh level and track the same physical mode.
6. Reconcile voltage normalization and definitions against the older 2D drive result and the measured `Vpi` calibration before making any RF-power comparison.

Until these checks are done, keep the manuscript's frequency-shift discussion framed as motivation or potential application rather than demonstrated performance.

## Additional 3D driven-response attempt (2026-10-20)

A 1 V harmonic study was added to a copy of the refined 6 um model at the tracked 3.291194 GHz mode, using an assumed structural loss factor `eta_s = 5e-4` (nominal Q about 2000). The solver completed, and the LN-domain average of `|V|` was about 0.15 V, but the reported LN displacement and strain integrals were exactly zero at all sampled frequencies. This is not a physical zero-coupling result: it indicates that the electrical-to-mechanical coupling or result-variable binding is not functioning in this model variant. The run and its zero-valued CSV are invalid for performance analysis and must not be cited.

The initial model copy required repair of the terminal/electrode boundary assignment and addition of the piezoelectric charge-conservation equation. The corrected model now produces nonzero displacement and strain; see the follow-up sections below. The original eigenmode sweep remains unchanged.
## Follow-up verification (2026-10-21)

The initial zero-response result was traced to two missing/inconsistent parts in the driven-model copy:

- The positive- and negative-electrode box selections both included the same LN top boundary when using an intersection rule. Tightening those selections to faces fully inside each contact window produces separate contact faces (entities 7 and 13 in the 6 um geometry).
- The 3D model lacked the ChargeConservationPiezo feature present in the earlier working 2D driven model. Adding it on the LN domain produces a nonzero 1 V response in a copied model.

At 3.3044 GHz, with an assumed structural loss factor of 5e-4, the corrected fine-mesh copy reports average absolute displacement components of approximately 7.8, 1.5, and 6.5 pm over the LN volume, and average absolute normal strains of order 10^-5. This proves that the corrected model can return a nonzero driven mechanical field. It is not yet a calibrated optical frequency-shift result.

Adding the piezoelectric charge-conservation equation shifts the nearby short-circuit coupled eigenfrequency to 3.305664 GHz in the 100/50 nm model. Early volume-average samples did not reveal a peak, but a later complex-field projection onto the matching eigenvector resolves a clear modal response maximum at this frequency. The projection is relative and unweighted; a physical modal amplitude, linewidth/Q, and voltage-normalized optical overlap remain unverified.

The candidate coupled mode has now been matched by displacement shape across four mesh levels: 3.337995, 3.305664, 3.294186, and 3.290168 GHz, with nearest-node shape correlations of 0.973, 0.994, and 0.995 between successive levels. Frequency drift decreases with refinement but has not been extrapolated. The aperture recommendation from the original eigenmode overlap remains provisional because this coupled-mode tracking was done only at 6 µm.

The latest model variants and logs are isolated under D:\comsol_ao_run\convergence; they do not alter the repository's original eigenmode files. The earlier zero-valued CSV remains invalid. Current status: electrode selections and electromechanical coupling are corrected; the target mode has a clear unweighted modal-projection peak on one mesh; mesh-converged absolute drive response, actual-mode optical perturbation including moving-boundary terms, and experimental validation remain pending.

## Coupled-mode tracking and driven sweep (2026-10-21)

### Mesh-to-mesh mode tracking

The same short-circuit coupled mode was tracked by comparing real displacement vectors on LN nodes, after nearest-node mapping between meshes; this is an unweighted node-sample shape correlation, not a mass-weighted MAC. The best-pair MAC values and frequencies are:

| LN/Al target mesh | Mode index | Frequency | MAC to next finer mesh |
|---|---:|---:|---:|
| 150/80 nm | 4 | 3.337995 GHz | 0.973 to 100/50 nm mode 2 |
| 100/50 nm | 2 | 3.305664 GHz | 0.994 to 75/38 nm mode 2 |
| 75/38 nm | 2 | 3.294186 GHz | 0.995 to 65/33 nm mode 2 |
| 65/33 nm | 2 | 3.290168 GHz | — |

The tracked mode is consistent by shape, but its frequency shifts monotonically downward. The last refinement changes the frequency by 4.018 MHz (0.122%); the 100-to-65 nm change is 15.496 MHz (0.469%). This supports mode identity and indicates reduced mesh sensitivity, but it is not a fully extrapolated frequency or proof of convergence to a chosen tolerance. The 65/33 nm mesh has about 1.18 million tetrahedra; its eigen solve used an iterative solver after COMSOL reported that MUMPS could not use its out-of-core fallback. All 12 eigenvalues converged in the iterative run.

### 1 V frequency response

The corrected 100/50 nm driven model was first swept from 3.285 to 3.296 GHz in 1 MHz steps, using a 1 V terminal drive, the opposite terminal grounded, ChargeConservationPiezo on LN, and assumed structural loss factor `eta_s = 5e-4`. All 12 points converged. This band is below the corresponding 100/50 nm short-circuit coupled eigenmode at 3.305664 GHz, so this sweep is an off-resonance background reference and is not evidence about that mode’s peak. The component-wise LN volume averages of absolute displacement rose smoothly from 5.98, 1.23, and 5.60 pm to 6.83, 1.34, and 6.01 pm (x, y, and z components). A volume average of the displacement-vector magnitude was not computed.

A second, coarser sweep at 3.304, 3.306, 3.308, 3.310, and 3.312 GHz includes the 3.305664 GHz 100/50 nm eigenmode but uses 2 MHz spacing. It does not show a clear peak in the sampled component-wise averages, but the spacing is too coarse to resolve the expected narrow response reliably. The driven boundary setup is 1 V on `selGp` and ground on `selGn`; the short-circuit eigenmode grounds both electrode faces, which is intended to represent the same small-signal eigenfrequency.

### Updated status

Completed: repaired contact selections and piezoelectric charge-conservation equation; obtained nonzero 1 V response; tracked the coupled eigenmode across four mesh levels; completed a broad and a fine driven sweep; projected the complex response onto the same-mesh eigenmode and found a resonance peak.

Still unverified: mass/energy-normalized modal amplitude and a mesh/damping-validated linewidth/Q; mesh-converged, actual-mode voltage-normalized optical perturbation; moving-boundary optical overlap; modulation index/sideband efficiency for a specified optical architecture; consistency with the older 2D voltage calibration; experimental chip measurements. The current calculations support a candidate coupled acoustic mode near 3.3 GHz and a simulated mode-projected 1 V response. They do not yet establish practical optical frequency shifting or its efficiency.

### Photoelastic-only optical perturbation per volt

The complex driven strain fields from the five-point fine sweep were post-processed with the same scalar TE slab-mode intensity profile (`n_e = 2.138`) and 1 µm-FWHM Gaussian lateral optical weighting used for the original screening calculation. This gives a first-order photoelastic-only effective-index perturbation per applied terminal volt; the optical field is an assumed weighting, not a solved waveguide eigenmode. Moving-boundary effects, vectorial optical fields, and optical mode normalization are not included.

At 3.305664 GHz, the largest value in the chosen interior band (waveguide centers 4–6 µm) is `|delta n_eff| = 1.610e-7/V` at 6.0 µm; the value at the earlier 5.5 µm recommendation is `1.545e-7/V`. In the edge bands (2–3 µm and 7–8 µm), the maximum is `1.266e-7/V` at 7.0 µm, giving edge/interior = 0.786. Thus, for this driven field and assumed optical weighting, the interior maximum exceeds the edge maximum by about 21%. This differs from the original arbitrary-normalized eigenmode proxy and must not be generalized to the full aperture sweep or treated as an experimental edge-placement result.

The derived phase perturbation at 5.5 µm is `0.000626 rad mm^-1 V^-1` at resonance. This remains a model-dependent, first-order estimate: no actual optical eigenmode, moving-boundary contribution, independently validated drive calibration, or sideband conversion calculation is included. The profile and summary are in `data/coupled_drive/driven_photoelastic_profile_1V.csv` and `data/coupled_drive/driven_photoelastic_summary_1V.csv`; the plot is `images/drive_photoelastic_per_V.png`.


### Fine scan around the matching 100/50 nm eigenmode

The broad 2 MHz sweep was followed by a 0.5 MHz-spaced sweep at 3.304664, 3.305164, 3.305664, 3.306164, and 3.306664 GHz. All five points converged. The volume-averaged displacement components rise mostly smoothly and show only small component-specific features. To isolate the target mode, the complex displacement field at each frequency was projected onto the 3.305664 GHz coupled eigenvector on the exact same LN node set (46,647 nodes). The normalized projection magnitudes at detunings -1, -0.5, 0, +0.5, and +1 MHz are 0.480, 0.740, 1.000, 0.758, and 0.504; its phase also rotates through the central frequency. This resolves a clear mode-projected resonance centered at the 100/50 nm coupled eigenfrequency, showing that the IDT excites the tracked mode in this model. The projection is an unweighted nodal overlap and is normalized only relative to its maximum, so it is not an absolute modal amplitude or a mass-weighted generalized coordinate. The broader same-mesh projection also falls to 0.250, 0.145, and 0.105 at detunings +2.336, +4.336, and +6.336 MHz, respectively, confirming decay away from the peak. A single-pole complex Lorentzian fit to all ten points, with free center and width, gives a center of 3.305676 GHz, FWHM 1.132 MHz, and Q≈2,920 with 1.02% normalized RMS residual. This is a preliminary simulated Q under the assumed LN structural loss factor, not a measured or mesh-validated Q. The fit summary and plot are saved under `data/coupled_drive/`.

