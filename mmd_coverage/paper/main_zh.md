# Pauli-Z 矩匹配损失下的未见有效覆盖预算（方法·噪声预算）

**轨道：** `mmd_coverage/`（Bot C）  
**日期：** 2026-10-13（Asia/Shanghai）  
**数字出处：** 凡带键名的数均来自本轮 `/workspace/mmd_coverage/data/summary.json`（固定种子脚本重跑）。

---

## 摘要

本稿仅限课题组内部：仿真与方案工作稿，实测待做，无伪造数据，Fiber-Q 对本方向 N/A，无自有流片；不得作为公开或可引用结果；verify/ 第三方 PDF 禁止入库。仓写完后再改 private。

在基数约束比特串空间上（N=**10**，有效串 ⇔ Hamming 重量=**5**，\|V\|=**252**；键 `headline.N` / `k_weight` / `n_valid`），我们构造已知目标分布 p\*，从中抽样训练集，并用**同一类** Pauli-Z 二阶矩 MMD² 损失训练两个生成模型：**ProductValid**（独立比特）与 **PairIsingValid**（成对 Ising）。先验 Raj, Mathur, Perdomo-Ortiz, arXiv:2608.31117 指出矩匹配损失收敛时未见有效覆盖仍可分叉——本稿**不抄**其 30-qubit / 基因组表内数字，**不新证**硬件必不可少，N 取态矢量可全枚举。

在匹配损失水平 L\*=**0.177510**（`headline.L_star_matched_loss`）处：ProductValid MMD²=**0.177510**、未见有效覆盖=**0.2802**；PairIsingValid MMD²=**0.173894**、未见有效覆盖=**0.3922**（`headline.model_*_matched_*`）。相对损失差 **0.021**≤0.25，未见覆盖差 \|Δ\|=**0.1121**≥0.05 → 判决 **损失接近但覆盖分开**（`headline.verdict_zh` / `loss_coverage_separated=true`）。前向 KL(p\*∥q) 在匹配处分别为 **0.0778** / **0.0945**（`headline.model_*_matched_forward_kl`）——本轮中覆盖更高者 KL 略大，说明「损失 / 覆盖 / KL」三者不必同向，负向对照照写。

---

## 1. 问题与边界

Raj 等（arXiv:2608.31117）强调：同一矩匹配损失可对应差很多的未见有效样本覆盖率；覆盖与前向 KL 往往比训练损失更能反映泛化。本稿在**可全枚举**的 N=10 上复现「损失–覆盖」对照图，目标分布由本脚本自构（故 KL 可精确算）。

不做：30 量子比特、基因组数据、量子硬件、把 Raj 覆盖率（如文献中的分叉示例）写入本轮结果表、证明「硬件必不可少」。

---

## 2. 方法

### 2.1 有效串与目标分布

- 空间 \(\{0,1\}^{10}\)；**有效** \(V=\{x:\mathrm{wt}(x)=5\}\)，\|V\|=252（`protocol.n_valid`）。
- 目标：在 V 上 \(p^*(x)\propto\exp(\beta\, w\cdot x)\)，β=**1.8**（`protocol.beta_target`）；权重向量 w 由种子 `seeds.target=301` 生成（`target.weight_vector`）。
- 训练：从 p\* 有放回抽 **48** 次（`headline.n_train_draws`）→ 唯一串 **20**；未见有效 **232**（`headline.n_train_unique` / `n_unseen_valid`）。
- 经验分布 emp 的 Pauli-Z 特征均值 μ_train 作为 MMD 靶。

### 2.2 损失与两模型（全经典）

特征 φ(x)：单比特 \(Z_i=1-2x_i\) 与成对 \(Z_i Z_j\)（阶 ≤2）。  
损失：\(L(q)=\|\mu_q-\mu_{\mathrm{train}}\|^2\)（`protocol.loss`）。

