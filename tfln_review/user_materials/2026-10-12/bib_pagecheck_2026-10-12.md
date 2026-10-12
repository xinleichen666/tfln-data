# Bibliographic page / DOI check — 2026-10-12 (Asia/Shanghai)

Sources checked: Crossref API / DOI.org BibTeX, arXiv Atom `journal_ref`, local PDFs under `/workspace/dir11/paperB/verify/` and `/workspace/tfln_review/user_materials/`.  
Policy: **do not invent**; fill page ranges only when Crossref or arXiv `journal_ref` (or local publisher PDF) confirms. Qiu stays **摘要**.

Drafts audited:
1. `/workspace/freq_shift_noise/paper/refs.bib` + `references.md`
2. `/workspace/dir2/paper/main_zh.md` §References (no separate `.bib`)
3. Consistency: `/workspace/tfln_review/ao_shared_params_v1.md`

---

## Per-entry status

| Entry | Journal / venue | Vol / pages / year | DOI | Status | Notes |
|---|---|---|---|---|---|
| **Shao Optica 2019** | Optica | **6**, **1498–1505** (2019); issue 12 | 10.1364/OPTICA.6.001498 | **OK** (after fill) | Crossref lists start `1498` only; end **1505** from arXiv `journal_ref`. Local PDF is arXiv copy (no publisher page footers). |
| **Shao OE 2020** | Opt. Express | **28**(16), **23728–23738** (2020) | 10.1364/OE.397138 | **OK** (after fix) | Crossref start-only; end **23738** from arXiv `journal_ref`. dir2 previously had **23737** (off-by-one) → corrected. |
| **Hu Nature 2021** | Nature | **599**, **587–593** (2021); issue 7886 | 10.1038/s41586-021-03999-x | **OK** (after fill) | Crossref + arXiv `journal_ref` agree. D1 bib/md had start-only `587`. No local PDF (open item in shared table). |
| **Qiu OL 2025** | Opt. Lett. | **50**(4), start **1132** (2025) | 10.1364/OL.549857 | **abstract-only** | Crossref/DOI BibTeX: pages=`1132` only. Abstract page confirms title/authors/numbers. paperB comment cites Engineering Village **1132–1135**; **not upgraded** (no full text; end page not in Crossref). Shared table status remains **摘要**. Not cited in D1 or D2 preprint refs lists. |
| **Ni arXiv:2606.05337** | arXiv | (2026) preprint | — | **OK** (after author/title fix) | Local PDF `/workspace/dir11/paperB/verify/2606.05337.pdf`. Authors: **Haorui Ni, Sunil Bhave, Mengyue Xu** (not X.-B. Xu). Title filled. |
| **Zhu arXiv:2511.22585** | arXiv | (2025) preprint | — | **OK** (after author/title fix in D2) | Local PDF present. D2 had “Y. Zhu” → **Z.-X. Zhu** + title. |
| **Xu arXiv:2510.26596** | arXiv | (2025) preprint | — | **OK** | Local PDF `/workspace/tfln_review/user_materials/arxiv_2510.26596.pdf`. D2 ref #1 OK. |
| **Xu arXiv:2509.01940** | arXiv | (2025) preprint | — | **OK** | In D1 `refs.bib` / `references.md` only (params table). No local PDF; shared table marks HTML 全文已核. |
| **Ogi 2002** | J. Appl. Phys. | **92**, **2451–2456** (2002); issue 5 | **10.1063/1.1497702** | **OK** (DOI added) | Crossref full page range. |
| **Andrushchak 2009** | J. Appl. Phys. | **106**, article **073510** (2009); issue 7 | **10.1063/1.3238507** | **OK** (DOI added) | AIP article-number style (Crossref `page` empty; `article-number=073510`). |
| **Shao PRA 2022** (D2 #2) | Phys. Rev. Applied | **18**, **054078** (2022) | **10.1103/PhysRevApplied.18.054078** | **OK** (DOI added) | Article-number style; arXiv:2203.16003. |

---

## Fixes applied this session

### `/workspace/freq_shift_noise/paper/refs.bib`
- Hu2021: `pages={587--593}`, `number={7886}`
- Shao2019: `pages={1498--1505}`, `number={12}`
- Shao2020: `pages={23728--23738}`
- Header note pointing to this check

### `/workspace/freq_shift_noise/paper/references.md`
- Shao2020 → 23728–23738  
- Shao2019 → 1498–1505  
- Hu2021 → 587–593  

### `/workspace/dir2/paper/main_zh.md` §References
- #4 Ni: correct authors (**H. Ni, S. Bhave, M. Xu**) + full title (was wrong Xu = X.-B.)
- #5 Zhu: **Z.-X. Zhu** + full title
- #6 Shao OE: end page **23738** (was 23737) + title + DOI
- #2 Shao PRA, #3 Optica, #7 Hu, #8 Ogi, #9 Andrushchak: DOIs added

### `/workspace/tfln_review/ao_shared_params_v1.md`
- Cite strings for Shao OE / Shao Optica / Hu updated to full page ranges
- Ni author line → H. Ni, S. Bhave & M. Xu  
- **Qiu left at 摘要**; cite still `Opt. Lett. **50**, 1132 (2025)`

---

## Remaining gaps

1. **Qiu Opt. Lett. 2025** — still **摘要**. Crossref start page only; end **1135** not confirmed here. Need full PDF (or Optica HTML with page footer) before 「全文已核」or locking 1132–1135 in preprint bibliographies.
2. **Hu 2021** — no local PDF under `verify/`; page range OK via Crossref, but secondary page-spotting of numbers still depends on prior paperB tables.
3. **Xu 2509.01940** — no local PDF on disk (HTML/核对表 only).
4. **Optica / OE Crossref** still expose start page only; end pages rely on arXiv `journal_ref` (confident, but not Crossref-native).
5. D1 does not cite Qiu / Ni / Xu 2510.26596 / Ogi / Andrushchak (by design); D2 does not cite Qiu / Xu 2509.01940.

---

## Consistency with shared params

- Shao / Hu / Zhu / Xu / Ni numeric status rows unchanged.  
- Qiu three rows remain **摘要** + EO serrodyne 对照.  
- Page-range cite strings now match the two preprint drafts.
