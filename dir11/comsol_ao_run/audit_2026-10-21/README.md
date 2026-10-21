# audit_2026-10-21

只读审计：不改动 `D:\comsol_ao_run` 下的模型与原始导出，不启动 COMSOL 求解。
结论与优先级见 `REPORT.md`。

## 脚本

| 文件 | 作用 |
|---|---|
| `audit_geometry.py` | 由 Java 常量重算指条/膜几何，给出金属覆盖率与无金属通道宽度 |
| `audit_photoelastic.py` | 3m 光弹张量与晶轴映射自洽性；比较"沿 x"与"沿 z"两种传播方向 |
| `audit_optical_mode.py` | 一阶等效折射率法：竖直/横向模式、FWHM、膜内功率占比、间隙外泄漏 |
| `audit_mode_cross_section.py` | 二维横向模式求解（逆迭代+LU）：铝只在指条下，带布局断言、残差/MAC/网格敏感性检查，输出损耗与插损 |
| `audit_optical_validation.py` | 最小验证：三档网格 + 边界扩展 + 复场重叠 + 图，给出 PASS/FAIL |
| `audit_metal_loss.py` | **数值已作废**（积分跨越无金属区间、间距参考点错误），仅保留过程记录 |
| `audit_response_magnitude.py` | 相位分辨诊断、光场权重敏感性、驱动量级记录、移动边界记录（均不作结论） |

## 数据来源（只读）

- `D:\comsol_ao_run\Wap_6um_mode_06_3.304066GHz.csv`
  6 μm 候选本征模导出，10 列：`x,y,z,x,y,z,eXX,eYY,eZZ,Ws`
- `D:\comsol_ao_run\idt3d_sus_mode_06_f3.302387GHz_field.csv`
  10 μm 基础模型导出，17 列：`x,y,z,x,y,z,u,v,w,Ws,eXX,eYY,eZZ,eXY,eYZ,eXZ,mises`
- `D:\comsol_ao_run\tfln_ao_preprint_package_2026-10-21\data\`
  受驱扫频、模态投影、网格追踪等既有结果

列数不一致（10 / 17）的原因：COMSOL 会在表达式之前额外输出坐标列。
脚本按列数自动选择映射，并打印校验信息。

## 输出

- `geometry_audit.csv`
- `optical_mode_audit.csv`
- `mode_cross_section_audit.csv`
- `optical_validation.csv`（本轮验证，含 overall 判定）
- `metal_loss_audit.csv`（作废）
- `response_magnitude_audit.csv`
- `figs/cross_section_and_mode.png`
- `OPTICAL_VALIDATION.md`（本轮验证记录）

## 已知局限

- 节点求和不是体积加权积分；该偏差已量化，但成因未定。
- EIM 为标量一阶方法，不能替代全矢量光模。
- κ_Al 取体材料筛选值，未做薄膜实测标定。
- Q2、Q3 的输出仅为记录，不构成结论。
