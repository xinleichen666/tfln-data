# 参数表 · dir1_metrology（run7 / TM 自洽）

来源优先级：`tm_coeff.json` > `run7.json` 头字段 > `report_v7.md`。  
**kind：** `public_trace` = 公开文献曲线；`computed` = 本组模式求解；`assumed` = 假设；`loss_lit` = 文献损耗公式。

## A. 过程与几何

| 量 | 值 | kind | 注 |
|---|---|---|---|
| 过程 | x-cut TFLN；泵 TM 764 nm；信号 TE 1528 nm；闲频 TM 1528 nm | computed / lit-aligned | 对齐 Kuttner type-II 口径 |
| 膜厚 t | 0.6 µm | lit / assumed center | Kuttner 标称 600 nm |
| 波导宽 w | 1.4 µm | **assumed** | Kuttner 未给；SEM 读数另有 ±0.2 µm 量级不确定性 |
| 刻蚀 h | 0.3 µm | **assumed** | Kuttner 未给 |
| 侧壁 | 垂直 | assumed | — |
| 极化周期 Λ | 2.826 µm（0.002826 mm） | computed | 同套中心折射率 |

## B. 相位 / 群速度系数（`tm_coeff.json`）

| 符号 | 值 | 单位 | kind | 方法 |
|---|---|---|---|---|
| St | −3.129339067917858 | rad/mm/nm | computed | 600 nm 局部中心差分 ±5 nm；**非** 560–640 割线 |
| （未用割线） | −3.1614231863126006 | rad/mm/nm | computed unused | `not_used_secant_560_640` |
| Sw | −0.3346835390647174 | rad/mm/nm | computed | w ±40 nm @ t=0.6, h=0.3 |
| Sh | 0.5170102050508385 | rad/mm/nm | computed | h ±10 nm @ t=0.6, w=1.4 |
| A | 0.5730288805776356 | ps/mm | computed | 泵−信号群速度失配 |
| B | −0.12024417114865216 | ps/mm | computed | 泵−闲频群速度失配 |

## C. 蒙特卡洛与计量

| 量 | 值 | kind | 注 |
|---|---|---|---|
| 种子 | 2027 | fixed | — |
| NMC | 64 / 每长度 | fixed | — |
| 膜厚迹线 | Chen 2023 Fig.1d；Xin 2024 Fig.2b | **public_trace** | L≤5 mm 各半；更长全 Chen |
| 宽度起伏基线 | 2 nm RMS（1/f） | **assumed** | 应力：10 nm |
| 刻蚀起伏 | ~0.2 nm（Chen 路径粉红噪声） | assumed / proxy | Xin 路径用曲线第 3 列 |
| 残余泵啁啾 | ±0.25 τ² | assumed | — |
| 计量间距 Δz | 不处理 / 0.2 / 0.1 / 0.04 mm | scan | 自适应极化用采样点插值补偿 St·δt |
| 膜厚测量误差 ε | 0.3 nm（主表） | **assumed** | 应力：1 nm |

## D. 损耗 → 预告效率（不进纯度主曲线）

| 量 | 值 | kind | 注 |
|---|---|---|---|
| 信号传播 | 0.54 dB/cm | loss_lit | Zhao 等近 1569 nm |
| 泵传播 | 0 | assumed this round | — |
| 端面 | 10^(−0.7) | loss_lit | 未抛光保守情形 |
| 探测 | 0.68 | loss_lit | — |
| η_h | 10^(−0.7)×0.68×Tph | derived | 2–20 mm：0.134→0.120 |
| B（json 第 2 列） | 原始 JSA 范数 | computed | **未**乘 gen |

## E. 主结果提要（中位纯度；基线假设）

| L (mm) | 不处理 | Δz=0.2 | Δz=0.1 | Δz=0.04 |
|---|---|---|---|---|
| 2 | 0.941 | 0.972 | 0.977 | 0.984 |
| 5 | 0.574 | 0.916 | 0.950 | 0.969 |
| 10 | 0.372 | 0.789 | 0.879 | 0.906 |
| 15 | 0.255 | 0.671 | 0.790 | 0.849 |
| 20 | 0.162 | 0.579 | 0.717 | 0.756 |

理想纯度一律 **0.995**。完整 10–90% 分位见 `report_v7.md` §3 与 `run7_summary.json`。
