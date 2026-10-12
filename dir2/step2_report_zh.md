# 方向二 Step 2 报告：LN/LNoS 热声 α + 单光波导光弹

## 结论（可交给总结包评审的数字）

| 量 | 名义值 | 对照 | 判定 |
|---|---|---|---|
| **α_LNoS** | **25.1 rad/W**（L_heater=200 µm） | Shao 实测 0.52 °/mW ≈ **9.08 rad/W** | 比值 ~2.8，**同量级** |
| **α_bulk LN** | **148 rad/W** | Shao 2.6 °/mW ≈ **45.4 rad/W** | 比值 ~3.3，**同量级** |
| **VπL_calc**（行波、η_IDT=10%） | **0.47 V·cm** | Shao 悬空共振 **0.045**；Ni 非悬空 **1.004**（全文已核） | **不宣称超越任一锚定**；带 0.08–1.35 |
| Gate1 vs Xu | 见 `gate1_*` | 4.03 rad/W | **同量级，不确定度带覆盖 Xu**（不写「复现了 4.03」） |

**结构**：声学 MZI 总线 + 热相移臂 + **一根**光波导重叠区。**没有**耦合双环 / Zhu 光子分子。

**仿真声明**：仅仿真；不宣称已流片；不写「片上已经集成移频+延时」；不做未核全文的气体传感卡片。传感 = 加热器 1 mW 步进对应的可分辨声相位 |\alpha|×1 mW。

---

## 1. 材料常数（均有出处）

- **弹性 / 压电**：Ogi et al., *J. Appl. Phys.* **92**, 2451 (2002) Table I（c11=199.56 GPa …；e15=3.65 C/m² …）。
- **光弹**：Andrushchak et al., *J. Appl. Phys.* **106**, 073510 (2009)；本关 AO 取 **p_eff = |p31| = 0.141**（与 Shao *Optica* 2019 TE↔s_xx 用法一致）。
- **κ_LN = 4.2 W/(m·K)**、**TCF_LN = −80 ppm/K**：文献中位，**假设并扫描**。
- **κ_sapphire = 35**：与 Gate1 相同。

切型 / 模族（写进结果）：

- LNoS：X-cut LN on sapphire，声沿晶 Y，quasi-Rayleigh/剪切（Shao 2022）；f≈2.45 GHz，v≈4165 m/s。
- Bulk：128° Y-cut，声沿晶 X，Rayleigh（Shao 2022）；f≈1.385 GHz，v≈3800 m/s（假设量级）。
- 光：单脊 **TE0 @ 1550 nm**，n≈2.14（假设）。

## 2. 热声路径（沿用 Gate1 标定逻辑）

\[
\alpha=-\frac{\omega L}{v}\,\mathrm{TCF}\,R_{\mathrm{th}}
\]

二维截面热传导：加热器在 LN/蓝宝石表面 → 有限 \(R_{\mathrm{th}}\)（非无限）。  
LNoS：\(R_{\mathrm{th}}\approx 425\,\mathrm{K/W}\) → α≈25 rad/W。  
Bulk：低 κ → \(R_{\mathrm{th}}\approx 4.0\times 10^3\,\mathrm{K/W}\) → α≈148 rad/W。  
相对 Shao 偏高约 3 倍，仍在一个数量级内；偏差来自 TCF/κ/加热器长度中位假设与侧壁绝热。

群时延：\(\tau_g=L/v_g\approx 200\,\mu\mathrm{m}/4165\,\mathrm{m/s}\approx 48\,\mathrm{ns}\)（LNoS 重叠段）。

## 3. 单光波导光弹（行波）

