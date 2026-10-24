# 论文 B（设计研究）：声学驱动光子分子单光子频移器——声学频移器类别中的记录水平（仿真）

> **定位（务必如实）**：本文是仿真/设计预测，不是实测。设计 B 远超已发表的 TFLN 声光频移器（Shao 2020 实测片上效率 3.5%），但与**同样做了阻抗匹配的 EO 驱动相比没有显著功率优势**（0.36–3.9 倍，电感损耗低时 EO 更优），而且 EO 的 RF 带宽宽约 100 倍。所以不主张"超过总体 SOTA"。

## 1. 结构与方法
- 结构：Hu et al. 的耦合双环光子分子（Nature 599, 587 (2021)，arXiv:2005.09621），只有环 1 与总线耦合。环 1 的 100 µm 段嵌入悬空 LN 声学谐振腔，腔由 IDT 驱动（几何与标定来自 Shao et al., Optica 6, 1498 (2019)，arXiv:1907.08593）。环长 0.667 mm（覆盖比 0.15，与 Shao 跑道腔的 η_cav 相同），n_g=2.3。双环劈裂 2μ = 声频 Ω_m/2π = 3.33 GHz。
- 方程：Hu 补充材料 Eq. S2，全时域 RK4 积分（不做 RWA）：
  $\dot a_1=[-i(\omega_1-\omega_L+\delta\omega\cos\Omega_m t)-(\gamma+\kappa_i)/2]a_1-i\mu a_2-\sqrt\gamma\alpha_{in}$，
  $\dot a_2=[-i(\omega_2-\omega_L+s\,\delta\omega\cos\Omega_m t)-\kappa_i/2]a_2-i\mu a_1$。
  其中 AO 取 s=0（只调制单环），EO 推挽取 s=−1。输出 $a_{out}=\alpha_{in}+\sqrt\gamma a_1$，投影到 $\omega_L+q\Omega_m$ 各阶。
- 定义：η_shift = P_shift/P_out（与 Hu 相同）；绝对效率 = P_shift/P_in。
- 声致调制：$\delta\omega=\Delta\phi\,c/(n_gL_{ring})$，$\Delta\phi=\pi V/V_\pi(L_a)$，Shao 单臂 MZI 实测 $V_\pi$=4.6 V @100 µm。**Shao 的 $V_\pi$ 是用 VNA 源功率 $P_{in}=V_p^2/(2\cdot50\,\Omega)$ 从 S21 反推的（正文 Eq. 1，补充材料 Eq. S8）**，所以已经包含他们 IDT 实测约 50% 的电-声耦合（S11 −3 dB）。得到 $K_{AO}$=2π×21.3 GHz/V（源端）。
- EO 基线：Hu 的系数 0.5 GHz/V（以电容电压 V_c 计），电极参数 C=0.11 pF、L=0.12 nH、R=1.5 Ω（Hu Supp. Sec. V，已核实）。
- 光学参数：γ/2π=0.6 GHz。κ_i 取 **Shao 2019 实测值**：κ/2π=95 MHz、2κe/κ=0.3，所以 κ_i/2π=80.75 MHz、Q_i≈2.4×10⁶（Table S2，数值记录在主 report 中；本会话未重新打开 Table S2）。

## 2. 主要结果（`data/results_B.json`）
| | AO（设计 B） | 匹配 EO（相同光学参数，推挽） |
|---|---|---|
| η_shift | 98.3% | 99.6% |
| 绝对效率 / IL | 55% / 2.5 dB | 56% / 2.5 dB |
| 载波（相对移频线） | −23 dB | −26 dB |
| 最大寄生阶 | −21 dB（q=−1） | −30 dB |

