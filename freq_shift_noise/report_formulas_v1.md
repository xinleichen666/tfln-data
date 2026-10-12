# 移频噪声账本 · 公式细节 v1

> 目录：`/workspace/freq_shift_noise/`  
> 日期：2026-10-12（Asia/Shanghai）  
> 口径：室温台面；目标刊物 OE / APL 噪声账本短文。  
> **禁止**：无损、\(n_\mathrm{th}\to0\)、效率追平 Hu≈99%、液氦主结果。  
> 主图叠点规则已定稿，本文只补公式，**不改** `plot_vis_vs_carrier.py` 叠点逻辑。  
> 自测表保持全「待测」；等卡宝定波长后再填点。

参数优先对齐 `/workspace/tfln_review/ao_shared_params_v1.md`（下称「共用表」）。与共用表不一致处见 §6。

代码：`models.py`、`hom_visibility.py`、`params.json`。读数由 `python models.py` / `hom_visibility.py` 复现。

---

## 0. 统一前提：频率仓 HOM 与时间重叠

### 0.1 双光子设定

理想参考光子已在信号频率仓 \(\omega_s\)（例如未移频的另一路 SPDC，或已校准到 \(\omega_s\) 的参考臂）。器件输出态在频率仓基 \(\{\omega_k\}\) 下写成

\[
|\psi\rangle=\sum_k c_k\,|\omega_k\rangle,\qquad
p_k=\lvert c_k\rvert^2\Big/\sum_j\lvert c_j\rvert^2.
\]

与参考光子在 50:50 合束器上做 HOM。**本轮取**：

1. **无光谱滤波**（或滤波透过率对各仓相同，可消掉）；
2. **完美时间重叠**，即两路波包时间模式完全相同，重叠积分 \(\mathcal{O}=1\)。

此时可见度上限就是信号仓纯度：

\[
\boxed{
V_\mathrm{upper}=p_s=\lvert\langle\omega_s|\psi\rangle\rvert^2
\Big/\sum_k\lvert\langle\omega_k|\psi\rangle\rvert^2.
}
\]

错频仓（残余载波、寄生边带、同频但非相干的自发分量等）在无滤波时**全部稀释** \(V\)，不另乘经验因子。

### 0.2 有滤波时

令 \(T_k\) 为频率仓 \(k\) 的**强度**透过率（不是振幅）。滤波后

\[
p_s'=\frac{T_s\,p_s}{\sum_k T_k\,p_k},\qquad
V_\mathrm{upper}^\mathrm{(filt)}=p_s'.
\]

代码：`hom_visibility.V_upper_filtered(p, T)`，\(T\) 按强度约定。  
（模块顶注释若曾写 \(T^2\)，以本式与函数实现为准：\(T\) 已是强度。）

### 0.3 以后加重叠积分怎么接

若脉冲 SPDC / 器件色散导致时间波包 \(\psi_\mathrm{ref}(t)\)、\(\psi_\mathrm{dev}(t)\) 不完全相同，定义

\[
\mathcal{O}
=\Biggl\lvert\int\psi_\mathrm{ref}^*(t)\,\psi_\mathrm{dev}(t)\,\mathrm{d}t\Biggr\rvert^2
\in[0,1]
\]

（归一 \(\int|\psi|^2=1\)）。在**频率仓纯度与时间模式近似可分离**时，

\[
V_\mathrm{upper}\;\longrightarrow\;
V_\mathrm{upper}\times\mathcal{O}
=p_s\,\mathcal{O}.
\]

偏振失配、功率不平衡另有各自的可区分性因子，与 \(p_s\)、\(\mathcal{O}\) 同属「可区分性账」；**插损仍不进** \(V\)（见 §1.3）。本轮 \(\mathcal{O}=1\)，代码未乘重叠；以后加时在 `hom_visibility` 里对 `V_upper` 再乘 \(\mathcal{O}\) 即可，**不必改** \(p_s(R_c)\) 主曲线形状。

### 0.4 台面 HOM 可见度定义（与卡宝清单对齐）

实测：

\[
V=\frac{C_\max-C_\min}{C_\max+C_\min}
\]

