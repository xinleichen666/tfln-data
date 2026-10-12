# 方向一 · 本文参数表（实测 / 计算 / datasheet / assumed 分列）

> 与 `/workspace/freq_shift_noise/params.json`、`report_formulas_v1.md`、`/workspace/tfln_review/ao_shared_params_v1.md` 一致。  
> **乙类脚注**：锁定用 Table S2 **2.007 GHz**（\(n_\mathrm{th}\approx3.11\times10^3\)）；共用表 §3 的 **2.17 GHz** 只对应跑道环 \(g_0\) 语境，**不要混用**。

## A. 文献实测锚定

| 量 | 数值 | 平台 / 条件 | 来源 | 栏 |
|---|---|---|---|---|
| Shao 片上转换效率 η | **3.5%** @ 30 dBm | 行波布拉格偏转口；**非本实验** | Shao et al., Opt. Express **28**, 23728 (2020) | 文献实测 |
| Shao CSR \(R_c\) | **≈31 dB**（Stokes）；anti-Stokes≈33；摘要 >30 | 偏转口 \(P_{+1}/P_0\) | 同上 Fig.3 | 文献实测（锚） |
| Shao SSR | **>40 dB**（噪声底以下） | 对侧边带 | 同上 | 文献实测（账本按下界 **40 dB**） |
| Shao 光纤–光纤 IL | **−15 dB** | 透射口 fiber-to-fiber | 同上 Fig.4 附近 | 文献实测（**只进计数率**） |
| Shao 声频（行波） | **~3 GHz** | 行波 Bragg AOFS | 同上 | 文献实测 |
| Shao 微波带宽 | **~70 MHz**（3 dB） | 行波 IDT | 同上 | 文献实测 |
| Shao \(V_\pi\) | **4.6 V** @ 100 µm → \(V_\pi L\approx0.046\) V·cm | 悬空 X-cut TFLN；~3.33 GHz | Shao et al., Optica **6**, 1498 (2019) | 文献实测 |
| Shao \(g_0/2\pi\) | **1.1 kHz** | Table S2 | 同上 | 文献实测 |
| Shao \(\kappa/2\pi\) | **95 MHz**；\(2\kappa_e/\kappa=0.3\) | Table S2 | 同上 | 文献实测 |
| Shao \(\gamma/2\pi\) | **1.28 MHz**；\(2\gamma_e/\gamma=0.34\) | Table S2 | 同上 | 文献实测 |
| Shao \(\Omega/2\pi\) | **2.007 GHz**（Table S2） | 乙类锁定全套；**非** 2.17 GHz 跑道行 | 同上 Table S2 | 文献实测 |
| Shao \(C_0\) | **\(\approx4\times10^{-8}\)** | 单光子合作参量 | 同上；代码算 3.98e-8 | 文献实测 |
| Shao \(Q_\mathrm{ac}\) | 典型建模 **2000**；文中最高约 **3600** | Fig.3(c) | 同上 | 文献实测 |
| Zhu \(C/P_a\) | **2.46 mW⁻¹** | 声学光子分子 / DBM | Zhu et al., arXiv:2511.22585 | 文献实测 |
| Zhu \(R_\max\) | **24%** @ 6.3 mW 声功率 | Al IDT 功率受限 | 同上 | 文献实测 |
| Zhu 声频 | **8.54 GHz** | backward Brillouin | 同上 | 文献实测 |
| Xu \(\alpha\) | **1774±171 GHz²/W** | LNOS 环耦合；8.533 GHz | Xu et al., arXiv:2509.01940 | 文献实测 |
| Xu RF→acoustic | **≈10%** | IDT 效率量级 | 同上 | 文献实测 |
| Hu 电光转换 | ~99% | 电光双环；**效率定义不同，不与 3.5% 比胜负** | 共用表 / 选题简报 | 文献（旁注） |

## B. 本文计算（甲 / 乙 / 丙读数）

| 量 | 名义值 | 带 / 备注 | 栏 |
|---|---|---|---|
| \(V_\mathrm{bin}\)（Shao 锚） | **≈0.9991** | \(R_c=31\,\mathrm{dB}\)，SSR=40 dB；**偏转口纯度 ≠ 台面 HOM** | 本文计算 |
| \(F_\mathrm{rate}\)（Shao 工作点） | **≈1.11×10⁻³** | \(\eta=0.035\times10^{-1.5}\)；**不进 \(V\)** | 本文计算 |
| \(C_0\)（乙） | **≈3.98×10⁻⁸** | 与文献 \(4\times10^{-8}\) 一致 | 本文计算 |
| \(n_\mathrm{th}\)（乙，2.007 GHz，300 K） | **≈3.11×10³** | 公式计算，非噪声谱实测 | 本文计算 |
| \(N_\mathrm{add}\)（乙） | **≈1.52×10⁴** | \(n_\mathrm{th}\,\gamma_i/\gamma_e\)；**非主结果** | 本文计算 |
| \(n_\mathrm{th}\)（丙，8.54 GHz，300 K） | **≈7.31×10²** | 与共用表 §3 一致 | 本文计算 |
| \(C\)（丙，Zhu 锚） | **≈15.5** | \(2.46\times6.3\) mW | 本文计算 |
| \(\delta_\mathrm{sp}\)（丙，\(R=24\%\)） | **≈0.922** | 模型假设 | 本文计算（assumed 公式） |
| \(V_\mathrm{upper}\)（丙，\(R=24\%\)） | **≈0.019** | \(C\times0.5/1/2\) → ≈0.0098 / 0.019 / 0.035 | 本文计算 |

## C. Datasheet（商用台面对照，非本组测量）

| 参数 | 取值 | 说明 |
|---|---|---|
| fiber_AOM 消光 | ≥50 dB（on/off，1st order） | G&H Fiber-Q；**≠ 已测 \(R_c\)** |
| fiber_AOM IL | typ −2～−2.5 dB（40/80 MHz） | 只进符合计数率估计 |
| 驱动频率量级 | ~40–200 MHz | **≠** 片上 ~3 GHz |

## D. 关键假设（计算输入，非实测）

| 参数 | 取值 | 说明 |
|---|---|---|
| \(\delta_\mathrm{sp}=n_\mathrm{th}/(n_\mathrm{th}+4C)\) | 公式 | 丙类自发进信号仓；kind=**assumed**；图注「模型假设」 |
| fiber_AOM_eta_typical | ~0.5（量级） | 商用衍射效率量级对照；主账本不依赖精确值 |
| 时间重叠 \(\mathcal{O}\) | 1 | 本轮完美重叠；以后可乘 |
| SSR 模型 | 40 dB 下界 | 现用 Shao；台面自测寄生阶后可替换 |
| Zhu \(R=99\%\) @ ~26 mW | 理论外推 | **不作**主结果；仅敏感性参考 |

材料 / 公式出处详见 `../report_formulas_v1.md` §6 与共用表。Xu 4.03 rad/W 为方向二锚，**方向一不引用**。
