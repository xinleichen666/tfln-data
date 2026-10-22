# Step 6h 文献对比：已发表的薄膜铌酸锂（TFLN）声光调制器 vs 本设计（仿真）

本稿仅限课题组内部。本设计的数值都是仿真预测（理想馈电网络、准二维、周期超胞），不是实测；文献数值是对方的实测或对方给出的换算。

检索方式：Cursor 内置网页搜索（parallel-cli 未登录，经用户同意改用）。检索到的原文文本只存在本地 `lit/`，不入库。
只采用能在原文里核对到的数字。

## 1) 文献数值

| 工作 | 平台 / 结构 | 频率 | 作用长度 L | 文献给出的效率 | 来源 |
|---|---|---|---|---|---|
| Shao 等，Optica 2019 | 悬空 TFLN，100 µm 长声学谐振腔，单臂 MZI | **3.33 GHz**（声学 Q 最高 3600） | 100 µm | **Vπ = 4.6 V，VπL = 0.046 V·cm**（由 S21 提取，50% 微波-声耦合） | [S1] |
| 同上，跑道腔 | 同上，光学 Q 2.2e6 | 2 GHz | 100 µm | 等效 Vπ = 0.77 V（腔增强） | [S1] |
| 同上，Wan 等整理 | — | 3.33 GHz | 100 µm | αp = 0.27 rad/√mW | [S2] 表 1 |
| Hassanien 等，Photonics Research 2021（宽带） | 悬空 TFLN，Lamb 波穿过光子晶体波导 | 1.9 GHz，带宽 140 MHz | 45 µm | αp = 0.0166 rad/√mW（0.37 rad/√mW/mm） | [S3][S4] |
| 同组，谐振型（Wan 等整理） | 悬空 TFLN 声学腔 | 1.16 GHz | 45 µm | αp = 0.54 rad/√mW，VπL = 0.019 V·cm | [S2] 表 1 |
| Wan 等，LSA 2022 | 非悬空 TFLN + 硫系玻璃，推挽 MZI | 0.844 GHz | 120 µm | Vπ = 2.5 V，VπL = 0.03 V·cm；αp 0.4 rad/√mW | [S2] |
| Cai 等（Wan 表 1 引用） | TFLN，金属栅反射腔，Rayleigh 表面波 | 0.11 GHz | 1200 µm | VπL = 2.5 V·cm，αp 0.073 rad/√mW | [S2] 表 1 |
| LPOR 2025，跑道微环 | 非悬空 TFLN + 硫系玻璃 | 0.84 GHz | — | VπL = 9 mV·cm，αp 1.49 rad/√mW | [S5] |
| LPOR 2025，无刻蚀 BIC 波导 | LNOI 无刻蚀 | 0.76 GHz | — | VπL = 1.133 V·cm | [S6] |
| Sarabalis 等，Optica 2021 | 悬空 X 切 LN，共线模式转换（TE0↔TE1） | 0.44 GHz | 250 µm | 完全转换 Pπ/2 = 60 mW（外推） | [S7] |
| Shao 等，Optics Express 2020 | TFLN 声光移频器（Bragg 偏转） | 约 3 GHz | — | 30 dBm 驱动下效率 3.5%，再加功率会烧坏 IDT | [S8] |

按 Pπ = (π/αp)² 换算（我们自己算的，不是原文数字）：
- Shao 3.33 GHz 器件约 0.14 W
- Hassanien 宽带器件约 36 W
- Hassanien 谐振器件约 34 mW
- Wan 推挽器件约 62 mW

## 2) 本设计（仿真，主峰 v 模，铝 100 nm）

| 配置 | f (GHz) | VπL（以指间电压计） | 到达 π 的信号源功率 | αp (rad/√mW) |
|---|---|---|---|---|
| NP=15，不分段，最优 L=1.64 mm | 3.342 | 0.87 V·cm（峰处） | 16.9 W | 0.024 |
| NP=15，L=1 mm，分 8 段 | 3.342 | 同上 | 13.7 W | 0.027 |
| NP=15，分 8 段，L=5 mm | 3.342 | 同上 | 3.1 W | 0.056 |
| NP=11，不分段，最优 L=1.17 mm | 3.344 | 0.75 V·cm（峰处） | 6.1 W | 0.040 |
| NP=11，L=1 mm，分 8 段 | 3.346 | 同上 | 2.9 W | 0.059 |
| NP=11，分 8 段，L=5 mm | 3.344 | 同上 | 0.92 W | 0.104 |

αp = π/√P_源。功率按无损 L 型匹配到 50 Ω 计算，电极按分布 RC 线，汇流条和馈电网络理想。
NP=9 和 NP=7 的 VπL 分别为 1.28 和 2.28 V·cm。

## 3) 对比结论

