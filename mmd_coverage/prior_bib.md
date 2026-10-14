# 先验短表 · Bot C `mmd_coverage/`

**日期**：2026-10-13 · 文献包  
**用途**：只 bib / 引用边界；**不改**本轨任何数字。

## 先验

| 项 | 内容 |
|---|---|
| 题名 | “Train classical, deploy quantum” requires rethinking generalization |
| 作者 | Snehal Raj, Natansh Mathur, Alejandro Perdomo-Ortiz |
| 出处 | arXiv:**2608.31117** (2026) |
| 主张（摘要级） | 同一 MMD² / Pauli-Z 矩匹配损失可对应差很多的**未见有效样本覆盖率**；覆盖与前向 KL 更一致；损失收敛≠泛化 |
| 本轨可用 | 损失–覆盖对照叙事；基数约束比特串设定的思想 |
| 本轨禁止复用 | 其 30 qubit / 基因组 SNV 覆盖率与 MMD 数值；「硬件必不可少」新证 |

## 引用边界

- 可写：「Raj et al. 指出矩匹配损失收敛时未见覆盖仍可分叉；本稿在态矢量可全采样的 N（约 8–12）上用**自构目标分布**复现损失–覆盖图。」
- 不可写：碰 30 量子比特或基因组数据；把其 IQP vs TN 覆盖差（如 0.09 vs 0.41）抄进结果表。

## BibTeX

```bibtex
@article{Raj2026MMD,
  title={``Train classical, deploy quantum'' requires rethinking generalization},
  author={Raj, Snehal and Mathur, Natansh and Perdomo-Ortiz, Alejandro},
  year={2026},
  eprint={2608.31117},
  archivePrefix={arXiv},
  primaryClass={quant-ph},
  url={https://arxiv.org/abs/2608.31117}
}
```

---
**统一禁令（文献包）**：文献数字只作对照；正文表内数必须来自本轨 `summary.json`；禁止把先验准确率/覆盖率/间隙抄成己方结果；禁止第三方 PDF 入库。