（或组内既定等价定义）。理论曲线给的是 \(V_\mathrm{upper}(R_c)\)；自测点填 \(V\) 与 \(R_c\)，**纵轴未测前不贴理论线**。

---

## 1. 甲 · 行波 Bragg（主曲线）

器件模型参数来自 Shao et al., *Opt. Express* **28**, 23728 (2020)；台面叠点是**商用光纤 AOM**，不是片上 3 GHz。

### 1.1 从 Bragg 输出态到各仓权重

偏转口（+1 衍射阶 / 移频口）收集到的光，在频率仓上近似三份（相对移频线）：

| 仓 | 物理 | 相对功率权重 |
|---|---|---|
| 信号 \(s\) | 移频到 \(\omega_0+\Omega\)（或 Stokes 红移） | \(w_s=1\) |
| 残余载波 | 未偏转的 \(\omega_0\) 漏进偏转口 | \(w_c=10^{-R_c/10}\) |
| 对侧边带 | 反向边带 / 寄生阶 | \(w_\mathrm{sb}=10^{-\mathrm{SSR}/10}\) |

**载波抑制**与台面测量定义一致（清单 §光路与测量步骤）：

\[
\boxed{
R_c=10\log_{10}\frac{P_{+1}}{P_0}\quad(\mathrm{dB}).
}
\]

即 \(R_c=\mathrm{CSR}\)。边带抑制对最强寄生阶同法：\(\mathrm{SSR}=10\log_{10}(P_{+1}/P_\mathrm{sb})\)。  
Shao 原文对侧边带在噪声底以下 **>40 dB** → 账本取 **SSR = 40 dB 下界**（`params.json` → `shao2020_SSR_dB`）。

代码：`models.typeA_bin_weights(CSR_dB, SSR_dB)`：

\[
r_c=10^{-R_c/10},\quad
r_\mathrm{sb}=10^{-\mathrm{SSR}/10},\quad
w_s=1,\;w_c=r_c,\;w_\mathrm{sb}=r_\mathrm{sb}.
\]

可选 `n_extra_sb` 再叠更多寄生阶（默认 0）。

### 1.2 归一得 \(p_s\) 与 \(V_\mathrm{upper}\)

\[
p_s=\frac{w_s}{w_s+w_c+w_\mathrm{sb}}
=\frac{1}{1+10^{-R_c/10}+10^{-\mathrm{SSR}/10}},
\quad
p_\mathrm{carrier}=\frac{w_c}{\sum w},\quad
p_\mathrm{sb}=\frac{w_\mathrm{sb}}{\sum w}.
\]

在 §0 前提下：

\[
\boxed{
V_\mathrm{upper}(R_c,\mathrm{SSR})=p_s
=\frac{1}{1+10^{-R_c/10}+10^{-\mathrm{SSR}/10}}.
}
\]

代码：`hom_visibility.V_vs_Rc(CSR_dB, SSR_dB)` 对每个 \(R_c\) 调 `typeA_bin_weights` 取 `p_s`。

**文献锚读数（非台面点）**：\(R_c=31\,\mathrm{dB}\)（Stokes）、SSR = 40 dB →

\[
V_\mathrm{bin}=p_s\approx 0.9991.
\]

这是**偏转口频率仓纯度（残余载波账）**，**不是**台面 HOM 可见度，也**不是**「台面已近单位可见度」。主图用竖虚线标该 \(R_c\)，标注写明 ≠ 台面 HOM。

低 \(R_c\) 时 \(V\) 由载波残留主导；高 \(R_c\) 时被 SSR 钉住（主图另画 SSR=30/50 dB 敏感性虚线）。

### 1.3 计数率因子与 \(V\) 脱钩

片上转换效率 \(\eta_\mathrm{onchip}\) 与光纤到光纤插损 \(\mathrm{IL_{dB}}\)（透射为负 dB）**只缩放符合计数率**，**不进** \(p_s\) / \(V_\mathrm{upper}\)：

\[
\boxed{
F_\mathrm{rate}=\eta_\mathrm{onchip}\times 10^{\mathrm{IL_{dB}}/10}.
}
\]

