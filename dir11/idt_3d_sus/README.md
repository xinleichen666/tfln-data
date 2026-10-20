# 悬空三维叉指（idt_3d_sus）COMSOL 存档

仿真记录，不是已完成的器件设计。模型在本地 `D:\comsol_ao_run\idt_3d_sus\Idt3dSus_Model.mph`（未放入本仓库，体积过大）。

## 几何与孔径

见 `data/aperture_geometry.csv`。周期 `p = 2.58 µm` 来自二维悬空叉指竖模扫描（`data/period_source_2d_sus_p2p58.csv`）。孔径方向为 `z`：叉指占用 `z ∈ [2, 12] µm`，铌酸锂条总宽 `14 µm`。

## 数据文件

| 文件 | 说明 |
|------|------|
| `data/modes_eigen_scan.csv` | 12 支本征模：频率、应变分区、铌酸锂内位移分量占比 |
| `data/aperture_centerline_*.csv` | 孔径中线（x≈p/2，y≈膜厚中点）上 u,v,w 与应变随 z 的剖面 |
| `data/fields/idt3d_sus_mode_*_displacement_strain.csv` | 全场网格点：位移 u,v,w、应变张量分量、Mises 应力、应变能密度 |
| `scripts/ExportIdt3dSus.java` | 从 mph 导出原始场（输出到 `D:\comsol_ao_run\`） |
| `scripts/postprocess_export.py` | 整理 COMSOL 导出并生成 `data/` 下 CSV |

场 CSV 列名：`x_m,y_m,z_m,u_m,v_m,w_m,strain_energy_density_J_m3,eXX,eYY,eZZ,eXY,eYZ,eXZ,mises_N_m2`。坐标 SI 单位 m。

## 复现导出

```text
comsolcompile D:\comsol_ao_run\idt_3d_sus\ExportIdt3dSus.java
comsolbatch -inputfile D:\comsol_ao_run\idt_3d_sus\ExportIdt3dSus.class
python D:\tfln\tfln-data\dir11\idt_3d_sus\scripts\postprocess_export.py
```
