# STATUS · qkernel_budget（Bot A）

**日期：** 2026-10-13（Asia/Shanghai）  
**指派：** 总结包拍定 A → 工作包  
**状态：** 本轮仿真 + 工作稿已齐；**未推仓**

## 交付树

```
qkernel_budget/
  STATUS.md
  scripts/
    run_qkernel_budget.py   # 主实验，写死种子
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
      fig_aligned_acc_f1.{png,pdf}
      fig_mismatch_gap.{png,pdf}
      fig_flip_gap.{png,pdf}
      fig_flip_abs.{png,pdf}
  .venv/                    # 本地依赖（不必入库）
```

不建 `verify/`，不建 upstream 软链，无第三方 PDF。

## 种子（写死）

| 键 | 值 |
|---|---|
| master | 20261013 |
| data_order3_bal | 101 |
| data_order3_unbal | 102 |
| data_order4_bal | 103 |
| data_order4_unbal | 104 |
| split | 777 |
| svm | 42 |

## 顶格数字（均 → `data/summary.json` · `headline`）

| 套件 | BF acc / F1 | RBF acc | TPL acc | BF−RBF | 失配 vs RBF | 翻转 vs RBF 消失点 |
|---|---|---|---|---|---|---|
| order3_balanced | 0.735 / 0.741 | 0.475 | 0.760 | +0.260 | 本扫范围内未消失 | cross_x=0.5 |
| order3_unbalanced | 0.700 / 0.824 | 0.705 | 0.850 | −0.005 | 对准即 ≤0 | 对准即 ≤0 |
| order4_balanced | 0.765 / 0.725 | 0.470 | 0.820 | +0.295 | 本扫范围内未消失 | cross_x=0.4 |
| order4_unbalanced | 0.700 / 0.824 | 0.700 | 0.885 | 0.000 | 对准即 ≤0 | 对准即 ≤0 |

相对 TrueProd-Lin：四套在对准时 gap 已 ≤0（BF 不超过先知块乘积线性）。

## 挂仓声明

本稿仅限课题组内部：仿真与方案工作稿，实测待做，无伪造数据，Fiber-Q 对本方向 N/A，无自有流片；不得作为公开或可引用结果；verify/ 第三方 PDF 禁止入库。仓写完后再改 private。

（已写入 `paper/README.md`、`main_zh` 摘要、`non_claims.md`。）

## 重跑校验

```bash
./scripts/run_all.sh
```

`summary.json` sha256 前 16 位（本轮）：`b274b15e70e3e871`（重跑应稳定，因种子固定）。

## 未做 / 阻塞

- 未推 GitHub。
- 无量子硬件、无欺诈真实数据、无 C 超参网格。
- 文献包先验短表若稍后丢入本目录，只作 bib/页码，不改本轮数字。