| 模型 | 参数 | 支撑 |
|---|---|---|
| ProductValid | 独立 logit θ∈R^{10} | q∝∏ Bernoulli，在 V 上归一 |
| PairIsingValid | 场 h∈R^{10} + 成对 J（45 维） | q∝exp(−E_Ising)，在 V 上归一 |

二者用同一 MMD²；在有限 V 上用解析梯度更新 **120** 步（`protocol.n_steps`），每 5 步记录损失与覆盖。

### 2.3 覆盖、KL 与「相近损失」

- 每个检查点从 q **直接采样** n=**2000**（`headline.n_sample_eval`）：  
  训练覆盖 = \|命中 ∩ 训练唯一集\| / \|训练唯一集\|；  
  未见有效覆盖 = \|命中 ∩ (V∖训练)\|\ / \|V∖训练\|。
- 前向 KL(p\*∥q) 在 V 上精确求和。
- **匹配损失：** L\* = max(两模型终态 MMD²)；各取**首次** loss≤L\* 的检查点再比覆盖（`protocol.matched_loss_rule`）。相对差 ≤0.25 视为接近；\|Δ未见覆盖\|≥0.05 视为分开；否则写「本设置未分开」。

种子：`seeds.master=20261013`，其余见 `seeds.*`。

---

## 3. 结果

### 3.1 损失–未见覆盖曲线（Fig.loss_unseen）

横轴训练 MMD²、纵轴未见有效覆盖（跳过 step=0 的初始巨损以便读图；原始点仍在 `models[*].history`）。两曲线在中等损失区即分离：同级损失下 PairIsingValid 的未见覆盖系统性高于 ProductValid。黑圈标匹配损失快照；灰竖线为 L\*。

### 3.2 匹配损失处的覆盖与 KL（Fig.matched_coverage / Fig.kl）

| 模型 | step | MMD² | 训练覆盖 | 未见有效覆盖 | KL(p\*∥q) |
|---|---:|---:|---:|---:|---:|
| ProductValid | 120 | 0.177510 | 0.85 | 0.2802 | 0.0778 |
| PairIsingValid | 20 | 0.173894 | 0.95 | 0.3922 | 0.0945 |

键：`separation.matched_snapshots[*]` 与 `headline.model_*_matched_*`。  
相对损失差 **0.0206**（`headline.rel_loss_diff_matched`）；未见覆盖差 **0.1121**（`headline.abs_unseen_coverage_gap_matched`）。

**判决：** `headline.verdict_zh` = **损失接近但覆盖分开**（`loss_coverage_separated=true`）。

### 3.3 终态（续训参考，非匹配主结论）

| 模型 | 终态 MMD² | 终态未见覆盖 | 终态 KL |
|---|---:|---:|---:|
| ProductValid | 0.177510 | 0.2802 | 0.0778 |
| PairIsingValid | 0.121111 | 0.4052 | 0.0864 |

键：`headline.model_*_final_*`。PairIsingValid 续训可把损失压得更低；主比较仍以 L\* 匹配快照为准，避免「不同损失量级」混谈覆盖。

### 3.4 解读（限本扫）

- 同属 Pauli-Z 矩 MMD²，容量更大的 PairIsingValid 在相近损失下给出更高未见有效覆盖（+0.11）。
- 本轮匹配处 ProductValid 的前向 KL 反而略低——**覆盖分叉与 KL 排序不必一致**；不把「覆盖更高」自动写成「更接近 p\*」。
- 未使用 Raj 文中的具体覆盖率数字；未外推到 N≫10 或硬件。

---

## 4. 结论

在自构基数约束任务上，两个同损失类经典生成模型在 **L\*\≈0.18** 的相近 MMD² 下，未见有效覆盖分别为 **0.280** 与 **0.392**，满足本轮「损失接近但覆盖分开」判据。标题与主张保持**方法·噪声预算**：训练损失不足以单独担保未见有效覆盖；不声称量子优势或硬件必要。

重跑：`./scripts/run_all.sh`；本轮 `headline.rerun_sha16` 见 `summary.json`。
