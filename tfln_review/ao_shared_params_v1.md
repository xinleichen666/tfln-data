# 声光方向一/二共用参数表（初版）

> 整理日期：2026-10-12（Asia/Shanghai）  
> 用途：方向一（移频噪声账本 / 移频 HOM）与方向二（同路声驱动移频 + 声相位）共用标定；**实测与计算分列**；不发明数字。  
> 范围：仅声光 / 声子标定与 EO 对照；**不扩** SPDC / 雷达主线。

**引用 Zhu 时的硬规矩**：我们引用 Zhu et al. arXiv:2511.22585 的标定数字（C/Pₐ、κ、DBM 反射率），但**不做双环光子分子**；差分几何留给后续选题说明，本表只取参数。

---

## 1. 实测标定（状态 = 全文已核 或 摘要）

| 量 | 数值 | 出处 | 状态 |
|---|---|---|---|
| 片上频移效率 | **3.5% @ 30 dBm** RF（anti-Stokes 配置；随功率近似线性） | Shao et al., *Opt. Express* **28**, 23728–23738 (2020)；arXiv:2005.03794 | 全文已核 |
| 载波抑制 | Stokes **31 dB** / anti-Stokes **33 dB**（文中亦写 **>30 dB**） | 同上 | 全文已核 |
| 杂散边带抑制 | **>40 dB**（噪声底以下） | 同上 | 全文已核 |
| 光纤–光纤插入损耗 | **−15 dB**（含耦合） | 同上 | 全文已核 |
| RF 3 dB 带宽 | **70 MHz**（IDT 决定） | 同上 | 全文已核 |
| 频移量 | 约 **2.9–3 GHz**（Stokes 实测红移 2.89 GHz） | 同上 | 全文已核 |
| 单 IDT 微波→声效率 | 约 **31%**（由一对 IDT 的 S₂₁≈−10 dB 推断） | 同上 | 全文已核 |
| MZI 单臂 Vπ | **4.6 V**（100 µm 作用区，声模 ~3.33 GHz） | Shao et al., *Optica* **6**, 1498–1505 (2019)；arXiv:1907.08593 | 全文已核 |
| VπL | 文中表述 **≈0.045 V·cm**；由 Vπ=4.6 V × 100 µm 抽出为 **0.046 V·cm**；仿真表 TE 3.24 GHz 档 **0.0454 V·cm** | 同上（正文 + Supp. Table） | 全文已核 |
| 声学 Q（MZI） | 最高约 **3600**（文中 “up to 3,600”） | 同上，Fig. 3(c) | 全文已核 |
| IDT→声模耦合效率 | 最高约 **50%** | 同上 | 全文已核 |
| 跑道环有效 Vπ | **0.77 V** | 同上 | 全文已核 |
| 单光子声光耦合 g₀ | **~1.1 kHz**（约 2.17 GHz 声模） | 同上 | 全文已核 |
| 光子数转换效率 η | **0.0017% @ 1 mW** 光功率 | 同上 | 全文已核 |
| 单光子 cooperativity C₀ | **≈4×10⁻⁸** | 同上 | 全文已核 |
| 光学 Q（跑道环） | 加载 Q **>2×10⁶**（文中约 2.2×10⁶） | 同上 | 全文已核 |
| 声频 Ω/2π | **∼8.54 GHz**（匹配超模劈裂） | Zhu et al., arXiv:2511.22585 | 全文已核 |
| β/√Pₐ | **2π×1.33 GHz/√mW** | 同上 | 全文已核 |
| 归一化 cooperativity C/Pₐ | **2.46 mW⁻¹**（Pₐ=2.5 mW 时 C=6.2） | 同上 | 全文已核 |
| 超模线宽 κ/2π | **≈0.93 GHz / 0.69 GHz**（κ₂ / κ₁） | 同上 | 全文已核 |
| DBM 反射率 | **24% @ Pₐ=6.3 mW**（Al IDT 功率上限；文中预言 ~26 mW 可达 R≈99%） | 同上 | 全文已核 |
| Brillouin 耦合标定 α | **G² = α Pₐ**，**α = 1774±171 GHz²/W** @ **8.533 GHz** | Xu et al., arXiv:2509.01940 | 全文已核 |
| RF→声效率（Xu） | 约 **10%** | 同上 | 全文已核 |
| 本征线宽 κ₀/2π | **≈0.32 GHz**（另文中 κ₁/2π≈0.38 GHz） | 同上 | 全文已核 |
| 隔离度 | **45 dB** @ 声功率 **5.7 dBm** | 同上 | 全文已核 |
| π 回转插入损耗 | **≈8.2 dB** @ **−0.3 dBm** 声功率 | 同上 | 全文已核 |
| 热声相位器效率 | **4.03 rad/W**（相移器长度 **100 µm**；平台 **GaN-on-sapphire**，非 LN） | Xu et al., arXiv:2510.26596 | 全文已核 |
| 非悬空 AO MZI VπL | **1.004 V·cm** @ **0.842 GHz**（作用长度 **400 µm**） | H. Ni, S. Bhave & M. Xu, arXiv:2606.05337；§IV / Abstract / Table I | 全文已核 |
| 平台差（对照时必写） | **X-cut TFLN-on-Si**（360 nm LN / 4.7 µm BOX / Si），**不是** LNoS，也不是 Shao 悬空膜 | 同上 | 全文已核 |
| 非悬空 AO 调制带宽 | **132.5 MHz**（3 dB；中心 ~0.84 GHz） | 同上，Fig. 4 / Table I | 全文已核 |
| 非悬空器件堆栈 | X-cut TFLN **360 nm** LN / **4.7 µm** BOX / Si；**非悬空** push-pull MZI | 同上，§II–III | 全文已核 |
| 光栅耦合 / 片上损耗 | 耦合约 **4.5 dB/面**；片上传播损耗约 **0.76 dB** @ 1550 nm | 同上，§III / Fig. 2(g) | 全文已核 |
| Qiu serrodyne Vπ（**EO 对照，非 AO**） | **≈2.3 V** | Qiu et al., *Opt. Lett.* **50**, 1132 (2025)；LNOI 级联行波 PM + serrodyne | 摘要 |
| Qiu 移频效率（EO） | **>98.8%** | 同上 | 摘要 |
| Qiu CSR / SSR（EO） | **42 dB / 31 dB** | 同上 | 摘要 |

