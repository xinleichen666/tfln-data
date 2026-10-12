# Joint error budget for thermo-acoustic phase and photoelastic frequency shift on a shared acoustic drive

# 同一路声驱动下的热声相位与光弹移频：联合误差传递

**Manuscript type:** simulation + benchtop cross-check (Optics Express / Applied Physics Letters / preprint tone). No proprietary fabrication claims.  
**Geometry:** acoustic Mach–Zehnder (MZI) bus + thermal phase arm + **single** optical waveguide overlap (**no** coupled double rings / photon-molecule geometry).  
**Numbers locked to:** `../data/gate1_alpha.json`, `../data/step2_summary.json`.

**Preprint status (2026-10-12 · V1):** Internal group use only: simulation and scheme draft; measurements pending; no fabricated data; Fiber-Q not ordered; no fab. Not for public citation. Third-party PDFs under verify/ must not enter the repo.

**推仓声明（V1）：** 本稿仅限**课题组内部**：仿真与方案工作稿，实测待做，**无伪造数据**，Fiber-Q **未下单**，**无流片**；**不得作为公开或可引用结果**；`verify/` 第三方 PDF **禁止入库**。

---

## Abstract (English)

We add a single-waveguide photoelastic overlap to an acoustic Mach–Zehnder model and derive a joint error transfer for frequency-shift strength and acoustic phase under a shared RF–heater drive, anchored to published thermo-acoustic and \(V_\pi L\) data. On GaN-on-sapphire, calculated \(\alpha\) is the **same order of magnitude** as Xu et al. (4.03 rad/W at 100 µm), and the uncertainty band **covers** that value (we do **not** claim to reproduce 4.03). With LN / LNoS constants, \(\alpha\) remains the same order as Shao thermo-acoustic measurements (~2.8× for LNoS, ~3.3× for bulk vs 0.52 and 2.6 °/mW). A traveling-wave estimate gives \(V_\pi L\approx 0.47\) V·cm (10% IDT efficiency), tabulated **between**—without surpassing—the suspended Shao anchor (\(\approx 0.045\) V·cm) and the non-suspended X-cut **TFLN-on-Si** Ni et al. anchor (1.004 V·cm at 0.842 GHz, 400 µm; 360 nm LN / 4.7 µm BOX / Si). Phase-error slopes are **4.0** and **1.8 rad/W** (heater / RF). Benchtop checks use a Fiber-Q **80 MHz** AOM at ~**1550 nm** (model locked; **measurements pending**); photoelastic overlap stays simulation-only. Internal group use only: no fabricated data; Fiber-Q not ordered; no fab; not for public citation; verify/ PDFs banned from the repo.

**Keywords:** thin-film lithium niobate; acousto-optics; thermo-acoustic phase; Mach–Zehnder; error transfer; benchtop verification

---

## 摘要（中文）

在已有声学马赫–曾德尔模型上加入光弹重叠，用 Xu 的热声相移与 Shao 的 \(V_\pi L\) 做锚，给出同一路声驱动下移频强度与声相位的联合误差传递；误差公式用商用 AOM 加光纤相位的台面核对。GaN-on-sapphire 原材料路径上，热声效率 \(\alpha\) 与 Xu 报道的 4.03 rad/W（100 µm）为**同一数量级**，不确定度带**覆盖**该锚点（**不声称复现** 4.03）。换 LN / LNoS 材料后，\(\alpha\) 相对 Shao 热声实测仍为同量级（LNoS ~2.8×，bulk ~3.3×）。单根光波导行波光弹给出 \(V_\pi L\approx 0.47\) V·cm（叉指电声效率 10%），与 Shao 悬空共振锚（约 0.045 V·cm）及 Ni 等非悬空 **TFLN-on-Si** 锚（1.004 V·cm）**分平台并列表**，**不宣称超过任一实测**。干涉相位误差斜率约 **4.0 rad/W**（加热）与 **1.8 rad/W**（射频）。台面波长与 AOM 型号叙述锁定为 ~1550 nm、G&H Fiber-Q 80 MHz；**实测数据仍 pending**。本稿仅限**课题组内部**，**不得作为公开或可引用结果**；**无伪造数据**；Fiber-Q **未下单**；**无流片**；`verify/` PDF 禁止入库。

