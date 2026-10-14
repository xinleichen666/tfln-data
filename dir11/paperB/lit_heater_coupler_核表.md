# 文献核表 · 可调耦合 / TFLN 加热器效率

**日期**：2026-10-14 · 文献包  
**用途**：供工作包改仿真主线（加热调 |2µ−Ω|）；**只录带出处的数，不发明。**  
**工作目录**：`/workspace/dir11/paperB/`

---

## ① Zhang et al., *Nat. Photonics* **13**, 36–40 (2019)

| 项 | 核实结果 | 出处位置 |
|---|---|---|
| 题名 / DOI / arXiv | Electronically programmable photonic molecule；DOI [10.1038/s41566-018-0317-y](https://doi.org/10.1038/s41566-018-0317-y)；arXiv:[1809.08638](https://arxiv.org/abs/1809.08638) | 期刊页 + arXiv |
| 平台 | 耦合 LN 微环光子分子；**电光（EO）差分电极**，**不是**热光加热器调耦合 | arXiv 正文 Fig.1、方法段 |
| 几何耦合 2µ | **由环间间隙固定**：间隙 ~500 nm（正文）/ 器件表 ~700 nm（补充）；测得 **2µ = 2π × 7 GHz**；线宽 γ = 2π × 96 MHz | arXiv Fig.1c 及正文 |
| 2µ 随「加热相位」？ | **文中无加热器调 2µ。** 几何 µ 由间隙决定；DC 偏置做的是两环**失谐**（Stark / 反交叉），不是改间隙耦合强度 | Fig.1d：±15 V DC → 反交叉；渐近线给出 **g = 2π × 0.5 GHz/V** |
| 「有效」能级耦合 | 微波失谐大时的 **AC Stark** 可改变两能级之间的*有效*耦合（原文："control the effective coupling strength … otherwise determined by geometric factors"）；这是 **EO 微波驱动**下的有效量，**不是**热光相位 φ 下的 µ(φ) | Fig.2c 及正文 |
| 可调定向耦合器 / MZI 耦合公式 | **Zhang 2019 未给出** µ(φ) 或定向耦合器随加热相位的解析式 | 全文检索（ar5iv HTML） |

**本稿边界（写给工作包）**

- **可写**：Zhang 2019 证明 TFLN 光子分子可用电极做 DC 失谐与微波相干控制；几何 2µ 由间隙定，他们的样件 ~7 GHz。  
- **不可写**：把 Zhang 的 0.5 GHz/V 或 7 GHz 劈裂当成「加热调 2µ」的标定；不可声称 Zhang 给了 µ∝cos(φ/2) 一类加热公式。  
- **若仿真要加热调耦合**：须**另标假设**（例如 MZI 型可调耦合器的教科书关系 κ∝sin²(Δφ/2)），并在 STATUS / params_table 写「非 Zhang 2019 复现」；或另引真正带加热臂的可调耦合器文献（本稿①未核到 Zhang 提供该曲线）。

---

## ② 已发表 TFLN 加热器效率（Pπ 或相位/功率）

| 量 | 数值 | 出处 | 几何 / 条件（须当假设保留） | 本稿可用边界 |
|---|---|---|---|---|
| 环谐振全 FSR 热调功率 | **14.9 mW** 扫过 1 个 FSR；效率 **53.7 pm/mW** | Liu et al., *Opt. Lett.* **45**, 6318 (2020)；DOI [10.1364/OL.410192](https://doi.org/10.1364/OL.410192)（摘要已核） | LNOI 微环 + **隔热槽**（相对无槽 >20×）；摘要**未给**对应 Pπ（波导移相器）也未给 FSR 数值 | **可作**「有隔热槽的环调谐效率」对照；**不可**直接当环–环耦合区加热的 Pπ，除非换算并写明 FSR/几何假设 |
| 波长热调效率（SHG 波导） | **94 pm/mW**；~50 mW 扫约 5 nm；空气槽 + NiCr 加热器 | Liu et al., *Opt. Lett.*（热调 SHG / micro-heater；公开 PDF/摘要叙述） | 5 mm 级 PPLN 直波导、上包层 ~1.5 µm、NiCr 5 µm 宽等 | **可作**直波导热调效率量级；**不是**移频器耦合器 Pπ |
| 多波导热光移相器仿真 | 约 **34 mW** 量级热调制（摘要写 approximately 34 mW）、响应 ~180 µs | Designs and Comparisons of Heater Configurations…（TFLN 多波导加热电路仿真；Researching 摘要） | **仿真**，非流片实测；几何依赖加热电阻布局 | 仅作量级；**不可**当实测 Pπ 写进结果表 |
| 可见–近红外 TFLN 调制器加热偏置 | 报道多波长 **Pπ** 约 **34.7–150.3 mW**（随波长升高） | ACS Photonics「Visible and Near-Infrared Thin-Film Lithium Niobate Modulators with Thermo-Optic Bias」（摘要综述；正式页码以出版社为准） | 可见光/NIR 波段；几何异于 1550 nm AO 环 | **可对照波段依赖**；**不可**无换算抄进 1550 nm 双环稿 |
| 各向异性 TO 模型 + P_{π/4} | 给出按偏振/晶向的 dn_eff/dP；文中用 **P_{π/4}** 作基准（HTML 正文 Fig.3）；**主文未在摘要段写死单一 Pπ 毫瓦数** | Shim et al., arXiv:[2601.00174](https://arxiv.org/abs/2601.00174)（Harvard/KAIST；x-cut MgO:TFLN） | NiCr 加热器：W_h=3 µm，L_h=750 µm，G_h=2 µm；racetrack | **可引**几何与「须标晶向/偏振」；取具体 mW 前需从补充/Fig.3 读斜率，**本稿不编造 Pπ** |
| 商业模组加热器 Pπ | typ **2.5 mW** / max 3.0 mW（datasheet） | NeonCQ TFLN Intensity Modulator 规格书 PDF | **非同行评审**；未知是否与本研究几何可比 | **不推荐**作论文主表；内部敏感性可标「商业规格书，非文献」 |

**教科书关系（非 Zhang，仅作建模选项时必须标假设）**

- MZI 型可调耦合器：功率耦合比常取 \(T=\sin^2(\Delta\phi/2)\) 或 \(\cos^2(\Delta\phi/2)\)（标准集成光学；**不是** Zhang 2019 的测量结论）。  
- 相位与功率：在线性热光假设下 \(\Delta\phi \propto P\)，则 \(P_\pi\) 定义为 \(\Delta\phi=\pi\) 时的功率；具体 mW **必须**绑上表某一出处的几何，或明确写「假设 Pπ = … mW」。

---

## 给仿真主线的一句话建议

1. **加热调 |2µ−Ω|**：不要从 Zhang 2019 抽 µ(φ)；Zhang 的 2µ 是**固定间隙**，电极调的是**失谐**。耦合可调用 **MZI 耦合器假设** + 自选/文献 Pπ，或保持间隙蒙特卡洛 + 加热只进 δr/Δ（两环温差）。  
2. **加热器效率**：优先在 params_table 写清采用哪一行（建议：Liu 2020 隔热槽作乐观环调谐对照；移相 Pπ 若无实测几何则标**假设**并扫 10–50 mW 量级，与上表仿真/可见光文献同阶）。  
3. **禁止**：把文献 Pπ / 7 GHz / 0.5 GHz/V 抄进 `summary.json` 的结果键冒充本轨扫出来的数。

---

## Bib（核验用）

```bibtex
@article{Zhang2019PhotonicMolecule,
  author  = {Zhang, Mian and Wang, Cheng and Hu, Yaowen and Shams-Ansari, Amirhassan and Ren, Tianhao and Fan, Shanhui and Lon{\v{c}}ar, Marko},
  title   = {Electronically programmable photonic molecule},
  journal = {Nat. Photonics},
  volume  = {13},
  pages   = {36--40},
  year    = {2019},
  doi     = {10.1038/s41566-018-0317-y},
  eprint  = {1809.08638},
  archivePrefix = {arXiv}
}
@article{Liu2020TOLNOI,
  author  = {Liu, Xiaoyue and Ying, Pan and Zhong, Xuming and Xu, Jian and Han, Ya and Yu, Siyuan and Cai, Xinlun},
  title   = {Highly efficient thermo-optic tunable micro-ring resonator based on an {LNOI} platform},
  journal = {Opt. Lett.},
  volume  = {45},
  pages   = {6318--6321},
  year    = {2020},
  doi     = {10.1364/OL.410192}
}
@article{Shim2026AnisotropicTO,
  title   = {Generalized model of anisotropic thermo-optic response on thin-film lithium niobate platform},
  author  = {Shim, Joonsup and Kim, Seonghun and Lu, Shengyuan and others},
  year    = {2026},
  eprint  = {2601.00174},
  archivePrefix = {arXiv}
}
```

---

## ③ 追加：1550 nm 附近实测移相器 Pπ（有几何）

| 量 | 数值 | 出处 | 几何 / 条件 | 本稿可用边界 |
|---|---|---|---|---|
| MZI 热光移相器 **Pπ** | **44.4 mW**（λ≈1516 nm 经典扫；单光子路由在 1550 nm） | Maeder et al., *Quantum Sci. Technol.* **9**, 035040 (2024)；DOI [10.1088/2058-9565/ad4b98](https://doi.org/10.1088/2058-9565/ad4b98)；全文 PDF（IOP OA）Fig.3b / Abstract / Table 1 | 300 nm x-cut LNOI；Au 加热条 **Lh = Ls = 1.0 mm**，wh≈1 µm，hh=100 nm；SiO₂ 包层；波导宽 1200 nm、刻蚀 ~200 nm（有效 hwg≈235 nm）；**无**隔热槽报告；响应可达 0.7 µs（过驱动） | **可写**为「无槽、~1 mm Au 加热臂」的 **1550 nm 量级实测 Pπ 对照**；几何与本稿声光双环耦合区不同，**不可**直接当环–环耦合器标定。params_table 若采用须写「Maeder 2024 几何假设，非本版图」 |
| 同文仿真 Pπ（对照） | **57.2 mW**（hTOX=1 µm、Lh=1 mm） | 同上，正文 Fig.2e | 有限元热+模式；作者称与实测同阶、定量差因界面热阻等 | 仅作仿真–实测差对照；**不**当实测结果 |

**与上表关系**：相对 Liu 2020（环 + 隔热槽、14.9 mW/FSR，**非**移相器 Pπ），本行是 **waveguide MZI 移相器** 的对口量；相对「仿真 ~34 mW」行，本行为**同行评审实测**。MZI 功率耦合比仍用教科书 \(T=\sin^2(\Delta\phi/2)\)（Maeder Appendix A），**不是** Zhang 2019 的 µ(φ)。

```bibtex
@article{Maeder2024LNOIMZI,
  author  = {Maeder, Andreas and Finco, Giovanni and Kaufmann, Fabian and Sabatti, Alessandra and Kellner, Jost and Chapman, Robert J. and Grange, Rachel},
  title   = {On-chip tunable quantum interference in a lithium niobate-on-insulator photonic integrated circuit},
  journal = {Quantum Sci. Technol.},
  volume  = {9},
  pages   = {035040},
  year    = {2024},
  doi     = {10.1088/2058-9565/ad4b98}
}
```

---

## ④ 流片路径 · 加热器→环热串扰（mK @Pπ）

**日期补记**：2026-10-14 · 用户定流片；v2 ALL_PASS 绑串扰假设。

| 量 | 核表结论 |
|---|---|
| 耦合器加热臂 → 双环共模 / 差分串扰（mK @Pπ） | **核表无同几何发表值**。已扫 Zhang 2019（无加热调耦合）、Liu 2020（环调谐效率，无 mK 串扰）、Maeder 2024（MZI Pπ，无环–环串扰标定） |
| 仿真 v2 采用值 | `dT_cm@Pπ=3 mK`、`dT_diff@Pπ=2 mK` — **仅仿真假设**（隔热加强叙事），**禁止**写入核表「已发表」列或摘要当实测 |
| 可写 | 「串扰为假设；须流片后第1步用加热功率→劈裂/失谐标定」 |
| 不可写 / 不可做 | 编造任何 mK 进核表；把 3/2 mK 标成文献数；达不到假设时仍按 ALL_PASS 叙事（回退 v1，判据① FAIL） |

**与 Maeder / Zhang 边界无关**：Pπ=44.4 mW 仍标 Maeder 几何假设；µ(φ) 仍自标 MZI，不抽 Zhang。

**Cursor GO 锁定（PR #14，2026-10-14）**

- Maeder Pπ=44.4 mW：**仍只作几何假设**，GO 流片不改变该标签；实测 Pπ 须本片独立标定后另记，不得回填冒充 Maeder 发表值。
- 串扰 3/2 mK：**永不进核表「已发表/实测」列**。步1须**开环**（环加热停住，只扫 MZI；共模对暗参考环 + 差分，在实测 Pπ 处判）。标定结果可写进测量表实测栏，**不**并入核表文献行。
- 比 v1 好但未到 3/2 → 仍 FAIL，不许用文献插值成品率。
