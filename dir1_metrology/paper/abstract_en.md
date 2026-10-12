# Abstract (English) · Direction-1 metrology noise budget (ex-adaptive-poling / run7)

**Manuscript working title (EN):** A metrology noise budget for film-thickness sampling and SPDC heralded-purity upper bounds on thin-film lithium niobate

**Genre / venue target (Cursor A lock):** **PRA methods · noise budget** body tone; **preprint first**. **Not** an Optics Express device-design narrative.

## Abstract

We present a **metrology noise budget** that maps film-thickness sampling pitch and assumed measurement error onto Monte Carlo **upper bounds** on the heralded spectral purity of a type-II SPDC source on x-cut thin-film lithium niobate (TFLN). Adapted poling is only a compensation operator on the metrology samples; we do **not** sell a fabricable length. Thickness traces are public wafer data (Chen *et al.*; Xin *et al.*); group-velocity mismatch, poling period, and thickness/width/etch phase coefficients are one self-consistent TM-pump solve (`tm_coeff.json`). Baseline assumptions (width RMS 2 nm, thickness measurement error 0.3 nm, N = 64, seed 2027): uncompensated 5 mm median purity 0.574 (10th–90th 0.448–0.791). The **only** main-table **stable** point with both median and 10th percentile ≥ 0.90 is **5 mm at 0.04 mm pitch** (0.969; 0.932–0.982). The 10 mm row at the same pitch is reported **as a distribution only** (median 0.906 / 10th 0.855) and is **never** a design point. Raising width noise to 10 nm or measurement error to 1 nm collapses these medians. Round-6 TE-mixed design stories are obsolete under the TM set. **Simulation + public wafer traces only; no in-house fab; no invented measurements.** **Internal use only (research group): simulation and scheme working draft; measurements pending; no fabricated data; Fiber-Q N/A for this direction; no in-house fab; not for public citation. No third-party verify/ PDFs in repo. Make the repository private after the drafts are finished.**

## Keywords

thin-film lithium niobate; film-thickness metrology; adapted poling; SPDC; heralded purity; Monte Carlo upper bound; noise budget

## Notes (internal, not for preprint body)

- Framing (Cursor A): **metrology noise budget** (PRA methods); stable point **only** 5 mm @ 0.04 mm; 10 mm = distribution only (median 0.906 / 10th 0.855), never design point.
- All headline numbers from `upstream_dir01/data/run7.json` / `report_v7.md`.
- Hang-repo disclaimer retained (group-internal; sim+scheme; pending; no fab; no verify/).
