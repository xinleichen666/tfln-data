# STATUS · Dir1 paperB heater/ξ · **v2 耦合器隔热改版**

**日期**：2026-10-14 · 工作包  
**目录**：`/workspace/dir11/paperB/`  
**脚本**：`scripts/run_heater_xi_mc.py`  
**主结果**：`data/summary_heater_xi.json`（= v2）· 归档 `data/summary_heater_xi_v1.json` · 副本 `summary_heater_xi_v2.json`  
**种子 master**：`20261114`（v1 为 20261014）  
**未推仓**。

## v1 → v2 改了什么（旋钮）

失败分析（v1 MC）：η<0.90 与 **|Δ|（共模热失谐）** 相关最强（corr≈−0.66）；`|2µ−Ω|` 已 100% hit，不是卡点。

| 旋钮 | v1 | v2 | 列 |
|---|---|---|---|
| `dT_cm_at_Ppi_mK`（耦合器→环共模串扰 @Pπ） | 10 | **3** | **假设**（版图隔热加强） |
| `dT_diff_at_Ppi_mK`（差分串扰 @Pπ） | 5 | **2** | **假设** |
| `sigT_lock_mK` | 5 | 5（不变） | 假设 |
| `ki_extra_frac` 主列 | 1（×2） | 1（×2，不变） | 假设/保守验收 |
| Pπ / MZI / design_mu_factor | 44.4 / sin(Δφ/2) / √2 | 同左 | Maeder 几何假设 + 自标 MZI |

**未**放松 κi×2；**未**从 Zhang 抽 µ(φ)。物理故事：MZI 加热臂与双环之间加隔热/拉远，降低热串扰，使共模 Δ 落回 η≥0.90 窗口。

## 关键数字（v2 · heater ON · κi×2）

| 量 | v1 | **v2** |
|---|---|---|
| η p10 / 中位 | 0.874 / 0.950 | **0.9167 / 0.9638** |
| frac(η≥0.90) | 81.9% | **94.0%** |
| IL 中位 (dB) | 4.77 | 4.72 |
| 最坏杂散 q=−1 | 100% | 100% |
| 保守功率 ξ=0.5×IDT10%×Qa1570 | 171.9 µW | 171.9 µW（不变） |

插损两列（v2 加热 ON）：Shao Qi IL 中位 2.48 dB · yield 98.8%；κi×2 IL 4.72 dB · yield 94.0%。

ξ 功率（IDT10%·Qa1570）：0.3/0.5/1/2 → 478 / 172 / 43 / 11 µW。

## 流片判据（v2）

| # | 判据 | 结果 |
|---|---|---|
| ① | 加热 ON + κi×2 + IDT10%：≥90% 样品 η≥90% | **PASS**（94.0%；p10=0.9167） |
| ② | 保守射频 ≪ Shao 1 W | **PASS**（172 µW） |
| ③ | 最大杂散仍为 q=−1 | **PASS**（100%） |

**总判 ALL_PASS = True** — 仿真侧允许在 **v2 隔热假设** 下带着测量接口推进版图；串扰 3/2 mK 仍是假设，流片后须用加热功率→劈裂/失谐标定核验。不写进摘要当成绩。

## 文件

- 图已覆写：`fig/figB6_heater_on_off.*`、`figB7_xi_power.*`、`figB8_residual_spur.*`（+ `paper/notes/`）
- `fab_criteria.md`、`heater_xi_report_zh.md`、`paper/notes/params_table_heater_xi.md` 已按 v2 更新

## 稿件（总结包）

`paper/main.tex` 已对齐 **v2** 加热开主数字（摘要/MC/五步表/结论/限制(vi)）。摘要**未**写 ALL_PASS 或串扰为实测。`测量计划表_五步.md` 同步 v2。PDF 重编译见 `paper/main.pdf`。

## 流片路径（Xinlei 已定 tape-out）

- **交付清单**：`流片交付清单.md`（版图要素 / MZI+隔热 / IDT / 加热分路 / 五步映射 / 闸门回退）。
- **路径**：按当前版图流片；**第 1 步串扰标定必须闸住**。PASS → 沿用 v2（步4 接受 η p10≈0.917）。FAIL → **回退 v1 叙事**（判据① FAIL，步4 用 v1 p10≈0.874），禁止宣称 ALL_PASS。
- 测量计划：`测量计划表_五步.md`。未推仓。

## GO fab 硬闸（Cursor PR#14）

- 清单已补：`流片交付清单.md` — **开环步1**（环加热冻结、只扫 MZI；暗参考环拆 CM/差分；@实测 Pπ 判 3/2 mK；**禁止**按串扰插值成品率）；隔热设计意图；暗参考环 + 直波导 IL + IDT GSG；**§9 HOLD GDS**。
- 步1 FAIL（含未达 3/2）→ 回退 v1，禁 ALL_PASS，步4 p10≈**0.874**；PASS → v2 p10≈**0.917**。
- 测量计划表已加一行开环指针（NOTES 仍归卡宝）。未推仓。
