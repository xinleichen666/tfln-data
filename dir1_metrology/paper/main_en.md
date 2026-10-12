# A metrology noise budget for film-thickness sampling and SPDC heralded-purity upper bounds on thin-film lithium niobate

**Chinese title:** 膜厚计量噪声预算：TFLN 上 SPDC 预告纯度上界（方向一 · PRA 方法·噪声预算工作稿）

**Genre / venue target (Cursor A lock):** **PRA methods · noise budget** body tone; **preprint first**. Product: metrology noise budget → purity **upper bounds** under stated spacing/error assumptions. **Only** main-table stable point: **5 mm @ Δz = 0.04 mm**. **10 mm** reported as distribution only (median 0.906 / 10th 0.855)—**never** a design point. **Not** an OE device-design paper.

**Number lock:** `/workspace/dir01/report_v7.md`, `data/run7.json`, `data/tm_coeff.json`, and this pack’s `run7_summary.json` / `params_table.md`. Primary numbers are **not** recomputed here.

**Superseded draft:** `/workspace/dir01/paper/main.tex` (Optics Express device-design narrative, including a 10 mm design-point tone) is **withdrawn** as the main frame. Round-6 TE-mixed medians **must not** be used as design points.

> **Preprint status (2026-10-12):** **Simulation + public wafer traces**; no in-house fab; no invented measurements; measured cells empty.
>
> **Hang-repo disclaimer:** Internal use only (research group): simulation and scheme working draft; measurements pending; no fabricated data; Fiber-Q N/A for this direction; no in-house fab; not for public citation. No third-party verify/ PDFs in repo. Make the repository private after the drafts are finished.

Companion files: Chinese body `main_zh.md`; standalone abstract `abstract_en.md`; forbidden claims `non_claims.md`.

---

## Abstract

We present a **metrology noise budget** that maps film-thickness sampling pitch and assumed measurement error onto Monte Carlo **upper bounds** on the heralded spectral purity of a type-II SPDC source on x-cut thin-film lithium niobate (TFLN). Adapted poling is only a compensation operator on the metrology samples; we do **not** sell a fabricable length. Thickness traces are public wafer data (Chen *et al.*; Xin *et al.*); group-velocity mismatch, poling period, and thickness/width/etch phase coefficients are one self-consistent TM-pump solve (`tm_coeff.json`). Baseline assumptions (width RMS 2 nm, thickness measurement error 0.3 nm, N = 64, seed 2027): uncompensated 5 mm median purity 0.574 (10th–90th 0.448–0.791). The **only** main-table **stable** point with both median and 10th percentile ≥ 0.90 is **5 mm at 0.04 mm pitch** (0.969; 0.932–0.982). The 10 mm row at the same pitch is reported **as a distribution only** (median 0.906 / 10th 0.855) and is **never** a design point. Raising width noise to 10 nm or measurement error to 1 nm collapses these medians. Round-6 TE-mixed design stories are obsolete under the TM set. **Simulation + public wafer traces only; no in-house fab; no invented measurements.** **Internal use only (research group): simulation and scheme working draft; measurements pending; no fabricated data; Fiber-Q N/A for this direction; no in-house fab; not for public citation. No third-party verify/ PDFs in repo. Make the repository private after the drafts are finished.**

**Keywords:** thin-film lithium niobate; film-thickness metrology; adapted poling; SPDC; heralded purity; Monte Carlo upper bound; noise budget

---

## 1. Introduction: a metrology noise budget, not a device recipe

This manuscript is a **PRA-style methods · noise-budget** note (preprint first): it budgets how film-thickness **metrology** limits heralded SPDC purity on TFLN. A heralded photon is useful only if its partner pins the signal spectral state; on TFLN that first means whether **quasi-phase matching survives the grown film**. Kuttner *et al.* reported type-II JSI purities near 95% (phase-matching estimates near 98%) on x-cut TFLN [Kuttner2026]. Chen *et al.* and Xin *et al.* recovered **classical** SHG efficiency or wavelength yield with adapted / non-periodic QPM [Chen2024, Xin2025], but did not turn public thickness traces into a **heralded-purity metrology noise budget**. Waveguide-error budgets [Santandrea2019], thickness-compensation notes without purity [Babel2025], loss/sensitivity anchors [ZhaoLu2023], deleted-domain poling [Tambasco2016], and Sellmeier constants [Zelmon1997] are method context only—not fabricable design recipes.

