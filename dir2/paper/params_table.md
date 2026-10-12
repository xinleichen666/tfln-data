# 方向二 · 本文参数表（文献实测 / 本文计算分栏）

> 与 `/workspace/dir2/data/step2_summary.json`、`gate1_alpha.json`、`ao_shared_params_v1.md` 一致。  
> Ni：arXiv:2606.05337 **全文已核**。

## A. 文献实测锚定

| 量 | 数值 | 平台 / 条件 | 来源 | 栏 |
|---|---|---|---|---|
| 热声 α_Xu | **4.03 rad/W**（相移器 L=100 µm） | GaN-on-sapphire PnIC；quasi-Rayleigh ~1.5 GHz | Xu et al., arXiv:2510.26596 Fig. 2h | 文献实测 |
| Shao 热声（LNoS） | **0.52 °/mW** ≈ 9.08 rad/W | LN-on-sapphire；加热器 100–250 µm 量级 | Shao et al., Phys. Rev. Applied **18**, 054078 (2022) | 文献实测 |
| Shao 热声（bulk） | **2.6 °/mW** ≈ 45.4 rad/W | 块体 128° Y-cut LN | 同上 | 文献实测 |
| Shao AO VπL | **≈0.045 V·cm**（Vπ=4.6 V，L=100 µm） | **悬空** X-cut TFLN；声模 ~3.33 GHz；声学 Q 最高约 3600 | Shao et al., *Optica* **6**, 1498 (2019) | 文献实测 |
| Ni AO VπL | **1.004 V·cm** @ **0.842 GHz**，作用长 **400 µm** | **非悬空** X-cut **TFLN-on-Si**：360 nm LN / **4.7 µm BOX** / Si；Device 3 | Ni/Bhave/Xu, arXiv:2606.05337（全文已核） | 文献实测 |
| Shao 行波频移效率 | 片上 **3.5% @ 30 dBm** | 行波布拉格；与 VπL **分列** | Shao et al., Opt. Express **28**, 23728 (2020) | 文献实测 |
| Hu 电光转换 | ~99% | 电光双环；**效率定义不同，不与 3.5% 比胜负** | 共用参数表 / 选题简报 | 文献（旁注） |
| Zhu 声光标定 | 按共用表（线宽、耦合等） | **耦合双环 / 光子分子几何**；本文结构 **不用** 该几何 | Zhu 等；见 `ao_shared_params_v1.md` | 文献实测（几何有别） |

## B. 本文计算（Gate1 / Step2）

| 量 | 名义值 | 带 / 备注 | 栏 |
|---|---|---|---|
| α_calc（GaN，Gate1） | **11.2 rad/W**（L=100 µm） | 带 **[4.5, 28]**；与 Xu **同量级**，带覆盖 4.03；**不写复现** | 本文计算 |
| α_LNoS | **25.1 rad/W**（L_heater=200 µm） | 相对 Shao LNoS ~**2.8×**，同量级 | 本文计算 |
| α_bulk | **148 rad/W** | 相对 Shao bulk ~**3.3×**，同量级 | 本文计算 |
| VπL_calc | **0.47 V·cm**（η_IDT=10%，推挽行波） | η=50% 时 0.21；扫描带 **[0.08, 1.35]**；**不宣称超过** 0.045 或 1.004 | 本文计算 |
| dφ_err / dP_H | **4.0 rad/W** | 热光串扰为主 | 本文计算 |
| dφ_err / dP_RF | **1.8 rad/W** | RF 热份额 + 热声 | 本文计算 |
| 可分辨相位（传感定义） | **≈0.025 rad / mW** 加热器 | =\|α_LNoS\|×1 mW；**非**气体传感卡 | 本文计算 |
| 群时延（重叠段） | **≈48 ns** | L=200 µm / v≈4165 m/s | 本文计算 |

## C. 关键假设（计算输入，非实测）

| 参数 | 取值 | 说明 |
|---|---|---|
| Γ_area | 8（扫 3–20） | 非悬空声模有效面积放大 |
| Γ_ov | 0.45（扫 0.25–0.70） | 声–光重叠 |
| η_IDT | 10%（主）；50% 对照 | 电声效率 |
| ξ_H→光 / ξ_RF→热 | 0.35 / 0.05 | 热串扰份额 |
| κ_LN / TCF_LN | 4.2 W/(m·K) / −80 ppm/K | 文献中位，已扫描 |
| 光脊宽 / AO 长 | 1.5 µm / 200 µm | 单根 TE0 @1550 nm |

材料出处：弹性/压电 Ogi *JAP* 92, 2451 (2002)；光弹 p31 Andrushchak *JAP* 106, 073510 (2009)。详见 `../data/params_sources.md`。

## 台面锁定（与方向一共用）

| 量 | 数值 | 备注 | 状态 |
|---|---|---|---|
| SPDC / 仿真波长 | **~1550 nm** | wavelength selection locked; TE0 @1550 nm | 已锁 |
| AOM | G&H Fiber-Q **80 MHz** PM（`T-M080-…-F2P`）+ A35 | model locked; 780 nm path not procured | **型号已锁，实测待测** |
