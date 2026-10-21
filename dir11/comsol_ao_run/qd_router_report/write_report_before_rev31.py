# -*- coding: utf-8 -*-
from docx import Document
from docx.shared import Pt, Cm, Emu
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

OUT = r"D:\comsol_ao_run\qd_router_report\量子点铌酸锂腔与可编程路由-方案报告.docx"
FIG = r"D:\comsol_ao_run\qd_router_report\fig1.png"

doc = Document()
sec = doc.sections[0]
sec.page_width = Cm(21.0)
sec.page_height = Cm(29.7)
sec.left_margin = Cm(2.6)
sec.right_margin = Cm(2.6)
sec.top_margin = Cm(2.5)
sec.bottom_margin = Cm(2.5)
sec.header_distance = Cm(1.2)
sec.footer_distance = Cm(1.2)

def set_run(run, name, size, bold=False):
    run.bold = bold
    run.font.size = Pt(size)
    run.font.name = name
    r = run._element
    rPr = r.get_or_add_rPr()
    rFonts = rPr.find(qn("w:rFonts"))
    if rFonts is None:
        rFonts = OxmlElement("w:rFonts")
        rPr.append(rFonts)
    rFonts.set(qn("w:ascii"), name)
    rFonts.set(qn("w:hAnsi"), name)
    rFonts.set(qn("w:eastAsia"), name)

def p(text, *, size=12, bold=False, center=False, indent=True, before=0, after=6, name="宋体", space=22):
    para = doc.add_paragraph()
    para.alignment = WD_ALIGN_PARAGRAPH.CENTER if center else WD_ALIGN_PARAGRAPH.JUSTIFY
    pf = para.paragraph_format
    pf.space_before = Pt(before)
    pf.space_after = Pt(after)
    pf.line_spacing = Pt(space)
    if indent and not center:
        pf.first_line_indent = Cm(0.74)
    run = para.add_run(text)
    set_run(run, name, size, bold)
    return para

def h(text, level):
    para = doc.add_paragraph()
    para.alignment = WD_ALIGN_PARAGRAPH.LEFT
    pf = para.paragraph_format
    pf.space_before = Pt(14 if level == 1 else 10)
    pf.space_after = Pt(6)
    pf.line_spacing = Pt(22)
    pf.first_line_indent = Cm(0)
    run = para.add_run(text)
    set_run(run, "黑体", 16 if level == 1 else 14, True)
    return para

# header / footer
header = sec.header.paragraphs[0]
header.alignment = WD_ALIGN_PARAGRAPH.RIGHT
hr = header.add_run("方案报告")
set_run(hr, "宋体", 9)
footer = sec.footer.paragraphs[0]
footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
# page number field
def add_page_field(paragraph):
    run = paragraph.add_run()
    set_run(run, "宋体", 9)
    fld1 = OxmlElement("w:fldChar")
    fld1.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = " PAGE "
    fld2 = OxmlElement("w:fldChar")
    fld2.set(qn("w:fldCharType"), "end")
    run._r.append(fld1)
    run._r.append(instr)
    run._r.append(fld2)

fr = footer.add_run("— ")
set_run(fr, "宋体", 9)
add_page_field(footer)
fr2 = footer.add_run(" —")
set_run(fr2, "宋体", 9)

p("量子点–薄膜铌酸锂腔与片上可编程路由的分区方案", size=18, bold=True, center=True, indent=False, before=18, after=8, name="黑体", space=28)
p("方案报告", size=14, center=True, indent=False, before=0, after=4, name="黑体")
p("陈鑫磊", size=12, center=True, indent=False, before=8, after=2)
p("上海电力大学", size=12, center=True, indent=False, before=0, after=2)
p("2026年10月19日（rev.3：补钉 0003 + 0004 测算结论）", size=12, center=True, indent=False, before=0, after=10)
p("本报告依据已发表结果提出架构建议。第 10–11 节补钉的是任务 0003 / 0004 的预测测算（二维半矢量有限差分模 + 解析电光公式），不是新的实验数据，也不是 COMSOL Wave Optics 结果。其余器件指标均引自所注文献；新闻稿中的带宽数据单独标明。", size=10.5, center=False, indent=False, before=4, after=8)

