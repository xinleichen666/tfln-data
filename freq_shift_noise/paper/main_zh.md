# 声光移频的频率仓纯度与 HOM 可见度上限：噪声账本（方向一工作稿）

**English subtitle:** *Frequency-bin purity and HOM visibility bounds for acousto-optic frequency shifters: a room-temperature noise budget*

**体裁**：室温台面 + 公开实测锚定的噪声账本短文（Optics Express / Applied Physics Letters / 预印本级）。无自有流片器件文腔调。  
**结构**：三类器件分账——甲行波 Bragg（主曲线）/ 乙共振换能（只锁参）/ 丙布里渊·DBM（模型假设）。  
**数字来源**：`../report_formulas_v1.md`、`../params.json`、`../models.py`（本文不重算主数字）。  
**波长**：**已锁定 A · ~1550 nm**（Cursor 2026-10-12 拍板；本学期只做这一条）。**型号已锁** G&H Fiber-Q 80 MHz；**实测待测**。

> **预印本口径（2026-10-12 总结包修订）：** 现挂 **仿真+方案** 无数据预印本工作稿；实测格空着；主图计划自测点标 **pending**；主数字不动；先不下单 Fiber-Q。
>
> **Preprint status (2026-10-12):** simulation + scheme manuscript; **no experimental data**; measured cells empty; planned self-test markers **pending**; primary numbers unchanged; Fiber-Q not ordered yet.
>
> **挂仓声明：** 本稿仅限课题组内部：仿真与方案工作稿，实测待做，无伪造数据，Fiber-Q 未下单，无流片；不得作为公开或可引用结果；verify/ 第三方 PDF 禁止入库。  
**英文摘要 / 关键词**：见同目录 `abstract_en.md`。  
**参考文献**：见 `references.md` / `refs.bib`（与共用表一致）。

---

## 摘要

把片上声光移频器件的残余载波与边带写成频率仓纯度，给出室温 HOM 可见度上限对载波抑制的主曲线；用商用光纤 AOM 台面自测核对公式，插损只进符合计数率。甲类以 Shao 行波 Bragg 公开数（片上效率 3.5%@30 dBm、CSR≈31 dB、SSR>40 dB、光纤–光纤 IL≈−15 dB）作器件模型参数 [Shao2020]，主图横轴为自测载波抑制 \(R_c\)，纵轴为可见度上限；计划自测点只标横轴位置，Shao 文献锚为竖虚线且写明偏转口频率仓纯度 **≠** 台面 HOM。乙类只锁定 Shao 2019 Table S2（含 \(\Omega/2\pi=2.007\,\mathrm{GHz}\)）[Shao2019]，给出室温 \(n_\mathrm{th}\) 与附加噪声上界，**不**画频率仓 HOM 主曲线。丙类在模型假设 \(\delta_\mathrm{sp}=n_\mathrm{th}/(n_\mathrm{th}+4C)\) 下，Zhu 实测 \(R=24\%\) 对应 \(V_\mathrm{upper}\approx0.019\)（室温）[Zhu2025ao]。禁止无损、\(n_\mathrm{th}\to0\)、效率追平电光 ~99%、液氦主结果。

**关键词**：薄膜铌酸锂；声光移频；载波抑制；HOM 可见度；噪声账本；商用 AOM

---

## 1. 引言

可编程光子源与量子网络节点需要把光子挪到指定频率仓，同时保持与参考光子的不可区分性。公开声光工作中，Shao 等在行波布拉格器件上测得片上转换效率 3.5%（30 dBm）、偏转口载波抑制约 31–33 dB、对侧边带抑制 >40 dB、光纤到光纤插损约 −15 dB [Shao2020]；共振声光 MZI 给出 \(V_\pi L\approx0.046\,\mathrm{V\cdot cm}\) 与单光子合作参量 \(C_0\sim10^{-8}\) [Shao2019]；Zhu 等在声学光子分子 / DBM 上测得归一化合作参量与反射率上限 24% [Zhu2025ao]。电光双环转换效率约 99%（Hu 等 [Hu2021]）若提及则**分列**，因效率定义不同，**不比胜负**。

