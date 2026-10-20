# 悬空二维叉指 + 光弹（p = 2.8326 µm）

COMSOL 6.3 仿真记录，不是流片定稿。`.mph` 在本地 `D:\comsol_ao_run\photoelastic\Photo_Model.mph`（约 12 MB，未入库）。

## 锁定周期与声模

- **p = 2.8326 µm**，指宽 **0.7082 µm**（duty 0.25）
- 选用本征模 **f = 3.330092 GHz**，**k = 2.218169×10⁶ rad/m**
- LN **500 nm** 平板，**刻蚀深度 0**；铝 **100 nm**
- 1 V 驱动频域解 + 光弹系数（Weis & Gaylord / Andrushchak 表，见 `Photo.java` 注释）

## 坐标与晶体

| 几何 | 含义 |
|------|------|
| **x** | 周期 / 声波与环切向在单元内的方向；周期性边界 |
| **y** | 膜厚，LN y∈[0,500 nm]，铝在其上 |
| **z** | 孔径（2D 模型中不变） |

**X 切**：晶体 **x** ∥ 几何 **+y**（法线）；几何 **+x** ∥ 晶体 **−y**（传播）；晶体 **z** ∥ 孔径。与 `idt_2d` 任务书一致。

## 光窗口（后处理，非脊波导）

`sweep_rows.txt` → `data/light_window_sweep.csv`。在 **x** 上矩形窗 `(x0, x0+w)`，**y** 上整膜 + `wTE=cos²(kTE·(y−250 nm))` 权重。

**ξ 最大窗**（p=2.8326 µm）：**w=0.5 µm**，**x ∈ (2.333, 2.833) µm** → `light_window_best.csv`。

环参数用于换频移：**La = 100 µm**，**Lring = 0.667 mm**，**f_opt = 193.4 THz**（见 `Sweep.java`）。

## 数据文件

| 文件 | 内容 |
|------|------|
| `geometry_and_crystal.csv` | 结构与取向摘要 |
| `slab_analytic_500nm.csv` | 500 nm 平板 TE/TM neff、ng |
| `eigenmodes_2d_suspended.csv` | 16 支本征模摘要 |
| `drive_frequency_detuning.csv` | 5 频点 1 V 驱动 |
| `photoelastic_summary.csv` | AT_EIG / PEAK 两行结果 |
| `light_window_sweep.csv` | 全部 WIN 扫窗 |
| `light_window_best.csv` | BEST 窗 |

脚本：`scripts/Photo.java`、`Sweep.java`、`pack_from_comsol.py`。
