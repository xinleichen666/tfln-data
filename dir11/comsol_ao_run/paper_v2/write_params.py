# -*- coding: utf-8 -*-
"""Parameter list for the TFLN acousto-optic shifter design calculation."""
from pathlib import Path
import win32com.client
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

DOCX = Path(r"D:\comsol_ao_run\paper_v2\参数说明.docx")
PDF = Path(r"D:\comsol_ao_run\paper_v2\参数说明.pdf")
PDF_DL = Path(r"C:\Users\Administrator\Downloads\声光移频器-参数说明.pdf")
NAVY = RGBColor(0x1A, 0x1A, 0x1A)


def font(run, size=10.5, bold=False, italic=False):
    run.font.name = "Times New Roman"
    run._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic
    run.font.color.rgb = NAVY


def P(doc, text, size=10.5, bold=False, italic=False, center=False, before=0, after=6):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER if center else WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.space_before = Pt(before)
    p.paragraph_format.space_after = Pt(after)
    p.paragraph_format.line_spacing = 1.08
    r = p.add_run(text)
    font(r, size, bold, italic)
    return p


def H(doc, text):
    P(doc, text, size=13, bold=True, center=False, before=12, after=4)


def shade(cell):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), "F3F3F3")
    tcPr.append(shd)


def table(doc, headers, rows, widths):
    t = doc.add_table(rows=1 + len(rows), cols=len(headers))
    t.style = "Table Grid"
    t.autofit = False
    for i, h in enumerate(headers):
        cell = t.rows[0].cells[i]
        cell.text = ""
        r = cell.paragraphs[0].add_run(h)
        font(r, 8, True)
        shade(cell)
        cell.width = Cm(widths[i])
    for ri, row in enumerate(rows):
        for ci, val in enumerate(row):
            cell = t.rows[ri + 1].cells[ci]
            cell.text = ""
            r = cell.paragraphs[0].add_run(val)
            font(r, 8, ci == 0)
            cell.width = Cm(widths[ci])
        trPr = t.rows[ri + 1]._tr.get_or_add_trPr()
        trPr.append(OxmlElement("w:cantSplit"))
    P(doc, "", size=6, after=2)


