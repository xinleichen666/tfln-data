# 方向一：薄膜铌酸锂仿真与文稿草稿

**预印本口径（2026-10-12 · V1）：** 本稿仅限**课题组内部**：仿真与方案工作稿，实测待做，**无伪造数据**，Fiber-Q **未下单**，**无流片**；**不得作为公开或可引用结果**；`verify/` 第三方 PDF **禁止入库**。

Internal group use only: simulation and scheme draft; measurements pending; no fabricated data; Fiber-Q not ordered; no fab. Not for public citation. Third-party PDFs under verify/ must not enter the repo.

本仓库是方向一的仿真与设计文稿草稿，不是已经完成的器件设计。

当前作为主要结果给出的数字，把 TM 泵浦的厚度灵敏度与 TE 泵浦的群速度和极化周期混在一起，不得作为器件结果引用。

第三方论文 PDF 是有意未放入本仓库的。

## 后来放入的仿真目录

下面这些目录是仿真记录和文稿草稿。第三方论文 PDF 仍然没有放入。

- `dir11/`：声光方向的根目录文件，包括脚本、数据、图和这一层自己的文稿草稿。这些文件不在 `paperB/` 或 `paperC/` 里面。
- `dir11/idt_3d_sus/`：悬空三维叉指 COMSOL 本征模场 CSV（含孔径几何与 z 向剖面）。`.mph` 仍在本地 `D:\comsol_ao_run\idt_3d_sus\`。
- `dir11/photoelastic_p283/`：悬空二维叉指 **p=2.8326 µm** 光弹与 **x 向光窗口** 扫窗 CSV。`.mph` 在本地 `D:\comsol_ao_run\photoelastic\`。
- `dir11/paperB/`：论文 B 的脚本、数据、`fig/`、`fig1/` 和文稿草稿。
- `dir11/paperC/`：论文 C 的存档。这是一份否定结果，不是准备投稿的论文。
- `dir13/`：方向 13 的仿真记录。
- `dir15/`：方向 15 的仿真记录。
- `tfln_sim/`：另一些薄膜铌酸锂仿真记录。
- `dir2/`：方向二工作稿（声学马赫–曾德尔 + 热声相位 + 单波导光弹重叠 + 联合误差传递）。`dir2/fig/` 是脚本出图目录；`dir2/paper/fig/` 是文稿用图。
- `dir1_metrology/paper/`：方向一方法工作稿（膜厚计量间距 → SPDC 预告纯度上界）。出图脚本在 `dir1_metrology/scripts/`。
- `tfln_review/ao_shared_params_v1.md`：声光方向一/二共用参数表。
- `tfln_review/user_materials/2026-10-12/bib_pagecheck_2026-10-12.md`：2026-10-12 文献页码核对记录。

论文 B，以及 `dir11/`、`dir13/`、`dir15/`、`dir2/` 和 `tfln_sim/` 里的其他草稿，都是仿真记录或方案工作稿，不是已经完成的器件设计。方向二实测待做，Fiber-Q 未下单，无流片，不得作为公开或可引用结果。

## 移频噪声账本工作稿

`freq_shift_noise/paper/` 是方向一（移频噪声账本）的工作稿包；配套脚本、参数和仍待测的自测表在 `freq_shift_noise/`，共用参数表在 `tfln_review/ao_shared_params_v1.md`。

本稿仅限课题组内部：仿真与方案工作稿，实测待做，无伪造数据，Fiber-Q 未下单，无流片；不得作为公开或可引用结果；verify/ 第三方 PDF 禁止入库。仓写完后再改 private。

## 计量→纯度上界方法稿

`dir1_metrology/paper/` 是方向一（计量 → SPDC 纯度上界）的方法工作稿包；出图脚本在 `dir1_metrology/scripts/`。

本稿仅限课题组内部：仿真与方案工作稿，实测待做，无伪造数据，Fiber-Q 对本方向 N/A，无自有流片；不得作为公开或可引用结果；verify/ 第三方 PDF 禁止入库。仓写完后再改 private。

## 仿真写作六轨 A–F（内部工作稿）

`qkernel_budget/`、`qcnn_protocol/`、`mmd_coverage/`、`floquet_crit_budget/` 是 2026-10-13 已汇合的仿真与方案工作稿。`skyrmion_noise/`、`qfc_domain_budget/` 是 2026-10-14 已汇合的仿真与方案工作稿。汇合页是根目录 `sim_tracks_汇合_STATUS.md`。各轨表内数字出自该轨 `data/summary.json`。无 `verify/`，无第三方 PDF。

- `qkernel_budget/`：分块保真度核的失配 / 标签噪声预算。
- `qcnn_protocol/`：无噪声模拟器上的 QCNN–CNN 协议对照。
- `mmd_coverage/`：Pauli-Z 矩匹配损失与未见有效覆盖。
- `floquet_crit_budget/`：Floquet SSH 临界签名的无序与损耗预算。标准模型诊断，不是该实验的复现。
- `skyrmion_noise/`：自旋–轨道纹理上的经典噪声预算（纹理积分斯格明子数）。自定纹理上的预算，不是 Zhao 实验的复现。
- `qfc_domain_budget/`：标准准相位匹配的畴 / 膜厚预算。标准模型预算，不是该实验的复现。

本稿仅限课题组内部：仿真与方案工作稿，实测待做，无伪造数据，Fiber-Q 对本方向 N/A，无自有流片；不得作为公开或可引用结果；verify/ 第三方 PDF 禁止入库。仓写完后再改 private。