An earlier Direction-1 draft read as an **Optics Express device-design** paper (“longer + denser metrology → recommended design point,” including 10 mm). That frame is rejected. Round 6 mixed TE group-velocity ratio and period under a partial TM thickness update; those design points are void. **Cursor A lock** for this draft:

> **Metrology noise budget:** given pitch and measurement-error assumptions, what MC purity upper bound follows? The **only** main-table point that is **stable** (median **and** 10th percentile ≥ 0.90) is **5 mm @ 0.04 mm**. Report **10 mm** only as a distribution (median 0.906 / 10th 0.855)—**never** as a design point.

Adapted poling is a compensation operator on metrology samples, not a product definition.

---

## 2. Methods

### 2.1 Process and self-consistent coefficients

The process follows Kuttner’s type-II assignment: x-cut film; TM pump at 764 nm; TE signal and TM idler near 1528 nm. Geometric center: film thickness \(t = 0.6\,\mu\mathrm{m}\); **waveguide width 1.4 µm and etch depth 0.3 µm are assumptions** (not stated in the source paper). Modes and Sellmeier follow the upstream solver. All phase and group-velocity coefficients in this round come from one TM-pump solve in `tm_coeff.json`:

| Quantity | Value |
|---|---|
| \(S_t\) (local, 600 nm) | −3.129 rad/mm/nm |
| \(A\), \(B\) | 0.573, −0.120 ps/mm |
| \(\Lambda\) | 2.826 µm |
| \(S_w\), \(S_h\) | −0.335, +0.517 rad/mm/nm |

The 560–640 nm secant −3.161 rad/mm/nm is **not** used. Ideal (zero-fluctuation) purity is **0.995** at every length; pump duration \(\tau\) is optimized per \(L\) (report_v7 §1).

### 2.2 Monte Carlo and the metrology operator

- Seed 2027; \(N = 64\) draws at each \(L \in \{2,5,10,15,20\}\) mm.
- Film thickness: **public traces** from Chen Fig. 1d and Xin Fig. 2b; for \(L \le 5\) mm the two sources are split evenly; longer devices use Chen only.
- Baseline width fluctuation: 2 nm RMS (1/\(f\), **assumed**); etch fluctuation ~0.2 nm; residual pump chirp \(\pm 0.25\,\tau^2\).
- **Uncompensated:** phase \(= S_t\cdot\delta t + S_w\cdot\delta w + S_h\cdot\delta h\).
- **Compensated:** sample thickness along \(z\) at pitch \(\Delta z \in \{0.2, 0.1, 0.04\}\) mm, add measurement noise \(\varepsilon = 0.3\) nm on the main table (stress test: 1 nm), interpolate, and subtract \(S_t\cdot\delta t_\mathrm{meas}\).
- Loss enters only the heralding efficiency \(\eta_h\); it is **not** folded into the raw JSA norm \(B\) stored in the JSON. The purity main curve is not propped up by loss.

Implementation: `run7.py`; raw samples: `data/run7.json`.

### 2.3 Reading rules (fixed)

1. Tabulated purities are **Monte Carlo upper bounds** under the stated noise and compensation model—**not** measured device results.
2. “Longest \(L\) with median ≥ 0.90” is a **metrology prescription**, not a recommended fab point.
3. If the 10th percentile is below 0.90, the text **must** state that purity does **not** stay stably above 0.90.
4. Do **not** divide \(B\) across different lengths and call the ratio a poling “gain.”

---

## 3. Results

### 3.1 Main figure: purity versus length × metrology pitch

**Fig. main** `fig/purity_vs_L.png`: median curves versus \(L\) for each \(\Delta z\), with 10th–90th percentile bands.

Mandatory caption line:

> **MC upper bound under stated assumptions (width RMS 2 nm, meas. err. 0.3 nm). Not a measured device result.**

