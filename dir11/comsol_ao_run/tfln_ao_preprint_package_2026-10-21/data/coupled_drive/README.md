# Coupled 6 µm model: validation data

These are derived data exports from exploratory COMSOL 6.3 model copies. They are separate from the original 12-aperture eigenmode sweep used for the photoelastic overlap figures.

- `tracked_coupled_mode_meshes.csv`: short-circuit coupled eigenmode tracked across four LN/Al mesh settings. Mode identity uses nearest-node displacement-field MAC. Frequencies continue to drift downward; these values do not establish asymptotic convergence.
- `coupled_eigenmodes_65nm.csv`: all 12 coupled eigenfrequencies from the finest run (LN/Al hmax 65/33 nm; 1.18 million tetrahedra). The iterative eigensolver converged all 12 modes after COMSOL reported that MUMPS could not use its out-of-core fallback for this run.
- `drive_sweep_3285_3296GHz.csv`: 1 V frequency-domain driven response, 3.285–3.296 GHz in 1 MHz increments.
- `drive_sweep_3304_3312GHz.csv`: coarse 1 V frequency-domain sweep that includes the 100/50 nm tracked mode.
- `drive_sweep_3p304664_3p306664GHz.csv`: 0.5 MHz-spaced 1 V frequency-domain sweep centered on the matching 100/50 nm coupled eigenmode at 3.305664 GHz.
- `mode_projected_drive_response.csv`: complex driven displacement projected onto that same-mesh eigenmode at five fine-sweep and five coarse-sweep frequencies. The projection is unweighted and normalized relative to its peak; use it to compare frequency response, not as an absolute modal coordinate.
- `modal_projection_fit_summary.csv`: preliminary single-pole complex Lorentzian fit to the 10-point modal projection. The fitted linewidth and Q rely on the assumed structural loss and have not been validated against a second mesh or measurements.
- `driven_photoelastic_profile_1V.csv`: first-order complex effective-index perturbation per 1 V versus waveguide center and drive frequency, computed from driven strain using the assumed TE slab-mode weighting and 1 µm-FWHM Gaussian optical intensity.
- `driven_photoelastic_summary_1V.csv`: interior and edge maxima and the value at the previously recommended 5.5 µm center for each fine-sweep frequency.

The driven sweeps used corrected separated electrode selections, ChargeConservationPiezo on LN, one terminal at 1 V and the other grounded, and assumed structural loss factor `eta_s = 5e-4`. Displacement and strain columns are LN volume averages of absolute values. The same-mesh mode projection has a clear peak near 3.3057 GHz. The peak-normalized projection does not establish an absolute modal coordinate or mesh-validated linewidth. The derived optical CSVs give a first-order photoelastic-only `delta n_eff/V` using the assumed TE slab profile and Gaussian weighting; they are not based on an actual waveguide eigenmode and omit moving-boundary effects. They do not establish phase-modulation index or sideband efficiency, and the assumed loss is not measured. See `../phonon_shift_validation_audit.md` for interpretation and remaining limitations.

