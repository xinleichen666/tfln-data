# 方向一工作稿包（方法·噪声预算：膜厚计量 → SPDC 纯度上界）

路径根：`/workspace/dir1_metrology/paper/`

对齐结构：`/workspace/freq_shift_noise/paper/`（移频噪声账本）与 `/workspace/dir2/paper/`。

> **预印本口径（2026-10-12）：** **仿真 + 公开晶圆迹线** 方法文工作稿；无自有流片；不虚构测量；实测格空着。主数字锁在 run7，本轮只改框、不出新 MC。
>
> **挂仓声明：** 本稿仅限课题组内部：仿真与方案工作稿，实测待做，无伪造数据，Fiber-Q 对本方向 N/A，无自有流片；不得作为公开或可引用结果；verify/ 第三方 PDF 禁止入库。仓写完后再改 private。

**状态（2026-10-12 · Cursor A 锁定）**：**PRA methods·噪声预算** 正文语气；**预印本先挂**。**不是** OE 器件设计文。主表**唯一稳态点** = **5 mm @ Δz=0.04 mm**（中位 0.969；10%–90% 0.932–0.982）。**10 mm** 只报分布（中位 0.906 / 10th 0.855），**永不当设计点**。挂仓声明 / non_claims **不删不砍**。

## 本目录

| 文件 | 说明 |
|---|---|
| `main_zh.md` | 中文技术工作稿（计量→上界） |
| `main_en.md` | **英文全文**（与中文同框；摘要与 `abstract_en.md` 对齐） |
| `abstract_en.md` | 英文摘要 + 关键词 |
| `references.md` | 参考文献可读列表 |
| `refs.bib` | BibTeX |
| `params_table.md` | 文献/计算/假设分列参数表 |
| `non_claims.md` | 禁令清单（一眼过） |
| `README.md` | 本索引 |
| `run7_summary.json` | 出图用分位数汇总 |
| `fig/purity_vs_L.png/.pdf` | **Fig.主** L × 计量间距 → 纯度中位+10–90% 带（MC 上界） |
| `fig/metrology_prescription.png/.pdf` | **Fig.处方** 中位≥0.90 的最长 L（标明非设计点） |
| `fig/assumption_stress.png/.pdf` | **Fig.应力** w_rms=10 nm / ε=1 nm |

## 上游定稿数字（勿在审稿前擅自重算主结果）

| 文件 | 用途 |
|---|---|
| `/workspace/dir01/report_v7.md` | 第 7 轮文字结论 |
| `/workspace/dir01/data/run7.json` | MC 原始（seed 2027，N=64） |
| `/workspace/dir01/data/tm_coeff.json` | 自洽 TM 泵系数 |
| `/workspace/dir01/run7.py` | 复现入口 |
| `/workspace/dir1_metrology/upstream_dir01` | 软链到上述树 |
| `/workspace/dir1_metrology/scripts/plot_run7_bounds.py` | 本包出图 |

## 复现出图

```bash
/workspace/dir13/venv/bin/python /workspace/dir1_metrology/scripts/plot_run7_bounds.py
```

## 摘要首句（中 / 英）

- **中**：在公开晶圆膜厚迹线与自洽 TM 泵系数下，用蒙特卡洛把**膜厚计量间距与测量误差假设**映射为 SPDC 预告纯度上界与处方；仿真+公开迹线，无自有流片，不虚构测量。
- **EN：** We map film-thickness metrology spacing and assumed measurement error onto Monte Carlo upper bounds on SPDC heralded purity using public wafer traces and a self-consistent TM-pump coefficient set; simulation only—no in-house fab, no invented measurements.

## 边界快查（Cursor A）

- 框：**PRA methods·计量噪声预算**；预印本先挂；不是器件 recipe。
- 主表**唯一稳态点**：**5 mm @ Δz=0.04 mm**（0.969；0.932–0.982）。
- **10 mm** @ 0.04 mm：只报分布（中位 0.906 / 10th 0.855），**永不当设计点**。
- 第 6 轮数字作废；只认 run7。
- 宽度 2 nm、误差 0.3 nm = 假设；应力图已画。
- 挂仓声明 / `non_claims.md` **不删不砍**（do not cut）。
