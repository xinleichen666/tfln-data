# -*- coding: utf-8 -*-
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn

doc = Document()
sec = doc.sections[0]
sec.page_width = Cm(21.0)
sec.page_height = Cm(29.7)
sec.left_margin = Cm(1.8)
sec.right_margin = Cm(1.8)
sec.top_margin = Cm(1.8)
sec.bottom_margin = Cm(1.8)

def set_run(run, size=11, bold=False, color=None):
    run.font.name = "Microsoft YaHei"
    run._element.rPr.rFonts.set(qn("w:eastAsia"), "Microsoft YaHei")
    run.font.size = Pt(size)
    run.bold = bold
    if color:
        run.font.color.rgb = RGBColor(*color)

def add_p(text, size=11, bold=False, space_after=6, space_before=0):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.space_before = Pt(space_before)
    p.paragraph_format.line_spacing = 1.15
    r = p.add_run(text)
    set_run(r, size, bold)
    return p

def add_h(text, level=1):
    p = doc.add_heading(text, level=level)
    for r in p.runs:
        set_run(r, 16 if level == 1 else 13, True, (0x1F, 0x4E, 0x79))
    return p

def shade(cell, hex_color):
    tc = cell._tePr if hasattr(cell, "_tePr") else cell._tc
    tcPr = tc.get_or_add_tcPr()
    shd = tcPr.makeelement(qn("w:shd"), {
        qn("w:val"): "clear",
        qn("w:color"): "auto",
        qn("w:fill"): hex_color,
    })
    tcPr.append(shd)

def add_table(headers, rows, col_widths=None):
    t = doc.add_table(rows=1 + len(rows), cols=len(headers))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, h in enumerate(headers):
        cell = t.rows[0].cells[i]
        cell.text = ""
        p = cell.paragraphs[0]
        r = p.add_run(h)
        set_run(r, 9, True, (0xFF, 0xFF, 0xFF))
        shade(cell, "1F4E79")
    for ri, row in enumerate(rows):
        for ci, val in enumerate(row):
            cell = t.rows[ri + 1].cells[ci]
            cell.text = ""
            p = cell.paragraphs[0]
            r = p.add_run(str(val))
            set_run(r, 9, False)
            if ri % 2 == 1:
                shade(cell, "F3F6F9")
    if col_widths:
        for row in t.rows:
            for i, w in enumerate(col_widths):
                row.cells[i].width = Cm(w)
    doc.add_paragraph().paragraph_format.space_after = Pt(4)
    return t

add_p("声光双环移频器：数据汇总", 18, True, 2)
add_p("对照稿：Chen & Li，2026-10-14 预印本。求解文件：D:\\comsol_ao_run\\ao_global_ode.mph。日期：2026-10-15。", 10, False, 8)

add_h("1  文章里的数从哪来", 1)
add_p("预印本写明：下面所有器件数字都是仿真预测，测量栏是空的。这些数没有一组来自 COMSOL 的波导模式、压电本征频率、光弹或稳态热。文章的算法是式 (1) 的四阶龙格–库塔（每周期 80 步，共 40 ns，最后 20 ns 投影到 q，|q| ≤ 3），再加上电压功率换算，以及在同一方程上的参数扫描和 1000 次抽样。")
add_p("这次在 COMSOL 6.3 里实际求解的，是同一条全局常微分方程，只覆盖理想工作点（s = 0，δω/2π = 0.55 GHz）。它用来核对文章第 III 节的理想点，不代替文章里的扫描、抽样和 HOM。手册第二到第六部分（ng、双波导缝、叉指周期、光弹、加热器）这次没有算。")

