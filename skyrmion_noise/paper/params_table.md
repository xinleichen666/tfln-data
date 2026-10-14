# 参数表 · skyrmion_noise

分列：**文献**（仅对照引用） / **本轮计算**（脚本产出） / **假设**（构造选择）。

| 项 | 文献 | 本轮计算 | 假设 |
|---|---|---|---|
| 先验 | Zhao et al., *Nat. Phys.* (2026), doi:10.1038/s41567-026-03487-x：芯片光子量子斯格明子 | **不复现**实验；结果表不抄 1.981 / 89% / 0.34 / 0.25 / 0.5 | — |
| 模型口径 | — | — | **自定纹理噪声预算，不是该实验的复现** |
| 两光子态 | 路径纠缠 + 自旋纹理（实验语境） | \(\lvert\Psi\rangle=(\lvert L0\rangle+\lvert R1\rangle)/\sqrt{2}\)（`protocol.state`） | A=圆偏振 L/R；B=伴侣路径/偏振量子比特 |
| 空间模式 | 微环角光栅编自旋纹理（实验） | \(u_L=\mathrm{LG}_{0,0}\)，\(u_R=\mathrm{LG}_{0,1}\)；w=1；97×97 格，半宽 4w | 教科书 LG；非器件模式 |
| 斯格明子数 | 实验报道单光子斯格明子数≈**1.981**（**仅对照**） | 条件斯托克斯纹理积分 \(N_\mathrm{sk}=(1/4\pi)\iint n\cdot(\partial_x n\times\partial_y n)\,dx\,dy\)；干净 \|N_sk\|=**0.953**（`clean_skyrmion_abs`） | B 投到 \(\lvert+\rangle=(\lvert0\rangle+\lvert1\rangle)/\sqrt{2}\) 后取 A 的 2×2；**非** 4×4 本征值 |
| 退极化 | 近各向同性噪声（实验语境） | \(\rho'=(1-\xi)\rho+(\xi/4)I_4\)；ξ∈[0,1]×21 | `protocol.channels.depolarizing` |
| 相位翻转 | 相位翻转混合（实验语境） | \(\rho'=(1-p)\rho+p(Z\otimes I)\rho(Z\otimes I)\)；p∈[0,1]×21 | 翻转作用在斯格明子光子 A |
| 比特相位翻转 | 比特相位翻转混合（实验语境） | \(\rho'=(1-p)\rho+p(Y\otimes I)\rho(Y\otimes I)\) | 同上 |
| concurrence | — | Wootters 两比特（`protocol.concurrence`） | — |
| discord | — | \(D(A\mid B)=I-J_{\max}\)；B 上投影测量 Bloch 角数值优化 | `protocol.discord` |
| 过零阈 | 实验纯度≈0.34/0.25 等为**文献** | \|metric\|≤**0.02** 记到零（`zero_threshold_abs`） | 本扫网格首次点 |
| 种子 | — | master=20261014；depol=401；phase=402；bitphase=403；probe=404 | 写死于脚本 `SEEDS` |
| 硬件 | SiN 芯片实验（文献） | 本机经典 CPU | 无量子硬件；Fiber-Q N/A；无自有流片 |
