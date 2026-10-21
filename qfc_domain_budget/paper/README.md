# qfc_domain_budget · 量子频率转换畴/膜厚噪声预算（Bot F）

**体裁：** 方法·噪声预算（经典数值仿真工作稿）  
**先验对照（仅引用，不复现实验）：** Phys. Rev. Lett. doi:10.1103/wx56-plcm（393 nm→1550 nm 周期极化薄膜铌酸锂 QFC）  
**日期：** 2026-10-14（Asia/Shanghai）  
**模型口径：** **标准模型预算，不是该实验的复现。**

---

## 挂仓声明（不得删）

本稿仅限课题组内部：仿真与方案工作稿，实测待做，无伪造数据，Fiber-Q 对本方向 N/A，无自有流片；不得作为公开或可引用结果；verify/ 第三方 PDF 禁止入库。

---

## 一句话

自设泵浦/信号/闲频与极化周期，用标准准相位匹配把畴壁抖动、占空比、膜厚偏移扫进相对转换效率；同一组温度与周期扫描上比较频率转换与泵浦寄生 SPDC 的 Δk 斜率。斜率反号才写「本模型里见到反向调谐」，否则写「未见到」。不抄器件效率/噪声数，不设推荐长度。

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
cd /workspace/qfc_domain_budget
./scripts/run_all.sh
```

固定种子见 `STATUS.md` 与 `summary.json` → `seeds`。本轮 sha16=`3cf8304f4934b627`。