代码：`models.typeA_count_rate_factor(eta_onchip, IL_fiber_dB)`。

| 用途 | Shao 文献值 | 是否进 \(V\) |
|---|---|---|
| \(\eta_\mathrm{onchip}\) | 3.5% @ 30 dBm | **否** |
| 光纤–光纤 IL | −15 dB | **否**（可作「同等 IL 掉多少计数」量级锚） |
| 商用 AOM IL | 手册 ≤2.5 dB 等 | **否**；进实测符合率估计 |

Shao 工作点示例：\(F_\mathrm{rate}=0.035\times10^{-1.5}\approx1.11\times10^{-3}\)（相对「η=1 且 IL=0」）。  
**禁止**用 3.5% 填自测表实测格；**禁止**用 −15 dB 抬/压 \(V\) 上限。

### 1.4 与商用 AOM 台面测量对齐

清单路径：`/workspace/方向一_台面可执行清单.md`。

| 项 | 台面做法 | 账本怎么用 |
|---|---|---|
| \(R_c\) | OSA/外差自测 \(10\log_{10}(P_{+1}/P_0)\) | 主图**横轴**；计划扫点只标横轴位置 |
| 边带抑制 | 对最强寄生阶同法 | 可替代模型 SSR；现用 Shao 40 dB 下界 |
| 插损 | 光纤–光纤自测 | 只进符合计数率 |
| \(V\) | HOM 符合扫延迟 | 纵轴；**未测前不贴理论线** |
| 频率 | 商用 AOM ~40–200 MHz | ≠ 片上 ~3 GHz；图注强制句 |

图注强制句（保留）：

> **AOM≠片上 3 GHz 声模，\(n_\mathrm{th}\) 不由本次 HOM 测出**

主图叠点（已定稿，不改）：

- 理论 \(V(R_c)\) 实线 + SSR 敏感性；
- Shao：竖虚线文献锚（偏转口纯度，≠ 台面 HOM）；
- 商用 AOM：底边竖线，**只标计划 \(R_c\)**，纵轴不贴线；
- 手册 on/off 消光 ≥50 dB：旁注「≠已测 \(R_c\)」。

自测表：`selftest_table.md`，**全待测**。

### 1.5 甲类参数引用行

| id | 值 | 条件 | 出处 | kind |
|---|---|---|---|---|
| shao2020_eta_onchip | 0.035 | 30 dBm | Shao OE 28, 23728 (2020) | measured（文献；非本实验） |
| shao2020_CSR_dB | 31 | Stokes；anti-Stokes≈33；摘要>30 | 同上 Fig.3 | measured（文献锚） |
| shao2020_SSR_dB | 40 | 对侧边带噪声底以下 | 同上 | measured（下界） |
| shao2020_IL_fiber_dB | −15 | fiber-to-fiber 透射口 | 同上 | measured（只进计数率） |
| shao2020_Omega_GHz | ~3 | 行波 Bragg | 同上 | measured |
| fiber_AOM_CSR_dB | ≥50 | 手册 on/off 消光 | G&H Fiber-Q | datasheet（≠已测 \(R_c\)） |
| fiber_AOM_IL_dB | typ −2～−2.5 | 40/80 MHz | 同上 | datasheet |

---

## 2. 乙 · 共振换能（**非主结果**）

只锁定 \(g_0\) / \(V_\pi\) / \(Q\) 等；**不把** \(\eta\to\) 单光子频率仓 HOM 画成主曲线。

### 2.1 锁定参数表（Shao 2019 Table S2）

出处：Shao et al., *Optica* **6**, 1498 (2019)；arXiv:1907.08593。