h("摘要", 1)
p("把高折射率路由层放在出射总线、不放进微环，可以同时留下两样已经测到的性能：腔的品质因子停在 10^4 量级，路由区收在几十微米里。裸铌酸锂环的加载品质因子是 2.52×10^5；砷化镓贴进环内之后降到 1.9×10^4，约 13 倍，因为损耗按环行圈数累加。总线只经过一次，同样的覆盖不再进入这个平均。")
p("材料上，磷化镓在 910 nm 透明，35 μm 长、体吸收系数取 1.06 μm 的 0.1 cm^−1 时，单次吸收只有约 0.002 dB。晶体硅在 910 nm 的吸收系数是 272 cm^−1，同一长度上、光能有 30% 留在硅里时损耗约 1.2 dB，全部留在硅里时约 4.1 dB，不能用于这条单光子路径。砷化镓折射率 3.58，铌酸锂约 2.2，折射率差约 1.3，与通信波段硅相对铌酸锂的差同一量级，所以“高折射率覆盖加电光相位”的束缚方式有材料依据。砷化镓在室温 910 nm 正处在带边；器件本身在低温工作，带边移到约 816 nm，张加祥等已经把 912 nm 的光从砷化镓段送到光栅端口。")
p("路由区有发表尺寸：4×4 为 35 μm×14 μm，比自成像结构最多小 86%。量子点与腔的联合调谐窗是 0.30 nm。新闻稿给出的路由器工作范围超过 78 nm，比这个窗口宽两个数量级以上；该带宽以新闻稿为准。两路光走同一段路由时，公共损耗降低符合计数，不直接降低干涉可见度；可见度取决于两路是否被收成同一个 TE0。")
p("rev.3 补钉：薄磷化镓覆盖可通过与裸总线准 TE0 的重叠门；本取向下用 r13，5 V 移相仍为毫米级，不能放在 35 μm×14 μm 旁。外置裸铌酸锂电极在 Γ_eo=0.5（ASSUMED）下标称单侧 L_π≈3.75 mm（g=1 μm、5 V）；推挽理想约 1.88 mm 仅作备注、不锁默认。衔接顺序为腔→短磷化镓→过渡→外置电极。数字为预测，见第 10–11 节。")

h("1  目的", 1)
p("张加祥等的器件已经解决单节点上的两件事：量子点与腔模可以对准，光子可以在平面波导里走。下一步若要做两个或多个节点之间的干涉，出射光还需变成同一个空间模式，并且相对相位由电极设定。本报告给出一种与李林、程亚的协同设计方法相接的分区结构，并写明材料不能原样照搬的原因。")

h("2  两项已有工作", 1)
h("2.1  量子点–薄膜铌酸锂混合腔", 2)
p("王旭东、朱一帆等将 InGaAs 量子点埋在 180 nm 厚的砷化镓层中，用微转印贴到 X 切薄膜铌酸锂跑道环上，定位精度在百纳米量级。量子点发光在 910 nm 附近。砷化镓波导两端用锥形模斑转换器，弯曲段采用欧拉弯，砷化镓只覆盖环的一小段，以降低这段高折射率材料带来的散射和吸收。裸铌酸锂环在约 912 nm 处的加载品质因子为 2.52×10^5；贴合砷化镓之后，回音壁模的品质因子最高为 1.9×10^4。")
p("应变由薄膜铌酸锂的逆压电效应产生。量子点发射波长的连续调谐达到 4.82 nm（7.30 meV）。腔模则由电光电极调节，电极位于欧拉弯两侧，间隙 5 μm，波导上有 800 nm 厚的 HSQ 绝缘层以减小金属吸收；加上这组电极后，品质因子最高约为 1.2×10^4。应变与电光一起使用时，量子点与腔可以在 0.30 nm（0.45 meV）内保持共振，该范围约为量子点变换极限线宽的 230 倍，全程 Purcell 因子大于 1.89。")
p("在一次共振匹配中，相对失谐 0.41 nm 的情况，共振时的发射强度约提高 10 倍。寿命测量给出失谐时的衰减率 0.42 ns^−1、共振时 1.90 ns^−1，对应 Purcell 因子 3.52。实验在闭循环制冷机中完成，激发光为 785 nm。")
h("2.2  硅–铌酸锂有源–无源协同设计", 2)
p("张灵恩、钟浩宗等在未刻蚀的铌酸锂平板波导上制作高折射率硅微纳结构，把电光相位和硅的拓扑放进同一次优化。优化目标是器件最终要输出的一组可编程状态。2×2 与 4×4 相位可编程路由器的路由区分别为 15 μm×8 μm 和 35 μm×14 μm，相对自成像结构最多缩小约 86%。同一方法还做出可重构的 4×1 模式合成器，在 TE0 至 TE3 四种导模之间切换。华东师范大学对该工作的报道给出电光带宽约 2.5 GHz、工作波长范围超过 78 nm；这两项以新闻稿为准，正式论文摘要未列出。")

