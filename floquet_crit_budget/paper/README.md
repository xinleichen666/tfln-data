# floquet_crit_budget · Floquet SSH 临界签名噪声预算（Bot D）

**体裁：** 方法·噪声预算（经典数值仿真工作稿）  
**先验对照（仅引用，不复现实验）：** Cheng et al., *Nature* **658**, 358 (2026), doi:10.1038/s41586-026-11067-5  
**日期：** 2026-10-13（Asia/Shanghai）  
**模型口径：** **标准模型诊断，不是该实验的复现。**

---

## 挂仓声明（不得删）

本稿仅限课题组内部：仿真与方案工作稿，实测待做，无伪造数据，Fiber-Q 对本方向 N/A，无自有流片；不得作为公开或可引用结果；verify/ 第三方 PDF 禁止入库。

---

## 一句话

教科书一维两步 Floquet SSH 开链上，干净极限同时给出 0 / π 边缘模与半链纠缠熵；再扫**键无序**与**交错损耗**，记录体隙与 EE 相对干净极限的变化，并从本扫标出签名消失阈值（或写「本扫范围内未消失」）。不声称观测、不编造 Nature 耦合、不画推荐器件长度。

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
cd /workspace/floquet_crit_budget
./scripts/run_all.sh
```

固定种子见 `STATUS.md` 与 `summary.json` → `seeds`。