| 量 | 值 | 代码 id |
|---|---|---|
| \(V_\pi\) | 4.6 V @ 100 µm（→ \(V_\pi L=0.046\,\mathrm{V\cdot cm}\)） | `shao2019_Vpi_V` |
| \(g_0/2\pi\) | 1.1 kHz | `shao2019_g0_Hz` |
| \(\kappa/2\pi\) | 95 MHz | `shao2019_kappa_Hz` |
| \(2\kappa_e/\kappa\) | 0.3 → \(\kappa_e/\kappa=0.15\) | `shao2019_2ke_over_k` |
| \(\gamma/2\pi\) | 1.28 MHz | `shao2019_gamma_Hz` |
| \(2\gamma_e/\gamma\) | 0.34 → \(\gamma_e/\gamma=0.17\) | `shao2019_2ge_over_g` |
| \(\Omega/2\pi\) | 2.007 GHz（Table S2） | `shao2019_Omega_Hz` |
| \(C_0\)（文献） | \(\approx4\times10^{-8}\) | `shao2019_C0` |
| \(Q_\mathrm{ac}\) | 典型建模 2000；文中最高约 3600 | `shao2019_Q_ac_typical` |

单光子合作参量（角频率与「/2π」数值一致）：

\[
C_0=\frac{4g_0^2}{\kappa\gamma}
=\frac{4\,(g_0/2\pi)^2}{(\kappa/2\pi)(\gamma/2\pi)}.
\]

代码算得 \(C_0\approx3.98\times10^{-8}\)，与文献 \(4\times10^{-8}\) 一致（`typeB_locked_params`）。

### 2.2 \(n_\mathrm{th}\) 与附加噪声上界（非主结果）

热声子占据（**由公式计算，非实测噪声谱**；与共用表 §3 同式）：

\[
\boxed{
n_\mathrm{th}=\frac{1}{\mathrm{e}^{hf/k_\mathrm{B}T}-1}
=\frac{1}{\mathrm{e}^{\hbar\Omega/k_\mathrm{B}T}-1},\quad
\Omega=2\pi f.
}
\]

代码：`models.n_th_ordinary_f(f_Hz, T_K)`。  
乙类工作点 \(f=\Omega/2\pi=2.007\,\mathrm{GHz}\)、\(T=300\,\mathrm{K}\) → \(n_\mathrm{th}\approx3.11\times10^3\)。

输入端附加噪声上界（红失谐换能账，**标「非主结果」**）：

\[
\boxed{
N_\mathrm{add}\approx n_\mathrm{th}\,\frac{\gamma_i}{\gamma_e},\qquad
\frac{\gamma_i}{\gamma}=\!1-\frac{\gamma_e}{\gamma},\quad
\frac{\gamma_e}{\gamma}=\frac{1}{2}\cdot\frac{2\gamma_e}{\gamma}.
}
\]

Table S2：\(\gamma_e/\gamma=0.17\) → \(\gamma_i/\gamma_e\approx4.88\) → \(N_\mathrm{add}\approx1.52\times10^4\)（室温）。  
即便 4 K，\(n_\mathrm{th}(2.007\,\mathrm{GHz})\sim40\)，量子换能也不自动成立——**故不写液氦主结果，也不把乙类画成频率仓 HOM 主图**。

若强驱动到合作参量 \(C\)，可另给分束型效率因子 \(4C/(1+C)^2\)（再乘 \(\kappa_e/\kappa\)、\(\gamma_e/\gamma\)），代码 `typeB_noise_bound_if_driven`；**仍标非主结果**，不进入甲类主图。

**乙类交付止于：锁定表 + \(n_\mathrm{th}\) + \(N_\mathrm{add}\) 公式。**

---

## 3. 丙 · 布里渊 / DBM（模型假设）

### 3.1 分账公式

反射率 \(R\)（DBM reflectivity）与合作参量 \(C\)。保守分账（频率可区分极限 + 自发进信号仓稀释）：

\[
\begin{aligned}
\delta_\mathrm{sp}&=\frac{n_\mathrm{th}}{n_\mathrm{th}+4C},\\
p_{s,\mathrm{coh}}&=R\,(1-\delta_\mathrm{sp}),\\
p_\mathrm{carrier}&=1-R,\\
p_\mathrm{spont}&=R\,\delta_\mathrm{sp}.
\end{aligned}
\]

因 \(p_{s,\mathrm{coh}}+p_\mathrm{carrier}+p_\mathrm{spont}=1\)，

\[
\boxed{
V_\mathrm{upper}=R\,(1-\delta_\mathrm{sp}).
}
\]