h("3  为何分成两个区域", 1)
p("环的品质因子来自光在腔内的多次环行。裸环加载品质因子 2.52×10^5，贴上一段砷化镓后降到 1.9×10^4，再加入电光电极后约为 1.2×10^4。高折射率覆盖每多经过一次，环行损耗就按圈数累加。路由用的微纳结构若铺在环上，Purcell 增强会继续变弱。因此腔区只保留已经做出的砷化镓短覆盖、应变电极和电光电极。")
p("光子离开环之后只经过总线一次。多节点干涉要求各路出射的空间模式相同、相对相位可设。把这段功能放在总线上，微纳结构的损耗只计入一次。李林、程亚的结果表明，相位与高折射率结构一起按最终输出状态设计，可以把多端口路由收在几十微米的区域内。")
p("材料不能把硅原样搬过来。张加祥等的工作波长约 910 nm。晶体硅的带隙对应约 1100 nm，910 nm 的光子能量高于该带隙，硅在此波长吸收。李林、程亚所用的硅层适合硅透明的波段；用于本方案时，只取他们的设计方法，功能层改为在 910 nm 透明、并且折射率高于铌酸锂的材料。磷化镓在该波长透明，折射率约 3.3，能够承担硅在通信波段所起的模式束缚作用。砷化镓本身在 910 nm 也透明，但只适合作为光一次性经过的路由覆盖；若再铺进腔内，会重复张加祥等已经设法压低的那部分环行损耗。氮化硅在 910 nm 透明，折射率不高于铌酸锂，不能替代这一高折射率层。")

h("4  可行性估算", 1)
p("以下数字用于判断材料是否走得通。腔的品质因子沿用王旭东等的定义 Q = π n_g / (λ α)，取 n_g = 2.3、λ = 912 nm。这是量级估算，周长和群折射率未在正文中给出，不代替他们的补充材料。")
p("裸环 Q = 2.52×10^5，对应平均传播损耗 0.31 cm^−1。混合砷化镓之后 Q = 1.9×10^4，平均损耗升到 4.2 cm^−1。加上电光电极后 Q = 1.2×10^4，平均损耗 6.6 cm^−1。从裸环到混合环，损耗增加到约 13 倍。正文把新增损耗归于模斑转换器和砷化镓段，并且这段材料只占环的一小部分，所以局部损耗远高于 4.2 cm^−1。总线若再被纳入环内，品质因子会继续按同一机制下降。")
p("单次通过 35 μm（Optica 上 4×4 路由区的长边）的吸收如下。硅的 n 与 α 取 300 K 的列表值，910 nm 处 n = 3.614、α = 272 cm^−1。光能全部在硅中时透过率 0.39，损耗 4.1 dB；按能量占比 30% 折算，损耗 1.2 dB。磷化镓在 0.6–12 μm 透明，1.06 μm 处体吸收 0.1 cm^−1，35 μm 的吸收损耗 0.0015 dB。高阻砷化镓在 1.06 μm 的体吸收约 0.3 cm^−1，同样长度约 0.005 dB。室温下砷化镓在短于 910 nm 时吸收系数可以大于 200 cm^−1，35 μm 对应约 3 dB，因此不能靠室温带边透过。低温下砷化镓带隙约 1.519 eV，吸收边约 816 nm；本实验在制冷机中进行，912.3 nm 的发光已经从砷化镓波导经环和总线到达光栅耦合器，这是砷化镓在工作温度下可以导光的直接证据。")
p("折射率：910 nm 附近砷化镓 n = 3.58（由 900 nm 的 3.593 与 950 nm 的 3.545 线性内插），铌酸锂寻常光折射率约 2.2，差约 1.3。通信波段硅相对铌酸锂的折射率差也约为 1.3。磷化镓在 900 nm 附近约为 3.2，差约 1.0。氮化硅约 2.0，低于铌酸锂，不能提供这层覆盖所要的额外束缚。")
p("0.30 nm 的联合调谐窗相对 910 nm 只有 3.3×10^−4。Optica 论文给出的是路由区尺寸和缩小比例；超过 78 nm 的工作范围来自新闻稿。即便只取新闻稿的下限，该范围仍是 0.30 nm 的 260 倍。波长覆盖在数量级上不是限制项。限制项是 910 nm 的吸收，以及高折射率层是否进入环内。")

