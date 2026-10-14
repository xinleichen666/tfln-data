# 分块保真度核在失配与标签噪声下的表示预算（方法·噪声预算）

**轨道：** `qkernel_budget/`（Bot A）  
**日期：** 2026-10-13（Asia/Shanghai）  
**数字出处：** 凡带键名的数均来自本轮 `/workspace/qkernel_budget/data/summary.json`（固定种子脚本重跑）。

---

## 摘要

本稿仅限课题组内部：仿真与方案工作稿，实测待做，无伪造数据，Fiber-Q 对本方向 N/A，无自有流片；不得作为公开或可引用结果；verify/ 第三方 PDF 禁止入库。仓写完后再改 private。

在自造 thin-slab 二分类数据上（近邻几何几乎不携带标签；标签由稀疏分块高阶乘积决定），我们用**经典闭式**分块保真度核（Block-Fid）对照 Linear / RBF / Laplacian / 多项式核，以及「已知真实分块乘积 → 线性」基线。先验 Peng, Lu, Chen, arXiv:2608.24631 指出该类核可经典精确求值，优势在表示而非加速——本稿**不重跑**其欺诈基准、不上量子硬件。

**对准时（平衡设定）：** 阶 3 平衡套 Block-Fid 测试准确率 **0.735**、F1 **0.741**（`headline.order3_balanced.aligned_bf_accuracy` / `…aligned_bf_f1`），相对 RBF **0.475**（`…aligned_rbf_accuracy`）差值 **+0.260**（`…gap_bf_rbf_acc_aligned`）；阶 4 平衡套 Block-Fid **0.765** / F1 **0.725**（`headline.order4_balanced.aligned_bf_*`），相对 RBF **0.470** 差值 **+0.295**（`…gap_bf_rbf_acc_aligned`）。真实乘积线性基线仍略高（阶 3：**0.760**；阶 4：**0.820**，`…aligned_tpl_accuracy`），故表示优势相对 RBF 成立，但未超过「先知块乘积」上界。

**不平衡设定（约 70% 正类）：** Block-Fid 与 RBF 测试准确率几乎贴在多数类基线（阶 3：BF **0.700** vs RBF **0.705**，`headline.order3_unbalanced.aligned_*`；阶 4：二者均为 **0.700**，`headline.order4_unbalanced.aligned_*`）——本构造下**无**相对 RBF 的准确率 lift，负结果照写。

**失配 / 翻转预算：** 见结果节与 Fig.mismatch / Fig.flip；差值穿过 ≤0 的位置标出，未穿过则写「本扫范围内未消失」，不做外推。

---

## 1. 问题与边界

Peng 等（arXiv:2608.24631）表明分块保真度核存在经典闭式，适合讨论**表示**而非运行时量子加速。本稿新问题是：

1. 分块**对准**时，该核相对 RBF 与「真实块乘积线性」基线好多少；
2. **分块边界划错**、或**训练标签按比例翻转**时，相对优势（准确率差）在何处塌到 ≤0。

不做：欺诈基准复现、IBM/硬件、态矢量全空间、流片、把文献表数字写入本轮结果。

---

## 2. 方法

### 2.1 Thin-slab 数据

- 特征维 = `order × n_blocks`：阶 3 → 12 维（4 块）；阶 4 → 12 维（3 块）。
- 坐标 ~ i.i.d. `N(0,1)`，截断到 ±2.5（假设，见 `params_table.md`）。
- 块乘积特征 `φ_b = ∏_{j∈b} tanh(x_j)`；稀疏分数 `score = φ_0 φ_1 + 0.15 φ_2`（若有第三块）。
- 平衡：按 `score` 符号切类后强制 50/50；不平衡：30% 分位阈值 → 正类比例见 `headline.*.pos_frac`（本轮均为 **0.5** 或 **0.7**）。
- 样本量：训 **400** / 测 **200**（`protocol.n_train` / `n_test`）。
- 近邻诊断（子集 300）：同色 NN 比例接近随机（阶 3 平衡 `nn_same_class_frac`=**0.543**；阶 4 平衡 **0.527**），支持「几何不告知标签」的 thin-slab 设定。

种子：`seeds.data_order3_bal=101`，`data_order3_unbal=102`，`data_order4_bal=103`，`data_order4_unbal=104`；划分 `seeds.split=777`。

### 2.2 核与模型（全经典）

- **Block-Fid（本轮定义，经典闭式）：**  
  \(K(x,y)=\prod_b \frac{1+\phi_b(x)\phi_b(y)}{2}\)。  
  复杂度随块数与样本线性，**禁止**全 Hilbert 态矢量（`protocol.no_statevector=true`）。
- **Linear / RBF / Laplacian / Poly-3：** `sklearn` 预计算核 + `SVC(C=1.0)`；RBF/Lap 的 γ 取训练集成对距离中位数启发式。
- **TrueProd-Lin：** 把真实 `{φ_b}` 喂给 `LinearSVC`——表示「已知正确分块乘积」的线性上界式基线。

### 2.3 两类失配扫

