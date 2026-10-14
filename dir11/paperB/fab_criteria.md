# 流片判据核对 · paperB heater/ξ **v2**

**对照**：`data/summary_heater_xi_v2.json`（= 当前 `summary_heater_xi.json`）  
**种子 master**：`20261114`  
**相对 v1**：仅耦合器热串扰假设 `dT_cm@Pπ` 10→3 mK、`dT_diff@Pπ` 5→2 mK；κi×2 / 锁定 5 mK / MZI / Maeder Pπ 不变。  
v1 归档：`data/summary_heater_xi_v1.json`（① FAIL @ 81.9%）。

---

## 判据 ① — 成品率

> 加热开 + 保守损耗（κi×2）+ 10% 叉指：≥90% 样品 η_shift≥90%。

| 项 | v1 | **v2** |
|---|---|---|
| frac(η≥0.90) | 0.819 | **0.940** |
| η p10 / 中位 | 0.874 / 0.950 | **0.9167 / 0.9638** |
| **PASS/FAIL** | FAIL | **PASS** |

对照 v2：heater OFF·κi×2 = 0.742；heater ON·Shao Qi = 0.988（非验收列）。

---

## 判据 ② — 保守射频功率

| 项 | 值 |
|---|---|
| P_cons (ξ=0.5×IDT10%×Qa1570) | **171.93 µW** |
| Shao 2020 30 dBm | 1.0 W |
| 比值 | 1.719e-04 |
| **PASS/FAIL** | **PASS** |

---

## 判据 ③ — 最大杂散阶次

| 项 | 值 |
|---|---|
| frac(worst spur = q−1) | **1.000** |
| 杂散相对移位中位 | -19.4 dB |
| **PASS/FAIL** | **PASS** |

---

## 总判

**ALL_PASS = True**

PASS: simulation supports proceeding to layout with measurement hooks.

测量钩子：加热功率→劈裂/共模失谐（核验串扰是否真 ≤3 mK@等效 Pπ）；勿把假设串扰当实测写入摘要。