Median summary (full percentiles in report_v7 §3 and `run7_summary.json`):

| \(L\) (mm) | Uncompensated | 0.2 mm | 0.1 mm | 0.04 mm |
|---|---|---|---|---|
| 2 | 0.941 | 0.972 | 0.977 | 0.984 |
| 5 | **0.574** | 0.916 | 0.950 | 0.969 |
| 10 | 0.372 | 0.789 | 0.879 | **0.906** |
| 15 | 0.255 | 0.671 | 0.790 | 0.849 |
| 20 | 0.162 | 0.579 | 0.717 | 0.756 |

At 5 mm uncompensated the median is already 0.574 (0.448–0.791): on public-trace scales, discussing long-device purity without metrology is empty.

### 3.2 Prescription figure: how long can median ≥ 0.90 go?

**Fig. prescription** `fig/metrology_prescription.png`:

| Metrology | Longest \(L\) with median ≥ 0.90 | Median (10th–90th) | 10th ≥ 0.90? |
|---|---|---|---|
| Uncompensated | 2 mm | 0.941 (0.821–0.977) | No (0.821) |
| Every 0.2 mm | 5 mm | 0.916 (0.859–0.959) | No |
| Every 0.1 mm | 5 mm | 0.950 (0.899–0.967) | No (on the line) |
| Every 0.04 mm | **10 mm** | **0.906 (0.855–0.945)** | **No (0.855)** |

**Forbidden:** selling the last row as a “recommended 10 mm device design point.”  
The only main-table entry whose 10th percentile also clears 0.90 is **5 mm at 0.04 mm pitch** (median 0.969; 0.932–0.982).

### 3.3 Assumption stress test

**Fig. stress** `fig/assumption_stress.png`: at fixed \(\Delta z = 0.04\) mm,

- Width RMS 2 → 10 nm: 5 mm median falls to ~0.70; 10 mm to ~0.40 (report_v7: 0.699 and 0.395).
- Measurement error 0.3 → 1 nm: 5 mm median 0.896 (already below 0.90); 10 mm 0.771.

Thus the main-table line “10 mm / 0.04 mm / median 0.906” holds **only** under \(w_\mathrm{rms}=2\) nm and \(\varepsilon=0.3\) nm, and even then it fails a robust 10th-percentile cut.

### 3.4 Relation to round 6

Round 6 did not use a fully self-consistent TM set for \(A\), \(B\), and \(\Lambda\). Its 10 mm / 0.1 mm median stories **must not** be reused as design points. This pack recognizes **run7 only**.

---

## 4. Boundaries and non-claims

See `non_claims.md`. Abstract-level restatement:

- No in-house fab; thickness = public traces; width noise and measurement error = **assumptions**.
- No main narrative recommending a 10 mm design point (10th percentile **0.855** at 10 mm @ 0.04 mm).
- No fabricated data; no third-party `verify/` PDFs in the deliverable.
- Fiber-Q / acousto-optic benchtop work is **N/A** for this direction.

---

## 5. Conclusion (methods tone)

Under public TFLN thickness traces and a self-consistent TM-pump coefficient set, heralded purity is extremely sensitive to **film-thickness metrology pitch and measurement error**. Uncompensated, a 5 mm segment already sits at median 0.574; keeping the median at 0.90 demands sub-millimetre metrology, and clearing the **10th percentile** as well appears almost only for shorter devices at the densest pitch. What this draft supplies is a noise-budget-style **upper bound and prescription** for later comparison against real metrology and fab decisions—**not** a device recipe.

---

## Files and reproduction

| Path | Role |
|---|---|
| `../upstream_dir01/run7.py` | Monte Carlo |
| `../upstream_dir01/data/run7.json` | Samples |
| `../upstream_dir01/data/tm_coeff.json` | Coefficients |
| `../upstream_dir01/report_v7.md` | Text lock |
| `../scripts/plot_run7_bounds.py` | Three figures in this pack |
| `run7_summary.json` | Percentile summary |

```bash
/workspace/dir13/venv/bin/python /workspace/dir1_metrology/scripts/plot_run7_bounds.py
```
