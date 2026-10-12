# 方向二硬关 Gate 1 报告：热声相移效率 α（原材料 → 对标 Xu）

**结论：PASS**（与 Xu 实测同量级）

| | 数值 |
|---|---|
| α_Xu（实测） | **4.03 rad/W**（L = 100 µm，GaN-on-sapphire） |
| α_calc（名义） | **11.2 rad/W** |
| 比值 α_calc / α_Xu | **2.8**（判据：0.1–10 为同量级） |
| 不确定性带 | **4.5 – 28.1 rad/W**（扫 TCF、κ、加热器宽/缝） |
| 光波导 | **未加入** |
| 器件指标（Vπ 等） | **未写** |

---

## 1. 任务与边界

组内声学 MZI + 热调（汇报幻灯片 10–14）锚定 Xu et al. arXiv:2510.26596 的 GaN-on-sapphire PnIC。硬关要求：用**原材料 + 几何**算出热声相移效率 α，与

\[
\alpha_{\mathrm{Xu}}=4.03\,\mathrm{rad/W}\quad(L=100\,\mu\mathrm{m})
\]

比量级。对不上则停在模型标定；对上也不在本关切换 TFLN、不加光波导。

`/workspace/dir11/ao_model.py` 里的 `ALPHA_TA=4.03` 是硬编码实测值，**不算**材料计算。本关走出材料 → α 的路径。

## 2. 方法

### 2.1 相移公式

\[
\phi=\frac{\omega L}{v(T)},\qquad
\alpha=\frac{d\phi}{dP}=-\frac{\omega L}{v}\,\mathrm{TCF}\,R_{\mathrm{th}}
\]

其中 \(\mathrm{TCF}=(1/v)(dv/dT)\) 取 GaN/sapphire SAW 文献；\(R_{\mathrm{th}}=dT_{\mathrm{wg}}/dP\) 由二维截面稳态热传导得到（加热器 → 蓝宝石热沉，**有限热阻，非理想无限 R_th**）。

相速度用 Xu 的 \(v=4879\,\mathrm{m/s}\)（群速度 3904 m/s 不进入 φ）。\(f=1.5\,\mathrm{GHz}\)，\(L=100\,\mu\mathrm{m}\)。

### 2.2 材料输入（均有出处）

- **TCF**：近室温名义 **−55 ppm/K**（Lee 等 GaN/sapphire SAW 约 −50…−62 ppm/°C）；扫描 **−30**（Oota 等 TCD≈28 ppm 量级）到 **−96.5 ppm/K**（Nicoloiu et al. IEEE Access 2022，RT–500 °C 平均 |TCF|）。
- **κ_sapphire**：名义 **35 W/(m·K)**，扫描 23–46（各向异性）。
- **κ_GaN**（外延薄层）：**130 W/(m·K)**（Kyma/NCSU 一类薄模板报道）。
- **加热器几何**：Xu 正文/Fig. 2h **未给出**宽度与边距。采用 Shao et al. Phys. Rev. Applied 18, 054078 (2022) 微加热器量级：**宽 10 µm、边距 6 µm**（Shao 最小净距），并扫描 5/25 µm 与 3/10 µm。蓝宝石厚度取典型 **430 µm**（假设）。

### 2.3 二维热模型

截面：蓝宝石衬底 + 顶部 GaN 脊波导（宽 2.8 µm、厚 700 nm）；加热器落在**蓝宝石表面**（刻蚀露出衬底，不是悬空在空气上）。底面等温（吸盘），侧壁绝热。有限体积五点格式 + 稀疏直解。输出波导脊内平均温升 / 功率 = \(R_{\mathrm{th}}\)。

名义结果：\(R_{\mathrm{th}}\approx 1.06\times 10^3\,\mathrm{K/W}\)；条带解析估加热器 \(R\sim 468\,\mathrm{K/W}\)（同量级）。加热器与波导温升比 ≈ 1.1（缝不大时合理）。

### 2.4 与 Shao 的对照（按长度归一）

Shao：bulk LN 2.6 °/mW → 45.4 rad/W；LNoS 0.52 °/mW → 9.08 rad/W。加热器长度原文为 100–250 µm，**归一化时假设 200 µm**（仅对照用）。

α/L（×10⁴ rad/(W·m)）量级：Xu 测 ≈ 4.0；本计算 ≈ 11；Shao LNoS（蓝宝石热沉）≈ 4.5；Shao bulk（低 κ）≈ 23。本平台与 **LNoS / Xu** 一类同量级，高于蓝宝石热沉、低于块体 LN，物理图像一致。

### 2.5 MZI 透过率形状

用算出的 α 画 \(T=[1+\cos(\alpha P_H+\phi_0)]/2\)，与 Xu Fig. 2h 用 4.03 的曲线 qualitatively 同形（周期随 α 略快），见 `fig/gate1_mzi_thermal.*`。

## 3. 数字结果

\[
\alpha_{\mathrm{calc}}=-\frac{\omega L}{v}\cdot(-55\times 10^{-6})\cdot 1057
\approx 11.2\,\mathrm{rad/W}
\]

- 相对 Xu：**高约 2.8 倍**，仍在 **一个数量级内 → PASS**。
- 全扫描带 **4.5–28 rad/W**，覆盖 4.03；偏高主因可能是：(1) 侧壁绝热 / 有限域抬高 \(R_{\mathrm{th}}\)；(2) 导模 TCF 可能小于平面 SAW 表值；(3) 加热器几何为假设。

**若曾 FAIL，需要补的信息**：Xu 器件加热器宽度、与波导边距、金属层叠、蓝宝石片厚与背面散热条件；以及该导模近室温的直接 TCF/延迟温度系数。本关 **PASS**，上述仍是后续收紧定量（非量级）时的优先测量。

## 4. 明确声明

1. **本关未加入任何光波导，未做光弹重叠，未写 Vπ / g0 / 移频效率等器件指标。**  
2. **未切换到 TFLN / LN-on-sapphire 材料常数**（总结包规定：过关后再做第二步）。  
3. 可复现：`/workspace/dir13/venv/bin/python /workspace/dir2/gate1_thermal_acoustic.py`（需 numpy/scipy/matplotlib；shebang 已指向该环境）。

## 5. 交付文件

| 路径 | 内容 |
|---|---|
| `/workspace/dir2/gate1_thermal_acoustic.py` | 可运行脚本 |
| `/workspace/dir2/data/gate1_alpha.json` | α_calc、α_Xu、比值、PASS、输入与来源 |
| `/workspace/dir2/data/params_sources.md` | 参数表 |
| `/workspace/dir2/fig/gate1_alpha.png/.pdf` | 计算 vs Xu（及 Shao 归一化） |
| `/workspace/dir2/fig/gate1_mzi_thermal.png/.pdf` | MZI 形状 + 温度场 |
| `/workspace/dir2/gate1_report_zh.md` | 本报告 |