add_h("2  这次 COMSOL 跑出来的数", 1)
add_p("求解设置：全局方程 12 个未知量；时间 0 到 39.9975 ns；步长 Strict，最大步长 3.75 ps；相对容差 1e-6；输出 10667 个时刻。参数与文章理想点相同：fa = 3.33 GHz，γ/2π = 0.6 GHz，κi/2π = 80.75 MHz，Δ = μ = Ω/2，δω/2π = 0.55 GHz，s = 0，αin = 1。")
add_p("末时刻的八个频谱积分（方程直接给出的量）：")
add_table(
    ["名称", "末时刻的值", "按被积函数实际对应的频率"],
    [
        ["m1r", "−7.709×10⁻¹²", "q = +1 的实部"],
        ["m1i", "1.488×10⁻⁸", "q = +1 的虚部"],
        ["c0r", "−7.009×10⁻¹⁰", "载波实部"],
        ["c0i", "−8.136×10⁻¹⁰", "载波虚部"],
        ["c1r", "1.290×10⁻⁹", "q = −1 的实部"],
        ["c1i", "1.429×10⁻¹⁰", "q = −1 的虚部"],
        ["c2r", "−2.597×10⁻¹¹", "q = −2 的实部"],
        ["c2i", "3.029×10⁻¹²", "q = −2 的虚部"],
    ],
    [3.2, 4.2, 8.5],
)
add_p("模型树里的变量 eta、dB0、dBm1、dB2 不能当结果。手册把 q = +1 写在 c1 上，写进 m1 的被积函数才是 ω+Ω；c2 积的是 q = −2。下面的比例是用最后 20 ns 的出口场重新投影得到的，q = +2 不在上面八个积分里。")
add_table(
    ["量", "这次 COMSOL", "文章理想点（式 (1)，RK4）"],
    [
        ["ηshift（进 q = +1 的比例）", "98.31%", "98.3%"],
        ["ηabs = Pshift/Pin", "55.4%", "55%"],
        ["插损", "2.49 dB", "2.5 dB"],
        ["载波，相对移频线", "−22.82 dB", "−23.2 dB"],
        ["q = −1", "−21.18 dB", "−21.2 dB"],
        ["q = +2", "−23.64 dB", "−23.6 dB"],
        ["q = −2", "−54.6 dB", "文章未单列"],
        ["q = +3", "−53.6 dB", "文章投影到 |q|≤3，未单列"],
        ["q = −3", "−58.4 dB", "同上"],
    ],
    [6.2, 4.5, 5.5],
)
add_p("各阶相对输入的功率：q = +1 为 0.5536，载波 0.00289，q = −1 为 0.00422，q = +2 为 0.00239。载波比文章高约 0.4 dB，其余落在文章给出的理想点上。6.7 µW 不在这个微分方程的输出里。")

add_h("3  文章数据按来源", 1)
add_p("式 (1) 直接积分。理想点用 s = 0；电光对照是同一光学参数、s = −1。这次 COMSOL 只重算了声光这一列。", space_before=4)
add_table(
    ["量", "声光理想点", "电光对照 s = −1", "来源"],
    [
        ["δω/2π", "0.55 GHz", "各自最优点", "式 (1) 扫描"],
        ["ηshift", "98.3%", "99.6%", "式 (1)"],
        ["ηabs", "55%", "56%", "式 (1)"],
        ["插损", "2.5 dB", "2.5 dB", "式 (1)"],
        ["载波", "−23.2 dB", "−26.0 dB", "式 (1)"],
        ["最大杂散 q = −1", "−21.2 dB", "−30.6 dB", "式 (1)"],
        ["q = +2", "−23.6 dB", "文章未单列", "式 (1)"],
    ],
    [4.0, 3.2, 4.0, 4.5],
)

add_p("由理想点再换算的源功率。式 (2) 用邵 2019 的 VπL = 0.046 V·cm，得到 21.3 GHz/V（ξ = 1）。0.55 / 21.3 = 26 mV。50 Ω 上 PRF = V²/(2R)。叉指效率和 Qm 是换算系数，不进入微分方程。", space_before=6)
add_table(
    ["驱动与馈电", "源功率", "来源"],
    [
        ["声光，邵叉指约 50%，Qm = 2000", "6.7 µW", "式 (2) + 电路"],
        ["声光，理想叉指 100%", "3.4 µW", "上值乘 0.5/ηIDT"],
        ["声光，叉指 10%", "34 µW", "同上"],
        ["ξ = 0.3 / 0.5 / 1 / 2，ηIDT = 10%，Qm = 1570", "478 / 172 / 43 / 11 µW", "功率按 1/ξ²"],
        ["电光，Vc = V0", "3.1 mW", "式 (1) 最优点 + 胡的电极电路"],
        ["电光，开路电容 Vc = 2V0", "0.77 mW", "同上"],
        ["电光，LC，QL = 30", "13 µW", "同上，带宽约 122 MHz"],
        ["电光，LC，QL = 100", "4.8 µW", "同上"],
        ["电光，理想电感", "1.2 µW", "同上"],
    ],
    [8.5, 4.2, 3.5],
)

