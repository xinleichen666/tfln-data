# 方向二工作稿（preprint polish）

> **预印本口径（2026-10-12 · V1）：** 本稿仅限**课题组内部**：仿真与方案工作稿，实测待做，**无伪造数据**，Fiber-Q **未下单**，**无流片**；**不得作为公开或可引用结果**；`verify/` 第三方 PDF **禁止入库**。

已加 English Abstract、正规 References、英文 Keywords；中文正文为组内工作稿语气打磨版。禁令与「型号已锁、实测待测」仍有效；数字锁在 `../data/step2_summary.json`。

路径根：仓库内 `dir2/paper/`（本地原 `/workspace/dir2/paper/`）。

## 公开/推仓前必须写死的声明

本稿仅限**课题组内部**：仿真与方案工作稿，实测待做，**无伪造数据**，Fiber-Q **未下单**，**无流片**；**不得作为公开或可引用结果**；`verify/` 第三方 PDF **禁止入库**。

Internal group use only: simulation and scheme draft; measurements pending; no fabricated data; Fiber-Q not ordered; no fab. Not for public citation. Third-party PDFs under verify/ must not enter the repo.

- 推仓路径：`dir2/`（`paper/` + `data/` + 图 + 脚本报告）+ 共用表 `tfln_review/ao_shared_params_v1.md`（若仓内尚无则更新）
- **绝不**纳入 `verify/` 第三方 PDF
- 仓保持 public

## 本目录

| 文件 | 说明 |
|---|---|
| `main_zh.md` | 中英摘要 + 中文正文 + 正规参考文献 |
| `params_table.md` | 文献实测 / 本文计算分栏参数表 |
| `non_claims.md` | 禁令清单 |
| `README.md` | 本索引 |
| `fig/fig1_structure.png/.pdf` | Fig.1 器件结构（单光波导；无双环） |
| `fig/fig3_benchtop.png/.pdf` | Fig.3 台面方案（pending；无假数据） |
| `fig/step2_joint_transfer.png/.pdf` | Fig.2 Step2 联合传递主图 |
| `fig/gate1_alpha.png/.pdf` | Gate1 α vs Xu（辅图） |
| `fig/gate1_mzi_thermal.png/.pdf` | Gate1 热场 / MZI（辅图） |

## 上游定稿数字（勿擅自重算主结果）

| 文件 | 用途 |
|---|---|
| `../data/gate1_alpha.json` | Gate1 α、带、对 Xu 比 |
| `../data/step2_summary.json` | α_LNoS/bulk、VπL、dφ_err |
| `../data/params_sources.md` | 全参数出处 |
| `../step2_report_zh.md` | Step2 中文方法报告 |
| `../gate1_report_zh.md` | Gate1 中文报告 |
| `tfln_review/ao_shared_params_v1.md` | 声光共用表（仓内路径） |

## 复现

```bash
python dir2/gate1_thermal_acoustic.py
python dir2/step2_ln_photoelastic.py
```

（环境可用仓库内既有 venv 或本地等价环境。）