代码：`models.typeC_visibility_vs_R(R, C, n_th_val)`。

### 3.2 \(\delta_\mathrm{sp}\) 假设来源与敏感性含义

| 项 | 说明 |
|---|---|
| 来源 | **模型假设**（光力分束型噪声账启发），**不是** Zhu/Xu 器件实测公式；`params.json` → `typeC_spont_model`，kind=assumed |
| \(4C\) | 合作参量进入「相干换能信道」相对权重的量级；与乙类 \(4C/(1+C)^2\) 同源量级，此处用于稀释比 |
| 敏感性 | 对 \(C\) 做 **0.5× / 1× / 2×** 缩放：\(\delta_\mathrm{sp}\) 与 \(V\) 随 \(C\) 变，用来看「公式形式固定时，标定不确定差几倍会怎样」——**不是**扫实测器件 |
| 室温 \(n_\mathrm{th}\) | Zhu 声频 \(\Omega/2\pi\approx8.54\,\mathrm{GHz}\) → \(n_\mathrm{th}(300\,\mathrm{K})\approx7.31\times10^2\)（与共用表 §3 一致） |

Zhu 实测锚（全文已核）：\(C/P_a=2.46\,\mathrm{mW}^{-1}\)，\(R=24\%\) @ \(P_a=6.3\,\mathrm{mW}\) → \(C\approx15.5\)。  
代入：\(\delta_\mathrm{sp}\approx0.922\)，\(V_\mathrm{upper}\approx0.019\)。  
（理论外推 \(R=99\%\) @ ~26 mW **不作为**主结果；仅敏感性参考。）

Xu 标定（对接用，非主曲线）：\(\alpha=1774\pm171\,\mathrm{GHz}^2/\mathrm{W}\)，RF→acoustic ≈10%。

**Zhu 硬规矩**（共用表脚注）：只取 C、κ、R 等标定；**不做**双环光子分子 / Möbius。

### 3.3 图注必须句

丙类图（`fig/vis_vs_R.*`）必须含：

> **模型假设**：\(V=R(1-\delta_\mathrm{sp})\)，\(\delta_\mathrm{sp}=n_\mathrm{th}/(n_\mathrm{th}+4C)\)。室温 \(n_\mathrm{th}\)；非液氦主结果。

---

## 4. 代码 ↔ 公式对照