h("5  方案", 1)
p("整体分两段，如图 1。")
p("腔区沿用张加祥等的混合跑道环。含量子点的砷化镓只覆盖一小段，两端用他们已采用的锥形转换和欧拉弯，把光收成总线中的准 TE0。应变电压 VS 调节量子点，电光电压 VEO 调节腔模。这两套电极的几何，包括 5 μm 间隙和 HSQ 绝缘层，保持不变。路由用的高折射率层不进入环内。")
p("路由区位于出射总线。在未刻蚀的铌酸锂上制作 910 nm 透明的高折射率微纳结构，并设置电光电极。优化变量是该结构的拓扑和这些电极上的相位。目标函数取为：在 0.30 nm 的对准窗口内，任意两个节点的总线输出都变为同一个 TE0，相对相位由电极设定。窗口内的若干对准波长同时放进优化，避免结构只在一个波长上满足模式匹配。")
p("4×1 模式合成器放在两路总线交汇处，用来把两侧可能略有差别的出射场收成同一个 TE0。张加祥等的光子来自回音壁模经模斑转换后的准 TE 基模；砷化镓覆盖和工艺偏差会使不同节点的出射场不完全相同。模式合成器针对的就是这一差别。")

doc.add_picture(FIG, width=Cm(15.6))
cap = doc.add_paragraph()
cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
cap.paragraph_format.space_before = Pt(4)
cap.paragraph_format.space_after = Pt(8)
cap.paragraph_format.first_line_indent = Cm(0)
cr = cap.add_run("图 1  分区结构示意。腔区保持量子点–铌酸锂混合环；路由区位于出射总线，高折射率层在 910 nm 透明。")
set_run(cr, "宋体", 10.5)

h("6  优化时遵守的约束", 1)
p("第一，硅或任何在 910 nm 吸收的材料不进入腔区，也不进入单光子必经的总线。第二，量子点的空间位置由转印确定，腔区的模场在该位置保持足够的场强，应变电极仍能在量子点处产生可观测的发射移动。第三，电光电极的电场沿铌酸锂晶体 Z 轴的投影保持张加祥等已经采用的方向，X 切薄膜上电极布置不另起一套晶体取向。第四，路由区的电光电极做在裸露的铌酸锂上；高折射率覆盖若压在电极间隙上，会改变静电场并增加吸收，电极与微纳结构在版图上分开。第五，允许失败的范围只限于 0.30 nm 窗口之外的波长。窗口之内的模式匹配作为硬条件。")

h("7  判据", 1)
p("本方案尚未流片。第 10 节已补钉总线覆盖模场/重叠与电光移相长度的预测；逆向优化、双节点可见度、重做量子点腔与 Purcell 仍未做。若以后实现，用下面四项判断，不把李林、程亚在其自身波段上的尺寸和带宽直接当成 910 nm 的结果。")
p("（1）混合并完成电极之后，腔的品质因子仍在 10^4 量级，与张加祥等加电光电极后约 1.2×10^4 的结果同一量级。（2）应变与电光仍能在不少于 0.30 nm 的范围内把量子点与腔对准，该范围内 Purcell 因子仍大于 1。（3）两个独立节点的出射经路由区之后，空间模式重叠足够高，双光子干涉可见度达到实验可分辨的水平；可见度的数值目标需在测得总线出射场之后再定，本报告不预设。（4）路由区的插入损耗单次通过计量，并与腔的收集效率分开报告。")

h("8  风险", 1)
p("磷化镓或砷化镓路由层与铌酸锂的异质界面、对准和残余应力都没有在本报告中计算。910 nm 上的电光系数、群折射率和电极几何需要按该波长重新取值，不能沿用通信波段路由器的版图。量子点的不可区分性还受声子边带和激发方式限制；空间模式重合只去掉其中一项。张加祥等的展望写了片上路由和纠缠分发，本方案只对应其中的空间模式与相位这一段。")

