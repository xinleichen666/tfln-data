# 先验短表 · Bot F `qfc_domain_budget/`（优先）

**日期**：2026-10-14 · 文献包  
**用途**：只 bib / 引用边界；**不改**本轨任何数字。

## 先验

| 项 | 内容 |
|---|---|
| 题名 | （393 nm→1550 nm 量子频率转换；正式题名以出版社页为准） |
| 作者 | 潘建伟、张强、郑名扬 等 |
| 出处 | *Phys. Rev. Lett.*；DOI: [10.1103/wx56-plcm](https://doi.org/10.1103/wx56-plcm) |
| 主张（摘要级） | 周期极化薄膜铌酸锂脊波导上的量子频率转换；器件报道端到端效率、泵浦噪声及钙离子节点信噪比；方法上涉及畴缺陷相位扰动与短波泵浦时转换/泵浦 SPDC 噪声的反向调谐 |
| 本轨可用 | 标准准相位匹配：畴壁抖动、占空比、膜厚→Δk→sinc²；同一扫描上比较 QFC Δk 与泵浦 SPDC Δk 斜率 |
| 本轨禁止复用 | 器件数：**28.8%**、**35 个/秒**、**120:1**；编造其畴缺陷公式系数；离子纠缠 / DIQKD 叙事；把 `dir1_metrology` run7 **纯度**当成转换效率 |

## 引用边界

- 可写：「潘等报道 PPLN 薄膜上的量子频率转换器件；本稿为**标准模型预算，不是该实验的复现**（STATUS / params_table 必写）。读不到原文公式则用教科书 QPM。」
- 不可写：28.8% / 35/s / 120:1 进结果表；推荐波导长度或周期；可流片设计。
- 与膜厚计量稿：材料同属 PPLN 薄膜、误差同属畴/厚度，但**可写量不同**（转换效率与泵浦噪声 vs SPDC 纯度上界）；run7 纯度 ≠ 转换效率。

## BibTeX

```bibtex
@article{Pan2026QFC,
  author={Pan, Jianwei and Zhang, Qiang and Zheng, Mingyang and others},
  title={Quantum frequency conversion from 393 nm to 1550 nm in periodically poled thin-film lithium niobate},
  journal={Phys. Rev. Lett.},
  year={2026},
  doi={10.1103/wx56-plcm},
  note={Device result (efficiency/noise/SNR are theirs). Our track: standard QPM budget, not a reproduction — do not copy 28.8%, 35/s, or 120:1 into results. Verify full author list and title from the publisher page before camera-ready.}
}
```

---
**统一禁令（文献包）**：文献/新闻数字只作对照；正文表内数必须来自本轨 `summary.json`；禁止第三方 PDF 入库；负结果照写。
