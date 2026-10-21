# dir11/comsol_ao_run：本地 COMSOL 工作目录快照（2026-10-21）

来源：`D:\comsol_ao_run`。按原目录结构放入；本地根目录的散文件放在 `_root/`。
仿真数字是模型预测，不是实测。

## 收录规则

- 收录：除 `.mph` 外的全部文件，按原文件存放，不压缩。包括脚本、日志、记录与报告、汇总表，
  以及逐节点场 CSV（孔径扫描 `_root/Wap_*_mode_*`、`convergence/` 网格追踪与受驱场、
  光学基线中间场）。单个文件最大约 40 MB。
- 不收录：
  - 全部 `.mph` 模型（留在本地，清单见 `local_only_large_files.csv`）；
  - COMSOL 编译与状态文件（`.class` `.recovery` `.status`）。
- 光学基线 `comsol_vector_optical_baseline/` 是 2026-10-21 19:16 的快照，之后仍在更新。
- 已在仓库其他位置的不重复放：`photoelastic` → `dir11/photoelastic_p283/`；
  悬空三维 10 µm 场 → `dir11/idt_3d_sus/`。

## 目录

| 目录 | 内容 |
|---|---|
| `idt_2d/` | 不悬空二维叉指，p = 0.940 µm，3.330 GHz |
| `idt_3d/` | 不悬空三维叉指，孔径 10 µm |
| `idt_2d_sus/`、`idt_2d_task/`、`archive_nonsuspended/` | 悬空二维与早期不悬空存档 |
| `idt_3d_sus/` | 悬空三维脚本，含 `aperture_sweep/` |
| `_root/` | 孔径扫描各档 `Wap_*_modes_summary.csv` 与运行日志、早期预印本复现脚本与文档 |
| `convergence/` | 6 µm 孔径网格追踪、受驱扫频、模态投影的脚本与日志 |
| `audit_2026-10-21/` | 只读审计报告与脚本 |
| `tfln_ao_preprint_package_2026-10-21/` | 预印本稿包（`main.tex`、数据、图） |
| `comsol_vector_optical_baseline/` | 全矢量光模基线（进行中，快照时间 2026-10-21 约 19:00） |
| `paper_v2/` | 设计稿 v2 |
| `qd_router_report/` | 量子点铌酸锂腔与可编程路由方案报告 |

## 已知问题

三维叉指模型（`idt_3d/`、`idt_3d_sus/` 及由其派生的 `convergence/` 模型）把位移设为一阶单元
（`order_displacement = 1`），二维模型用默认二次单元。三维与二维的频率和能量占比不是在同等精度下比较的，
`convergence/` 中频率随网格加密单调下降也与此一致。改回二次单元前，三维结果只作参考。
