# Abstract (English) · Direction-1 metrology rewrite (ex-adaptive-poling / run7)

**Manuscript working title (EN):** Film-thickness metrology spacing and SPDC heralded-purity upper bounds on thin-film lithium niobate

**Genre / venue target:** PRA / OE methods·noise-budget style / preprint-first. **Not** an Optics Express device-design narrative.

## Abstract

This work maps **film-thickness metrology**—sampling pitch along the waveguide and assumed measurement error—onto Monte Carlo **upper bounds** on the heralded spectral purity of a type-II SPDC source on x-cut thin-film lithium niobate (TFLN). Adapted poling is treated only as a compensation operator that uses the metrology samples; we do **not** sell a fabricable device length or a recommended design point. Thickness traces are taken from public wafer data (Chen *et al.*; Xin *et al.*); group-velocity mismatch, poling period, and thickness/width/etch phase coefficients are a single self-consistent TM-pump mode solve (`tm_coeff.json`). With baseline assumptions (width RMS 2 nm, thickness measurement error 0.3 nm, N = 64, seed 2027), an uncompensated 5 mm segment has median purity 0.574 (10th–90th 0.448–0.791). Holding **median** purity ≥ 0.90 requires metrology no coarser than every 0.2 mm at 5 mm, or every 0.04 mm to stretch the median to 10 mm (0.906)—but that 10 mm case has 10th percentile 0.855 and **must not** be read as a stable ≥ 0.90 design point. The only main-table entry whose 10th percentile also clears 0.90 is 5 mm at 0.04 mm pitch (0.969; 0.932–0.982). Raising width noise to 10 nm or measurement error to 1 nm collapses these medians. Round-6 TE-mixed design stories are obsolete under the TM set. **Simulation + public wafer traces only; no in-house fab; no invented measurements.** **Internal use only (research group): simulation and scheme working draft; measurements pending; no fabricated data; Fiber-Q N/A for this direction; no in-house fab; not for public citation. No third-party verify/ PDFs in repo. Make the repository private after the drafts are finished.**

## Keywords

thin-film lithium niobate; film-thickness metrology; adapted poling; SPDC; heralded purity; Monte Carlo upper bound; noise budget

## Notes (internal, not for preprint body)

- Framing: **metrology → bound / prescription under assumptions**, not 「推荐 10 mm 器件设计点」.
- All headline numbers from `upstream_dir01/data/run7.json` / `report_v7.md`.
- Hang-repo disclaimer retained (group-internal; sim+scheme; pending; no fab; no verify/).