**关键词：** 薄膜铌酸锂；声光；热声相移；马赫–曾德尔；误差传递；台面核对

---

## 1. 引言

可编程声子回路需要在同一芯片尺度上同时操纵声相位与声–光耦合。公开文献中，Xu 等在 GaN-on-sapphire 声子集成电路上报道热声相移效率 4.03 rad/W（相移器长 100 µm）[1]；Shao 等在块体 LN 与 LN-on-sapphire（LNoS）上报道热声响应 2.6 °/mW 与 0.52 °/mW [2]，并在悬空薄膜铌酸锂声光 MZI 上给出 \(V_\pi L\approx 0.045\) V·cm [3]。非悬空对照取 Ni 等在 **X 切 TFLN-on-Si**（360 nm LN / 4.7 µm BOX / Si）上、0.842 GHz、作用长 400 µm 的 Device 3：\(V_\pi L=1.004\) V·cm [4]。上述三条 \(V_\pi L\) **分属不同平台**（悬空膜 / LNoS 类计算工况 / 硅上非悬空 TFLN），并列表时不合为同一柱。

本文回答：在**同一路**叉指射频与热调功率下，声相位与光弹移频强度如何联合漂移，误差以何种斜率进入干涉可见度或条纹位移。工作定位为**仿真加台面**；台面用已锁型号的商用 AOM（G&H Fiber-Q 80 MHz，波长选择锁定 ~1550 nm）与光纤相位旋钮核对**误差公式**，不在台面复现铌酸锂光弹重叠积分，也不声称片上已同时集成移频与声延迟。

与 Zhu 等耦合双环工作的关系：可引用其公开声光线宽与耦合标定 [5]，但**本文几何不采用耦合双环**。Shao 行波片上频移效率 3.5%（30 dBm）[6] 与电光双环转换效率约 99%（Hu 等）[7] 若提及则**分列**，因效率定义不同，**不比胜负**。

一个自然的问题是：移频若可由电光完成、声子若只做存储，为何绑在同一驱动上？本通道同时给出光频移与可编程声相位；电光频移器没有这路机械相位；本文结果是这两项的**联合误差**。

---

## 2. 模型与方法

### 2.1 结构（Fig. 1）

正式图：`fig/fig1_structure.png`。拓扑备忘：

```
  IDT ──► 声学 MZI 总线 ──┬── 热相移臂（微加热器旁路）──┐
                          │                            ├─► 声合束 / 读出
                          └── 单根光波导重叠区（行波光弹）─┘
                                      ▲
                                 光 TE0 输入/输出
```

- **包含**：声学生总线、热声相位臂、与**一根**光波导的重叠区、端口。  
- **不包含**：耦合双环、动态 Bragg 镜、光子分子拓扑。

晶向与模族：LNoS 取 X-cut LN on sapphire、声沿晶 Y、quasi-Rayleigh/剪切族，\(f\approx 2.45\) GHz，\(v\approx 4165\) m/s；块体对照 128° Y-cut、声沿晶 X、Rayleigh，\(f\approx 1.385\) GHz。光为单脊 TE0 @ 1550 nm（\(n\approx 2.14\)，假设）。

### 2.2 热声相移

\[
\phi=\frac{\omega L}{v(T)},\qquad
\alpha=\frac{d\phi}{dP}=-\frac{\omega L}{v}\,\mathrm{TCF}\,R_{\mathrm{th}}.
\]

\(\mathrm{TCF}=(1/v)(dv/dT)\) 取文献 SAW 温度系数；\(R_{\mathrm{th}}=dT/dP\) 由二维截面稳态热传导（加热器 → 衬底热沉，**有限热阻**）得到。第一阶段在 **GaN-on-sapphire**、Xu 几何量级上做原材料路径，不以硬编码实测 \(\alpha\) 代替材料推导。随后将弹性、压电、光弹与热导换为 LN/LNoS 文献表值 [8,9]，重算 \(\alpha\)。

### 2.3 单光波导光弹（仅仿真）