**源端 RF 功率（公平对比表，图 B1a、B2c；`data/eff_vs_power.csv`）**
| 驱动情形 | 源功率 |
|---|---|
| AO，Shao IDT 实测（约 50%） | **6.7 µW** |
| AO，理想匹配 IDT（100%） | 3.4 µW |
| AO，IDT 效率 10%（Xu 2025 LNOS 的水平） | 34 µW |
| AO，非谐振行波（Xu α 换算，10% IDT，迭代 7） | 约 0.47 mW |
| EO 不匹配（V_c=V_0，Hu 的约定） | 3.1 mW |
| EO 开路电容（V_c=2V_0） | 0.77 mW |
| EO LC 匹配，电感 Q=30（带宽约 122 MHz） | 13 µW |
| EO LC 匹配，电感 Q=100 | 4.8 µW |
| EO LC 匹配，理想电感 | 1.2 µW |
| Hu 2021 实测（28.2 GHz，η=98.7%） | 96 mW |

注：本表在 γ/2π=0.6 GHz 处取 η_shift 最优点，所以数值与迭代 6/7（7.4 µW、3.25 mW）有约 10% 的差别，这是优化网格不同造成的，结论不变。

**结论**：
- 不匹配对不匹配：AO 约为 EO 的 1/460。
- **匹配对匹配：AO 3.4 µW 对 EO 1.2–13 µW，在 0.36–3.9 倍之间，没有实质优势。**
- 对已发表的 AO 频移器：Shao 2020 在 30 dBm（1 W）下片上效率 3.5%，本设计在约 7 µW 下 η_shift 98%，绝对效率 55%，属于该类别的记录水平（仿真）。

**容差**（图 B2）：
- Q_i：Q_i ≳ 1.3×10⁶ 时 η_shift ≈ 98%；绝对效率在 Q_i=2.4×10⁶ 时为 55%，9.7×10⁶ 时为 87%；Q_i=6.4×10⁵ 时 η_shift 降到 82%。
- RF 失谐（声学 Q=2000，FWHM 1.67 MHz）：η_shift 在 ±0.4 MHz 内 ≥96.7%，1 MHz 处 80%，2 MHz 处 44%，5 MHz 处 10%。EO 在 5 MHz 失谐内保持 99.6%（以 LC 带宽约 122 MHz 内驱动近似恒定为前提）。
- IDT 效率：AO 功率与 1/η_IDT 成正比。η_IDT 低于约 25% 时 AO 就不如 Q=30 的 LC 匹配 EO（图 B2c）。

## 3. 补充：HOM 可见度与热声子噪声
- **HOM**（`hom_post.py`，`data/HOM.csv`，图 B3）：输入为高斯单光子（强度谱 rms 宽 σ），用全时域计算移频通道的复传递函数 H(Δ)；参考光子做延迟匹配（群延迟约 1.1 ns），只滤出目标频率 bin。
  - 1−V = 8×10⁻⁷（σ=10 MHz）、3×10⁻⁵（25 MHz）、6×10⁻⁴（50 MHz）、1.1×10⁻²（100 MHz）、9×10⁻²（200 MHz）。
  - 不滤波时，V 受 η_shift 限制，约 0.983。
  - 适用对象：窄带光子源（σ ≲ 50 MHz，例如腔增强 SPDC、量子点/原子发射）。
- **热声子**：
  - 移频是无光泵浦、粒子数守恒的分束器型过程。没有输入光子就不产生噪声光子；热声子只给耦合加入量级为 n_th/N_coh 的非相干涨落。
  - 驱动声子数 N_coh=4γ_e/γ²·P/ħΩ ≈ 1.75×10¹¹（γ=Ω_m/2000，γ_e/γ=0.15，取自 Shao 2019 Supp.）。
  - n_th = 1877（300 K）、24.5（4 K）、1.1×10⁻⁷（10 mK），对应 n_th/N_coh = 1.1×10⁻⁸、1.4×10⁻¹⁰、7×10⁻¹⁹，**均可忽略，室温即可工作**。
  - 未建模：光子被热声子自发散射到其他光学模式（g0=1.1 kHz 量级），预计远小于上述量级。

