# STATUS · mmd_coverage（Bot C）

**日期：** 2026-10-13（Asia/Shanghai）  
**指派：** 总结包拍定 C → 卡宝  
**状态：** 本轮仿真 + 工作稿已齐；**未推仓**

## 交付树

```
mmd_coverage/
  STATUS.md
  scripts/
    run_mmd_coverage.py   # 主实验，写死种子
    plot_figures.py       # 出图
    run_all.sh            # 清空 data/ 后重跑
  data/
    summary.json          # 全部数字
  paper/
    README.md
    main_zh.md
    non_claims.md
    params_table.md
    fig/
      fig_loss_unseen_coverage.{png,pdf}
      fig_loss_vs_step.{png,pdf}
      fig_matched_coverage_bars.{png,pdf}
      fig_matched_forward_kl.{png,pdf}
  prior_bib.md            # 文献包先验短表（不改数字）
  .venv/                  # 本地依赖（不必入库）
```

不建 `verify/`，不建 upstream 软链，无第三方 PDF。

## 种子（写死）

| 键 | 值 |
|---|---|
| master | 20261013 |
| target | 301 |
| train_sample | 302 |
| product_init | 303 |
| ising_init | 304 |
| eval_sample | 305 |

## 顶格数字（均 → `data/summary.json` · `headline`）

| 项 | 值 | JSON 键 |
|---|---|---|
| N / 有效定义 | 10 / Hamming_weight==5（\|V\|=252） | `headline.N` / `valid_definition` / `n_valid` |
| 训练抽样 | 48 次 → 唯一 20；未见有效 232 | `n_train_draws` / `n_train_unique` / `n_unseen_valid` |
| 两模型 | ProductValid / PairIsingValid | `model_a` / `model_b` |
| 匹配损失 L* | 0.177510 | `L_star_matched_loss` |
| 匹配处 MMD² | 0.177510 / 0.173894 | `model_*_matched_loss_mmd2` |
| 匹配处未见覆盖 | 0.2802 / 0.3922（\|Δ\|=0.1121） | `model_*_matched_unseen_valid_coverage` / `abs_unseen_coverage_gap_matched` |
| 匹配处训练覆盖 | 0.85 / 0.95 | `model_*_matched_train_coverage` |
| 匹配处前向 KL(p\*∥q) | 0.0778 / 0.0945 | `model_*_matched_forward_kl` |
| 判决 | **损失接近但覆盖分开** | `verdict_zh` / `loss_coverage_separated=true` |

## 挂仓声明

本稿仅限课题组内部：仿真与方案工作稿，实测待做，无伪造数据，Fiber-Q 对本方向 N/A，无自有流片；不得作为公开或可引用结果；verify/ 第三方 PDF 禁止入库。仓写完后再改 private。

（已写入 `paper/README.md`、`main_zh` 摘要、`non_claims.md`。）

## 重跑校验

```bash
./scripts/run_all.sh
```

`summary.json` sha256 前 16 位（本轮）：`9afad65469a28a3f`（重跑应稳定，因种子固定）。

## 未做 / 阻塞

- 未推 GitHub。
- 无量子硬件、无 30 qubit、无基因组 SNV、未抄 Raj 覆盖率数字。
- 未新证「硬件必不可少」；理论句只引用先验。
- Fiber-Q 对本方向 N/A。