行波声功率 \(P_a=\eta_{\mathrm{IDT}}P_{\mathrm{RF}}\)；有效面积 \(A_{\mathrm{eff}}=\Gamma_{\mathrm{area}} W_{\mathrm{ac}} H_{\mathrm{LN}}\)（\(\Gamma_{\mathrm{area}}\) 为假设）；应变由 \(\tfrac12 c_{\mathrm{eff}}S^2 v A_{\mathrm{eff}}=P_a\) 给出；光相位

\[
\phi_{\mathrm{AO}}=\frac{2\pi}{\lambda}\frac{n^3}{2}p_{\mathrm{eff}}S\,\Gamma_{\mathrm{ov}}L,
\]

其中 \(p_{\mathrm{eff}}=|p_{31}|=0.141\) [9]（与 Shao *Optica* 2019 中 TE–\(s_{xx}\) 用法一致 [3]），\(\Gamma_{\mathrm{ov}}\) 为假设。推挽 \(V_\pi\) 由单臂 \(\phi=\pi/2\) 反推；主算例 \(\eta_{\mathrm{IDT}}=10\%\)。

该 \(V_\pi L\) 为**非悬空行波**估算；Shao 0.045 V·cm 对应**悬空 + 声学共振** MZI [3]，**不宜**作为「超越」目标。

### 2.4 联合传递与串扰

加热功率 \(P_H\) 与射频 \(P_{\mathrm{RF}}\) 均产生热。声相位 \(\phi_{\mathrm{ac}}=\alpha P_H+\alpha\xi_{\mathrm{RF}}P_{\mathrm{RF}}\)；光热光 \(\phi_{\mathrm{TO}}\propto(dn/dT)R_{\mathrm{th}}(\xi_H P_H+\xi_{\mathrm{RF}}P_{\mathrm{RF}})\)。干涉相位误差 \(\phi_{\mathrm{err}}\) 进入 MZI 暗态残光 \(\sin^2(\phi_{\mathrm{err}}/2)\)（载波抑制 / 移频保真度代理）。文中「可分辨相位」指加热器 1 mW 步进对应的 \(|\alpha|\times 1\,\mathrm{mW}\)；不引入未核全文的气体传感应用叙事。

### 2.5 台面核对方案（Fig. 3）

正式图：`fig/fig3_benchtop.png`。

> **状态：** 波长选择锁定 ~**1550 nm**；AOM 型号锁定 G&H Fiber-Q **80 MHz** PM（`T-M080-…-F2P` + A35）。**实测格仍待测**（驱动功率、载波抑制、相位旋钮标定、干涉读出）；不把文献数字填进实验栏；图上无假数据点。

- **移频支路：** Fiber-Q 80 MHz（独立射频旋钮）→ 残余载波可调。  
- **相位支路：** 光纤延迟线或热调光纤 MZI（独立相位旋钮）。  
- **读出：** 两臂干涉；扫描两旋钮，记录可见度或条纹位移。  
- **核对对象：** 误差公式（残余载波与相位漂移如何同时进入读出），**不是** LN 光弹重叠积分。  
- **不出现的表述：**「片上已经同时集成频移与声延迟」。

---

## 3. 结果

### 3.1 GaN 热声 \(\alpha\) 与 Xu 锚

| | 数值 |
|---|---|
| Xu 实测 [1] | 4.03 rad/W（L=100 µm） |
| 本文计算（名义） | 11.2 rad/W |
| 不确定度带 | [4.5, 28] rad/W |
| 表述 | **同一数量级**；带**覆盖** Xu；**不声称复现** 4.03 |

图：`fig/gate1_alpha.png`；热场与 MZI 形状见 `fig/gate1_mzi_thermal.png`。

### 3.2 LN / LNoS 热声 \(\alpha\)

加热器长度取 Shao 区间中位 200 µm。

| | 本文计算 | Shao 实测 [2] | 比值 | 表述 |
|---|---|---|---|---|
| LNoS | **25.1 rad/W** | 9.08 rad/W（0.52 °/mW） | ~2.8 | **同量级** |
| Bulk | **148 rad/W** | 45.4 rad/W（2.6 °/mW） | ~3.3 | **同量级** |

群时延（重叠段 \(L=200\,\mu\mathrm{m}\)）：\(\tau_g\approx 48\,\mathrm{ns}\)。