## 4. 先行工作与文献（逐条核实情况）
| 文献 | 数值 | 核实 |
|---|---|---|
| Hu et al., Nature 599, 587 (2021), https://arxiv.org/abs/2005.09621 | η=99.1% / 99.4%（12.5 GHz），98.7%（28.2 GHz）；IL 0.45 dB；96 mW（3.1 V）；0.5 GHz/V；C=0.11 pF、L=0.12 nH、R=1.5 Ω；γ/2π=5.31 GHz、κ_i/2π=0.17 GHz | 全文 |
| Shao et al., Opt. Express 28, 23728 (2020), https://doi.org/10.1364/OE.397138, https://arxiv.org/abs/2005.03794 | 3 GHz；载波抑制 >30 dB；反向边带 >40 dB；3 dB 带宽 70 MHz；30 dBm 下片上效率 3.5% | ar5iv 摘要与正文片段；"3.5% @30 dBm"来自检索摘要，未在全文中逐句定位 |
| Shao et al., Optica 6, 1498 (2019), https://arxiv.org/abs/1907.08593 | V_π=4.6 V（MZI）、0.77 V（跑道腔）；g0=1.1 kHz；声学 Q 最高 3600；约 50% 电-声耦合；IDT 宽 90 µm 用于匹配 50 Ω；V_π 以 50 Ω 源功率计 | 全文（ar5iv）；Table S2 的 κ 数值沿用主 report 的记录 |
| **Zhu et al., arXiv:2511.22585**（先行工作：声学驱动的 LN-on-sapphire 光子分子） | 毫瓦级驱动下超模强耦合；协同度 2.46 /mW；动态布拉格镜反射率最高 24% | 仅摘要核实；8.54 GHz、κ 约 0.9 GHz 等细节来自写作者的全文阅读。本文因此不主张"首个声学光子分子"，差异点是：前向、单总线、η_shift≈98% 的频移器工作点 |
| Xu et al., arXiv:2509.01940 | α=1774±171 GHz²/W；RF→声约 10%；κ0/2π≈0.32 GHz；隔离 45 dB；−0.3 dBm 实现 π gyration，IL 8.2 dB | 全文 |
| Qiu et al., Opt. Lett. 50, 1132 (2025) | V_π≈2.3 V；η>98.8%；CSR 42 dB、SSR 31 dB（宽带 serrodyne） | **仅摘要，未核实** |
| Zhu et al., Light Sci. Appl. 11, 327 (2022), https://arxiv.org/abs/2112.09961 | 单光子 ±641 GHz shearing；18 倍带宽压缩 | 摘要 |

## 5. 局限与前提（必须写进论文）
1. 声致 δω 是把 Shao 的 MZI V_π 线性外推到"环上 15% 覆盖"的几何（与 Shao 跑道腔的 η_cav 相同），模式重叠与 IDT 效率按原器件取值，需要实验验证。
2. 频移量固定为声学谐振频率；RF 可用带宽约 1 MHz（声学 Q=2000），需要稳频 RF 源，双环劈裂也需要热调谐到 ≪κ 的精度。
3. IL 2.5 dB、绝对效率 55%（受 Shao 实测 Q 限制）。
4. 未建模：IDT 与金属的光学损耗、声致发热与热光漂移、悬空结构的机械稳定性。
5. 匹配 EO 在功率上等价或更优；本文的优势只针对"已发表的声光频移器"这一类别。
6. Q_i 的数值、Shao 2020 的 3.5%、Qiu 2025 都需要在投稿前对照全文再核实一次。

## 6. 文件
- 脚本：`core.py`（模型）、`make_all.py`（全部数据与图）、`hom_post.py`、`iter6_fair.py`、`iter7_matching.py`、`data/eo_baseline.py`
- 数据：`data/results_B.json`、`eff_vs_power.csv`、`Q_tolerance.csv`、`RF_detuning.csv`、`IDT_sensitivity.csv`、`H_shift.csv`、`HOM.csv`、`iter6_fair.json`、`iter7_matching.json`
- 图：`fig/figB1_eff_power_spectrum`（效率–源功率，含 AO/EO 匹配与不匹配曲线；频谱）、`fig/figB2_tolerance_IDT`（Q、RF 失谐、IDT 效率）、`fig/figB3_HOM`，均有 png 与 pdf。
