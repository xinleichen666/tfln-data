# 自旋–轨道斯格明子数相对 concurrence / discord 的噪声预算（方法·噪声预算）

**轨道：** `skyrmion_noise/`（Bot E）  
**日期：** 2026-10-14（Asia/Shanghai）  
**数字出处：** 凡带键名的数均来自本轮 `/workspace/skyrmion_noise/data/summary.json`（固定种子脚本重跑）。  
**模型口径：** **自定自旋–轨道纹理上的经典噪声预算，不是 Zhao 实验的复现。**

---

## 摘要

本稿仅限课题组内部：仿真与方案工作稿，实测待做，无伪造数据，Fiber-Q 对本方向 N/A，无自有流片；不得作为公开或可引用结果；verify/ 第三方 PDF 禁止入库。

Zhao et al., *Nat. Phys.* (2026), doi:10.1038/s41567-026-03487-x 在氮化硅芯片上报道光子量子斯格明子相关实验。本稿**不写观测**、不复现其器件数：在自定 LG 自旋–轨道锁定纹理与伴侣量子比特构成的两光子纯态上，对三类可写信道做**方法·噪声预算**，比较纹理积分斯格明子数、concurrence、discord 谁先到零。

**干净极限：** \|N_sk\|=**0.953**（`headline.clean_skyrmion_abs`；有限格离散积分）、concurrence=**1.000**、discord=**1.000**（`clean_concurrence` / `clean_discord`）。

**退极化 ξ∈[0,1]：** concurrence 于 ξ=**0.7** 首次到零（`vanish_depolarizing.concurrence.cross_x`），discord 于 ξ=**0.9**，\|N_sk\| 于 ξ=**1.0**；**谁先到零：concurrence**（`who_first_depolarizing.who_first_to_zero`）。

**相位翻转 / 比特相位翻转 p∈[0,1]：** discord 于 p=**0.45** 首次到零，concurrence 与 \|N_sk\| 于 p=**0.5**；**谁先到零：discord**。p>0.5 因与纯翻转态对称而回升，照写。

文献实验数（约 1.981、89%、纯度 0.34/0.25、混合 0.5）只进对照列，**不进**结果表。

---

## 1. 问题与边界

先验（Zhao *Nat. Phys.* 2026）给出「拓扑数是否可比纠缠指标更晚垮」的实验语境。本稿问题收窄为：

1. 在自定横截面斯托克斯纹理上，斯格明子数是否可算为纹理积分；
2. 近各向同性退极化、相位翻转、比特相位翻转下，\|N_sk\|、concurrence、discord、保真度、纯度如何随 ξ 或 p 变化；
3. 谁先到零——落在本扫网格则报 `cross_x`，否则写「本扫范围内未到零」。

不做：声称观测、抄 Zhao 器件数进结果、芯片制备、态转移优势、与 Floquet 轨并篇、量子硬件、第三方 PDF 入库。

---

## 2. 方法

### 2.1 两光子纯态与空间纹理（假设）

希尔伯特空间：A = 圆偏振 \(\{\lvert L\rangle,\lvert R\rangle\}\)，B = 伴侣路径/偏振 \(\{\lvert0\rangle,\lvert1\rangle\}\)。初态

\[
\lvert\Psi\rangle=\frac{1}{\sqrt{2}}\big(\lvert L\rangle_A\lvert0\rangle_B+\lvert R\rangle_A\lvert1\rangle_B\big)
\]

（`protocol.state`）。空间包络（假设，非器件模式）：\(u_L=\mathrm{LG}_{0,0}\)，\(u_R=\mathrm{LG}_{0,\ell}\) 且 ℓ=**1**、腰斑 w=**1**；笛卡尔格 97×97、半宽 4w（`protocol.spatial`）。

### 2.2 斯格明子数 = 纹理积分

将 B 投影到 \(\lvert+\rangle=(\lvert0\rangle+\lvert1\rangle)/\sqrt{2}\)，得 A 上条件 2×2 偏振密度矩阵（`protocol.conditional_projection`）。与 \(u_L,u_R\) 合成局域斯托克斯 \(S_{0,1,2,3}\)，单位化 \(n=S/|S|\)，