1. **频段**：3.3 GHz 已有直接先例。Shao 2019 就是悬空 TFLN、3.33 GHz、IDT 驱动的声学谐振腔，光波导放在腔内 [S1]。
   “GHz 级悬空 TFLN 声光相位调制”本身不是新点。
2. **VπL**：本设计 0.75–0.87 V·cm，是 Shao 实测值 0.046 V·cm 的 16–19 倍。
   两者 Vπ 的定义不同：文献以 50 Ω 信号源电压计，本设计以指间电压计。但这种差别不足以解释一个数量级的差距。
3. **功率效率**：本设计最好的 αp 约 0.10 rad/√mW（NP=11、分 8 段、L=5 mm、理想馈电），
   低于 Shao（0.27，实测，100 µm）和 Hassanien 谐振型（0.54，实测，45 µm）；
   不分段时（0.024–0.040）与 Hassanien 宽带器件（0.0166）同一量级。
4. **亚瓦级不是卖点**：同频段文献按 αp 换算的 π 功率约 0.14 W，本设计最好的情况也有 0.9 W。
   另外 6h 已表明，低频峰的亚瓦结果依赖超胞周期。
   所以“Sub-watt in-plane Lamb-mode …”这个题目既不成立，也没有新意。
5. **本设计相对文献可能有价值的地方**（需要论证，不是现成结论）：
   - 把电极分布电阻（RC 传输线）、50 Ω 匹配和分段馈电纳入功率预算。检索到的文献给的都是 S21 或 Vπ 的实测或换算，
     没有看到对长孔径叉指电极电阻损耗的定量分析；本设计中电极电阻占功率的 85–99%。
   - 周期超胞模型的收敛问题：主峰 |tot| 随 NP 变化 3 倍，低频峰频率随 NP 变化。这对同类仿真是一个方法论上的提醒。

## 4) 论文定位建议

- 不建议用“Sub-watt …”题目。
- 若坚持“Co-design of acoustic, optical and electrical domains for in-aperture acousto-optic phase modulation …”，
  应定位为**建模与设计方法**的文章：声-光-电三域联合、分布电极损耗、分段馈电、超胞收敛，并如实写明性能不及 Shao 2019 [S1]。
- 若想在性能上有竞争力，需要先回答“为什么孔径内（in-aperture）方案比腔内波导方案差一个数量级”。
  可能的原因（未验证）：长孔径带来很大的 Re(Y)·L 和电极电阻；光模只覆盖了声学孔径的一小部分；
  主模在脊处的应变相位分布不理想。可以考虑用一个 Shao 型基准结构（100 µm 腔、波导在腔内）在同一套仿真流程里复现
  0.046 V·cm 作为模型校准。如果复现得出来，就能确认差距来自结构本身，而不是模型。

## 来源

- [S1] [Shao et al., Microwave-to-optical conversion using lithium niobate thin-film acoustic resonators, Optica 6, 1498 (2019)](https://doi.org/10.1364/OPTICA.6.001498)；全文 [arXiv:1907.08593](https://arxiv.org/html/1907.08593)
- [S2] [Wan et al., Highly efficient acousto-optic modulation using nonsuspended thin-film lithium niobate-chalcogenide hybrid waveguides, Light Sci. Appl. (2022)](https://www.nature.com/articles/s41377-022-00840-6)；[表 1](https://www.nature.com/articles/s41377-022-00840-6/tables/1)
- [S3] [Hassanien et al., Efficient and wideband acousto-optic modulation on thin-film lithium niobate for microwave-to-photonic conversion, Photonics Research 9, 1182 (2021)](https://doi.org/10.1364/PRJ.421612)
- [S4] [Hassanien, PhD thesis, UIUC (2022)](https://www.ideals.illinois.edu/items/124689/bitstreams/409792/data.pdf)
- [S5] [Hybrid Thin-Film Lithium Niobate Micro-Ring Acousto-Optic Modulator with Low Half-Wave-Voltage-Length Product, Laser Photonics Rev. (2025)](https://doi.org/10.1002/lpor.202401832)
- [S6] [Highly Efficient Intramodal and Intermodal Acousto-Optic Modulation on an Etchless Lithium Niobate Integrated Platform, Laser Photonics Rev. (2025)](https://doi.org/10.1002/lpor.202401525)
- [S7] [Sarabalis et al., Acousto-optic modulation of a wavelength-scale waveguide, Optica 8, 477 (2021)](https://doi.org/10.1364/OPTICA.413401)
- [S8] [Shao et al., Integrated microwave acousto-optic frequency shifter on thin-film lithium niobate, Opt. Express 28, 23728 (2020)](https://doi.org/10.1364/OE.397138)

本地原文文本（不入库）：`step6_optics/lit/*.txt`
