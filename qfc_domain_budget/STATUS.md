# STATUS · qfc_domain_budget（Bot F）

**日期：** 2026-10-14（Asia/Shanghai）  
**指派：** 群聊交办 F（优先）→ 工2（工1 改接 E，不碰 F）  
**状态：** 本轮仿真 + 工作稿已齐；**未推仓**

## 模型口径（必读）

**标准模型预算，不是该实验的复现。**  
读不到 PRL 原文畴缺陷公式系数；本轨用教科书准相位匹配：畴壁抖动 / 占空比 / 膜厚→波矢误差进 sinc²。**禁止**把新闻器件数 28.8%、35/s、120:1 写进结果表。未用 `dir1_metrology` run7 纯度。

## 交付树

```
qfc_domain_budget/
  STATUS.md
  requirements.txt
  scripts/
    run_qfc_budget.py
    plot_figures.py
    run_all.sh
  data/
    summary.json
  paper/
    README.md
    main_zh.md
    non_claims.md
    params_table.md
    fig/
```

不建 `verify/`，不建软链，无第三方 PDF。

## 种子（写死）

| 键 | 值 |
|---|---|
| master | 20261014 |
| domain_wall | 401 |
| duty_cycle | 402 |
| thickness | 403 |
| temp_scan | 404 |

## 顶格数字（均 → `data/summary.json` · `headline`）

| 项 | 值 | 键 |
|---|---|---|
| λ_s / λ_i / λ_p | 393.0 / 1550.0 / 526.4909 nm | `protocol.lambda_*` |
| Λ₀ | 1.6807 μm | `headline.Lambda0_um` |
| L（对齐整数周期） | 5.0000 mm；N=2975 | `headline.L_mm` / `n_periods` |
| 畴壁 η→0.5 | σ/Λ=0.2200 | `headline.wall_half_eta*` |
| 膜厚 η→0.5 | δH≈0.0020 μm（正侧） | `headline.thickness_half_eta*` |
| 温度扫反向调谐 | **未见到** | `headline.reverse_tuning_temp_note` |
| 周期扫反向调谐 | **未见到** | `headline.reverse_tuning_period_note` |
| 膜厚扫 Δk 反向 | **未见到**（附加诊断） | `headline.reverse_tuning_thickness_note` |

## 挂仓声明

本稿仅限课题组内部：仿真与方案工作稿，实测待做，无伪造数据，Fiber-Q 对本方向 N/A，无自有流片；不得作为公开或可引用结果；verify/ 第三方 PDF 禁止入库。

（已写入 `paper/README.md`、`main_zh` 摘要、`non_claims.md`。）

## 重跑校验

```bash
./scripts/run_all.sh
```

`summary.json` sha256 前 16 位（本轮）：`3cf8304f4934b627`（种子固定应稳定）。

## 未做 / 阻塞

- 未推 GitHub。
- 未读 / 未使用 PRL 畴缺陷公式系数；非实验复现。
- 未设推荐波导长度或推荐周期。
- 未引用离子纠缠 / DI-QKD；未写成可流片设计。
- 温度 / 周期 / 膜厚三条扫描上，QFC 与泵浦 SPDC 的 Δk 斜率**均未反号** → 写「未见到」。
- Fiber-Q 对本方向 N/A。
