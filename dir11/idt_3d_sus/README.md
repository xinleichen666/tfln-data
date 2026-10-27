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

## 孔径长度扫描与推荐

新增 `scripts/ApertureRun.java`，在 COMSOL 6.3 中按孔径长度重建几何和网格，并求解每组 12 个本征模。保持周期 `p=2.58 µm`、起始位置 `z0=2 µm`，每个模型在指端外留 2 µm，因此 `Wstack=Wap+4 µm`。扫描长度为 4、4.5、4.75、5、5.25、5.5、6、8、10、12、14、16 µm。

沿 x 传播的 TE 光场按 `y` 向 slab TE0 权重与 `z` 向高斯光斑加权。完整结果见：

- `analysis/aperture_sweep_modes.csv`：各孔径的 12 个本征频率、应变能分区和位移分量占比。
- `analysis/aperture_sweep_overlap.csv`：TE/TM、0.5/1.0/1.5 µm FWHM 下的全孔径峰值、两端各 1 µm 内的边缘峰值、距两端至少 2 µm 的内部峰值及其比值。
- `analysis/aperture_sweep_recommendation.csv`：TE、1 µm FWHM、3.33 GHz ±50 MHz 筛选下，每个孔径的最佳内部耦合及边缘峰值。

按目标频率附近的 TE 内部耦合选 `Wap=6 µm`：第 6 模 `3.304066 GHz`，内部峰值 `39.54 1/√J`（`z0=5.5 µm`），同一模式的边缘峰值 `66.77 1/√J`（`z0=7.7 µm`），边缘/内部为 `1.69`。相较原 10 µm 孔径的目标频带内最佳模式，内部峰值提高约 16%，边缘/内部比从 `1.74` 降至 `1.69`。因此波导应放在孔径内部，避开指端。

不加目标频率限制时，5 µm 孔径第 12 模在 `3.423687 GHz` 有更大的 TE 内部峰值 `140.73 1/√J`，边缘峰值为 `110.87 1/√J`。该模比 3.33 GHz 高约 94 MHz；若后续允许把工作频率调到这一模态附近，5 µm 可作为另一候选。4 µm 的 2 µm 边缘留量之间只剩单个内部采样点，不建议用作最终设计。

在 Windows COMSOL 6.3 环境中编译并扫描孔径；原始导出写入 `D:\comsol_ao_run`：

```powershell
$comsol = "D:\COMSOL63\Multiphysics\bin\win64"
& "$comsol\comsolcompile.exe" D:\tfln\tfln-data\dir11\idt_3d_sus\scripts\ApertureRun.java
$lengths = 4, 4.5, 4.75, 5, 5.25, 5.5, 6, 8, 10, 12, 14, 16
foreach ($w in $lengths) {
  & "$comsol\comsolbatch.exe" -np 4 `
    -inputfile D:\tfln\tfln-data\dir11\idt_3d_sus\scripts\ApertureRun.class `
    -outputfile "D:\comsol_ao_run\Wap_${w}um_cli.mph" `
    -batchlog "D:\comsol_ao_run\Wap_${w}um_run.log" $w
}
python D:\tfln\tfln-data\dir11\idt_3d_sus\analysis\aperture_sweep.py `
  --exports D:\comsol_ao_run `
  --output D:\tfln\tfln-data\dir11\idt_3d_sus\analysis
```

COMSOL `.mph` 模型和原始导出场保存在本机 `D:\comsol_ao_run`，仓库只保留汇总数据。孔径扫描的耦合值以导出本征场的相位 0 实数形状计算，采用单位 LN 应变能归一化；未包含压电驱动或 COMSOL 声光耦合求解。