**Zhu 脚注（必读）**：上表 Zhu 各行仅作声–光耦合强度与线宽标定。选题**不实现** Zhu 的耦合双环 / 动态 Bragg 镜 / Möbius 拓扑；方向一用 α、C、κ 估自发布里渊上限，方向二用公开标定对接组内声学 MZI，均**不做双环光子分子**。

---

## 2. EO 对照（Hu 2021，非声光）

| 量 | 数值 | 出处 | 状态 |
|---|---|---|---|
| 频移最高 | **28.2 GHz** | Hu et al., *Nature* **599**, 587–593 (2021)；arXiv:2005.09621 | 全文已核（既有核对表） |
| 转换效率 η | **98.7% @ 28.2 GHz**；12.5 GHz 上/下移约 **99.1% / 99.4%** | 同上 | 全文已核（既有核对表） |
| 驱动功率（常见引用） | 约 **96 mW**（3.1 V peak @ 50 Ω 探针）对应 η=98.7%@28.2 GHz | 同上，Supp. | 全文已核（既有核对表） |
| 插入损耗 | 约 **0.45 dB**（28.2 GHz）– **1.2 dB**（12.5 GHz） | 同上 | 全文已核（既有核对表） |
| RF 带宽 | **>3 GHz** 量级（放大器限制）；可级联至约 **119.2 GHz** 移位 | 同上 | 全文已核（既有核对表） |

说明：AO 与 EO 的「效率」定义不同（Shao 2020 的 3.5% 是片上偏转/频移功率比；Hu 的 ~99% 是双环转换效率）。方向一文中禁止混柱比较。

---

## 3. 计算量（状态 = 计算；**非实测**）

热声子平均占据数由 Bose–Einstein 公式算出，**不是**文献噪声谱：

\[
n_{\mathrm{th}} = \frac{1}{\mathrm{e}^{hf/k_{\mathrm{B}}T}-1}
\]

| 量 | 数值 | 出处（声频） | 状态 |
|---|---|---|---|
| n_th（2.17 GHz，300 K / 4 K） | **≈2.88×10³ / ≈38** | 声频：Shao 2019 跑道环 g₀ 语境；公式见选题 PDF §2.3 | 计算 |
| n_th（2.007 GHz，300 K / 4 K） | **≈3.11×10³ / ≈40** | 声频：Shao 2019 **Table S2**（与同表 κ/γ/g₀ 一套） | 计算 |
| n_th（3.33 GHz，300 K / 4 K） | **≈1.88×10³ / ≈25** | 声频：Shao 2019 MZI | 计算 |
| n_th（3.0 GHz，300 K / 4 K） | **≈2.08×10³ / ≈27** | 声频：Shao 2020 行波频移 | 计算 |
| n_th（8.54 GHz，300 K / 4 K） | **≈7.32×10² / ≈9.3** | 声频：Zhu；Xu 为 8.533 GHz | 计算 |