### 3.3 声光 \(V_\pi L\)：三分平台并列表

| 条目 | \(V_\pi L\) (V·cm) | 平台 | 备注 |
|---|---|---|---|
| Shao 2019 [3] | **≈0.045** | **悬空** X-cut TFLN；~3.33 GHz；共振增强 | 文献实测 |
| **本文计算** | **≈0.47**（η=10%）；带 [0.08, 1.35] | **LNoS 类**行波 + 单光波导；Γ_area/Γ_ov/η 为假设 | **不宣称超过**上下两行 |
| Ni et al. [4] | **1.004** | **非悬空** X-cut **TFLN-on-Si**（360 nm / 4.7 µm BOX / Si）；**0.842 GHz**；L=**400 µm** | **不是** LNoS，**不是**悬空膜 |

η=50% 对照时计算值约 0.21 V·cm，仍置于两锚之间叙事，**仍不写超越**。

### 3.4 联合传递（Fig. 2）

名义斜率（LNoS）：

| 斜率 | 数值 |
|---|---|
| \(d\phi_{\mathrm{ac}}/dP_H\) | 25.1 rad/W |
| \(d\phi_{\mathrm{err}}/dP_H\) | **4.0 rad/W** |
| \(d\phi_{\mathrm{err}}/dP_{\mathrm{RF}}\) | **1.8 rad/W** |
| 可分辨相位 | ≈0.025 rad / mW（加热器） |

图：`fig/step2_joint_transfer.png`。Xu 的 4.03 标为 GaN 锚点；Shao \(V_\pi L\) 标为实测参考线。

---

## 4. 台面方案与预期读出

**状态：** 波长与型号已锁（~1550 nm；Fiber-Q 80 MHz）；**实测仍待测**，本节不含实测曲线。预期：固定 AOM 载波抑制，扫光纤相位，条纹位移应随相位旋钮线性；引入受控相位扰动时，可见度退化应与 \(\sin^2(\phi_{\mathrm{err}}/2)\) 代理一致量级。实验点只落在 AOM + 光纤通道；片上 \(g_0\) 与光弹重叠为仿真外推，不在本台面声称测得。

与并行「移频噪声账本」工作的接口：后者给出可见度对残余载波的上限；本文给出热调 / 射频热把相位匹配与载波抑制推离该上限的**速度**（上表斜率）。台面光路在 AOM 通路上增加光纤相位臂。

---

## 5. 讨论

1. **量级而非百分号拟合。** 热声路径含 TCF、κ、加热器几何假设；相对 Xu / Shao 偏高约三倍仍接受为同量级，用于放行光波导，而非宣称材料模型已精细校准。  
2. **\(V_\pi L\) 不可跨平台宣称超越。** 悬空共振、LNoS 行波计算、TFLN-on-Si 非悬空实测三者声约束与电声效率不同；并列表只回答计算点落在哪一区间。  
3. **串扰是主结果之一。** 4.0 / 1.8 rad/W 表明加热旋钮对干涉误差的贡献不可忽略；优化方向是热隔离或共模抑制，而非压低名义 \(V_\pi L\) 话术。  
4. **与 Zhu [5]。** 若引用其声光强度标定，须同时写明几何为耦合双环，与本文单波导总线不同。  
5. **非互易隔离**不进主结果；相关布里渊标定可留在共用参数表供后续「移频后再隔离」讨论。

---

## 6. 结论

本文在声学 MZI 上完成热声相移的原材料量级核对，并在 LN/LNoS 参数下加入**单根**光波导光弹重叠，给出同一路 \(P_{\mathrm{RF}}\)–\(P_H\) 下声相位与移频相关误差的联合传递。相对 Xu 与 Shao 热声均为**同量级**叙述；\(V_\pi L\) 计算值约 0.47 V·cm 与两条公开锚**分平台**并列且**不声称超越**。误差公式设计由商用 Fiber-Q 80 MHz AOM（~1550 nm，型号已锁）与光纤相位台面核对，**实测数据待测**。工作属仿真 + 台面文，不含自有流片器件指标宣称。

---

## 7. 边界声明

