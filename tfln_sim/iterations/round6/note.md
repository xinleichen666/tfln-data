# 第 6 轮：TE 路消光比、文献查新、工艺容差、EME 收敛性、3D FDTD 询价

## (a) TE 路消光比
**ADC 精确计算方法**：把孤立波导的本征模投影到耦合超模上，再沿 L 传播。结果见 adc_exact_*.json。
- 第 5 轮的 W=2.2、间隙 0.3 方案：交叉口 TE0 串扰实际为 −19 ~ −23 dB。第 5 轮的 −14 dB 只是保守上限，偏悲观。
- **改用 W=2.6、w_n=1.21、间隙 0.3 µm、L=80 µm**：
  - TE1→TE0 插损：1500–1600 nm 内 ≤0.15 dB，1450/1650 nm 处约 0.57 dB。
  - 交叉口串扰的包络（L 在 70–90 µm 内取最差值）：在 1450–1650 nm 内 ≤ −22 dB。
- **直通口问题**：没被转换的 TE1（带边约 −9 dB）经过输出端的收窄锥形时，会有 −6 ~ −9 dB 重新变回 TM0。即使用 5 µm 的突变锥形也是如此（EME 结果见 thru_filter.json），所以单靠锥形滤不掉 TE1。
  - 单级 ADC：直通口 TM 串扰为 −18/−29/−28/−23/−15 dB（对应 1450/1500/1550/1600/1650 nm）。
  - **级联第二级同参数 ADC 作为 TE1 吸收口**：串扰降到 −27/−52/−49/−39/−25 dB，整带 >25 dB。
- 渐变 ADC（窄臂宽度渐变）方案：按 LZ 公式估算约需 220 µm，太长，**淘汰**。

## (b) 文献查新：X 切 Z 向传播 PSR **已有人报道**
- Shen Y. et al., "Broadband polarization splitter-rotator on a thin-film lithium niobate with conversion-enhanced adiabatic tapers," Opt. Express 31(2), 1354 (2023)，doi:10.1364/OE.481652，PDF：https://einstein.nju.edu.cn/upload/uploadify/20230224/20230103-oe-Broadbandpolarizationsplitter-rotatoronathin-filmlithiumniobatewithconversion-enhancedadiabatictapers_202302241153325247.pdf
  - 平台：600 nm X 切，刻蚀 350 nm，侧壁 60°，SiO2 包层，**沿光轴 Z 传播**。
  - 设计：多段锥形，仿真 82.2 µm 内转换 99.8%；ADC 90 µm；加 MMI TE1 滤波器。
  - 实测：带宽 160 nm，TM 路插损 <2 dB、ER>11 dB；TE 路插损 <1 dB、ER>22 dB；器件长 405 µm，优化版 271 µm。
- 背景文献：Wang J., Dai D., Liu L., IEEE Photonics J. 12(3) (2020), doi:10.1109/JPHOT.2020.2995317（X 切波导偏振耦合与传播方向的关系）；Bull & Jaeger, JLT 25, 387 (2007)（Z 向传播 LN 波导中的寄生模式转换）。
- 对比：APL Photonics 2025, doi:10.1063/5.0240402 用的是 Y 向传播（为了兼容电光器件），三段锥形 + 三波导结构。
- **结论**："Z 向传播增强杂化"**不能**作为创新点。本工作与 Shen 2023 属于同一思路，区别只在于等绝热度锥形设计、空气包层，以及更完整的仿真指标。

## (c) 工艺容差（结果见 tol_adc_summary.json、thru_xt_summary.json、tol_taper.json）
**锥形段**
- 刻蚀 +20 nm 或侧壁 55°/65°：g 在 0.023–0.026 之间，交叉点 1.77–1.80 µm，都在 1.2–2.6 µm 的锥形覆盖范围内，**稳健**。
- **刻蚀 −20 nm（只刻 280 nm）**：杂化点比平板 TE 只高 0.02，处在横向泄漏边缘。**欠刻蚀是最敏感的方向**，工艺上宜偏深刻。

**ADC 段**（固定 L=80 µm）
- 交叉口串扰在所有工艺角下都 ≤ −19 dB，最差是 −20 nm 刻蚀在 1650 nm 处。
- 转换插损在带边会退化到 1–2.4 dB，最差的是 −20 nm 刻蚀和 +50 nm 宽度。

**级联后的直通口 PER**
- 所有工艺角下，1500–1600 nm 内都 ≥20 dB。
- 带边最差 14–19 dB，出现在 ±20 nm 刻蚀和 +50 nm 宽度的情况。
- 带边处达不到 >20 dB 的鲁棒性要求。

## (d) EME 收敛性
- 细网格：dx=10 nm、截面数从 57 增加到 113、res 60。在 1550 nm 处与粗网格的转换效率相差 <1%（L=101 µm 时为 99.25% 对 99.52%）。
- 数值损耗从 0.5% 降到 0.25%。
- L>500 µm 时的效率回落在细网格下消失，确认是离散伪影。

## 3D FDTD（只询价，未运行）
- 最终级联器件：总长约 302 µm 的仿真域，1.83×10^8 个网格，60,801 个时间步，带宽 1450–1650 nm。
- **Tidy3D 估价 3.37 FlexCredit**，这是上限，实际运行有自动截止，通常会更低。
- task id：fdve-47d8e3d1-aeb9-4803-975b-c4d588839c29。只上传，**未提交运行**。
- 文件：fdtd/build_fdtd.py、psr_final_3d.hdf5、geometry_top.png、cost_estimate.json