1. **错误分块：** 对特征列做循环移位 `shift∈{0,1,2,3,4,5}`，再按固定宽度切连续块；`shift=0` 即对准。注：当 `shift` 为 `order` 的整数倍时，块集合仅重排，核与对准等价（阶 3 的 `shift=3`、阶 4 的 `shift=4` 可见准确率回到对准点）。
2. **标签翻转：** 仅打乱训练集标签，翻转率 `protocol.flip_rates`；测试集保持干净。Block-Fid 分块保持对准。

差值定义：`gap = Acc(Block-Fid) − Acc(基线)`。首次 `gap≤0` 记为消失点；若扫完仍 >0，记 **「本扫范围内未消失」**（`vanish_*.note`）。

---

## 3. 结果

### 3.1 对准时的准确率 / F1（Fig.aligned）

| 套件 | BF acc | BF F1 | RBF acc | TPL acc | BF−RBF acc |
|---|---:|---:|---:|---:|---:|
| order3_balanced | 0.735 | 0.741 | 0.475 | 0.760 | +0.260 |
| order3_unbalanced | 0.700 | 0.824 | 0.705 | 0.850 | −0.005 |
| order4_balanced | 0.765 | 0.725 | 0.470 | 0.820 | +0.295 |
| order4_unbalanced | 0.700 | 0.824 | 0.700 | 0.885 | 0.000 |

键：`headline.<tag>.aligned_bf_accuracy` 等；差值 `headline.<tag>.gap_bf_rbf_acc_aligned`。

其余对准基线（键 `aligned_linear_accuracy` / `aligned_laplacian_accuracy` / `aligned_poly_accuracy`）：

- 阶 3 平衡：Linear **0.490**，Laplacian **0.495**，Poly-3 **0.540**；
- 阶 4 平衡：Linear **0.480**，Laplacian **0.530**，Poly-3 **0.475**。

解读（限本扫）：平衡 thin-slab 上，度量核（RBF/Lap）与原始线性接近随机；Block-Fid 捕捉块乘积表示后明显抬升，但仍低于 TrueProd-Lin。不平衡上准确率被多数类吸住，Block-Fid **未**相对 RBF 给出正 gap——列为负结果。

### 3.2 分块划错（Fig.mismatch）

- **相对 RBF（平衡）：** 阶 3 / 阶 4 在 `shift∈[0,5]` 内 gap 始终 >0 → `vanish_mismatch_vs_rbf.note` = **「本扫范围内未消失」**（`headline.order3_balanced.vanish_mismatch_vs_rbf` / `order4_balanced.…`）。但 `shift=1` 时阶 4 gap 已降到 **0.005**（`suites[order4_balanced].mismatch_sweep`），优势幅度实质塌缩；正式「穿过 0」判据仍未触发，故不外推消失阈值。
- **相对 TrueProd-Lin：** 对准时 gap 已 ≤0（BF 不超过先知线性）→ `vanish_mismatch_vs_tpl.vanished_in_sweep=true`，`cross_x=0`（四套皆然，见各 `headline.*.vanish_mismatch_vs_tpl`）。
- **不平衡：** 对准时相对 RBF 的 gap 已 ≤0，消失点记在 `cross_x=0`。

### 3.3 训练标签翻转（Fig.flip / Fig.flip_abs）

- **阶 3 平衡 vs RBF：** gap 在翻转率 **0.5** 首次 ≤0（`headline.order3_balanced.vanish_flip_vs_rbf.cross_x = 0.5`）。
- **阶 4 平衡 vs RBF：** 首次 ≤0 在 **0.4**（`headline.order4_balanced.vanish_flip_vs_rbf.cross_x = 0.4`）。
- **相对 TrueProd-Lin：** 对准即 ≤0（`cross_x=0.0`）。
- **不平衡：** 对准即相对 RBF gap ≤0。

翻转过程中绝对准确率见 `suites[*].flip_sweep[*].block_fidelity.accuracy` 等；随噪声增大 BF 与 RBF 一并走向 ~0.5，符合标签信息被毁的预期。

---

## 4. 结论（方法·预算口径）

1. 在本轮平衡 thin-slab 上，**对准的**块保真度核相对 RBF 给出约 **0.26–0.30** 的测试准确率差；该差是表示差异，不是量子运行时优势。
2. 相对「真实块乘积线性」基线，Block-Fid **未**取得正 gap——闭式核是乘积特征的核化近似，不是先知特征本身。
3. 分块循环移位下，相对 RBF 的 gap 在本扫网格 **未穿过 0**（写「本扫范围内未消失」），但非零移位后幅度可降到接近 0；`shift` 为块宽整数倍时因块重排而恢复。
4. 标签翻转：平衡套相对 RBF 的优势分别在翻转率 **0.5**（阶 3）与 **0.4**（阶 4）首次 ≤0。
5. 不平衡套：本构造下无相对 RBF 的准确率优势（负结果）。

---

## 5. 图件

| 文件 | 内容 |
|---|---|
| `fig/fig_aligned_acc_f1.{png,pdf}` | 对准时各模型 Accuracy / F1 |
| `fig/fig_mismatch_gap.{png,pdf}` | 划错分块时 BF−RBF / BF−TPL 准确率差 |
| `fig/fig_flip_gap.{png,pdf}` | 标签翻转时差值曲线 |
| `fig/fig_flip_abs.{png,pdf}` | 翻转下绝对准确率 |

重跑：`scripts/run_all.sh`（先清空 `data/` 再生成 `summary.json` 与图）。
