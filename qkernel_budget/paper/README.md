# qkernel_budget · 分块保真度核 · 失配/标签噪声预算（Bot A）

**体裁：** 方法·噪声预算（经典数值仿真工作稿）  
**先验对照（仅引用，不重跑欺诈任务）：** Peng, Lu, Chen, arXiv:2608.24631  
**日期：** 2026-10-13（Asia/Shanghai）

---

## 挂仓声明（不得删）

本稿仅限课题组内部：仿真与方案工作稿，实测待做，无伪造数据，Fiber-Q 对本方向 N/A，无自有流片；不得作为公开或可引用结果；verify/ 第三方 PDF 禁止入库。

---

## 一句话

自造 thin-slab 数据上，**分块对准**时块保真度核相对 RBF 有表示优势；**分块边界划错**或**训练标签翻转**增大时，该差值如何塌到 ≤0（或本扫范围内未消失）。不声称量子加速、不跑 IBM、不重写欺诈基准。

## 目录

| 路径 | 内容 |
|---|---|
| `main_zh.md` | 中文技术工作稿 |
| `non_claims.md` | 禁令 / 本轮未做 |
| `params_table.md` | 文献 / 本轮计算 / 假设 分列 |
| `fig/` | 脚本出图 png+pdf |
| `../data/summary.json` | 全部数字出处 |
| `../scripts/run_all.sh` | 从空 `data/` 重跑 |

## 重跑

```bash
cd /workspace/qkernel_budget
./scripts/run_all.sh
```

固定种子见 `STATUS.md` 与 `summary.json` → `seeds`。
