# 先验短表 · Bot D `floquet_crit_budget/`

**日期**：2026-10-13 · 文献包  
**用途**：只 bib / 引用边界；**不改**本轨任何数字。

## 先验

| 项 | 内容 |
|---|---|
| 题名 | Observation of critical topological phase transition |
| 作者 | Zheyu Cheng, Xiuhai Zhang, Xue-Jia Yu, Longwen Zhou, Jiangbin Gong, Baile Zhang |
| 出处 | *Nature* **658**, 358–364 (2026)；DOI: [10.1038/s41586-026-11067-5](https://doi.org/10.1038/s41586-026-11067-5) |
| 主张（摘要级） | 声学超材料上 **观测** 一维 Floquet 临界拓扑相变（含零能 / π 边缘模等） |
| 复现数据 | NTU dataset DOI:10.21979/N9/ALTJGQ（可选读补充；**禁止**把实验耦合数编进未读到的参数） |
| 本轨可用 | Floquet SSH 叙事对照；干净极限 + 无序/损耗**预算扫**框架 |
| 本轨禁止 | 写「观测到」；编造 Nature 文中的耦合数值；画「推荐器件长度」 |

## 引用边界

- 可写：「Cheng et al. 报道声学超材料实验观测；本稿做**无噪声数值模拟预算**（标准 Floquet SSH 诊断，若读不到实验参数须在 STATUS/`params_table` 标明非该实验复现）。」
- 多临界点：仅当本轨相图能定出两条临界边界交点时才报；定不出不报可加对数。
- 签名消失阈值必须来自本轨扫；扫不到写「本扫范围内未消失」。

## BibTeX

```bibtex
@article{Cheng2026Floquet,
  author={Cheng, Zheyu and Zhang, Xiuhai and Yu, Xue-Jia and Zhou, Longwen and Gong, Jiangbin and Zhang, Baile},
  title={Observation of critical topological phase transition},
  journal={Nature},
  volume={658},
  pages={358--364},
  year={2026},
  doi={10.1038/s41586-026-11067-5},
  note={Experimental acoustic metamaterial observation; our track is classical numerical budget only — do not claim observation or invent their couplings}
}
```

---
**统一禁令（文献包）**：文献数字只作对照；正文表内数必须来自本轨 `summary.json`；禁止把先验准确率/覆盖率/间隙抄成己方结果；禁止第三方 PDF 入库。
