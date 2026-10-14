# STATUS · floquet_crit_budget（Bot D）

**日期：** 2026-10-13（Asia/Shanghai）  
**指派：** 总结包拍定 D → 卡宝  
**状态：** 本轮仿真 + 工作稿已齐；**未推仓**

## 模型口径（必读）

**标准模型诊断，不是该实验的复现。**  
读不到 Cheng *Nature* 658, 358 (2026) 的实验耦合参数；本轨采用教科书一维两步 Floquet SSH（自设 γ₁、γ₂），**禁止**把 Nature 耦合数编进结果表。先验短表见 `prior_bib.md`（只 bib/边界）。

## 交付树

```
floquet_crit_budget/
  STATUS.md
  prior_bib.md
  requirements.txt
  scripts/
    run_floquet_budget.py   # 主实验，写死种子
    plot_figures.py         # 出图
    run_all.sh              # 清空 data/ 后重跑
  data/
    summary.json            # 全部数字
  paper/
    README.md
    main_zh.md
    non_claims.md
    params_table.md
    fig/
      fig_clean_spectrum.{png,pdf}
      fig_disorder_gap.{png,pdf}
      fig_disorder_ee.{png,pdf}
      fig_loss_gap.{png,pdf}
      fig_loss_ee.{png,pdf}
  .venv/                    # 本地依赖（不必入库）
```

不建 `verify/`，不建 upstream 软链，无第三方 PDF。

## 种子（写死）

| 键 | 值 |
|---|---|
| master | 20261013 |
| disorder_sweep | 301 |
| loss_sweep | 302 |
| phase_diag_probe | 303 |

## 顶格数字（均 → `data/summary.json` · `headline` / `clean_limit`）

| 项 | 值 | 键 |
|---|---|---|
| γ₁/π, γ₂/π（假设） | 0.25, 0.80 | `headline.gamma1_over_pi` / `gamma2_over_pi` |
| N | 60 | `headline.n_sites` |
| 干净 0 体隙 / π 体隙 | 1.730 / 0.176 | `headline.clean_gap_0_bulk` / `clean_gap_pi_bulk` |
| 干净边缘模数 n₀ / nπ | 2 / 2 | `clean_n_edge_0` / `clean_n_edge_pi` |
| 半链纠缠熵 EE | 1.194 | `clean_half_chain_ee` |
| 无序扫 W | [0, 1.2]×13 点，每点 8 实现 | `disorder_W_range` |
| 损耗扫 κ | [0, 0.80]×17 点（交错格点损耗） | `loss_kappa_range` |
| 无序→0 签名消失 | W=**1.2** | `vanish_disorder_0.cross_x` |
| 无序→π 签名消失 | W=**0.4** | `vanish_disorder_pi.cross_x` |
| 损耗→0 签名 | **本扫范围内未消失** | `vanish_loss_0.note` |
| 损耗→π 签名消失 | κ=**0.5** | `vanish_loss_pi.cross_x` |
| 多临界 / 可加对数 | **不报** | `multicritical_additive_log.reported=false` |

## 挂仓声明

本稿仅限课题组内部：仿真与方案工作稿，实测待做，无伪造数据，Fiber-Q 对本方向 N/A，无自有流片；不得作为公开或可引用结果；verify/ 第三方 PDF 禁止入库。仓写完后再改 private。

（已写入 `paper/README.md`、`main_zh` 摘要、`non_claims.md`。）

## 重跑校验

```bash
./scripts/run_all.sh
```

`summary.json` sha256 前 16 位（本轮）：`4a792cb60da790cc`（重跑应稳定，因种子固定）。

## 未做 / 阻塞

- 未推 GitHub。
- 未读到 / 未使用 Nature 实验耦合数值；非实验复现。
- 未画「推荐器件长度」；不写「观测到」。
- 粗网格相图探测不足以定两条临界边界交点 → 不报多临界可加对数。
- Fiber-Q 对本方向 N/A。
