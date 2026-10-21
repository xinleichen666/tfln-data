# mmd_coverage · Pauli-Z 矩匹配损失与未见有效覆盖（Bot C）

**体裁：** 方法·噪声预算（经典数值仿真工作稿）  
**先验对照（仅引用，不抄其覆盖率表）：** Raj, Mathur, Perdomo-Ortiz, arXiv:2608.31117  
**日期：** 2026-10-13（Asia/Shanghai）

---

## 挂仓声明（不得删）

本稿仅限课题组内部：仿真与方案工作稿，实测待做，无伪造数据，Fiber-Q 对本方向 N/A，无自有流片；不得作为公开或可引用结果；verify/ 第三方 PDF 禁止入库。

---

## 一句话

在基数约束比特串（N=10，有效 ⇔ Hamming 重量=5）上，用**同一类** Pauli-Z 矩 MMD² 训练 ProductValid 与 PairIsingValid；在相近损失水平比较训练集覆盖、未见有效覆盖与对自构目标的前向 KL。本轮判决：**损失接近但覆盖分开**。不声称硬件必要、不碰 30 qubit / 基因组、不抄 Raj 表内数字。

## 有效串定义

\[
V = \{ x \in \{0,1\}^{10} : \mathrm{wt}(x)=5 \},\qquad |V|=\binom{10}{5}=252.
\]

未见有效串 = \(V\) 减去训练集出现过的唯一串。

## 目录

| 路径 | 内容 |
|---|---|
| `main_zh.md` | 中文技术工作稿 |
| `non_claims.md` | 禁令 / 本轮未做 |
| `params_table.md` | 文献 / 本轮计算 / 假设 分列 |
| `fig/` | 脚本出图 png+pdf |
| `../data/summary.json` | 全部数字出处 |
| `../scripts/run_all.sh` | 从空 `data/` 重跑 |
| `../prior_bib.md` | 文献包先验短表 |

## 重跑

```bash
cd /workspace/mmd_coverage
./scripts/run_all.sh
```

固定种子见 `STATUS.md` 与 `summary.json` → `seeds`。
