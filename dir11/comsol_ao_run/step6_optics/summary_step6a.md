# Step 6a：光路 B（周期平均 / K 分量）与分箱 δn(x)

## 1) 检查与自检

| 项目 | 值 |
|---|---|
| SELFCHECK phiL=0.405367 expect=0.4054 |  |
| GROUND_CHECK nTerm=1 nGn=1 |  |
| TERMINAL_CHECK nTerm=1 nGnd=1 |  |
| NUMELEM n_elem=2502 |  |
| DATASET dset1 |  |
| TENSOR_CHECK i=0 value=2.02897000e+11 |  |
| TENSOR_CHECK i=1 value=2.43075000e+11 |  |
| TENSOR_CHECK i=2 value=8.99874000e+09 |  |
| TENSOR_CHECK i=3 value=-8.99874000e+09 |  |
| TENSOR_CHECK i=4 value=-8.98526000e+09 |  |
| PEAK_INDEX 56 PEAK_F_GHz=3.329800000 PEAK_ABS_Y=4.580679652e+01 |  |
| REF320_INDEX 0 F=3.200000000 |  |
| BINCHECK f_GHz=3.329800000 avgPE_rel=9.8313e-10 avgEO_rel=2.4505e-10 avgMB_rel=6.0143e-10 KPE_rel=1.9776e-03 KEO_rel=1.1893e-03 KMB_rel=3.4233e-03 |  |
| BINCHECK f_GHz=3.200000000 avgPE_rel=9.6070e-09 avgEO_rel=8.7099e-10 avgMB_rel=5.3016e-10 KPE_rel=9.0739e-05 KEO_rel=1.3990e-04 KMB_rel=7.2409e-04 |  |
| POINT6 Ex=1.009397e+06/5.966174e+05 Ey=2.264901e+02/-1.403169e+03 exx=-1.923036e-05/1.288038e-04 eyy=5.405330e-05/-1.735743e-04 v=-3.361026e-10/1.633777e-09 |  |
| RES6 fr_GHz=3.329800000 Yr=4.580679652e+01 fa_GHz=3.334000000 Ya=1.508832012e+00 k2=2.517909e-03 |  |

- 修正 1 自检：|δn|=1e-4 时 φ/L = 0.405367 rad/(mm·V)（期望 0.4054）

- 共振：fr = 3.329800000 GHz（|Y| = 4.580679652e+01 S）；反共振：fa = 3.334000000 GHz（|Y| = 1.508832012e+00 S）；k² = (fa²−fr²)/fa² = 2.517909e-03

## 2) 光路 B：共振峰与 3.20 GHz 的周期平均 / K 分量

| f_GHz | metric | avg Re | avg Im | avg Abs | K Re | K Im | K Abs |
|---|---|---|---|---|---|---|---|
| 3.200000000 | PE | None | None | None | None | None | None |
| 3.200000000 | EO | None | None | None | None | None | None |
| 3.200000000 | MB | None | None | None | None | None | None |
| 3.329800000 | PE | None | None | None | None | None | None |
| 3.329800000 | EO | None | None | None | None | None | None |
| 3.329800000 | MB | None | None | None | None | None | None |

## 3) 分箱 δn(x) 自检（Σ 箱 vs 二维积分）

- BINCHECK f_GHz=3.329800000 avgPE_rel=9.8313e-10 avgEO_rel=2.4505e-10 avgMB_rel=6.0143e-10 KPE_rel=1.9776e-03 KEO_rel=1.1893e-03 KMB_rel=3.4233e-03
- BINCHECK f_GHz=3.200000000 avgPE_rel=9.6070e-09 avgEO_rel=8.7099e-10 avgMB_rel=5.3016e-10 KPE_rel=9.0739e-05 KEO_rel=1.3990e-04 KMB_rel=7.2409e-04

## 4) 分箱窗口最佳值（光路 B TE）

- WIN6 f_GHz=3.329800000 w_um=0.30 j0=99 x0_um=2.477269 Tot_Re=1.191252e-04 Tot_Im=-7.258191e-04 Tot_Abs=7.355299e-04
- WIN6 f_GHz=3.329800000 w_um=0.50 j0=94 x0_um=2.352155 Tot_Re=8.637485e-05 Tot_Im=-5.507445e-04 Tot_Abs=5.574766e-04
- WIN6 f_GHz=3.329800000 w_um=0.80 j0=85 x0_um=2.126948 Tot_Re=2.710851e-05 Tot_Im=-2.304857e-04 Tot_Abs=2.320744e-04
- WIN6 f_GHz=3.200000000 w_um=0.30 j0=0 x0_um=0.000000 Tot_Re=-3.110626e-05 Tot_Im=2.416900e-08 Tot_Abs=3.110627e-05
- WIN6 f_GHz=3.200000000 w_um=0.50 j0=50 x0_um=1.251146 Tot_Re=2.908796e-05 Tot_Im=-9.675518e-09 Tot_Abs=2.908796e-05
- WIN6 f_GHz=3.200000000 w_um=0.80 j0=96 x0_um=2.402201 Tot_Re=-2.688237e-05 Tot_Im=-3.495354e-09 Tot_Abs=2.688237e-05

## 5) 说明

- 分箱：dx = p/114，箱指示函数 (x>=x_j)*(x<x_j+dx)；PE/EO 用 intLN 二维积分，MB 用 intTop/intBot 线积分。
- 采样频点：3.31–3.36 GHz 步长 1 MHz + 3.3280–3.3320 GHz 步长 0.05 MHz + 3.20/3.45 GHz。
- 只报数字，不下结论。

