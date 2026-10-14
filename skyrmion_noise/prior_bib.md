# 先验短表 · Bot E `skyrmion_noise/`

**日期**：2026-10-14 · 文献包  
**用途**：只 bib / 引用边界；**不改**本轨任何数字。

## 先验

| 项 | 内容 |
|---|---|
| 题名 | （芯片上光子量子斯格明子；正式题名以出版社页为准） |
| 作者 | Zhao 等 |
| 出处 | *Nat. Phys.* (2026)；DOI: [10.1038/s41567-026-03487-x](https://doi.org/10.1038/s41567-026-03487-x) |
| 主张（摘要级） | 氮化硅芯片上路径纠缠 + 微环角光栅把单光子编成自旋纹理；双光子上测到斯格明子型关联；拓扑数可在纠缠消失后仍作关联见证（**非**态转移操作优势） |
| 本轨可用 | 「斯格明子数 vs concurrence / discord 谁先垮」的噪声预算问法；近各向同性退极化 / 相位翻转 / 比特相位翻转信道框架 |
| 本轨禁止复用 | 新闻/实验数：**斯格明子数≈1.981**、四态平均保真度**≈89%**、纯度**≈0.34**（concurrence→0）/ **≈0.25**（斯格明子数掉）、混合比例**0.5**；氮化硅流片叙事；与 Floquet 轨并篇 |

## 引用边界

- 可写：「Zhao et al. 在芯片实验上报道光子斯格明子相关现象；本稿在**自定**自旋–轨道纹理上做经典噪声预算，斯格明子数必须为纹理积分。」
- 不可写：把 1.981 / 89% / 0.34 / 0.25 / 0.5 写入结果表；用 4×4 矩阵本征值冒充斯格明子数；声称态转移优势或芯片制备。
- 与 D（`floquet_crit_budget/`）只问法像、对象不同：**禁止**并成一篇或改成 TFLN 器件。

## BibTeX

```bibtex
@article{Zhao2026Skyrmion,
  author={Zhao and others},
  title={Photonic quantum skyrmions on a chip},
  journal={Nature Physics},
  year={2026},
  doi={10.1038/s41567-026-03487-x},
  note={Experimental SiN chip result; our track is classical noise budget on a self-defined texture — do not copy 1.981 / 89% / purity 0.34|0.25 / mix 0.5 into results. Verify full author list and title from the publisher page before camera-ready.}
}
```

---
**统一禁令（文献包）**：文献/新闻数字只作对照；正文表内数必须来自本轨 `summary.json`；禁止第三方 PDF 入库；负结果照写。
