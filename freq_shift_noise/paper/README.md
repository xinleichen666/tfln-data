# 方向一工作稿包（移频噪声账本）

路径根：`/workspace/freq_shift_noise/paper/`

对齐结构：`/workspace/dir2/paper/`（方向二）。

> **预印本口径（2026-10-12 总结包修订）：** 现挂 **仿真+方案** 无数据预印本工作稿；实测格空着；主图计划自测点标 **pending**；主数字不动；先不下单 Fiber-Q。
>
> **挂仓声明：** 本稿仅为仿真与台面方案，实测单元仍 pending，不含实测或伪造数据；Fiber-Q 尚未下单，无自有流片。

**状态（2026-10-12）**：**仿真+方案预印本工作稿**；波长/型号已锁（~1550 nm；G&H Fiber-Q 80 MHz）；**实测格仍空 / pending**。不扩腔调、不填假自测数据。主数字与 `../report_formulas_v1.md` / `../models.py` 一致，本轮未改。

## 本目录

| 文件 | 说明 |
|---|---|
| `main_zh.md` | 中文技术工作稿（含英文副题；摘要→结论边界） |
| `abstract_en.md` | **英文摘要**（≈197 词）+ 英文关键词 |
| `references.md` | 参考文献可读列表（与共用表一致） |
| `refs.bib` | BibTeX（Shao2020 / Shao2019 / Zhu2025ao / Hu2021；Xu2025b 参数表旁列） |
| `params_table.md` | 文献实测 / 计算 / datasheet / assumed 分列参数表 |
| `non_claims.md` | 禁令清单（一眼过） |
| `README.md` | 本索引 |
| `fig/vis_vs_carrier.png/.pdf` | **Fig.主** 甲类 \(V(R_c)\)（理论曲线定稿；自测点 **pending**） |
| `fig/vis_vs_R.png/.pdf` | **Fig.丙** \(V(R)\) 敏感性（模型假设） |

## 上游定稿数字与公式（勿在审稿前擅自重算主结果）

| 文件 | 用途 |
|---|---|
| `/workspace/freq_shift_noise/report_formulas_v1.md` | 公式细节定稿 |
| `/workspace/freq_shift_noise/params.json` | 带 cite/kind 的参数 |
| `/workspace/freq_shift_noise/models.py` | 甲/乙/丙分账 |
| `/workspace/freq_shift_noise/hom_visibility.py` | \(V_\mathrm{upper}\)、\(V(R_c)\) |
| `/workspace/freq_shift_noise/plot_vis_vs_carrier.py` | 主图 + 丙图（叠点已定稿） |
| `/workspace/freq_shift_noise/selftest_table.md` | 自测表（**全待测**） |
| `/workspace/freq_shift_noise/report_skeleton.md` | 初版骨架（对照） |
| `/workspace/方向一_台面可执行清单.md` | 卡宝台面口径 |
| `/workspace/tfln_review/ao_shared_params_v1.md` | 声光共用表（乙类 2.007 GHz 脚注已对齐） |

## 复现计算（仅当总结包要求重跑）

```bash
/workspace/dir13/venv/bin/python /workspace/freq_shift_noise/models.py
/workspace/dir13/venv/bin/python /workspace/freq_shift_noise/hom_visibility.py
/workspace/dir13/venv/bin/python /workspace/freq_shift_noise/plot_vis_vs_carrier.py
```

## 摘要首句（中 / 英）

- **中**：把片上声光移频器件的残余载波与边带写成频率仓纯度，给出室温 HOM 可见度上限对载波抑制的主曲线；用商用光纤 AOM 台面自测核对公式，插损只进符合计数率。
- **EN**：We cast residual carrier and sidebands of on-chip acousto-optic frequency shifters as frequency-bin purity and derive the room-temperature Hong–Ou–Mandel (HOM) visibility upper bound versus carrier suppression.

## 边界快查

- 主图叠点口径：**定稿**（计划自测只标横轴 / **pending**；Shao 竖虚线文献锚 ≠ 台面 HOM）。
- 波长：**已锁定 A · ~1550 nm**。型号已锁 G&H Fiber-Q 80 MHz；实测格：**全待测 / pending**；先不下单。
- 乙类：**非主结果**（锁定表 + \(n_\mathrm{th}\) + \(N_\mathrm{add}\)）。
- 丙类：\(\delta_\mathrm{sp}\) **模型假设**。
- 本轮打磨：**未改任何主数字**。
