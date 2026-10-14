# skyrmion_noise · 自旋–轨道斯格明子噪声预算（Bot E）

**体裁：** 方法·噪声预算（经典数值仿真工作稿）  
**先验对照（仅引用，不复现实验）：** Zhao et al., *Nat. Phys.* (2026), doi:10.1038/s41567-026-03487-x  
**日期：** 2026-10-14（Asia/Shanghai）  
**模型口径：** **自定自旋–轨道纹理上的经典噪声预算，不是 Zhao 实验的复现。**

---

## 挂仓声明（不得删）

本稿仅限课题组内部：仿真与方案工作稿，实测待做，无伪造数据，Fiber-Q 对本方向 N/A，无自有流片；不得作为公开或可引用结果；verify/ 第三方 PDF 禁止入库。仓写完后再改 private。

---

## 一句话

在自定 LG 自旋–轨道锁定纹理 + 伴侣量子比特的两光子纯态上，对近各向同性退极化、相位翻转、比特相位翻转做经典噪声预算；比较**纹理积分斯格明子数**、concurrence、discord 谁先到零。不声称观测、不抄 Zhao 实验数、不写芯片制备或态转移优势、不并入 Floquet 轨。

## 目录

| 路径 | 内容 |
|---|---|
| `main_zh.md` | 中文技术工作稿 |
| `non_claims.md` | 禁令 / 本轮未做 |
| `params_table.md` | 文献 / 本轮计算 / 假设 分列 |
| `fig/` | 脚本出图 png+pdf |
| `../data/summary.json` | 全部数字出处 |
| `../scripts/run_all.sh` | 从空 `data/` 重跑 |
| `../prior_bib.md` | 文献包先验短表（只 bib） |

## 重跑

```bash
cd /workspace/skyrmion_noise
./scripts/run_all.sh
```

固定种子见 `STATUS.md` 与 `summary.json` → `seeds`。