应变（行波功率）：\(P_a=\eta_{\mathrm{IDT}}P_{\mathrm{RF}}\)，\(P_a=\tfrac12 c_{\mathrm{eff}} S^2 v A_{\mathrm{eff}}\)，\(c_{\mathrm{eff}}=c_{11}\)。  
\(A_{\mathrm{eff}}=\Gamma_{\mathrm{area}} W_{\mathrm{ac}} H_{\mathrm{LN}}\)，\(\Gamma_{\mathrm{area}}=8\)（非悬空扩展开，**假设**，扫 3–20）。  
光相位：\(\phi=(2\pi/\lambda)(n^3/2)p_{\mathrm{eff}} S\,\Gamma_{\mathrm{ov}} L\)，\(\Gamma_{\mathrm{ov}}=0.45\)（**假设**）。  
推挽 Vπ：单臂 \(\phi=\pi/2\) 时的 RF 电压；\(V_\pi L\) 名义 **0.47 V·cm**（η=10%），η=50% 时约 **0.21 V·cm**。

**为何不能去碰 0.045**：Shao *Optica* 2019 是**悬空 + 声学共振**（Q 可至 ~3600）的 MZI；本关是**非悬空行波**估算，物理工况不同。带的下限 0.08 仍高于 0.045。  
相对 Ni 1.004：名义 0.47 更小，但 Γ_area/Γ_ov/η 为假设；Ni 为**非悬空 X-cut TFLN-on-Si**（360 nm/BOX/Si、0.842 GHz、L=400 µm，全文已核），与本关 LNoS 行波算值**不是同一平台** → **禁止写成算赢非悬空 SOTA，也不与 Shao 悬空同柱比较**。

## 4. 双旋钮与热串扰

- 声相位：\(\phi_{\mathrm{ac}}=\alpha P_H + \alpha\,\xi_{\mathrm{RF}}P_{\mathrm{RF}}\)（ξ_RF=0.05 假设）。
- 目标 AO 相位：\(\phi_{\mathrm{AO}}(P_{\mathrm{RF}})\)。
- 光热光串扰：\(\phi_{\mathrm{TO}}\propto (dn/dT)\,R_{\mathrm{th}}(\xi_H P_H+\xi_{\mathrm{RF}}P_{\mathrm{RF}})\)，ξ_H=0.35 假设。
- 干涉相位误差斜率（LNoS 名义，与 `step2_summary.json` 一致）：  
  - \(d\phi_{\mathrm{err}}/dP_H \approx 4.0\,\mathrm{rad/W}\)（热光）  
  - \(d\phi_{\mathrm{err}}/dP_{\mathrm{RF}} \approx 1.8\,\mathrm{rad/W}\)（RF 热 + 热声）  
- 移频/载波抑制代理：MZI 暗态残光 \(\sin^2(\phi_{\mathrm{err}}/2)\)，见图 CSR 色图。
- **可分辨相位（传感定义）**：\(|\alpha|\times 1\,\mathrm{mW}\approx 0.025\,\mathrm{rad}\)（LNoS）；**不是**气体传感指标卡。

## 5. 明确非宣称

1. 不写 Gate1「复现了 Xu 的 4.03」，只写同量级、带覆盖。  
2. 不宣称 VπL 超过 Shao 悬空 0.045 V·cm。  
3. 不宣称超过 Ni/Bhave 1.004 V·cm（全文已核；平台为 TFLN-on-Si 非悬空，与 LNoS 分列；重叠假设）。  
4. 无双环；无「已集成移频+延时」；无未核气体传感。  
5. 损耗与加热串扰进入传递函数；未令 n_th→0 或无损理想化作为主结论。

## 6. 文件

| 路径 | 内容 |
|---|---|
| `/workspace/dir2/step2_ln_photoelastic.py` | 可运行脚本 |
| `/workspace/dir2/data/step2_summary.json` | 汇总数字 |
| `/workspace/dir2/data/params_sources.md` | Gate1+Step2 参数表 |
| `/workspace/dir2/fig/step2_joint_transfer.png/.pdf` | α 对照、VπL 锚定、双旋钮、CSR |
| `/workspace/dir2/step2_report_zh.md` | 本报告 |

复现：`/workspace/dir13/venv/bin/python /workspace/dir2/step2_ln_photoelastic.py`