本文方向一回答：在**室温台面**口径下，残余载波与边带如何写成频率仓纯度，并给出 HOM 可见度上限对载波抑制的主曲线；台面用商用光纤 AOM（~10² MHz 量级）核对公式，**不是**复现片上 ~3 GHz 声模。插损与片上效率只缩放符合计数率，不进可见度上限。Zhu 几何若引用标定，**不做**双环光子分子首次结构叙事。

---

## 2. 方法：统一 HOM 上限

### 2.1 频率仓纯度

理想参考光子已在信号频率仓 \(\omega_s\)。器件输出在频率仓基下 \(p_k\) 归一。无光谱滤波（或各仓透过率相同）、完美时间重叠 \(\mathcal{O}=1\) 时：

\[
V_\mathrm{upper}=p_s.
\]

有强度透过率 \(T_k\) 时 \(p_s'=T_s p_s/\sum_k T_k p_k\)。以后若脉冲 SPDC / 色散导致时间波包不完全相同，可再乘重叠积分 \(\mathcal{O}\in[0,1]\)；本轮 \(\mathcal{O}=1\)。**插损仍不进** \(V\)。

台面可见度定义与卡宝清单对齐：\(V=(C_\max-C_\min)/(C_\max+C_\min)\)（或组内等价定义）。理论曲线给 \(V_\mathrm{upper}(R_c)\)；自测点填 \(V\) 与 \(R_c\)，**纵轴未测前不贴理论线**。

### 2.2 主图叠点口径（定稿，写死）

**Fig.主**（甲）：`fig/vis_vs_carrier.png` / `.pdf`。**状态：pending（无实测点）**；理论曲线 + Shao 竖虚线文献锚 + 计划 \(R_c\) 横轴位置保留。  
*EN caption (optional):* Theoretical \(V_\mathrm{upper}\) vs carrier suppression \(R_c\); Shao literature anchor is a vertical dashed line (deflection-port bin purity ≠ bench HOM); planned AOM self-tests mark abscissae only (**pending**, no measured \(V\)).

| 元素 | 规则 |
|---|---|
| 理论曲线 | \(V_\mathrm{upper}(R_c)\) 实线 + SSR 敏感性（30/40/50 dB） |
| Shao 锚 | **竖虚线**文献锚；标注偏转口频率仓纯度，**≠** 台面 HOM |
| 商用 AOM | **底边竖线**，只标计划 \(R_c\) 横轴位置；纵轴不贴线 |
| 手册消光 ≥50 dB | 旁注「≠已测 \(R_c\)」 |
| 禁止 | 把 Shao 3.5% / 片上 3 GHz 叠进同一实验系列；假自测点贴理论线 |

图注强制句：

> **AOM≠片上 3 GHz 声模，\(n_\mathrm{th}\) 不由本次 HOM 测出**  
> *EN:* AOM ≠ on-chip ~3 GHz acoustic mode; \(n_\mathrm{th}\) is not measured by this HOM run.

---

## 3. 三类分账

### 3.1 甲 · 行波 Bragg（主曲线）

器件模型参数来自 Shao OE 2020 [Shao2020]；台面叠点是**商用光纤 AOM**，不是片上 3 GHz。

偏转口相对权重：信号 \(w_s=1\)，残余载波 \(w_c=10^{-R_c/10}\)，对侧边带 \(w_\mathrm{sb}=10^{-\mathrm{SSR}/10}\)。载波抑制与台面定义一致：

\[
R_c=10\log_{10}\frac{P_{+1}}{P_0}\quad(\mathrm{dB}).
\]

归一后

\[
V_\mathrm{upper}(R_c,\mathrm{SSR})=p_s
=\frac{1}{1+10^{-R_c/10}+10^{-\mathrm{SSR}/10}}.
\]

Shao 原文对侧边带在噪声底以下 >40 dB → 账本取 **SSR = 40 dB 下界**。

**文献锚读数（非台面点）**：\(R_c=31\,\mathrm{dB}\)、SSR=40 dB → \(V_\mathrm{bin}=p_s\approx0.9991\)。这是**偏转口频率仓纯度（残余载波账）**，**不是**台面 HOM 可见度，也**不是**「台面已近单位可见度」。

计数率因子（**不进** \(p_s\) / \(V\)）：

\[
F_\mathrm{rate}=\eta_\mathrm{onchip}\times 10^{\mathrm{IL_{dB}}/10}.
\]

Shao 工作点示例：\(F_\mathrm{rate}=0.035\times10^{-1.5}\approx1.11\times10^{-3}\)。**禁止**用 3.5% 填自测表实测格；**禁止**用 −15 dB 抬/压 \(V\) 上限。

代码：`models.typeA_bin_weights`、`hom_visibility.V_vs_Rc`、`models.typeA_count_rate_factor`。

### 3.2 乙 · 共振换能（**非主结果**）

只锁定 \(g_0\) / \(V_\pi\) / \(Q\) 等；**不把** \(\eta\to\) 单光子频率仓 HOM 画成主曲线。

锁定参数（Shao 2019 **Table S2** [Shao2019]）：

| 量 | 值 |
|---|---|
| \(V_\pi\) | 4.6 V @ 100 µm（\(V_\pi L\approx0.046\,\mathrm{V\cdot cm}\)） |
| \(g_0/2\pi\) | 1.1 kHz |
| \(\kappa/2\pi\) | 95 MHz；\(2\kappa_e/\kappa=0.3\) |
| \(\gamma/2\pi\) | 1.28 MHz；\(2\gamma_e/\gamma=0.34\) |
| \(\Omega/2\pi\) | **2.007 GHz**（Table S2；**不混用** 2.17 GHz 跑道行） |
| \(C_0\) | 文献 \(\approx4\times10^{-8}\)；代码 ≈3.98×10⁻⁸ |
| \(Q_\mathrm{ac}\) | 典型建模 2000；文中最高约 3600 |

热声子占据（公式计算，非实测噪声谱）：

\[
n_\mathrm{th}=\frac{1}{e^{hf/k_\mathrm{B}T}-1}.
\]

乙类工作点 \(f=2.007\,\mathrm{GHz}\)、\(T=300\,\mathrm{K}\) → \(n_\mathrm{th}\approx3.11\times10^3\)。

附加噪声上界（红失谐换能账，**标「非主结果」**）：

\[
N_\mathrm{add}\approx n_\mathrm{th}\,\frac{\gamma_i}{\gamma_e}.
\]

Table S2：\(\gamma_e/\gamma=0.17\) → \(N_\mathrm{add}\approx1.52\times10^4\)（室温）。即便 4 K 也不自动成立量子换能——**故不写液氦主结果，也不把乙类画成频率仓 HOM 主图**。

**乙类交付止于：锁定表 + \(n_\mathrm{th}\) + \(N_\mathrm{add}\) 公式。**

### 3.3 丙 · 布里渊 / DBM（模型假设）

\[
\delta_\mathrm{sp}=\frac{n_\mathrm{th}}{n_\mathrm{th}+4C},\qquad
V_\mathrm{upper}=R\,(1-\delta_\mathrm{sp}).
\]

\(\delta_\mathrm{sp}\) 为**模型假设**（光力分束型噪声账启发），**不是** Zhu 器件实测公式。室温 \(n_\mathrm{th}(8.54\,\mathrm{GHz})\approx7.31\times10^2\)。

Zhu 实测锚 [Zhu2025ao]：\(C/P_a=2.46\,\mathrm{mW}^{-1}\)，\(R=24\%\) @ 6.3 mW → \(C\approx15.5\) → \(\delta_\mathrm{sp}\approx0.922\)，\(V_\mathrm{upper}\approx0.019\)。对 \(C\) 做 0.5×/1×/2× 敏感性（≈0.0098 / 0.019 / 0.035）。理论外推 \(R=99\%\) @ ~26 mW **不作为**主结果。

Zhu 硬规矩：只取 C、κ、R 等标定；**不做**双环光子分子 / Möbius。

**Fig.丙**：`fig/vis_vs_R.png` / `.pdf`。  
*EN caption (optional):* Model-assumption \(V(R)\) sensitivity at room-temperature \(n_\mathrm{th}\); not a liquid-helium primary result.

图注必须句：

> **模型假设**：\(V=R(1-\delta_\mathrm{sp})\)，\(\delta_\mathrm{sp}=n_\mathrm{th}/(n_\mathrm{th}+4C)\)。室温 \(n_\mathrm{th}\)；非液氦主结果。

---

## 4. 台面对接

清单：`/workspace/方向一_台面可执行清单.md`。

| 项 | 台面做法 | 账本怎么用 |
|---|---|---|
| \(R_c\) | OSA/外差自测 \(10\log_{10}(P_{+1}/P_0)\) | 主图**横轴**；计划扫点只标横轴位置 |
| 边带抑制 | 对最强寄生阶同法 | 可替代模型 SSR；现用 Shao 40 dB 下界 |
| 插损 | 光纤–光纤自测 | 只进符合计数率 |
| \(V\) | HOM 符合扫延迟 | 纵轴；**未测前不贴理论线** |
| 频率 | 商用 AOM ~40–200 MHz | ≠ 片上 ~3 GHz；图注强制句 |
| 波长 / 型号 | **A · ~1550 nm**；G&H Fiber-Q **80 MHz**（已锁） | 实测格 **pending**；先不下单 |

自测表：`../selftest_table.md`，**全待测**。手册参考列可写 datasheet 量级；**实测列禁止**用 Shao 3.5% / −15 dB / 假 \(V\) 填充。

Shao ~−15 dB 光纤到光纤只作计数率量级锚，**不进** \(V\) 上限。

---

## 5. 关键读数摘要（可复现）

```text
甲 Shao 锚 Rc=31 dB, SSR=40 dB → V_bin ≈ 0.9991（偏转口纯度，≠台面 HOM）
甲 F_rate(0.035, −15 dB) ≈ 1.11e-3
乙 C0_computed ≈ 3.98e-8；n_th(2.007 GHz, 300 K) ≈ 3.11e3；N_add ≈ 1.52e4
丙 n_th(8.54 GHz, 300 K) ≈ 731；C≈15.5 @ R=24% → δ_sp≈0.922，V≈0.019
丙 C×0.5/1/2 → V≈0.0098 / 0.019 / 0.035
```

复现：

```bash
/workspace/dir13/venv/bin/python /workspace/freq_shift_noise/models.py
/workspace/dir13/venv/bin/python /workspace/freq_shift_noise/hom_visibility.py
```

---

## 6. 结论边界

- **已定稿**：甲主图叠点口径；乙只锁参；丙标模型假设；插损不进 \(V\)；图注强制句；乙类 2.007 GHz 与共用表脚注对齐。
- **已定**：SPDC ~1550 nm；型号已锁 G&H Fiber-Q 80 MHz；实测待测。方向二仿真保持 1550。
- **不写**：台面近单位可见度；Shao 点当实验点；追平 Hu 99%；双环首次；液氦主结果；假自测。
- **与方向二**：共用 `/workspace/tfln_review/ao_shared_params_v1.md`；方向一不引用 Xu 4.03 rad/W；方向二仿真保持 1550，台面实测仍待测。

工作稿为 **仿真+方案** 无数据预印本口径；实测格空着 / **pending**；先不下单 Fiber-Q。流片先别碰。

---

## 参考文献

见同目录 `references.md`（可读列表）与 `refs.bib`（BibTeX）。键名：Shao2020、Shao2019、Zhu2025ao、Hu2021（旁列）；Xu2025b 仅参数表旁列。