h("9  结论", 1)
p("按已发表的品质因子和 910 nm 的材料常数，分区在“覆盖不进环、功能层用磷化镓”这一层仍然成立。任务 0003 钉死：薄磷化镓覆盖可通过与裸总线准 TE0 的重叠门；本取向下移相用 r13，5 V 下 π 相移仍为毫米级，放不进 35 μm×14 μm 旁。任务 0004 进一步钉死外置布局：电极画在磷化镓终止之后的裸铌酸锂上；Γ_eo=0.5（ASSUMED）时 g=1 μm、5 V 标称单侧 L_π≈3.75 mm；推挽理想约 1.88 mm 只备注、不锁默认；推荐外置有效长单侧约 2–8 mm。衔接顺序为腔/环→短磷化镓总线→终止过渡→外置裸铌酸锂 r13 π 段。弯耗与加载 Q 的三维硬证做不到。硅不进入这条单光子路径；出射场等项本回合仍不开。")

h("10  测算结论补钉（任务 0003，预测值）", 1)
p("来源：三人小组任务 0003；明细见 D:\\三人小组\\for-grok-bot\\0003_item1_reply.md 与 0003_item2_reply.md。方法为二维半矢量有限差分本征模（准 TE，Ex）与解析电光公式；不是 COMSOL 光学模型，也不是新实验。")
h("10.1  总线覆盖：模式、重叠、单次损耗", 2)
p("假设（写明）：未刻蚀 X 切薄膜铌酸锂总线，膜厚按平台口径取 300 nm（ASSUMED）；n_o(910 nm)≈2.243（Zelmon）；磷化镓 n≈3.2；低温砷化镓对照 n≈3.58；体吸收仍用任务给定的 1.06 μm 代理值。波长至少覆盖 908.75 nm、912.3 nm 与 0.30 nm 联合调谐窗两端。")
p("优选几何：磷化镓覆盖 50 nm × 0.8 μm。910 nm 处与裸总线准 TE0 的功率重叠 η≈0.76，判据通过。同尺寸低温砷化镓 η≈0.61。厚盖对照 180 nm × 1.5 μm 时磷化镓 η≈0.12、砷化镓 η≈0.08，重叠过低，停止，不做路由优化。")
p("35 μm 单次通过（只作长度标尺）：优选磷化镓的材料吸收约 0.00018 dB，进出覆盖的模式失配合计约 2.37 dB；吸收可忽略，失配占主导。晶体硅在 910 nm、α=272 cm^−1 时同长度吸收为分贝量级，只用于说明排除原因，不进入路径。")
p("覆盖不进环时：已发表的 1.9×10^4 / 1.2×10^4 是砷化镓贴在跑道环上一段（含模斑转换）的对照量级，不是总线-only 几何的目标值。覆盖只在总线、不按贴环损耗按圈累加；预期不单独把加载品质因子压破 10^4，但缺少总线–环耦合区的三维证明，此处写做不到硬证。")
h("10.2  电光移相长度（第一项通过后）", 2)
p("晶体取向与分量：直段传播沿晶体 Z，调制电场沿晶体 Z，准 TE0 主场沿 Y（膜面内），寻常光折射率。因此 Δn 走 r13，取 r13=8.6 pm/V；不用默认的“光沿 Y + r33”通信波段口头公式，也不把腔上 5 μm 电极间隙当成路由移相器的最小间隙。电极与覆盖图形在版图上分开。")
p("公式（均匀共面电极近似）V_π L = λ g / (n_o^3 r13 Γ_eo)。取 λ=910 nm、n_o=2.243、Γ_eo=0.5（ASSUMED，另报 0.3–0.7 敏感带）。间隙 g=1–4 μm 时，5 V 下 π 相移长度约 3.75–15 mm；即使用 g=1 μm 且 Γ_eo 提到 0.7，仍约 2.7 mm 量级。结论：放不进 35 μm×14 μm 路由区旁边。")
p("本项未做 COMSOL 静电场/光学联合仿真。若仍要片上电光相对相位，只能另开更长的总线移相路径（例如折线外置），而不是在 35×14 旁继续优化间隙。")
h("10.3  明确先不做", 2)
p("出射场、HOM 可见度、纠缠、逆向设计、非电光替代、重做量子点腔与 Purcell，本回合均不动。第 11 节（任务 0004）同样不开这些项。")