add_p("仍是式 (1)，改一个参数再积分。这些扫描和 1000 次抽样这次没有在 COMSOL 里重跑。加热器打开、κi×2 的中位数是文章当作主要预测的那一组。种子 master 20261114，N = 1000。", space_before=6)
add_table(
    ["扫描", "文章给出的结果", "来源"],
    [
        ["Qi ≳ 1.3×10⁶", "ηshift 仍约 98%", "式 (1)，每个点重优化 δω"],
        ["Qi = 6.4×10⁵", "ηshift 降到 82%", "同上"],
        ["ηabs 随 Qi", "33% / 55% / 87%（Qi = 1.3×10⁶ / 2.4×10⁶ / 9.7×10⁶）", "同上"],
        ["高 Q 插损", "0.56 dB（Qi = 9.7×10⁶）", "同上"],
        ["这段所需源功率", "6.1–8.5 µW", "式 (1) + 式 (2)"],
        ["声频偏 0.4 / 1 / 2 / 5 MHz", "ηshift ≥96.7% / 80% / 44% / 10%", "Qm = 2000 的洛伦兹线"],
        ["可用射频带宽", "约 1 MHz（半高全宽 1.67 MHz）", "同上"],
        ["公共失谐 Δ，ηshift ≥ 95%", "−72 到 +55 MHz", "式 (1)"],
        ["两环失配 δr，≥ 95%", "−104 到 +145 MHz", "式 (1)"],
        ["裂距误差 2µ−Ω，≥ 95%", "−96 到 +53 MHz", "式 (1)"],
        ["上述窗口内插损", "2.50–2.66 dB", "式 (1)"],
        ["只算热光，|df/dT| ≈ 2.8 GHz/K", "公共漂移 ±20 mK；两环温差 ±37 mK", "频率窗口换算"],
        ["加上体膨胀，约 5.6 GHz/K", "公共 ±9.8 mK；两环 ±18.6 mK", "同上"],
        ["加热器开，κi×2", "ηshift 中位 96.4%（10%–90%：91.7%–98.3%）", "式 (1) 抽样"],
        ["同上，成品率", "94.0% 的样本 ≥90%，67.8% ≥95%", "同上"],
        ["同上，绝对效率与插损", "中位 ηabs 32.3%，片上插损 4.72 dB；光纤到光纤 16.2%", "同上"],
        ["加热器开，只用邵的 Qi", "中位插损 2.48 dB，ηabs 55.0%", "式 (1) 抽样"],
        ["加热器关（只作对照）", "中位 94.5%（82.5%–97.9%），74.2% 的样本 ≥90%", "式 (1) 抽样"],
        ["加热器功率", "中位约 22 mW；Pπ = 44.4 mW 是假定", "抽样记录"],
        ["最差杂散", "100% 的样本仍是 q = −1", "式 (1) 抽样"],
    ],
    [5.5, 7.5, 3.2],
)

add_p("HOM 用式 (1) 在工作点上取 41 个失谐，得到 q = +1 的复传递函数，再按式 (3) 求和。热声子是闭合公式，不经过时间积分。这两项这次都没有重算。", space_before=6)
add_table(
    ["量", "文章的数", "来源"],
    [
        ["滤波后 1−V，σ = 10 / 25 / 50 / 100 / 200 MHz", "8×10⁻⁷ / 3×10⁻⁵ / 6×10⁻⁴ / 1.1×10⁻² / 9×10⁻²", "式 (1) 的 H(Δ) + 式 (3)"],
        ["不滤波", "σ = 10 MHz 时 V = 0.9835；50 MHz 时 V = 0.9829；1−V ≈ 1.7×10⁻²", "残余载波和杂散"],
        ["最佳参考延迟", "1.0–1.1 ns", "式 (3)"],
        ["nth（3.33 GHz）", "300 K：1877；4 K：24.5；10 mK：1.1×10⁻⁷", "玻色分布"],
        ["Ncoh", "约 1.75×10¹¹", "Qm = 2000，γe/γ = 0.15"],
        ["nth/Ncoh", "1.1×10⁻⁸ / 1.4×10⁻¹⁰ / 7×10⁻¹⁹", "上两行相除"],
        ["C0，nth C0（300 K）", "4.27×10⁻⁹，8.0×10⁻⁶", "g0/2π = 1.1 kHz"],
    ],
    [6.5, 6.5, 3.2],
)

