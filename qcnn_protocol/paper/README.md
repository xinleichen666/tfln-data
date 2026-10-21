# qcnn_protocol — 内部工作稿说明

**本稿仅限课题组内部：仿真与方案工作稿，实测待做，无伪造数据，Fiber-Q 对本方向 N/A，无自有流片；不得作为公开或可引用结果；verify/ 第三方 PDF 禁止入库。**

## 题目取向
无噪声模拟器上 **QCNN–CNN 协议对照**（参数量对齐 + 敏感性剪枝），**不是**「量子胜过经典」。

## 先验（只作框架，不抄结果数字）
见根目录 `prior_bib.md`：Elhag et al., arXiv:2408.08701。可引用其「无噪声模拟器 + 结构对应 CNN + DEA 删门」协议；**禁止**复用其喷注/HEP 准确率，正文也不声称 top-quark 结果。

## 本轨数据
- 本地生成 4×4「横条 vs 对角」二分类图（`scripts/run_protocol.py`），非公开 HEP 数据。
- 全部表内数字来自 `data/summary.json`（固定种子可重跑）。

## 重跑
```bash
bash scripts/regenerate.sh
```
需清空/覆盖 `data/summary.json`、`histories.json`、`examples.npz` 后由脚本再生；图写入 `paper/fig/`。

## 文件
| 路径 | 内容 |
|------|------|
| `main_zh.md` | 中文工作稿正文 |
| `non_claims.md` | 本轮未做声明 |
| `params_table.md` | 文献 / 本轮计算 / 假设 分列 |
| `fig/` | 脚本出图 png+pdf |
| `../data/summary.json` | 唯一结果源 |
| `../STATUS.md` | 进度与阻塞 |

## 模拟器
`numpy_statevector_v1`，4 qubit，优化器 SPSA；经典侧为参数量匹配的 tanh-MLP（非卷积实现细节见 params_table）。
