# 参数表（文献 | 本轮计算 | 假设）

**本稿仅限课题组内部：仿真与方案工作稿，实测待做，无伪造数据，Fiber-Q 对本方向 N/A，无自有流片；不得作为公开或可引用结果；verify/ 第三方 PDF 禁止入库。仓写完后再改 private。**

数字三列互不串：文献列只写引用线索；「本轮计算」必须能指到 `data/summary.json` 键；假设列不写进结果主表。

## A. 运行与模型

| 项 | 文献（Elhag arXiv:2408.08701，框架） | 本轮计算（summary.json） | 假设 |
|----|--------------------------------------|--------------------------|------|
| 任务类型 | 喷注图像分类（**不复现**） | 本地 4×4 横条/对角二分类 | 标签由几何图案决定 |
| 模拟器 | 文中无噪声经典模拟器 | `meta.simulator` = `numpy_statevector_v1` | 无退相干、无读出噪声 |
| 量子比特数 | （见原文，**不抄其数**） | `meta.n_qubits` = 4 | 浅层线路可编码 |
| 图像尺寸 | （喷注图，不抄） | `meta.img_size` = 4 | 降维到可编码 |
| 训练/测试样本量 | — | `meta.n_train`=96，`meta.n_test`=48 | 平衡近 1:1，见 `class_balance` |
| 优化器 | — | `meta.optimizer` = SPSA | 每步 2 次前向 |
| 轮数 | — | `meta.epochs` = 20 | 固定，不早停改种子 |
| QCNN 全参数量 | — | `qcnn_architecture.n_params_full` = 15 | 布局见同键 `layout` |
| 经典对照 | 结构对应 CNN | 参数量匹配 tanh-MLP：`16→h→1`，`n=17h+1` | 非 2D 卷积核实现；h 由 `choose_h` 对齐 |
| 编码（已跑） | 文中扫多种（不抄其表） | `angle4`, `amplitude`（`meta.encodings_finished`） | angle4=2×2 池化后 RY；amplitude=16 维归一化振幅 |
| 损失（已跑） | 文中有扫 | `mse`, `bce` | ⟨Z⟩∈[-1,1]；bce 用 (z+1)/2 |
| 批大小（已跑） | 文中有扫 | 16, 32 | — |
| 种子 | — | data=2408, init=8701, train=2026, split=42 | 锁定后不改 |

## B. 全参数对照（测试准确率）

来源：`comparison_table[*]`。Δ = QCNN − CNN。

| run_id | QCNN 测试 | CNN 测试 | Δ | Q 参数 | C 参数 (h) |
|--------|-----------|----------|---|--------|------------|
| angle4_mse_bs16 | 0.7917 | 1.0000 | −0.2083 | 15 | 18 (h=1) |
| angle4_mse_bs32 | 0.7708 | 1.0000 | −0.2292 | 15 | 18 (h=1) |
| angle4_bce_bs16 | 0.7917 | 1.0000 | −0.2083 | 15 | 18 (h=1) |
| angle4_bce_bs32 | 0.7708 | 1.0000 | −0.2292 | 15 | 18 (h=1) |
| amplitude_mse_bs16 | 0.5208 | 1.0000 | −0.4792 | 15 | 18 (h=1) |
| amplitude_mse_bs32 | 0.5625 | 1.0000 | −0.4375 | 15 | 18 (h=1) |
| amplitude_bce_bs16 | 0.5208 | 1.0000 | −0.4792 | 15 | 18 (h=1) |
| amplitude_bce_bs32 | 0.5625 | 1.0000 | −0.4375 | 15 | 18 (h=1) |

聚合：`aggregate.mean_delta_test_qcnn_minus_cnn_full` = −0.3385；`n_cnn_wins_full`=8；`verdict`=`cnn_better_on_average`。

## C. 剪枝前后（QCNN）

来源：`prune_table`；剪枝后保留参数数一律 9（`qcnn_n_params_pruned`）。

| run_id | 剪前测试 | 剪后测试 | 变化 |
|--------|----------|----------|------|
| angle4_mse_bs16 | 0.7917 | 0.7917 | 0 |
| angle4_mse_bs32 | 0.7708 | 0.7917 | +0.0208 |
| angle4_bce_bs16 | 0.7917 | 0.7917 | 0 |
| angle4_bce_bs32 | 0.7708 | 0.7917 | +0.0208 |
| amplitude_mse_bs16 | 0.5208 | 0.5208 | 0 |
| amplitude_mse_bs32 | 0.5625 | 0.6042 | +0.0417 |
| amplitude_bce_bs16 | 0.5208 | 0.5833 | +0.0625 |
| amplitude_bce_bs32 | 0.5625 | 0.6667 | +0.1042 |

## D. 低参数区（剪枝后 vs 匹配 CNN）

来源：`low_param_regime`。本轮 8 行 `winner` 均为 `cnn`。

## E. 文献列禁抄清单
Elhag 等喷注准确率、硬件结果、正式刊页码未核前的任何「他们的数字」——**不得**出现在 B–D 表或 `summary.json` 数值字段。