add_p("下面这些数写进了式 (1) 或功率公式，但不是这次积分算出来的，也不是 COMSOL 场仿真算出来的。", space_before=6)
add_table(
    ["量", "文章采用的值", "出处"],
    [
        ["γ/2π", "0.6 GHz", "按邵 2019 悬空跑道取的光学参数"],
        ["κi/2π，Qi", "80.75 MHz，约 2.4×10⁶", "邵 2019 表 S2：κ/2π = 95 MHz，2κe/κ = 0.3"],
        ["fa，Lring，覆盖长度", "3.33 GHz，0.667 mm，100 µm（覆盖 15%）", "邵 2019 悬空声谐振器"],
        ["ng", "2.3", "假定"],
        ["δω/2π 每伏", "21.3 GHz/V 定为 ξ = 1", "VπL = 0.046 V·cm 的直波导外推"],
        ["Qm", "计算用 2000；保守 1570；文献上限 3600", "2000 与 3600 来自邵 2019；1570 是假定"],
        ["ηIDT", "邵校准里约 50%；保守取 10%", "S11 约 −3 dB；10% 是保守取值"],
        ["耦合器 Pπ", "44.4 mW", "Maeder 几何假定"],
        ["加热器串扰", "Pπ 时差分 2 mK、共模 3 mK", "假定，待校准"],
        ["锁频抖动，缝误差", "5 mK rms，5 nm", "假定"],
        ["dne/dT", "3.34×10⁻⁵ /K", "文献，1523 nm"],
        ["电极电路（电光对照）", "C = 0.11 pF，L = 0.12 nH，R = 1.5 Ω，XC = 434 Ω", "胡等 2021"],
        ["电光系数", "约 0.5 GHz/V", "胡等 2021"],
        ["端面损耗", "1.5 dB/端面，用来估算光纤到光纤 16.2%", "假定优化端面耦合器"],
    ],
    [4.2, 7.0, 5.0],
)

add_p("别人器件的实测，只作对照，不属于这篇文章的方程，也不属于这次 COMSOL。", space_before=6)
add_table(
    ["器件", "文章引用的实测"],
    [
        ["胡等，电光双环", "28.2 GHz，ηshift = 98.7%，插损 0.45 dB，96 mW；另有 12.5 GHz 的 99.1% / 99.4%"],
        ["邵等 2020，行波声光", "约 3 GHz，片上绝对效率 3.5%，1 W，带宽 70 MHz"],
        ["朱等，反向布里渊", "8.54 GHz，反射率最高 24%，毫瓦级声功率；没有前向移频比"],
        ["邱等，电光 serrodyne", "移频比高于 98.8%，Vπ ≈ 2.3 V"],
    ],
    [5.0, 11.2],
)

add_h("4  和这次计算的关系", 1)
add_p("可以和这次 COMSOL 直接对比的，只有第 2 节那一行理想点：移频比、绝对效率、插损、载波、q = −1 和 q = +2。它们在文章里来自式 (1)，这次是同一方程在 COMSOL 里再积一遍。")
add_p("6.7 µW、3.4 µW、34 µW 和 ξ 的四档功率来自式 (2) 和电路换算。96.4%、4.72 dB、91.7% 来自式 (1) 的 1000 次抽样。HOM 的 8×10⁻⁷ 来自式 (1) 的传递函数。热声子数来自玻色分布和合作率公式。ng = 2.3、Pπ = 44.4 mW、2 mK / 3 mK、21.3 GHz/V 是输入假定。")
add_p("COMSOL 的波导、叉指、光弹和加热器还没有结果。那些算完之前，文章里的 ng、每伏频移和加热器温差保持为假定，不写成这次的场仿真结果。")

out = r"D:\comsol_ao_run\声光移频器-数据汇总.docx"
doc.save(out)
print(out)