详见 `non_claims.md`。要点：不声称复现/超越 Xu 或 Shao 热声数字；不声称 \(V_\pi L\) 超过 0.045 或 1.004；无双环；无「已片上集成移频+延时」；无未核气体传感叙事；\(d\phi_{\mathrm{err}}\) 用 **4.0 / 1.8 rad/W**；Ni 为 TFLN-on-Si 非悬空锚；型号已锁、实测待测。

---

## 图件索引

| 图号 | 文件 | 内容 |
|---|---|---|
| Fig. 1 | `fig/fig1_structure.png` / `.pdf` | 声学 MZI + 热相移臂 + **单根**光波导重叠区；无耦合双环。§2.1 ASCII 为备忘。 |
| Fig. 2 | `fig/step2_joint_transfer.png` / `.pdf`；辅图 `fig/gate1_alpha.png` | 双旋钮计算曲线；Xu 4.03 为 GaN 锚；Shao \(V_\pi L\) 参考线 |
| Fig. 3 | `fig/fig3_benchtop.png` / `.pdf` | 台面方案框图（**pending**：无实测点）；波长/型号锁定叙述保留；**无假数据点** |

---

## References

1. X.-B. Xu *et al.*, “Large-scale programmable phononic integrated circuits,” arXiv:2510.26596 (2025).
2. L. Shao, S. W. Ding, Y. Ma, Y. Zhang, N. Sinclair, and M. Lončar, “Thermal modulation of gigahertz surface acoustic waves on lithium niobate,” *Phys. Rev. Applied* **18**, 054078 (2022); DOI: [10.1103/PhysRevApplied.18.054078](https://doi.org/10.1103/PhysRevApplied.18.054078); arXiv:2203.16003.
3. L. Shao *et al.*, “Microwave-to-optical conversion using lithium niobate thin-film acoustic resonators,” *Optica* **6**, 1498–1505 (2019); DOI: [10.1364/OPTICA.6.001498](https://doi.org/10.1364/OPTICA.6.001498); arXiv:1907.08593.
4. H. Ni, S. Bhave, and M. Xu, “Push-Pull acousto-optic modulator based on non-suspended thin-film lithium niobate on silicon substrate,” arXiv:2606.05337 (2026). [Full text checked: Device 3, \(V_\pi L=1.004\) V·cm @ 0.842 GHz, \(L=400\,\mu\mathrm{m}\); non-suspended X-cut TFLN-on-Si (360 nm LN / 4.7 µm BOX / Si)—not LNoS, not suspended film.]
5. Z.-X. Zhu *et al.*, “Acoustically control of integrated optical microrings: from photonic molecule to Möbius strip,” arXiv:2511.22585 (2025). [Linewidth/coupling calibration only; coupled-ring / photon-molecule geometry not adopted herein.]
6. L. Shao *et al.*, “Integrated microwave acousto-optic frequency shifter on thin-film lithium niobate,” *Opt. Express* **28**, 23728–23738 (2020); DOI: [10.1364/OE.397138](https://doi.org/10.1364/OE.397138); arXiv:2005.03794. [On-chip traveling-wave frequency-shift efficiency 3.5% at 30 dBm; listed separately from EO metrics.]
7. Y. Hu *et al.*, “On-chip electro-optic frequency shifters and beam splitters,” *Nature* **599**, 587–593 (2021); DOI: [10.1038/s41586-021-03999-x](https://doi.org/10.1038/s41586-021-03999-x); arXiv:2005.09621. [EO dual-ring conversion ~99%; not compared head-to-head with AO 3.5%.]
8. H. Ogi, Y. Kawasaki, M. Hirao, and H. Ledbetter, “Acoustic spectroscopy of lithium niobate: Elastic and piezoelectric coefficients,” *J. Appl. Phys.* **92**, 2451–2456 (2002). DOI: [10.1063/1.1497702](https://doi.org/10.1063/1.1497702).
9. A. S. Andrushchak *et al.*, “Complete sets of elastic constants and photoelastic coefficients of pure and MgO-doped lithium niobate crystals at room temperature,” *J. Appl. Phys.* **106**, 073510 (2009). DOI: [10.1063/1.3238507](https://doi.org/10.1063/1.3238507).
