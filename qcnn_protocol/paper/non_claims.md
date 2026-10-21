# 非声明 / 本轮未做

**本稿仅限课题组内部：仿真与方案工作稿，实测待做，无伪造数据，Fiber-Q 对本方向 N/A，无自有流片；不得作为公开或可引用结果；verify/ 第三方 PDF 禁止入库。**

## 明确未做
1. **无量子硬件**：未在真机、云后端或含噪声设备上跑；仅 `numpy_statevector_v1` 无噪声态矢量。
2. **无自有流片 / 器件实测**：Fiber-Q 对本方向 N/A。
3. **无 HEP / 喷注 / top-quark 数据**：未使用 Elhag 等的喷注图像，未声称高能物理分类结果。
4. **无第三方 PDF / verify/**：未入库任何 verify 目录或外部 PDF。
5. **未跑完的设置不写入「我们比较了」**：本轮实际完成的编码/损失/批大小见 `summary.json` → `meta.encodings_finished` / `losses_finished` / `batch_sizes_finished`；`*_not_run` 为空表示没有额外宣称的未跑项。
6. **未安装 PennyLane / Qiskit / PyTorch**：经典对照为 numpy MLP；不声称与某商业/框架默认 QCNN 模板逐门等价。
7. **DEA 为本轨敏感性代理**：按参数对 ⟨Z⟩ 的探针方差剪枝（保留约 60%），不是对 Elhag 原文 DEA 算法的逐行复现。
8. **不声称量子加速或可引用器件 SOTA**。

## 负结果保留
全参数对照 8/8 跑次 CNN 测试准确率高于 QCNN（`aggregate.n_cnn_wins_full=8`）。**不**为此改种子或重挑成功跑次。