| 公式 | 函数 | 一致？ |
|---|---|---|
| \(R_c=10\log_{10}(P_{+1}/P_0)\) | 文档/清单；`typeA_bin_weights` 入参 CSR_dB | 是 |
| \(p_s=1/(1+10^{-R_c/10}+10^{-\mathrm{SSR}/10})\) | `typeA_bin_weights` → `p_s`；`V_vs_Rc` | 是 |
| \(V_\mathrm{upper}=p_s\)（无滤波、\(\mathcal{O}=1\)） | `V_upper_from_bins`；`V_vs_Rc` | 是 |
| 滤波 \(p_s'=T_s p_s/\sum T_k p_k\)（\(T\)=强度） | `V_upper_filtered` | 是（见 §0.2） |
| \(F_\mathrm{rate}=\eta\cdot10^{\mathrm{IL/10}}\) | `typeA_count_rate_factor` | 是；**不进** V |
| \(n_\mathrm{th}=1/(e^{hf/kT}-1)\) | `n_th_ordinary_f` | 是 |
| \(C_0=4g_0^2/(\kappa\gamma)\) | `typeB_locked_params` | 是（≈3.98e-8） |
| \(N_\mathrm{add}=n_\mathrm{th}\gamma_i/\gamma_e\) | `typeB_locked_params` | 是；非主结果 |
| \(V=R(1-\delta_\mathrm{sp})\)，\(\delta_\mathrm{sp}=n_\mathrm{th}/(n_\mathrm{th}+4C)\) | `typeC_visibility_vs_R` | 是；assumption=True |
| 主图叠点 | `plot_vis_vs_carrier.plot_main_V_vs_Rc` | 定稿：计划自测仅横轴；Shao 竖虚线≠台面 HOM |

**未发明** 99% 效率作主结果；Zhu 理论 \(R\to99\%\) 仅标 theory 外推。

---

## 5. 关键读数摘要（可复现）

```text
甲 Shao 锚 Rc=31 dB, SSR=40 dB → V_bin ≈ 0.9991（偏转口纯度，≠台面 HOM）
甲 F_rate(0.035, −15 dB) ≈ 1.11e-3
乙 C0_computed ≈ 3.98e-8；n_th(2.007 GHz, 300 K) ≈ 3.11e3；N_add ≈ 1.52e4
丙 n_th(8.54 GHz, 300 K) ≈ 731；C≈15.5 @ R=24% → δ_sp≈0.922，V≈0.019
丙 C×0.5/1/2 → V≈0.0098 / 0.019 / 0.035
```

---

## 6. 与共用参数表差异

共用表：`/workspace/tfln_review/ao_shared_params_v1.md`。

| 项 | 本账本 | 共用表 | 处理 |
|---|---|---|---|
| Shao2020 η / CSR / SSR / IL / ~3 GHz | 同 | 同 | 无差异 |
| Shao2019 \(V_\pi\)、\(g_0\)、\(C_0\)、Q 上限 3600 | 同；Q 建模用 2000 | 同 | 无差异 |
| Shao2019 声频用于 \(n_\mathrm{th}\) | **Table S2：2.007 GHz** → \(n_\mathrm{th}\approx3.11\times10^3\) | §3 列 **2.17 GHz**（跑道环 g0 语境）→ \(\approx2.88\times10^3\) | **有意**：乙类锁定跟 Table S2 全套 \(\kappa,\gamma,\Omega\)；不混用 2.17 GHz 行 |
| Zhu \(C/P_a\)、R=24%、8.54 GHz | 同 | 同 | 无差异；遵守「不做双环」脚注 |
| Xu \(\alpha\)、RF→acoustic 10% | 已写入 params | 同 | 无差异 |
| \(n_\mathrm{th}\) 公式与 3.0 / 8.54 GHz 数 | 与 §3 一致 | — | 无差异 |
| 商用光纤 AOM IL / 消光 | `fiber_AOM_*`（datasheet） | 共用表无此行（只管文献声光） | **预期外扩**；台面清单用 |
| \(\delta_\mathrm{sp}\) 模型 | kind=assumed | 共用表无此公式 | 本账本新增；图注「模型假设」 |
| Qiu / Hu ~99% | **不引用为主对照** | 共用表有（Qiu=摘要；Hu=EO 对照） | 遵守禁止「效率追平 Hu」 |
| Xu 4.03 rad/W | 不用 | 方向二 | 方向一不引用 |

---

## 7. 文件清单

| 文件 | 作用 |
|---|---|
| `report_formulas_v1.md` | **本文**：公式细节 |
| `report_skeleton.md` | 初版骨架（可保留对照） |
| `params.json` | 带 cite/kind 的参数 |
| `models.py` | 甲/乙/丙 |
| `hom_visibility.py` | \(V_\mathrm{upper}\)、\(V(R_c)\) |
| `plot_vis_vs_carrier.py` | 主图 + 丙图（叠点已定稿） |
| `fig/vis_vs_carrier.{png,pdf}` | 甲主图 |
| `fig/vis_vs_R.{png,pdf}` | 丙草稿 |
| `selftest_table.md` | 全待测 |
| `/workspace/方向一_台面可执行清单.md` | 卡宝台面口径 |
| `/workspace/tfln_review/ao_shared_params_v1.md` | 文献包共用表 |

---

## 8. 仍待对齐（不阻塞本版公式）

| 项 | 现状 |
|---|---|
| 卡宝波长 / 自测 \(R_c\) 点 | 全待测；定波长后再填 |
| 丙 \(\delta_\mathrm{sp}\) 是否改分账 | 现为 assumed 上界 |
| 甲 SSR 是否改台面自测寄生阶 | 现用 Shao 40 dB 下界 |
| 乙是否进短文正文 | 仅锁定表；总结包定稿时取舍 |
| 时间重叠 \(\mathcal{O}\) | 本轮=1；接法见 §0.3 |
