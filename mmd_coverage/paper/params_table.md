# 参数表 · mmd_coverage

分列：**文献**（仅对照引用） / **本轮计算**（脚本产出） / **假设**（构造选择）。

| 项 | 文献 | 本轮计算 | 假设 |
|---|---|---|---|
| 先验 | Raj, Mathur, Perdomo-Ortiz, arXiv:2608.31117：同一 MMD²/Pauli-Z 矩匹配损失可对应差很多的未见有效覆盖；覆盖与前向 KL 更一致 | 不抄其 30-qubit/基因组覆盖率；不新证硬件必要 | — |
| 比特串空间 | 基数约束思想来自先验叙事 | N=10；有效 \(V=\{\mathrm{wt}=5\}\)，\|V\|=252（`headline.n_valid`） | 有效定义写死为重量恰为 5 |
| 目标分布 p* | — | 在 V 上 \(p^*\propto\exp(\beta w\cdot x)\)，β=1.8；w 由种子 `target=301` 生成（`target.weight_vector`） | 自构目标，故前向 KL 可算 |
| 训练数据 | — | 从 p* 有放回抽 48 次 → 唯一串 20；未见有效 232（`headline.n_train_*`） | 经验矩作 MMD 靶 |
| 特征 / 损失 | Pauli-Z 矩 / MMD² 思想 | φ = {Z_i}∪{Z_i Z_j}，Z=1−2x；L=\|\|μ_q−μ_train\|\|² | 矩阶 ≤2；未用更高阶 |
| 模型 A | — | **ProductValid**：独立比特 logit，q=softmax(−E) 限在 V；参数维 10 | 同损失类 |
| 模型 B | — | **PairIsingValid**：成对 Ising 能量限在 V；参数维 10+45 | 同损失类 |
| 优化 | — | 解析梯度（有限 V 上精确期望）；Product lr=0.35，Ising lr=0.08；120 步；每 5 步检查点 | 未做 lr 大搜 |
| 匹配损失 | 「损失收到同一量级」 | L\*=max(终态损失)；各取首次 loss≤L\* 的检查点（`separation.matched_snapshots`） | 相对差 ≤0.25 视为接近 |
| 覆盖 / KL | 直接采样思想 | n_sample_eval=2000；训练覆盖、未见有效覆盖；KL(p\*∥q) | 覆盖=命中集合比例 |
| 分叉判据 | — | 损失接近且 \|Δ未见覆盖\|≥0.05 → 分开；否则「本设置未分开」 | 阈值写死于脚本 |
| 种子 | — | master=20261013；target/train/product/ising/eval = 301–305 | 写死于 `SEEDS` |
| 硬件 | — | 本机经典 CPU；全枚举 V | 无量子硬件 |
