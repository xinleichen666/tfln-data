# STATUS · dir1_metrology（方向一：计量→纯度上界）

**日期：** 2026-10-12（Asia/Shanghai）  
**触发：** Xinlei 锁定 + 总结包交办：把旧 adaptive-poling / run7 从 OE 器件设计叙事改写成 **膜厚计量 → SPDC 纯度上界** 方法文。

## 本轮交付

| 路径 | 内容 |
|---|---|
| `/workspace/dir1_metrology/paper/` | 工作稿包（对齐 freq_shift_noise/paper 结构） |
| `paper/README.md` | 索引 + 挂仓声明 |
| `paper/abstract_en.md` | 英文摘要（方法框） |
| `paper/main_zh.md` | 中文技术工作稿 |
| `paper/non_claims.md` | 禁令清单 |
| `paper/params_table.md` | 参数分列（测/算/假设） |
| `paper/references.md` / `refs.bib` | 文献 |
| `paper/fig/purity_vs_L.*` | 主图：L × 计量间距 → 纯度中位+分位带 |
| `paper/fig/metrology_prescription.*` | 处方图：中位≥0.90 的最长 L（并标明非设计点） |
| `paper/fig/assumption_stress.*` | 假设应力：w=10 nm / ε=1 nm |
| `paper/run7_summary.json` | 从图脚本抽出的分位数汇总 |
| `scripts/plot_run7_bounds.py` | 出图脚本（只读 `dir01/data/run7.json`） |
| `upstream_dir01` → `/workspace/dir01` | 上游数据/代码软链 |

## 框 vs 旧稿

| | 旧 `dir01/paper/main.tex` | 本包 |
|---|---|---|
| 卖点 | 自适应极化 → **器件设计点**（含 10 mm 叙事） | **计量间距/误差** → 纯度 **MC 上界**与处方 |
| venue 语气 | OE / OL design study | PRA / OE methods·noise budget / 预印本 |
| 10 mm @ 0.04 mm | 易被读成推荐点 | **明确禁止**当设计点（10% = 0.855） |
| 系数 | 旧稿混用痕迹；run7 已 TM 自洽 | **只认** run7 / `tm_coeff.json` |
| 第 6 轮数字 | 曾作设计点 | **作废**，不得硬推 |

## 顶格数字（皆可追溯 run7）

- 理想纯度：0.995（各 L）
- 5 mm 不处理：中位 **0.574**（0.448–0.791）
- 中位≥0.90 最长：不处理 2 mm；Δz=0.2/0.1 mm → 5 mm；Δz=0.04 mm → 10 mm（中位 0.906，**10%=0.855**）
- 主表内唯一 10% 也≥0.90：5 mm @ 0.04 mm（0.969；0.932–0.982）
- 基线假设：w_rms=2 nm，ε=0.3 nm；改 10 nm / 1 nm 则崩

## 未做 / 等拍板

- **未推** GitHub `tfln-data`（等总结包审后再推；可新目录 `dir1_metrology/`）。
- 是否保留英文全文（不止摘要）或投 PRA vs OE methods——等总结包。
- 仓仍 public；用户写完再改 private（既定）。

## 挂仓声明（摘要/README 已写死）

本稿仅限课题组内部：仿真与方案工作稿，实测待做，无伪造数据，Fiber-Q 对本方向 N/A，无自有流片；不得作为公开或可引用结果；verify/ 第三方 PDF 禁止入库。仓写完后再改 private。