h("11  测算结论补钉（任务 0004，外置毫米级 r13 π，预测值）", 1)
p("来源：三人小组任务 0004；明细见 D:\\三人小组\\for-grok-bot\\0004_reply.md。与第 10.2 节同一解析电光外推；非 COMSOL 全波/静电联仿，非完整版图，非实验。")
h("11.1  标称工作点与推荐长度", 2)
p("材料与取向同第 10.2 节：λ=910 nm，n_o=2.243（Zelmon），r13=8.6 pm/V，Γ_eo=0.5（ASSUMED）。标称：电极间隙 g=1 μm、驱动 5 V、单侧驱动时，预测 L_π≈3.75 mm。推挽理想（单侧×1/2）≈1.88 mm，仅作备注上限，不锁为版图默认。同条件 10 V 单侧亦约 1.88 mm。推荐外置有效电极长度：单侧约 2–8 mm；若改推挽理想则约 1–4 mm。若 Γ_eo 落到 0.3，同条件长度约 ×1.67（标称单侧约 3.8 mm → 约 6.3 mm）。")
h("11.2  衔接顺序与电极分区", 2)
p("布局顺序固定为：腔/环 → 短磷化镓总线（仍用 50 nm×0.8 μm，η≈0.76 通过重叠门）→ 磷化镓终止过渡 → 外置裸铌酸锂上的 r13 π 段（可折线）→ 后续总线。路由电极只画在磷化镓终止之后的裸铌酸锂上，与磷化镓覆盖版图分开；35 μm×14 μm 旁不再塞电光。")
h("11.3  折线、弯耗与加载品质因子", 2)
p("布局上允许 U 形或蛇形把约 2–8 mm 收进毫米×毫米窗；几何额外弯程可粗估，但弯耗（dB）做不到（无弯模/三维损耗仿真）。外置电极在量级上不改写“覆盖不进环”的前提（预测，非三维硬证）；品质因子是否被总线金属损耗间接牵动，需另开仿真才硬证。")
h("11.4  本钉仍不做", 2)
p("完整 GDS 与折线坐标、弯耗数值、加载品质因子三维硬证、出射场、可见度、非电光替代、逆向设计、重做量子点腔与 Purcell：本回合不开。")

h("参考文献", 1)

refs = [
    "[1] Wang X, Zhu Y, Zhang X, et al. Scalable all-solid-state cavity QED on a hybrid quantum dot–lithium niobate platform[J]. npj Quantum Information, 2026, 12: 143. DOI: 10.1038/s41534-026-01282-3.",
    "[2] Zhang L, Zhong H, Qu N, et al. Programmable heterogeneous lithium niobate photonic circuits via active–passive joint inverse design[J]. Optica, 2026, 13(10): 2163-2170. DOI: 10.1364/OPTICA.614691.",
    "[3] 华东师范大学精密光谱科学与技术高等研究院. Optica | 有源–无源协同设计实现硅–铌酸锂可编程异质集成光子芯片[EB/OL]. 微信公众号发布. 其中电光带宽约 2.5 GHz、波长范围超过 78 nm 引自该报道，正式论文摘要未列出。",
    "[4] 中国科学院上海微系统与信息技术研究所. npj Quantum Information：可扩展的片上全固态腔量子电动力学系统[EB/OL]. (2026-09-14). http://www.sim.cas.cn/xwzx2016/kyjz/202609/t20260914_8281496.html.",
    "[5] Green M A. Self-consistent optical parameters of intrinsic silicon at 300 K including temperature coefficients[J]. Solar Energy Materials and Solar Cells, 2008, 92: 1305-1310. 910 nm 处采用其列表值 α = 272 cm^−1，n = 3.614。",
    "[6] Batop GmbH. Refractive index of GaAs[EB/OL]. https://www.batop.de/information/n_GaAs.html. 900 nm 为 3.593，950 nm 为 3.545。",
    "[7] Optical properties of GaAs, GaP, and CVD diamond[C]. Proc. SPIE, 1991, 1498. GaP 在 0.6–12 μm 透明，1.06 μm 吸收系数 0.1 cm^−1；高阻 GaAs 在 1.06 μm 约 0.3 cm^−1。室温下 GaAs 在短于 910 nm 时吸收系数可大于 200 cm^−1、950 nm 处可小于 0.01 cm^−1，见材料供应商对窗口片透过范围的说明。",
]
for t in refs:
    p(t, size=10.5, indent=False, before=0, after=4, space=18)

doc.save(OUT)
print(OUT)
