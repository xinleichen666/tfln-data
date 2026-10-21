# STATUS · skyrmion_noise（Bot E）

**日期：** 2026-10-14（Asia/Shanghai）  
**指派：** 总结包拍定 E → 工1  
**状态：** 本轮仿真 + 工作稿已齐；**未推仓**

## 模型口径（必读）

**自定自旋–轨道纹理上的经典噪声预算，不是 Zhao 实验的复现。**  
先验 Zhao et al., *Nat. Phys.* (2026), doi:10.1038/s41567-026-03487-x。新闻/实验数（斯格明子≈1.981、保真度≈89%、纯度≈0.34/0.25、混合比例 0.5）**仅对照**，**禁止**写入结果表。斯格明子数必须为横截面斯托克斯纹理积分，禁止用 4×4 本征值冒充。先验短表见 `prior_bib.md`。

## 交付树

```
skyrmion_noise/
  STATUS.md
  prior_bib.md
  requirements.txt
  scripts/
    run_skyrmion_budget.py   # 主实验，写死种子
    plot_figures.py          # 出图
    run_all.sh               # 清空 data/ 后重跑
  data/
    summary.json             # 全部数字
    summary.sha256
  paper/
    README.md
    main_zh.md
    non_claims.md
    params_table.md
    fig/
      fig_clean_texture.{png,pdf}
      fig_depolarizing.{png,pdf}
      fig_phase_flip.{png,pdf}
      fig_bit_phase_flip.{png,pdf}
  .venv/                     # 本地依赖（不必入库）
```

不建 `verify/`，不建 soft link，无第三方 PDF。

## 种子（写死）

| 键 | 值 |
|---|---|
| master | 20261014 |
| depolarizing_sweep | 401 |
| phase_flip_sweep | 402 |
| bit_phase_flip_sweep | 403 |
| grid_probe | 404 |

## 顶格数字（均 → `data/summary.json` · `headline` / `clean_limit`）

| 项 | 值 | 键 |
|---|---|---|
| 干净 \|N_sk\|（纹理积分，离散格） | **0.953** | `headline.clean_skyrmion_abs` |
| 干净 concurrence | **1.000** | `clean_concurrence` |
| 干净 discord | **1.000** | `clean_discord` |
| 干净保真度 / 纯度 | 1 / 1 | `clean_fidelity` / `clean_purity` |
| ℓ, w, 格点 | 1, 1.0, 97 | `ell` / `waist` / `grid_n` |
| 退极化 ξ 扫 | [0, 1]×21 | `xi_range` |
| 相位/比特相位 p 扫 | [0, 1]×21 | `p_range` |
| 退极化→concurrence 到零 | ξ=**0.7** | `vanish_depolarizing.concurrence.cross_x` |
| 退极化→discord 到零 | ξ=**0.9** | `vanish_depolarizing.discord.cross_x` |
| 退极化→\|N_sk\| 到零 | ξ=**1.0** | `vanish_depolarizing.skyrmion.cross_x` |
| 退极化谁先到零 | **concurrence** | `who_first_depolarizing.who_first_to_zero` |
| 相位翻转→discord 到零 | p=**0.45** | `vanish_phase_flip.discord.cross_x` |
| 相位翻转→C 与 \|N_sk\| 到零 | p=**0.5** | `vanish_phase_flip.concurrence/skyrmion.cross_x` |
| 相位翻转谁先到零 | **discord** | `who_first_phase_flip.who_first_to_zero` |
| 比特相位翻转 | 与相位翻转同结构（本模型） | `vanish_bit_phase_flip` / `who_first_bit_phase_flip` |

过零判据：\|metric\| ≤ `protocol.zero_threshold_abs`=0.02，取扫线上**首次**满足点；相位/比特相位信道在 p>0.5 因混合对称会回升，正文照写。

## 挂仓声明

本稿仅限课题组内部：仿真与方案工作稿，实测待做，无伪造数据，Fiber-Q 对本方向 N/A，无自有流片；不得作为公开或可引用结果；verify/ 第三方 PDF 禁止入库。

（已写入 `paper/README.md`、`main_zh` 摘要、`non_claims.md`。）

## 重跑校验

```bash
./scripts/run_all.sh
```

`summary.json` sha256 前 16 位（本轮）：`7bda75637c864aaa`（重跑应稳定，因种子/网格固定）。

## 未做 / 阻塞

- 未推 GitHub。
- 未读原文公式；未使用 Zhao 器件/实验数作结果。
- 未写芯片制备、态转移优势；未与 Floquet 轨并篇。
- 干净 \|N_sk\|≈0.953（非整数 1）来自有限横截面离散积分，已在 STATUS/方法注明；**算得出纹理**，未停写。
- Fiber-Q 对本方向 N/A。
