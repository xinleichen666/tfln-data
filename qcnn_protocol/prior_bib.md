# 先验短表 · Bot B `qcnn_protocol/`

**日期**：2026-10-13 · 文献包  
**用途**：只 bib / 引用边界；**不改**本轨任何数字。

## 先验

| 项 | 内容 |
|---|---|
| 题名 | Quantum Convolutional Neural Networks for Jet Images Classification |
| 作者 | Hala Elhag, Tobias Hartung, Karl Jansen, Lento Nagano, Giorgio Pirina, Alice Di Tucci（作者表以 arXiv/正式刊为准） |
| 出处 | arXiv:**2408.08701**；正式刊 *Quantum Machine Intelligence*（Springer, DOI 见出版社页） |
| 主张（摘要级） | 无噪声经典模拟器上 QCNN vs 结构对应 CNN；扫编码/损失/批大小；DEA 删冗余参数；喷注标记任务他们已做完 |
| 本轨可用 | 协议对照框架、DEA 删门、参数量对齐的经典对照 |
| 本轨禁止复用 | top-quark / HEP 喷注准确率数字；硬件结果；把其「QCNN 更好」写成己方标题 |

## 引用边界

- 可写：「Elhag et al. 给出无噪声模拟器上 QCNN–CNN 协议对照；本稿换小规模本地/公开二分类图，只报**实际跑完**的编码/损失/批大小。」
- 不可写：声称顶夸克或高能物理结果；未跑完的设置写成「我们比较了」。

## BibTeX

```bibtex
@article{Elhag2024QCNN,
  title={Quantum Convolutional Neural Networks for Jet Images Classification},
  author={Elhag, Hala and Hartung, Tobias and Jansen, Karl and Nagano, Lento and Pirina, Giorgio and Di Tucci, Alice},
  year={2024},
  eprint={2408.08701},
  archivePrefix={arXiv},
  primaryClass={quant-ph},
  url={https://arxiv.org/abs/2408.08701},
  note={Also Quantum Machine Intelligence (Springer); verify journal pages via DOI before camera-ready}
}
```

---
**统一禁令（文献包）**：文献数字只作对照；正文表内数必须来自本轨 `summary.json`；禁止把先验准确率/覆盖率/间隙抄成己方结果；禁止第三方 PDF 入库。
