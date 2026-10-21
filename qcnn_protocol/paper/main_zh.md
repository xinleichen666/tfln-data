# 无噪声模拟器上 QCNN 与参数量对齐经典模型的协议对照（内部工作稿）

**本稿仅限课题组内部：仿真与方案工作稿，实测待做，无伪造数据，Fiber-Q 对本方向 N/A，无自有流片；不得作为公开或可引用结果；verify/ 第三方 PDF 禁止入库。**

## 摘要
本文在无噪声态矢量模拟器上，对浅层量子卷积网络（QCNN）与**参数量对齐**的经典前馈网络做协议级对照，并做基于参数敏感性的门参剪枝前后比较。数据为本地生成的 4×4「横条 / 对角」二分类图像，**不是**高能物理喷注任务。本轮实际跑完的设置为：编码 `{angle4, amplitude}` × 损失 `{mse, bce}` × 批大小 `{16, 32}`（共 8 组）。全参数对照下，测试集上 QCNN 相对 CNN 的平均准确率差为 **−0.3385**（`aggregate.mean_delta_test_qcnn_minus_cnn_full`），8/8 组 CNN 更高（`aggregate.n_cnn_wins_full`）。标题取「协议对照」，**不**写成量子胜过经典。方法框架参考 Elhag et al., arXiv:2408.08701（见 `prior_bib.md`），**不**复用其喷注准确率数字。

## 1. 动机与边界
Elhag 等给出无噪声模拟器上 QCNN 对结构对应 CNN、并用维数表达分析删冗余参数的协议；其喷注标记实验已完成，本轨**换小规模本地图**，只报实际跑完的编码/损失/批大小（`prior_bib.md` 引用边界）。本轨禁止：观测/实测声称、量子加速、自有流片、把文献表内准确率抄进结果表。

## 2. 数据与协议
- **数据**：`scripts/run_protocol.py` 固定种子 `meta.seeds.data=2408` 生成；训练 96、测试 48（`meta.n_train` / `meta.n_test`）；类别近平衡（`class_balance`）。样例见图 `fig/fig1_examples`。
- **编码**：`angle4`（2×2 均值池化后 4 路 RY）；`amplitude`（16 维振幅编码）。
- **QCNN**：4 qubit，15 可训角参（`qcnn_architecture.n_params_full`），CNOT 连接的 conv–pool 风格线路；读出 qubit 0 的 ⟨Z⟩。
- **经典对照**：`16→h→1` 的 tanh-MLP，选 h 使参数量接近 QCNN（全参时 h=1 → 18 参，见各行 `cnn_n_params_full`）。
- **训练**：SPSA（`meta.optimizer`），20 epoch（`meta.epochs`）；模拟器名 `numpy_statevector_v1`。
- **剪枝**：对训练探针集估计 ∂⟨Z⟩/∂θⱼ 方差，保留约 60% 高敏感参数后重训（`prune_table`）。

## 3. 结果（数字均指 summary.json）

### 3.1 全参数对照
测试准确率见表（详 `params_table.md` §B / `comparison_table`）：
- `angle4` 下 QCNN 测试约 **0.77–0.79**；CNN 均为 **1.00**。
- `amplitude` 下 QCNN 测试约 **0.52–0.56**；CNN 均为 **1.00**。
- 平均 Δ（QCNN−CNN）= **−0.3385** → `aggregate.verdict` = `cnn_better_on_average`。
图：`fig/fig2_acc_full`，`fig/fig3_delta`。

### 3.2 剪枝
全 8 组由 15 → 9 参（`prune_table.n_after`）。`angle4` 剪后测试维持约 0.79；`amplitude` 部分组剪后略升（最大 `amplitude_bce_bs32`：0.5625→0.6667，键 `prune_table` 对应该 `run_id` 的 `test_acc_change`）。图：`fig/fig4_prune`。

### 3.3 低参数区
剪枝后 QCNN（9 参）对匹配 CNN：8/8 `low_param_regime.winner=cnn`（CNN 测试仍为 1.00）。图：`fig/fig5_low_param`。

### 3.4 训练曲线例
`fig/fig6_train_curve` 对应 histories 首条 `run_id`（`angle4_mse_bs16`）。

## 4. 讨论（不外推）
在本合成几何任务上，参数量对齐的经典 MLP 稳定达到测试 1.00，而浅层无噪声 QCNN 未超过对照。这与「协议对照、允许负结果」的交件要求一致：**不**改种子追平，**不**把 Elhag 喷注结论迁移为本轨标题。`amplitude` 弱于 `angle4`，可能与 4×4 图案经振幅编码后的可分性及 SPSA 训练预算有关；机制不在本轮证明范围内。

## 5. 可重现
```bash
bash /workspace/qcnn_protocol/scripts/regenerate.sh
```
种子见 `meta.seeds`。正文凡数字均可回溯至 `data/summary.json` 键名（见 `params_table.md`）。

## 参考文献（框架）
Elhag et al., arXiv:2408.08701；BibTeX 见 `../prior_bib.md`。正式刊页码/DOI 以出版社为准，本内部稿不写未核页码。