**脚注（避免混用）：** 方向一噪声账本 **乙类锁定** 用 **2.007 GHz（Table S2）**，与同套 κ/γ/g₀ 一致，对应 \(n_\mathrm{th}(300\,\mathrm{K})\approx3.11\times10^3\)（见 `/workspace/freq_shift_noise/report_formulas_v1.md`）。**2.17 GHz** 只对应正文跑道环 g₀≈1.1 kHz 语境，**不要**拿来算乙类 \(n_\mathrm{th}\)。

方向一台面在室温；4 K 列仅说明：即便把 Shao 2019 器件放进液氦，n_th 仍为数十，量子换能不自动成立。

---

## 4. 开放项 / 未升级状态

| 项 | 现状 | 下一步 |
|---|---|---|
| **Qiu Opt. Lett. 2025** | 摘要数字已核对；**EO serrodyne（级联行波 PM），不是 AO**。本地仅 OPG 跳转页 → 保持 **摘要** | 全文到位再升「全文已核」；正文旁注必须写 EO 对照 |
| **Hu 2021 本地 PDF** | 本机无 `2005.09621.pdf`；数字来自 paperB 既有「全文」核对表（`report_B.md` / `sota_comparison.md`） | 需要时可补下 arXiv PDF 做二次页码定位 |
| **Xu 2509.01940 本地 PDF** | 本机无独立 PDF；本表数字已对照 **arXiv HTML 全文**（2026-10-12 拉取）与 paperB 核对表，标 **全文已核** | 可选：落盘 PDF 到 `verify/` |
| **Ni / Bhave arXiv:2606.05337** | **已全文核对**（2026-10-12）：VπL=**1.004 V·cm** @ 0.842 GHz、L=400 µm、非悬空、带宽 132.5 MHz；已写入 §1 | 已关闭；引用时写明非悬空 push-pull MZI，勿与 Shao 悬空 0.045 混比 |

---

## 5. 本地源文件路径

| 文献 | 本地路径 |
|---|---|
| Shao *Optica* 2019 | `/workspace/dir11/paperB/verify/1907.08593.pdf` (+ `.txt`) |
| Shao *OE* 2020 | `/workspace/dir11/paperB/verify/2005.03794.pdf` (+ `.txt`) |
| Zhu arXiv:2511.22585 | `/workspace/dir11/paperB/verify/2511.22585.pdf` (+ `.txt`) |
| Xu arXiv:2510.26596 (PnIC) | `/workspace/tfln_review/user_materials/arxiv_2510.26596.pdf`；文本 `/workspace/tfln_review/user_materials/pnic.txt` |
| Xu arXiv:2509.01940 | 无本地 PDF；核对用 arXiv abs/HTML + `/workspace/dir11/paperB/sota_comparison.md` 行 15、`sota_update_2026.md` N2 |
| Qiu *OL* 2025 | `/workspace/dir11/paperB/verify/qiu.html`（仅跳转，无全文） |
| Hu *Nature* 2021 | 无本地 PDF；既有核对：`/workspace/dir11/paperB/report_B.md`、`sota_comparison.md` |
| Ni / Bhave arXiv:2606.05337 | `/workspace/dir11/paperB/verify/2606.05337.pdf` (+ `.txt`) |
| 文献简报 | `/workspace/tfln_review/user_materials/2026-10-12/phonon_photon_literature_for_Cursor.md` |
| 选题 PDF | `/workspace/tfln_review/user_materials/2026-10-12/ao_two_directions_Cursor_2026-10-12.pdf` |
| 论文 B 参数来源 | `/workspace/dir11/paperB/data/params_sources.md` |

---

## 6. 行数统计

- §1 实测标定：**34** 行（其中 Qiu 3 行为摘要；Ni/Bhave 4 行 + 其余全文已核）
- §2 EO 对照：**5** 行
- §3 计算 n_th：**5** 行  
- **合计参数行：44**（不含脚注、开放项与路径索引）

初版后续修订（2026-10-12）：Ni/Bhave arXiv:2606.05337 已全文核对并写入 §1。方向一文案引用本表时，Shao/Zhu/Xu/Ni 用「全文已核」行；Qiu 保持「摘要」并避免当主对照；n_th 必须写明「由公式计算，非实测」。Ni 的 1.004 V·cm 是**非悬空**锚，与 Shao 悬空 ≈0.045 V·cm **分列**，禁止混比宣称打赢。