def build():
    doc = Document()
    sec = doc.sections[0]
    sec.page_width = Cm(21.0)
    sec.page_height = Cm(29.7)
    for m in ("top_margin", "bottom_margin", "left_margin", "right_margin"):
        setattr(sec, m, Cm(1.7))
    st = doc.styles["Normal"]
    st.font.name = "Times New Roman"
    st.font.size = Pt(10.5)
    st._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")

    P(doc, "声光双环移频器：计算里用到的参数", 16, True, center=True, after=2)
    P(doc, "数值从哪来，以及每一步怎么算", 12, italic=True, center=True, after=2)
    P(doc, "2026 年 10 月 16 日", 10, italic=True, center=True, after=8)
    P(doc, "下面全部是设计计算的输入和输出，不是已流片器件的测量。21.3 GHz/V、声学 Q 和 3.33 GHz 来自邵林波等人 2019 年的论文，再外推到这颗环上。叉指指间距和光弹重叠还没有算。")

    H(doc, "1  三类数")
    P(doc, "输入：写进方程之前就定死的数。有的来自已发表器件，有的是假设。")
    P(doc, "算出的结果：用这些输入做时间积分、扫描或抽样之后得到的数。理想点的移频比、边带、源功率、温度窗口、蒙特卡洛和 HOM 都属于这一类。")
    P(doc, "还没有的数：叉指周期，以及由应变和光弹系数得到的每伏频移。这两项要等工艺截面才能算，不能从现有表格里读出来。")

    H(doc, "2  写进方程的输入")
    P(doc, "光场用 Hu 等人 Nature 599, 587 (2021) 补充材料式 (S2)。只调制环 1。激光放在对称超模上，所以 Δ = μ。环 2 的调制系数 s：声光取 0，电光对照取 −1。方程在时域用四阶龙格–库塔积分，不做旋转波近似。3.33 GHz 的周期是 300 ps，每周期 80 步，步长 3.75 ps，总长 40 ns，只用最后 20 ns 做傅里叶投影，阶数取到 |q| ≤ 3。")
    table(doc,
          ["参数", "数值", "怎么定的"],
          [
              ["声频 fa", "3.33 GHz", "邵 2019 悬空声谐振器的频率。Ω = 2π fa。"],
              ["超模裂距 2μ", "等于 Ω", "设计目标：环–环耦合把两个简并共振劈开到声频。μ = Ω/2。"],
              ["总线耦合 γ/2π", "0.6 GHz", "设计选取。它决定临界耦合附近的工作点，不是测出来的。"],
              ["内禀损耗 κi/2π", "80.75 MHz", "邵 2019 表 S2：κ/2π = 95 MHz，2κe/κ = 0.3，所以 κi = 0.85×95 MHz。"],
              ["内禀 Q", "2.40×10^6", "Qi = 193.4 THz / (κi/2π)。193.4 THz 是 1550 nm 附近取的光频。"],
              ["环长 Lring", "0.667 mm", "设计值。自由光谱区 c/(ng Lring)，ng = 2.3 时约 196 GHz。"],
              ["声场覆盖长度 La", "100 μm", "与邵 2019 悬空跑道的覆盖比例相同。La/Lring = 15%。"],
              ["群折射率 ng", "2.3", "假设。还没有用这颗波导的模式算过。"],
              ["VπL", "0.046 V·cm", "邵 2019 马赫–曾德尔的测量。Vπ = 4.6 V，对应 100 μm。"],
              ["每伏频移", "21.3 GHz/V", "由下一节的式子从 VπL 外推。标定里已经含该叉指约 50% 的电声耦合。"],
              ["声学 Qm", "2000", "邵 2019 建模用的值。测到的上限是 3600。1570 没有文献来源，只作保守功率。"],
              ["声衰减分配", "γe/γ = 0.15", "邵 2019 建模用的值。γm = Ω/Qm，外耦合 γe = 0.15 γm。"],
              ["光弹标度 ξ", "1", "把 21.3 GHz/V 定义为 ξ = 1。真实截面的 ξ 还没算。功率按 1/ξ² 缩放。"],
          ],
          [3.4, 3.2, 10.6])
    P(doc, "环 1 的加载线宽是 γ + κi，折成频率是 680.75 MHz。这个数只用在后面的单声子协同系数里。")

    H(doc, "3  电压怎么变成源功率")
    P(doc, "覆盖段上的相移是 Δφ = π V La / (VπL)。V 是 50 Ω 源的峰值电压。环共振的移动是")
    P(doc, "δω = Δφ · c / (ng Lring)", center=True, after=4)
    P(doc, "代入 VπL = 0.046 V·cm、La = 100 μm、ng = 2.3、Lring = 0.667 mm，得到 δω/2π = 21.3 GHz/V。源功率")
    P(doc, "P = V² / (2×50 Ω) = V² / 100", center=True, after=4)
    P(doc, "理想点把 δω/2π 调到 0.552 GHz，所以 V = 0.552/21.3 = 26 mV，邵叉指（约 50%）下 P = 6.75 μW。理想匹配的叉指功率减半，是 3.37 μW。效率只有 ηIDT 时，功率再乘 0.5/ηIDT：10% 时是 33.7 μW。")
    P(doc, "换 Qm 时，功率再乘 2000/Qm。这是相对邵建模用的 Qm = 2000 做的缩放，不是新的测量。10% 叉指下，Qm = 3600 为 18.7 μW，Qm = 1570 为 43.0 μW。ξ 不是 1 时，功率再乘 1/ξ²。")
    P(doc, "电光对照用同一套光学参数。电容上的系数取 Hu 的 0.5 GHz/V。电极是集总电路 C = 0.11 pF、L = 0.12 nH、R = 1.5 Ω。3.33 GHz 下容抗 XC = 1/(ΩC) = 434 Ω。四种馈电：")
    table(doc,
          ["馈电", "源功率怎么算", "理想点的功率"],
          [
              ["Vc = V0", "P = Vc²/100", "3.09 mW"],
              ["开路电容，Vc = 2V0", "源电压是电容电压的一半", "0.772 mW"],
              ["LC 匹配，QL = 30", "P = Vc² (R + XC/QL) / (2 XC²)", "13.1 μW"],
              ["LC 匹配，QL = 100", "同一式", "4.78 μW"],
              ["理想电感", "P = Vc² R / (2 XC²)", "1.23 μW"],
          ],
          [4.4, 7.6, 5.2])
    P(doc, "Vc = δω / (2π×0.5 GHz/V)。电光的最佳驱动比声光小，δω/2π = 0.278 GHz。QL = 30 的匹配带宽，原稿记为约 122 MHz。")

    H(doc, "4  积分得到的理想工作点")
    P(doc, "在 γ、κi 和上面的驱动下扫描 δω，取移频比最大的点。移频比、绝对效率和插损的定义是")
    P(doc, "ηshift = P(q=+1) / Pout，   ηabs = P(q=+1) / Pin，   IL = −10 log10(Pout/Pin)", center=True, after=4)
    P(doc, "边带相对移频线，不相对输入。q = +1 是上移频 ω+Ω。")
    table(doc,
          ["量", "声光，龙格–库塔", "声光，COMSOL", "电光对照"],
          [
              ["δω/2π", "0.552 GHz", "0.55 GHz（同一输入）", "0.278 GHz"],
              ["ηshift", "98.35%", "98.31%", "99.60%"],
              ["ηabs", "55.5%", "55.4%", "56.2%"],
              ["插损", "2.49 dB", "2.49 dB", "2.48 dB"],
              ["q = −1", "−21.20 dB", "−21.18 dB", "−30.57 dB"],
              ["载波 q = 0", "−23.16 dB", "−22.82 dB", "−25.97 dB"],
              ["q = +2", "−23.56 dB", "−23.64 dB", "−32.01 dB"],
              ["源功率", "6.75 μW（邵叉指）", "同一标定", "见上表"],
          ],
          [3.2, 4.6, 4.8, 4.6])
    P(doc, "COMSOL 解的是同一组常微分方程，步长强制 3.75 ps，不是三维电磁场或声场。两套积分在论文使用的舍入下一致。插损由 κi 决定，不由驱动决定。声光的杂散边带来自只调制一个环时的共模相位；推挽电光把它消掉，所以边带更低。")
    P(doc, "内禀 Q 再优化驱动后：Qi = 9.67×10^6 时绝对效率 86.5%、插损 0.56 dB；Qi = 2.40×10^6 时移频比仍约 98%、插损 2.52 dB；Qi = 1.29×10^6 时移频比仍约 98%，但绝对效率降到 33%、插损 4.69 dB；Qi = 6.45×10^5 时移频比 81.5%、插损 7.67 dB。")

    H(doc, "5  失谐、温度和间隙")
    P(doc, "声频偏开时，驱动幅度乘上 Qm = 2000 的洛伦兹线型，半高全宽 fa/Qm = 1.665 MHz。移频比：偏 0.4 MHz 为 96.7%，1 MHz 为 79.8%，2 MHz 为 43.6%，5 MHz 为 10.0%。电光在同一窗口里保持约 99.6%。")
    P(doc, "温度窗口不是直接算热场。先在方程里扫描频率失谐，找到 ηshift ≥ 95% 的频率区间，再用 df/dT 把较窄的一侧换成温度。")
    P(doc, "df/dT = f/ng · (dn/dT + neff·α)", center=True, after=4)
    P(doc, "f = 193.4 THz，ng = 2.3。dn/dT = 3.34×10^−5 /K，取非常光的文献值。α = 1.54×10^−5 /K，是铌酸锂 a 轴的体膨胀，键合薄膜通常更小。neff = 2.14 是假设。只算热光时 df/dT = 2.81 GHz/K；加上体膨胀是 5.58 GHz/K。")
    table(doc,
          ["失谐", "ηshift≥95% 的频率窗", "只算热光", "加上体膨胀"],
          [
              ["两环一起偏，Δ", "−72.4 到 +54.7 MHz", "±19.5 mK", "±9.8 mK"],
              ["两环互差 δr", "−104 到 +145 MHz", "±36.9 mK", "±18.6 mK"],
              ["裂距误差 2μ−Ω", "−95.9 到 +52.6 MHz", "不宜换成 mK", "声频不随光频同样漂移"],
          ],
          [4.2, 5.2, 3.6, 4.2])
    P(doc, "温度取频率窗里较窄的一侧，再除以 df/dT。论文里写的锁定要求 ±9.8 mK，就是 Δ 这一行加上体膨胀之后的数。δr 可以用一个环上的加热器补偿。2μ−Ω 必须做在工艺里或用耦合器上的加热器修，不能靠整体温度。")
    P(doc, "间隙不重新解模式。假设耦合率 μ 和 γ 随间隙按 exp(−Δg / 150 nm) 变化，150 nm 是假设的倏逝衰减长度。间隙标准偏差 5 nm 时，裂距误差的标准偏差是 114 MHz，99.2% 的样本落在 ±1 MHz 的射频可调范围之外。")

    H(doc, "6  一千次抽样")
    P(doc, "脚本 realistic.py，种子 1，N = 1000。相对理想点做了这些改动，每一项都重新积分方程：")
    table(doc,
          ["改动", "取值", "性质"],
          [
              ["额外光学损耗", "κi 乘 2", "假设。邵的 Qi 已经来自带叉指的悬空器件，这项可能重复计入。"],
              ["Qi 片间起伏", "κi 再乘 0.7 到 1.3 的均匀随机数", "假设。"],
              ["间隙", "环–环、环–总线各自正态，σ = 5 nm", "假设。薄膜铌酸锂没有对应的实测分布。"],
              ["锁定残差", "5 mK，两环独立", "假设。静态失配假定已被加热器消掉。"],
              ["射频重调", "最多 ±1 MHz", "由声线宽限制，约半个 1.67 MHz。"],
              ["Qm 和叉指效率", "固定 2000 和 10%", "效率是保守假设；50% 只作对照。"],
              ["端面", "每端面 1.5 dB", "透镜光纤文献约 1.52 dB。最好的结果可以到 0.5 dB 量级。"],
          ],
          [3.6, 6.4, 7.2])
    P(doc, "端面只乘在绝对效率上：光纤到光纤 = 片上绝对效率 × 10^(−2×1.5/10)。它不改变移频比。")
    table(doc,
          ["结果", "中位数", "10%–90% 分位"],
          [
              ["ηshift", "94.3%", "82.4%–97.9%"],
              ["达到 90% 的样本", "73%", "—"],
              ["达到 95% 的样本", "44.7%", "—"],
              ["片上插损", "5.02 dB", "3.86–6.12 dB"],
              ["片上绝对效率", "28.4%", "21.5%–38.8%"],
              ["光纤到光纤", "14.2%", "10.8%–19.4%"],
              ["源功率", "33.7 μW", "这一档不随机"],
          ],
          [4.4, 4.4, 8.4])
    P(doc, "单独加大一项时：间隙 σ = 10 nm，移频比中位数降到 0.89（10% 分位 0.64）；锁定抖动 10 mK 时中位数 0.91，20 mK 时 0.80。加热器把裂距调准的那一次抽样不在这批表里，这里不用。")

    H(doc, "7  双光子干涉和热声子")
    P(doc, "先在理想点上扫描激光失谐，记下 q = +1 的复振幅，存成传递函数。光子频谱取高斯，均方根带宽 σ。可见度是这个传递函数和参考光子的重叠，参考延迟在 −20 ns 到 20 ns 里选使重叠最大的值。滤波是只保留目标频率箱；不滤波时，可见度最高就是移频比。")
    table(doc,
          ["光子均方根带宽", "滤波且延迟对准，1−V", "不滤波，1−V"],
          [
              ["5 MHz", "6.2×10^−8", "1.65×10^−2"],
              ["10 MHz", "7.8×10^−7", "1.65×10^−2"],
              ["25 MHz", "3.0×10^−5", "1.66×10^−2"],
              ["50 MHz", "6.1×10^−4", "1.71×10^−2"],
              ["100 MHz", "1.10×10^−2", "2.73×10^−2"],
              ["200 MHz", "9.2×10^−2", "1.07×10^−1"],
          ],
          [4.6, 6.3, 6.3])
    P(doc, "10 MHz 不滤波的 1.65×10^−2 就是 1−ηshift。延迟约 1.09 ns。这些数是理想点的频谱，没有放进蒙特卡洛。")
    P(doc, "热声子用理想点、邵叉指的 6.75 μW，不是 33.7 μW。相干声子数")
    P(doc, "Ncoh = 4 γe / γm² · Pac / (ℏ Ω)", center=True, after=4)
    P(doc, "γm = Ω/Qm，γe = 0.15 γm，Qm = 2000。得到 Ncoh = 1.75×10^11。热占据 nth = 1 / (exp(ℏΩ/kBT) − 1)。300 K 时 nth = 1877，nth/Ncoh = 1.07×10^−8。4 K 时 nth = 24.5。10 mK 时 nth = 1.15×10^−7。")
    P(doc, "单声子协同系数另算：C0 = 4 g0² / (κ γm)。g0/2π = 1.1 kHz 取自邵 2019 表 S2，那一行的声频是 2.01 GHz，不是 3.33 GHz，属于借来的数。κ/2π 用本设计的 680.75 MHz。C0 = 4.27×10^−9。300 K 下 nth C0 = 8.0×10^−6，小于已经漏到移频线外面的约 1.7% 光。")

    H(doc, "8  只用来对照、不参加计算的数")
    table(doc,
          ["数", "出处", "不要把它当成什么"],
          [
              ["移频 98.7%，28.2 GHz，96 mW，插损 0.45 dB", "Hu 2021 的测量", "不是这颗 3.33 GHz 声光器件的结果。"],
              ["片上效率 3.5%，1 W，带宽 70 MHz", "邵 2020 行波声光移频器", "那是绝对效率，不是 ηshift。"],
              ["教学截面：膜厚 600 nm，刻蚀 300 nm，顶宽 1.2 μm", "手册里的占位", "论文没有这组尺寸。现有数字都没有用它。"],
              ["Fiber-Q 一类成品光纤声光器", "以后的仪器", "与 3.33 GHz 片上双环不是同一张表。"],
          ],
          [6.6, 4.6, 6.0])

    H(doc, "9  还没有、也不能从现有表里读出的两项")
    P(doc, "叉指周期：二维压电本征频率，扫一对正负指的总宽，直到能量在铌酸锂里的模式落在 3.33 GHz ± 50 MHz。得到的是掩模上的指间距。二维单周期给不出 Qm。")
    P(doc, "光弹每伏频移：在那个周期上改成频域，电极 1 V，力学阻尼取 1/Qm，把应变乘光弹系数得到 Δn，再和光模做重叠。然后")
    P(doc, "Δφ = 2π/λ · Δneff · La，   δf = Δφ · c / (2π ng Lring)，   ξ = (δf，单位 GHz/V) / 21.3", center=True, after=4)
    P(doc, "La 已经在式子里，不要再乘 15%。材料库没有铌酸锂的光弹系数。本征模态的幅度不能直接当成 1 V。")
    P(doc, "开算之前需要工艺截面，而不是再向别人要一个 21.3 或一个指间距：膜厚、刻蚀深度、顶宽、侧壁角、包层、埋氧厚度、晶向、光和叉指各自沿哪个晶轴、是否悬空、电极金属和厚度。组里如果已有悬空叉指的 S11、Qm 或 Vπ，用那些数替换邵 2019 的外推。光弹系数用组里指定的表，并写明波长；没有指定就用文献表并注明。")

    doc.save(DOCX)
    print("docx", DOCX.stat().st_size)


def to_pdf():
    word = win32com.client.Dispatch("Word.Application")
    word.Visible = False
    word.DisplayAlerts = 0
    d = word.Documents.Open(str(DOCX))
    d.SaveAs(str(PDF), FileFormat=17)
    d.SaveAs(str(PDF_DL), FileFormat=17)
    d.Close(False)
    try:
        word.Quit()
    except Exception as e:
        print("quit", e)
    print("pdf", PDF.stat().st_size)


if __name__ == "__main__":
    build()
    to_pdf()
