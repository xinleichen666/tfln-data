# Simulation validation notes

## What was checked

- **Post-processing grid:** Recomputed the baseline 6 and 10 µm candidates on a grid increased from 130 × 25 samples with 0.1 µm z spacing to 195 × 38 samples with 0.05 µm z spacing. Interior overlap changed by -0.02% (6 µm) and +0.46% (10 µm). Edge maxima changed by +3.14% and -5.82%.
- **Optical spot width:** In the full baseline sweep, TE with 0.5, 1.0, and 1.5 µm intensity FWHM all selected 6 µm. For 1.5 µm the selected mode changes. This has not been rerun for all apertures at refined mesh.
- **Finite-element mesh audit:** Re-ran 6 and 10 µm with tighter mesh limits: LN hmax/hmin 100/25 nm; Al 50/12 nm. Baseline limits were LN 150/40 nm and Al 80/20 nm.
- **Mode tracking:** Compared the TE photoelastic strain scalar on a shared 3D grid using absolute normalized inner product. The 6 µm baseline winner maps most strongly to refined mode 2 (correlation 0.915), but its frequency moves from 3.304066 to 3.291194 GHz and its interior proxy changes from 39.54 to 35.42 J^-1/2. For 10 µm, the best shape correlation is only 0.420, so a reliable one-to-one mode match is not established.

## Interpretation

The post-processing sample grid is stable for the two checked modes. The finite-element mesh and the selected mode/aperture ranking are not yet converged. In particular, the refined 10 µm run selects mode 11 at 3.364042 GHz with 111.82 J^-1/2, while this mode has only 0.219 shape correlation with the baseline 10 µm winner. Do not claim that 6 µm is the established optimum yet. It remains a promising candidate near 3.3 GHz.

## Remaining numerical work

1. Add a third mesh level and check frequency/overlap trends against element count.
2. Repeat the full 12-aperture scan with the refined mesh and track branches by field overlap.
3. Recheck TE/TM spot-width ranking on the refined sweep.
4. Verify the crystal-axis/photoelastic tensor mapping and run material-parameter sensitivity.
5. If making claims about drive efficiency, solve the driven piezoelectric response with realistic electrical and mechanical boundaries.

Fabrication is not required to complete a simulation-only manuscript, but it is required for experimental performance claims.