\[
N_\mathrm{sk}=\frac{1}{4\pi}\iint n\cdot(\partial_x n\times\partial_y n)\,dx\,dy
\]

（`protocol.skyrmion_definition`）。**禁止**用 4×4 密度矩阵本征值冒充。干净极限 \|N_sk\|≈0.953，偏离整数 1 来自有限窗口离散差分，已注明。

### 2.3 纠缠量

- **Concurrence：** Wootters 两比特公式（`protocol.concurrence`）。
- **Discord：** \(D(A\mid B)=I(A\!:\!B)-\max_{\Pi_B}J\)；B 上 Bloch 角投影测量数值优化（`protocol.discord`）。
- **保真度** \(F=\langle\Psi\rvert\rho\lvert\Psi\rangle\)；**纯度** \(\mathrm{Tr}(\rho^2)\)。

### 2.4 三类信道（均可写）

1. **近各向同性退极化：** \(\rho'=(1-\xi)\rho+(\xi/4)I_4\)，ξ∈[0,1]×21。
2. **相位翻转：** \(\rho'=(1-p)\rho+p\,(Z\otimes I)\rho(Z\otimes I)\)，p∈[0,1]×21；Z 作用在 A。
3. **比特相位翻转：** 同上，以 \(Y\otimes I\) 替换。

过零：\|metric\|≤**0.02**（`zero_threshold_abs`）取扫线首次点。

种子：`seeds.master=20261014` 等，见 STATUS。

---

## 3. 结果

### 3.1 干净极限（Fig.clean_texture）

| 量 | 值 | 键 |
|---|---:|---|
| skyrmion_number | 0.953 | `clean_limit.skyrmion_number` |
| concurrence | 1.000 | `clean_limit.concurrence` |
| discord | 1.000 | `clean_limit.discord` |
| fidelity / purity | 1 / 1 | `fidelity` / `purity` |

条件斯托克斯横截面见图 `fig/fig_clean_texture`。**不**声称实验观测。

### 3.2 退极化预算（Fig.depolarizing）

- concurrence：ξ=**0.7** 首次到零（`headline.vanish_depolarizing.concurrence.cross_x`）。
- discord：ξ=**0.9**（`vanish_depolarizing.discord.cross_x`）。
- \|N_sk\|：ξ=**1.0**（`vanish_depolarizing.skyrmion.cross_x`）；在 concurrence 已为零的区间内 \|N_sk\| 仍保持 O(1)，直至全退极化。
- **谁先到零：concurrence**（`who_first_depolarizing`）。

阈值均来自本扫网格，不外推。

### 3.3 相位翻转预算（Fig.phase_flip）

- discord：p=**0.45** 首次到零；concurrence 与 \|N_sk\|：p=**0.5**。
- **谁先到零：discord**（`who_first_phase_flip`）。
- p↔(1−p) 对称：p>0.5 各量回升（p=1 回到纯 \(Z\otimes I\lvert\Psi\rangle\)），属本信道结构，负结果照写。

### 3.4 比特相位翻转预算（Fig.bit_phase_flip）

本模型下与相位翻转同结构的过零点（`vanish_bit_phase_flip` / `who_first_bit_phase_flip`）：discord@0.45，C 与 \|N_sk\|@0.5。

### 3.5 与文献对照（非结果）

Zhao 新闻/实验给出的约 1.981、89%、纯度 0.34/0.25、混合 0.5 见 `literature_contrast_only`（role=仅对照）。**不得**与上表混读。

---

## 4. 结论（限本扫）

在自定 LG 自旋–轨道纹理 + 伴侣比特（**非** Zhao 实验复现）上：退极化信道下 **concurrence 先于 discord、再先于 \|N_sk\| 到零**；相位/比特相位翻转混合下 **discord 略先，C 与 \|N_sk\| 同在 p=0.5 到零**，且 p>0.5 回升。斯格明子数始终来自纹理积分。以上为经典数值噪声预算，**不是**观测声明，也**不是**芯片或态转移优势声明。

---

## 5. 重跑

```bash
cd /workspace/skyrmion_noise && ./scripts/run_all.sh
```

`summary.json` sha256 前 16 位见 `STATUS.md` / `data/summary.sha256`。
