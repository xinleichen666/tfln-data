# Floquet SSH 边缘模在键无序与交错损耗下的噪声预算（方法·噪声预算）

**轨道：** `floquet_crit_budget/`（Bot D）  
**日期：** 2026-10-13（Asia/Shanghai）  
**数字出处：** 凡带键名的数均来自本轮 `/workspace/floquet_crit_budget/data/summary.json`（固定种子脚本重跑）。  
**模型口径：** **标准模型诊断，不是该实验的复现。**

---

## 摘要

本稿仅限课题组内部：仿真与方案工作稿，实测待做，无伪造数据，Fiber-Q 对本方向 N/A，无自有流片；不得作为公开或可引用结果；verify/ 第三方 PDF 禁止入库。

Cheng et al., *Nature* **658**, 358 (2026) 在声学超材料上报道一维 Floquet 临界拓扑相变的**实验观测**。本稿**不写观测**、不复现其实验耦合：在读不到可用实验参数的前提下，采用教科书一维两步 Floquet SSH（自设 γ₁/π=**0.25**、γ₂/π=**0.80**，`headline.gamma1_over_pi` / `gamma2_over_pi`），对开链 Floquet 算符做经典精确对角化，做**方法·噪声预算**。

**干净极限（N=60）：** 同时出现 n₀=**2** 个零能边缘模与 nπ=**2** 个 π 边缘模（`headline.clean_n_edge_0` / `clean_n_edge_pi`）；体隙 gap₀=**1.730**、gapπ=**0.176**（`clean_gap_0_bulk` / `clean_gap_pi_bulk`）；半链纠缠熵 EE=**1.194**（`clean_half_chain_ee`）。

**预算扫：** 键无序 W∈[0, 1.2]（`disorder_W_range`）下，π 签名于 W=**0.4** 首次按本轨判据消失（`vanish_disorder_pi.cross_x`），0 签名于 W=**1.2**（`vanish_disorder_0.cross_x`）。交错损耗 κ∈[0, 0.80]（`loss_kappa_range`）下，π 体隙于 κ=**0.5** 塌到 0 并判消失（`vanish_loss_pi.cross_x`）；0 签名 **本扫范围内未消失**（`vanish_loss_0.note`）。粗网格不足以定两条临界边界交点 → **不报**多临界可加对数（`multicritical_additive_log.reported=false`）。

---

## 1. 问题与边界

先验（Cheng *Nature* 2026）给出 Floquet 临界拓扑相变的实验语境。本稿问题收窄为：

1. 教科书 Floquet SSH 干净开链上，0 / π 边缘模与半链 EE 的数值诊断；
2. 键无序强度、交错损耗增大时，0 / π **体隙**与 EE 如何相对干净极限变化；
3. 签名消失阈值是否落在本扫网格内——落则报 `cross_x`，否则写「本扫范围内未消失」，不做外推。

不做：声称观测、编造 Nature 耦合、推荐器件长度、量子硬件、第三方 PDF 入库。

---

## 2. 方法

### 2.1 两步 Floquet SSH（假设）

开链 N=**60** 格点。半周期哈密顿只含奇键（强度 γ₁）或偶键（强度 γ₂）：

\[
U = e^{-i H_\mathrm{even}}\, e^{-i H_\mathrm{odd}},
\]

准能 ε 由 \(U|\psi\rangle=e^{-i\varepsilon}|\psi\rangle\) 取辐角，ε∈(−π,π]。参数 γ₁=0.25π、γ₂=0.80π 为**本轨假设**（异常 Floquet 区），使干净极限同时出现 0 与 π 边缘模；**不是** Cheng 实验耦合（`protocol.model_note`）。

### 2.2 边缘模与体隙

- 端区 4 格概率权重 ≥0.45 → 记为边缘模（`protocol.edge_weight_thr`）。
- 落在 \|ε\|≤0.40 窗且更靠近 0 → 0 模；更靠近 ±π → π 模。
- **体隙** gap₀ / gapπ：全体非边缘模到 0 / ±π\| 的最小距离。边缘模本身贴近 0 或 π，不进入体隙最小元。
- 签名存在：至少 1 个对应边缘模且体隙 ≥0.05（`gap_present_thr`）。
- 签名消失：签名判据不再成立，或体隙 \<0.02（`gap_vanish_thr`），取扫线上**首次**满足点为 `cross_x`。

### 2.3 半链纠缠熵

占据准能 ε≤0 的单粒子模；对右本征矢做 QR 正交化后构造相关矩阵，取半链约化谱熵（`protocol.ee_occupation`）。损耗下 U 非幺正，此为右矢近似。

### 2.4 两类预算扫

1. **键无序（Hermitian）：** \(J\to J(1+W\xi)\)，ξ~U[−1,1]，截断 ≥0.05；W 网格见 `protocol.disorder_W_grid`；每点 8 个无序实现，种子 `seeds.disorder_sweep=301`；报均值±标准差。
2. **交错损耗（非厄米）：** 仅在偶格点加 on-site −iκ（两半周期皆加）。**不用**均匀 −iκ I——后者只把 \|λ\| 整体缩放，不改变本征矢与准能角，无法作为拓扑签名预算通道（`protocol.loss_rule`）。

### 2.5 多临界

对 (γ₁,γ₂) 做 11×11 粗网格近零隙探测（`phase_diag_probe`）。**不足以**定出两条临界边界交点 → `multicritical_located=false`，**不报**可加对数。

种子总表：`seeds.master=20261013` 等，见 STATUS。

---

## 3. 结果

### 3.1 干净极限（Fig.clean_spectrum）

| 量 | 值 | 键 |
|---|---:|---|
| n_edge_0 / n_edge_π | 2 / 2 | `headline.clean_n_edge_0` / `clean_n_edge_pi` |
| gap_0_bulk | 1.730 | `clean_gap_0_bulk` |
| gap_π_bulk | 0.176 | `clean_gap_pi_bulk` |
| half_chain_ee | 1.194 | `clean_half_chain_ee` |
| sig_0 / sig_π | true / true | `clean_sig_0_present` / `clean_sig_pi_present` |

准能谱上可见 \|ε\|≈0 与 \|ε\|≈π 的高局域权重模（红点，见 `fig/fig_clean_spectrum`）。**不**声称实验观测。

### 3.2 键无序预算（Fig.disorder_gap / Fig.disorder_ee）

- π 签名：于 W=**0.4** 首次按判据消失（`headline.vanish_disorder_pi.cross_x`）；该点 mean gapπ=**0.0235**（`disorder_sweep` 对应行 `gap_pi_bulk_mean`），sig_π 实现分数降至 0.12。
- 0 签名：于 W=**1.2** 消失（`vanish_disorder_0.cross_x`）；mean gap₀=**0.0389**，sig₀ 分数 0.38\<0.5。
- 半链 EE：干净 1.194 → W=1.2 时均值 **0.804**（`half_chain_ee_mean`），相对干净 Δ=**−0.390**（`half_chain_ee_delta_vs_clean`）。

阈值均来自本扫网格，不外推网格外。

### 3.3 交错损耗预算（Fig.loss_gap / Fig.loss_ee）

- π 体隙随 κ 下降，于 κ=**0.5** 塌为 **0**，签名判为消失（`vanish_loss_pi.cross_x`；`loss_sweep` 该行 `gap_pi_bulk=0`，`sig_pi_present=false`）。
- 0 体隙在 κ≤0.80 内始终 ≳1.70，边缘模计数保持 2，签名 **本扫范围内未消失**（`vanish_loss_0.note`）。
- EE：κ=0.05 即相对干净明显下降（非厄米占据近似敏感），随后随 κ 非单调变化；κ=0.5 时 EE=**0.814**（`loss_sweep`）。

### 3.4 多临界 / 可加对数

`phase_diag_probe.multicritical_located=false`；`headline.multicritical_additive_log.reported=false`。正文**不报**可加对数项。

---

## 4. 结论（限本扫）

在教科书两步 Floquet SSH（**非** Cheng 实验复现）上，干净极限可同时诊断 0 / π 边缘模与半链 EE。键无序下 π 签名先于 0 签名消失（W=0.4 vs 1.2）；交错损耗下 π 体隙在 κ=0.5 关闭，而 0 签名在本 κ 网格内未消失。以上为经典数值噪声预算，**不是**观测声明，也**不是**器件长度推荐。

---

## 5. 重跑

```bash
cd /workspace/floquet_crit_budget && ./scripts/run_all.sh
```

`summary.json` sha256 前 16 位见 `STATUS.md` / `data/summary.sha256`。
