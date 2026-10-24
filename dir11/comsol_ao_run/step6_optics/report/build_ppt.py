import copy
import os
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

TPL = r"D:\学习资料\ppt模版\01 硬实力PPT模板.pptx"
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "汇报_声光相位调制器_思路与进展.pptx")
RED = RGBColor(0xB5, 0x31, 0x32)
LRED = RGBColor(0xDC, 0x5A, 0x5D)
PINK = RGBColor(0xF8, 0xE6, 0xE6)
GRAY = RGBColor(0x55, 0x55, 0x55)
DARK = RGBColor(0x26, 0x26, 0x26)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
FONT = "微软雅黑"
FOOT = "课题组内部工作稿｜器件数字均为 COMSOL 仿真预测，无实测、无流片"

prs = Presentation(TPL)
S = list(prs.slides)
TITLE_SRC = S[3]


def set_text(shape, text):
    tf = shape.text_frame
    p0 = tf.paragraphs[0]
    r0 = p0.runs[0] if p0.runs else p0.add_run()
    r0.text = text
    for r in p0.runs[1:]:
        r._r.getparent().remove(r._r)
    for p in tf.paragraphs[1:]:
        p._p.getparent().remove(p._p)


def find(slide, name):
    for sh in slide.shapes:
        if sh.name == name:
            return sh
        if sh.shape_type == 6:
            for c in sh.shapes:
                if c.name == name:
                    return c
    raise KeyError(name)


def style_run(r, size, bold=False, color=DARK):
    r.font.name = FONT
    r.font.size = Pt(size)
    r.font.bold = bold
    r.font.color.rgb = color
    rPr = r._r.get_or_add_rPr()
    ea = rPr.find("{http://schemas.openxmlformats.org/drawingml/2006/main}ea")
    if ea is None:
        ea = rPr.makeelement("{http://schemas.openxmlformats.org/drawingml/2006/main}ea", {})
        rPr.append(ea)
    ea.set("typeface", FONT)


SUP = dict(zip("⁰¹²³⁴⁵⁶⁷⁸⁹⁻ᴱ", "0123456789-E"))
SUB = dict(zip("₀₁₂₃₄₅₆₇₈₉ₐ", "0123456789a"))


def runs(p, s, size, bold=False, color=DARK):
    """Add runs to paragraph p, turning Unicode super/subscript characters into real super/subscript runs."""
    segs = []
    for ch in s:
        kind, c = ("sup", SUP[ch]) if ch in SUP else ("sub", SUB[ch]) if ch in SUB else ("n", ch)
        if segs and segs[-1][0] == kind:
            segs[-1][1] += c
        else:
            segs.append([kind, c])
    for kind, t_ in segs:
        r = p.add_run()
        r.text = t_
        style_run(r, size, bold=bold, color=color)
        if kind != "n":
            r._r.get_or_add_rPr().set("baseline", "30000" if kind == "sup" else "-25000")


def text(slide, x, y, w, h, lines, size=16, color=DARK, bullet=False, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP,
         spacing=4, bold_first=False):
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = Inches(0.05)
    for i, ln in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.space_after = Pt(spacing)
        segs = ln if isinstance(ln, list) else [(ln, False)]
        if bullet:
            r = p.add_run()
            r.text = "■ "
            style_run(r, size - 6, color=RED)
        for s, b in segs:
            runs(p, s, size, bold=b or (bold_first and i == 0), color=color)
    return tb


def box(slide, x, y, w, h, fill=RED, line=None, shape=MSO_SHAPE.ROUNDED_RECTANGLE, lines=(), size=14, color=WHITE,
        bold=False, align=PP_ALIGN.CENTER):
    s = slide.shapes.add_shape(shape, Inches(x), Inches(y), Inches(w), Inches(h))
    s.fill.solid()
    s.fill.fore_color.rgb = fill
    if line is None:
        s.line.fill.background()
    else:
        s.line.color.rgb = line
        s.line.width = Pt(1.25)
    s.shadow.inherit = False
    if shape == MSO_SHAPE.ROUNDED_RECTANGLE:
        s.adjustments[0] = 0.12
    tf = s.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = Inches(0.06)
    tf.margin_top = tf.margin_bottom = Inches(0.03)
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    for i, ln in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        segs = ln if isinstance(ln, list) else [(ln, bold if i == 0 else False)]
        for t_, b in segs:
            runs(p, t_, size if i == 0 else size - 2, bold=b, color=color)
    return s


def table(slide, x, y, w, data, colw, size=12, rowh=0.36, head_size=None, bold_col0=False):
    nr, nc = len(data), len(data[0])
    gt = slide.shapes.add_table(nr, nc, Inches(x), Inches(y), Inches(w), Inches(rowh * nr))
    tb = gt.table
    tot = sum(colw)
    for j, cw in enumerate(colw):
        tb.columns[j].width = Emu(int(Inches(w) * cw / tot))
    for i in range(nr):
        tb.rows[i].height = Inches(rowh)
        for j in range(nc):
            c = tb.cell(i, j)
            c.margin_left = c.margin_right = Inches(0.06)
            c.margin_top = c.margin_bottom = Inches(0.03)
            c.vertical_anchor = MSO_ANCHOR.MIDDLE
            c.fill.solid()
            c.fill.fore_color.rgb = RED if i == 0 else (PINK if i % 2 == 0 else WHITE)
            tf = c.text_frame
            tf.word_wrap = True
            val = data[i][j]
            segs = val if isinstance(val, list) else [(str(val), False)]
            p = tf.paragraphs[0]
            for t_, b in segs:
                if i == 0:
                    runs(p, t_, head_size or size, bold=True, color=WHITE)
                else:
                    runs(p, t_, size, bold=b or (bold_col0 and j == 0), color=DARK)
    return gt


def pic(slide, path, x, y, w=None, h=None):
    kw = {}
    if w:
        kw["width"] = Inches(w)
    if h:
        kw["height"] = Inches(h)
    return slide.shapes.add_picture(os.path.join(HERE, path), Inches(x), Inches(y), **kw)


def notes(slide, t):
    slide.notes_slide.notes_text_frame.text = t


def content(title, note=None):
    s = prs.slides.add_slide(prs.slide_layouts[7])
    for nm in ("矩形 1", "矩形 2", "文本框 3"):
        el = copy.deepcopy(find(TITLE_SRC, nm)._element)
        s.shapes._spTree.append(el)
    t = find(s, "文本框 3")
    t.width = Inches(10.6)
    set_text(t, title)
    text(s, 0.45, 7.08, 9.5, 0.3, [FOOT], size=9, color=GRAY)
    if note:
        notes(s, note)
    return s


def conclusion(slide, y, msg, h=0.5, size=15):
    box(slide, 0.6, y, 12.13, h, fill=PINK, line=LRED, lines=[msg], size=size, color=RED, bold=True)


# ---------------- 封面、目录、章节页 ----------------
cover, toc = S[0], S[1]
set_text(find(cover, "文本框 9"), "长孔径分段馈电薄膜铌酸锂声光相位调制器")
tb9 = find(cover, "文本框 9")
for r in tb9.text_frame.paragraphs[0].runs:
    r.font.size = Pt(34)
set_text(find(cover, "文本框 12"), "汇报：思路回顾与研究进展")
set_text(find(cover, "文本框 13"), "汇报人：陈鑫磊")
set_text(find(cover, "文本框 14"), "日期：2026.10")
find(cover, "文本框 12").width = Inches(3.2)
find(cover, "文本框 12").left = Inches(1.6)
text(cover, 1.2, 5.25, 10.9, 0.5, ["本稿仅限课题组内部：仿真与方案工作稿，实测待做，无伪造数据，Fiber-Q 未下单，无流片；不得作为公开或可引用结果"],
     size=11, color=GRAY, align=PP_ALIGN.CENTER)
notes(cover, "汇报内容分四部分：改进路线的思路、当前设计与参数、仿真结果、流片后续计划与时间安排。所有器件数字都是仿真预测。")

secs = [("改进路线回顾", "Route of Improvement"), ("当前设计与参数", "Device Design"),
        ("仿真模型与结果", "Simulation Results"), ("流片计划与时间安排", "Tape-out Plan & Schedule")]
for k, (cn, en) in enumerate(secs):
    set_text(find(toc, "文本框 %d" % (7 + 4 * k)), cn if k < 3 else "流片与时间安排")
    set_text(find(toc, "矩形 %d" % (8 + 4 * k)), en)
sec_slides = [S[2], S[7], S[12], S[17]]
for k, sl in enumerate(sec_slides):
    set_text(find(sl, "文本框 4"), secs[k][0])
    set_text(find(sl, "矩形 5"), secs[k][1])
    set_text(find(sl, "文本框 7"), "PART 0%d" % (k + 1))
end = S[23]
set_text(find(end, "文本框 12"), "")
set_text(find(end, "文本框 13"), "汇报人：陈鑫磊")
set_text(find(end, "文本框 14"), "")

order = [cover, toc, sec_slides[0]]

# ---------------- 01 改进路线 ----------------
s = content("起点：谐振式声光移频器（2026.10.7–10.16）",
            "最早的方案是双环光子分子加悬空叉指的谐振移频器，预印本草稿声称 98.3% 移频、6.7 微瓦。关键问题是驱动强度 21.3 GHz/V 是从 Shao 2019 外推借来的。10 月 16 日在本结构上做 1 V 光弹实算，只有 1.65 MHz/V，差一万多倍，方案放弃。")
text(s, 0.6, 1.25, 6.1, 4.3, [
    [("方案：", True), ("单总线双环（光子分子）+ 悬空叉指声学谐振腔，3.33 GHz，覆盖环 1 约 15% 周长", False)],
    [("原理：", True), ("声波驱动两超模之间跃迁，实现单边带移频（Hu 2021 耦合模理论）", False)],
    [("预印本草稿（10.14）声称：", True), ("移频效率 98.3%，驱动 6.7 µW，蒙特卡罗良率 96.4%", False)],
    [("关键假设：", True), ("驱动强度 21.3 GHz/V，由 Shao 2019 的 VπL = 0.046 V·cm 外推，", False),
     ("未在本结构上计算", True)],
    [("复现审计中已修正：", True), ("功率优势 1.3×10⁴ → 440 → 1.4–3.7 倍；良率 96.4%（无样本）→ 94.3%；变量标反（0.75% vs 98.31%）", False)],
], size=15, bullet=True, spacing=8)
text(s, 7.0, 1.25, 5.7, 0.4, ["本结构 1 V 压电 + 光弹实算（10.16）"], size=16, color=RED, bold_first=True)
table(s, 7.0, 1.75, 5.7, [
    ["量", "方案假设", "实算"],
    ["驱动强度", "21.3 GHz/V", [("1.65 MHz/V", True)]],
    ["差距", "—", [("约 1.3×10⁴ 倍", True)]],
    ["达到原指标所需电压", "—", "约 300 V"],
    ["可行窗口内最好", "—", "1.58 GHz/V，约 1.2 mW"],
], [2.2, 1.6, 2.1], size=13, rowh=0.5)
conclusion(s, 5.85, "结论：移频器在本结构下不成立，10.16 放弃（数据保留）。教训：借来的实验标定必须在本结构上用有限元复算。", h=0.7)
order.append(s)

s = content("改进路线总览：从移频器到分段馈电相位调制器",
            "这一页是整条路线。八个阶段，每个阶段一个关键数字。核心转变有三个：谐振移频改成行波相位调制；单段馈电改成分段串并联配 50 欧；二维模型扩展到三维加梁加引线。")
stages = [
    ("① 移频器方案", "10.7–10.15", "98.3%、6.7 µW\n（基于外推）"),
    ("② 光弹实算", "10.16", "1.65 MHz/V，差 1.3×10⁴\n→ 放弃移频"),
    ("③ 孔径内调制预研", "10.16–10.21", "审计：排序被网格推翻\n结论撤回"),
    ("④ 数值排查 Step 1–5", "10.21", "二维/三维一致 <0.01%\n周期 2.8526 µm"),
    ("⑤ 器件原型 6a–6e", "10.21–10.22", "VπL ≈ 0.87 V·cm\n标准脊方案"),
    ("⑥ 功率与超胞 6f–6h", "10.22", "电阻占 85–99%\n123 W → 2.9 W"),
    ("⑦ 校准与取向 6i–6j", "10.22", "Shao 取向 ×220，脊 ×7\n→ 约 2.5–2.8 mW"),
    ("⑧ 三维与可加工性 7–9", "10.22–10.23", "分段 + 梁 + 引线\n→ 3.26 mW"),
]
for k, (a, b, c) in enumerate(stages):
    row, col = divmod(k, 4)
    x = 0.6 + col * 3.1
    y = 1.35 + row * 2.35
    box(s, x, y, 2.75, 0.62, fill=RED if k >= 3 else LRED, lines=[a], size=15, bold=True)
    text(s, x, y + 0.66, 2.75, 0.3, [b], size=12, color=GRAY, align=PP_ALIGN.CENTER)
    box(s, x, y + 1.0, 2.75, 0.95, fill=WHITE, line=LRED, lines=c.split("\n"), size=14, color=DARK)
    if col < 3:
        a_ = s.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, Inches(x + 2.8), Inches(y + 0.18), Inches(0.26), Inches(0.26))
        a_.fill.solid(); a_.fill.fore_color.rgb = LRED; a_.line.fill.background()
conclusion(s, 6.15, "核心转变：谐振移频 → 行波相位调制；单段馈电 → 分段串并联配 50 Ω；二维截面 → 三维分段 + 支撑梁 + 引线", h=0.62)
order.append(s)

s = content("数值与建模排查（Step 1–5）：先让模型可信",
            "转向孔径内调制以后，先花了一个阶段让二维和三维模型给出一致结果。五个问题都是数值或设置问题，表里给了当时的数据。改完以后二维和三维频率一致到万分之一以内。")
table(s, 0.6, 1.3, 12.13, [
    ["步骤", "现象（当时数据）", "原因", "处理"],
    ["Step 1", "三维比二维频率低 1162 MHz；改二阶后仍高 230 MHz", "三维一阶单元、网格粗", "二阶单元并加密；早期三维结论重新核对"],
    ["Step 2", "二维/三维仍差约 35.6 MHz", "周期不一致（2.58 vs 2.8326 µm）；二维平面应变等价于强制面外位移为 0", "统一周期；改用面外扩展"],
    ["Step 3", "材料常数 cᴱ 等分量相差 16–200%", "二维材料张量的基矢取向错误", "改用 sys2 坐标系，每次运行打印张量自检"],
    ["Step 4", "约 48 MHz 偏差", "接地边按“相交”选择，多选了 5 条边", [("精确选择；二维/三维一致到 0.01% 以内，周期定为 2.8526 µm", True)]],
    ["Step 5", "相位调制 φ/L 数值偏大 10⁶ 倍", "rad/(m·V) 换 rad/(mm·V) 时乘了 1000（应乘 10⁻³）", "6a 自检发现并改正，原记录已补注"],
    ["早期", "压电场异常（出现两次）", "漏掉压电电荷守恒", "补上并加入检查项"],
], [1.0, 3.6, 3.9, 3.6], size=13, rowh=0.62, bold_col0=True)
conclusion(s, 6.0, "做法固定下来：每次运行在日志里打印张量、接地边、旋转方法和单位换算，便于复核", h=0.6)
order.append(s)

s = content("器件层面的问题与修正（6a–6j）",
            "有了可信的模型以后，问题转到器件层面。最关键的是三件事：功率里电极电阻占绝大部分；低频峰是超胞折叠假象；跟 Shao 的差距主要是取向造成的，改取向提高约 220 倍，400 纳米脊再提高约 7 倍。")
table(s, 0.6, 1.3, 12.13, [
    ["阶段", "现象（当时数据）", "原因", "处理"],
    ["6c", "合格判断由“合格”变为“不合格”", "伙伴模按频率最近认错", "按铝中能量占比 fracAl 认模"],
    ["6c", "沟槽脊方案光模横向泄漏", "结构光学上不可行", "改标准脊：平板 400 nm，缺陷胞 3 个"],
    ["6e", "VπL ≈ 0.87 V·cm（首个完整器件数字）", "调制参数应填 β；首轮扫描漏峰", "改正后重扫"],
    ["6f→6g", "低频峰“好 5.8 倍”；计入电极后 L = 1 mm 主峰需 123 W", "只按 Vπ 算功率，电极电阻占 85–99%", "分布 RC 模型，功率一律算到 50 Ω 信号源"],
    ["6h", "“亚瓦”低频峰", "周期超胞能带折叠假象，对 NP 不收敛", "撤回；以有限长模型为准（最低约 2.9 W）"],
    ["6h_lit→6i", "VπL 比 Shao 差 16–19 倍；首次校准异常", "需区分模型误差与结构差距；坐标旋转 inPlane 被截断", "改 general 重算 Shao 结构：本流程 Δn₀ 偏高 1.3–2.3 倍，功率需 ×1.7–5.3"],
    ["6j", "旧取向可用系数小；“无损匹配”0.7–1.4 Ω 配 50 Ω 不现实", "结构差距；匹配假设过乐观", [("Shao 取向 ×220，400 nm 脊 ×7；多段串并联直接配 50 Ω", True)]],
], [1.2, 4.0, 3.6, 3.3], size=12.5, rowh=0.6, bold_col0=True)
order.append(s)

s = content("功率预测的演变（L = 1 mm，信号源功率）",
            "这张图把相位调制器阶段每一步的功率预测画在一起，对数坐标。从 6g 的 123 瓦降到现在的 3.26 毫瓦。注意这些都是仿真值，乘校准系数后是 5.5 到 17 毫瓦。")
pic(s, "fig_history.png", 0.6, 1.25, w=8.2)
text(s, 9.05, 1.4, 3.75, 4.6, [
    [("灰：", True), ("旧取向、单段或少段馈电，瓦级", False)],
    [("橙：", True), ("二维截面优化后（取向 + 脊高 + 串并联），约 2.5–2.8 mW", False)],
    [("蓝：", True), ("三维分段：汇流条与指端的损失，经段长、汇流条、周期优化回到 2.85 mW", False)],
    [("绿 / 红：", True), ("计入支撑梁（×1.11）和引线（+3–4%），3.26 mW", False)],
    [("校准后：", True), ("5.5–17 mW（系数 1.7–5.3）", False)],
], size=14, bullet=True, spacing=10)
conclusion(s, 6.25, "瓦级 → 毫瓦级：主要来自取向（×220）、脊高（×7）和分段匹配，不是数值调参", h=0.55)
order.append(s)

s = content("三维阶段的修正（Step 7–9）与经验",
            "三维阶段也有几处修正：25 微米段损失太大，改成 100 微米段加 0.5 微米汇流条；周期估算改用实算斜率；梁的影响用幽灵几何确认是物理效应。下面四条是整个过程固定下来的做法。")
table(s, 0.6, 1.3, 12.13, [
    ["现象（当时数据）", "原因", "处理"],
    ["25 µm 段功率损失 2–2.6 倍", "汇流条与指端使主模分裂成一串模式", "100 µm 段 + 0.5 µm 汇流条，损失降到 1.10 倍（1 µm 汇流条有旁模并入，避开）"],
    ["按 f ∝ 1/p 估周期 1.86–1.89 µm", "频率不严格反比于周期", "实算斜率 −1.33 MHz/nm，取 1.84 µm（3.333 GHz）"],
    ["梁带来 1.11 倍，疑为网格效应", "需区分数值与物理", "幽灵几何对照逐位一致 → 物理效应；梁端 PML 与固定端差 <1%"],
    ["“校准系数与三维损失重复计算”", "表述错误", "两者独立，可直接相乘"],
], [3.6, 3.5, 5.0], size=13, rowh=0.55)
text(s, 0.6, 4.35, 12.1, 1.9, [
    [("借来的数字必须在本结构上复算", True), ("（移频器差 1.3×10⁴ 倍）", False)],
    [("每次运行打印自检；认模按物理量（fracAl），不按频率最近", True)],
    [("周期超胞结论用有限长核对；功率一律算到 50 Ω 信号源", True)],
    [("用已发表结构（Shao 2019）同流程校准，把模型误差和结构差距分开", True)],
], size=15, bullet=True, spacing=6)
order.append(s)

# ---------------- 02 当前设计 ----------------
order.append(sec_slides[1])
s = content("器件结构：毫米级孔径，分段串并联馈电",
            "当前设计：光波导放在叉指孔径中间，叉指平行于波导。1 毫米分成 10 段，每段 100 微米。段间隙电位依次是信号、浮空、地、浮空，相邻两段串联，共两串乘五并，直接配 50 欧。每个段间隙两侧各一根支撑梁，梁上走线引到锚区的引线轨。")
pic(s, "fig_layout.png", 0.7, 1.2, w=11.9)
text(s, 0.6, 5.85, 12.1, 1.1, [
    [("行波相位调制：", True), ("声波沿晶体 Z 横穿波导传播，光沿晶体 Y 在叉指孔径内传播", False)],
    [("分段的目的：", True), ("单段阻抗过低，分 10 段 2 串 × 5 并后输入阻抗 53–57 Ω，直接接 50 Ω 源", False)],
], size=14, bullet=True, spacing=4)
order.append(s)

s = content("波导截面：X 切悬空 LN，400 nm 平板 + 400 nm 脊",
            "截面是悬空的 X 切铌酸锂，平板 400 纳米，脊宽 1 微米、高 400 纳米。叉指是 100 纳米铝，放在脊两侧，周期 1.84 微米，七个周期里中间三个周期放波导。右边是两种截面的 TE0 模式，悬空和不悬空的有效折射率只差 0.0107。")
pic(s, "fig_xsec.png", 0.5, 1.2, w=7.3)
table(s, 0.6, 3.0, 6.9, [
    ["参数", "取值"],
    ["薄膜", "X 切 LN，平板 400 nm，悬空"],
    ["脊", "宽 1.0 µm × 高 400 nm"],
    ["取向", "声沿晶体 Z，TE 光沿晶体 Y（Shao 型）"],
    ["叉指", "铝 100 nm，周期 1.84 µm，指宽 0.25p"],
    ["缺陷胞", "NP = 7，中间 3 个周期放波导"],
    ["波长 / 光模", "1550 nm，TE0"],
], [1.6, 5.3], size=13, rowh=0.44)
pic(s, "fig_modes.png", 7.75, 1.35, w=5.2)
text(s, 7.8, 3.15, 5.1, 2.6, [
    "悬空段 neff 1.92670；普通段（SiO₂ 2 µm）1.93743",
    "模式基本约束在 LN 内；带 / 不带叉指 neff 相同",
    "悬空段带叉指时损耗 0.00053 dB/cm（铝吸收），可忽略",
], size=13, bullet=True, spacing=6)
order.append(s)

s = content("设计参数总表（仿真所用值）",
            "这是仿真所用的全部参数。灰色字的衬底和引线厚度是假设值，等工艺侧给出实际参数后需要重算。")
table(s, 0.6, 1.3, 12.13, [
    ["类别", "参数"],
    ["材料与取向", "悬空 X 切 LN，平板 400 nm，脊高 400 nm；Shao 取向（主要利用 r₃₃ 与光弹效应）；波长 1550 nm"],
    ["叉指", "周期 1.84 µm（谐振 3.333 GHz），铝，指宽 0.25p，厚 100 nm；NP = 7，中间 3 个周期放波导"],
    ["分段", "L = 1 mm = 10 段 × 100 µm；段间隙 0.5 µm，汇流条 0.5 µm，指端间隙 0.5 µm"],
    ["支撑梁", "每个段间隙两侧各一根，宽 2 µm、长 6 µm；梁上 100 nm 铝走线引出信号与地"],
    ["接法", "2 串 × 5 并；段间隙电位依次为 信号 / 浮空 / 地 / 浮空，浮空间隙不需引出"],
    ["引线（假设）", "锚区两侧各一对信号轨与地轨；500 nm 铝，信号轨 50 µm、间隙 10 µm、地轨 100 µm"],
    ["衬底（假设）", "锚区 LN 400 nm / SiO₂ 2 µm / 高阻 Si 500 µm，按无损介质处理"],
    ["损耗（假设）", "声学损耗因子 ηs = 5×10⁻⁴，给出驱动 Q ≈ 2000（非测得）"],
], [2.0, 10.1], size=14, rowh=0.56, bold_col0=True)
order.append(s)

s = content("关键参数的选择依据",
            "参数选择的依据：取向和脊高是二维截面上定的；段长、汇流条宽度、周期是三维模型定的；接法看输入阻抗和对段间失谐的敏感度。")
pic(s, "fig_ridge.png", 0.6, 1.3, w=4.6)
text(s, 0.7, 4.85, 4.5, 1.1, ["脊高 100 → 400 nm，PπL 明显下降，400 nm 时接近同流程 Shao 型（虚线）"], size=13, color=GRAY)
table(s, 5.5, 1.3, 7.23, [
    ["参数", "选择", "依据（仿真）"],
    ["晶体取向", "Shao 型", "相对旧取向效率约 ×220"],
    ["脊高", "400 nm", "相对浅脊约 ×7；同流程为 Shao 型单位长度效率的 0.77–0.87 倍"],
    ["段长", "100 µm", "汇流条损失：25 µm 段 1.9–3.4 倍，50 µm 2.0 倍，100 µm 1.10 倍"],
    ["汇流条", "0.5 µm", "0.3–0.7 µm 平滑；1 µm 附近有旁模并入，避开"],
    ["周期", "1.84 µm", "斜率 −1.33 MHz/nm，主峰到 3.333 GHz"],
    ["接法", "2 串 × 5 并", "输入阻抗 53–57 Ω；全并联作失谐保底"],
], [1.3, 1.4, 4.5], size=13, rowh=0.62, bold_col0=True)
conclusion(s, 6.2, "单位长度效率没有超过 Shao 型；可主张的差别是毫米级孔径 + 分段串并联后能直接配 50 Ω", h=0.55)
order.append(s)

# ---------------- 03 仿真结果 ----------------
order.append(sec_slides[2])
s = content("仿真模型与验证流程（COMSOL 6.3，批处理）",
            "仿真分四层：二维截面算压电和光模；三维分段单元加上汇流条、指端和梁；再把每段的导纳和调制系数放进馈电网络，含引线轨；最后单独算光学过渡和空气桥。右边是每一层的验证。")
steps = [
    ("二维截面", "压电 + 光弹 + 电光\n光模 TE0；周期 / 有限长"),
    ("三维分段单元", "沿波导周期边界\n含汇流条、指端、梁"),
    ("馈电网络", "段导纳 + 引线轨 RLC\n节点分析，50 Ω 源"),
    ("光学校核", "模式匹配（过渡）\n空气桥吸收"),
]
for k, (a, b) in enumerate(steps):
    y = 1.35 + k * 1.3
    box(s, 0.7, y, 2.6, 0.95, fill=RED, lines=[a], size=16, bold=True)
    box(s, 3.4, y, 3.4, 0.95, fill=WHITE, line=LRED, lines=b.split("\n"), size=14, color=DARK)
    if k < 3:
        a_ = s.shapes.add_shape(MSO_SHAPE.DOWN_ARROW, Inches(1.85), Inches(y + 0.97), Inches(0.3), Inches(0.3))
        a_.fill.solid(); a_.fill.fore_color.rgb = LRED; a_.line.fill.background()
table(s, 7.1, 1.35, 5.63, [
    ["验证项", "结果"],
    ["二维 / 三维频率一致", "< 0.01%（Step 4）"],
    ["三维无汇流条 vs 二维有限长", "PπL 2.49 vs 2.43（×10⁻⁶ W·m）"],
    ["同流程重算 Shao 2019", "Δn₀ 偏高 1.3–2.3 倍 → 校准 ×1.7–5.3"],
    ["网格对照", "沿波导 1.5 → 1.0 µm 变化 0.8%"],
    ["幽灵几何对照（梁）", "逐位一致，梁效应为物理"],
    ["梁端 PML vs 固定", "差 < 1%"],
    ["光学过渡粗 / 细网格", "五位有效数字相同"],
], [2.9, 2.73], size=13, rowh=0.6)
order.append(s)

s = content("三维分段：汇流条与指端的损失随段长减小",
            "左图是不同段长的频域响应。段越短，汇流条和指端占比越大，主模分裂成一串小峰。100 微米段只剩一个干净主峰。右图是主峰效率随段长的变化，Shao 型同流程也有同样的损失。")
pic(s, "fig_3d.png", 0.5, 1.25, w=8.0)
table(s, 8.7, 1.35, 4.03, [
    ["配置", "相对无汇流条"],
    ["25 µm 段，汇流条 2 µm", "1.9–3.4"],
    ["50 µm 段，汇流条 2 µm", "2.0"],
    ["100 µm 段，汇流条 2 µm", "1.44"],
    ["100 µm，汇流条 0.5 µm", "1.11"],
    [[("+ 周期 1.84 µm", True)], [("1.10", True)]],
    ["+ 支撑梁", "1.22"],
], [2.6, 1.43], size=12.5, rowh=0.5)
text(s, 0.6, 4.6, 12.1, 1.5, [
    "汇流条与指端打破沿波导的均匀性，主模分裂成间距 0.3–1 MHz 的一串模式，Δn₀ 分散到几个模上",
    "刻槽隔断相邻段无效：分裂来自段内汇流条区，而不是段间耦合",
    "Shao 型同流程：25 µm 段约 2 倍，100 µm 段约 1.2 倍——不是本设计特有",
], size=14, bullet=True, spacing=6)
order.append(s)

s = content("功率链：L = 1 mm 约 3.26 mW（仿真）",
            "左图是功率逐项计入的过程：二维 2.46 毫瓦，三维汇流条升到 3.9，优化后 2.85，加梁和引线到 3.26。右边是头条数据。等效电压 0.57 伏是匹配负载端的峰值，和文献 Vπ 定义不同，不能直接比较。")
pic(s, "fig_chain.png", 0.45, 1.25, w=7.6)
table(s, 8.25, 1.3, 4.48, [
    ["项目", "数值（仿真）"],
    ["谐振频率", "3.333 GHz"],
    ["驱动 Q", "1930–1970（假设损耗）"],
    ["PπL（含梁）", "2.87×10⁻⁶ W·m"],
    [[("信号源功率 Pπ", True)], [("3.26 mW", True)]],
    ["乘校准系数后", "5.5–17 mW"],
    ["输入阻抗", "53–57 Ω"],
    ["等效电压（负载端峰值）", "0.57 V"],
    ["L = 2 mm（粗估）", "约 1.8 mW"],
], [2.3, 2.18], size=12.5, rowh=0.46)
conclusion(s, 5.95, "各环节在模型范围内没有发现阻断性问题；绝对数值不确定度为数倍（校准系数与 Q 均待实测）", h=0.6)
order.append(s)

s = content("工艺容差与段间失谐",
            "左表是工艺偏差对单段的影响：膜厚和周期主要移频率，刻蚀深度主要影响效率。右表是段间随机失谐的影响。sigma 为 1 MHz 时，两串五并功率增加 27%，全并联只增加 8%。失谐未知时用全并联保底。")
table(s, 0.6, 1.3, 6.1, [
    ["偏差", "Δf", "PπL 变化"],
    ["膜厚 −10 / +10 nm", "+4.2 / −4.4 MHz", "+0.3% / −0.2%"],
    ["刻蚀浅 / 深 10 nm", "−0.1 / 0 MHz", "+6.9% / −6.3%"],
    ["周期 ±1%（±19 nm）", "∓25 MHz", "约 ±2%"],
], [2.4, 1.85, 1.85], size=13, rowh=0.5)
text(s, 0.6, 3.45, 6.1, 1.6, [
    "主峰 FWHM 约 1.7 MHz",
    "段间 1 MHz 失谐 ≈ 膜厚差 2.3 nm 或周期差 0.75 nm",
    "周期由光刻一次定义，段间差应远小于 1 nm；主要看膜厚均匀性",
], size=14, bullet=True, spacing=6)
table(s, 7.0, 1.3, 5.73, [
    ["接法（中位 / P90）", "σ = 0.5 MHz", "σ = 1 MHz", "σ = 2 MHz"],
    ["2 串 × 5 并", "1.10 / 1.20", "1.27 / 1.47", "1.71 / 2.38"],
    ["10 并", "1.02 / 1.04", "1.08 / 1.17", "1.37 / 1.96"],
    ["5 串 × 2 并", "1.06 / 1.14", "1.20 / 1.67", "2.05 / 2.92"],
], [1.8, 1.3, 1.3, 1.3], size=12.5, rowh=0.5)
text(s, 7.0, 3.45, 5.7, 1.6, [
    "数值为相对无失谐的功率倍数，L = 1 mm，每点 100 次随机",
    "串联段电流相同、电压按阻抗分配，失谐段分到的电压不对；并联段自动均衡",
], size=13, bullet=True, spacing=6)
conclusion(s, 5.6, "要把功率增量控制在约 30% 以内，需段间 σ 在 1 MHz 左右以内（膜厚差约 2.3 nm 以内）；不确定时用全并联（基准功率高约 20%）", h=0.75)
order.append(s)

s = content("光学：过渡、空气桥与引线",
            "光学上三项都可以忽略：悬空和普通波导之间的过渡每个 0.025 dB；空气桥离脊顶 1 微米以上看不出影响；引线主要是串联电阻，厚引线只增加 3 到 4%。唯一要注意的是普通波导段 BOX 不能小于 2 微米。")
table(s, 0.6, 1.3, 12.13, [
    ["项目", "仿真结果", "结论"],
    ["悬空 ↔ 普通波导过渡（二维模式匹配）", "T = 0.99429，每个 0.025 dB；R = 6.5×10⁻⁶", "1 mm 两端共约 0.05 dB，不需锥形过渡"],
    ["普通段 BOX 厚度", "2 / 4 µm 漏光可忽略；1 µm 时 0.55 dB/cm", [("BOX 需 ≥ 2 µm", True)]],
    ["空气桥（C 型走线）", "桥底离脊顶 0.5 µm：每座约 4.4×10⁻⁵ dB；≥ 1 µm：与无桥相同", "光学上不是障碍"],
    ["引线轨（二维静电）", "0.09–0.13 pF/mm，0.49–0.64 nH/mm，Z₀ 62–84 Ω", "影响主要来自串联电阻"],
    ["引线代价", "500 nm 铝、≥ 50 µm 轨：+3–4%；100 nm 薄窄轨：+10–17%", "用厚引线"],
], [3.5, 5.2, 3.4], size=13, rowh=0.62)
text(s, 0.6, 5.3, 12.1, 0.9, [
    "未覆盖：释放边缘的三维形貌（刻蚀斜面、底切、侧壁粗糙度散射）、光纤端面耦合——前者靠截断法实测，后者沿用成熟结构",
], size=13, bullet=True, color=GRAY)
order.append(s)

s = content("实验数据现状：尚无实测，以下为计划测量项",
            "需要说明：目前没有任何实测数据，也没有流片。表里左列是仿真预测，右列是流片后要测的量。唯一用到的实验数据是 Shao 2019 的文献值，用来做模型校准。")
table(s, 0.6, 1.3, 12.13, [
    ["物理量", "仿真预测（本工作）", "实测", "计划测量方法"],
    ["谐振频率", "3.333 GHz", "无", "VNA 测 S11"],
    ["驱动 Q", "≈ 2000（由假设损耗给出）", "无", "S11 半高宽"],
    ["输入阻抗", "53–57 Ω", "无", "S11，引线去嵌入"],
    ["信号源功率 Pπ", "3.26 mW（校准后 5.5–17 mW）", "无", "相位调制边带比 / MZI"],
    ["过渡与传播损耗", "0.025 dB / 个；0.00053 dB/cm", "无", "不同悬空长度的截断法"],
    ["f 对周期斜率", "−1.33 MHz/nm", "无", "周期系列（G3）"],
], [2.2, 3.9, 1.2, 4.8], size=13.5, rowh=0.55)
box(s, 0.6, 5.35, 12.13, 0.95, fill=PINK, line=LRED, lines=[
    "唯一引用的实验数据：Shao 等（Optica 2019）实测 VπL = 0.046 V·cm、Q 最高约 3600——仅用于校准本流程，",
    "校准系数 1.7–5.3 需在本批工艺上用 Shao 复刻结构（G8）重新确定"], size=14, color=RED, bold=True)
order.append(s)

s = content("覆盖范围与主要风险",
            "这一页列出还没覆盖的部分。最需要工艺侧意见的是机械可行性，也就是梁和薄膜的应力、释放。其次是工艺参数，现在用的都是假设值，拿到实际值以后重算只要几分钟。")
table(s, 0.6, 1.3, 12.13, [
    ["项目", "现状", "可能影响", "处理"],
    ["绝对精度", "校准系数 1.7–5.3；Q 为假设，功率 ∝ 1/Q", "功率偏差数倍", "流片后测 Q 与 Pπ，更新校准"],
    ["机械可行性", [("未算", True)], "释放、塌陷、翘曲", "需工艺侧应力与释放条件（A7）"],
    ["工艺参数", "膜厚、BOX、金属厚度、衬底均为假设", "频率中心、引线损耗", "参数到手 < 1 小时重算（A3）"],
    ["沿波导声学端部", [("未算", True), ("（三维为周期边界）", False)], "端部段响应、侧模、Q", "有限长三维（A2，先估内存）；长度系列实测"],
    ["斜侧壁", "三维未做", "Δn₀、f 的敏感度未知", "A4，可后置"],
    ["段间均匀性", "未假设具体数值", "σ > 1 MHz 时功率明显上升", "查晶圆规格；版图带全并联保底"],
    ["查新", "仅网页检索；Freedman 2025 最接近", "新颖性论证", "WoS / CNKI / 专利库全文（A8）"],
], [2.0, 3.8, 2.8, 3.5], size=13, rowh=0.58, bold_col0=True)
order.append(s)

# ---------------- 04 流片计划 ----------------
order.append(sec_slides[3])
s = content("如果加入流片：操作流程",
            "如果要加入流片，建议按这八步走。前两步是确定代工厂和班车截止日期，拿到实际工艺参数后重算。然后画版图，做成变体扫描而不是单一设计。下单以后同步准备测试平台。测完用实测的 Q 和 P pi 更新校准，再决定二轮设计。")
flow = [
    ("1 选定代工与班车", "MPW 截止日期\n设计规则、掩模网格"),
    ("2 工艺参数确认", "膜厚、BOX、金属厚度\n薄膜应力、释放条件"),
    ("3 按实际参数重算", "A3（<1 h）、A7 机械\n视内存做 A2 / A5"),
    ("4 版图 GDS", "主设计 + 变体 G1–G9\n测试结构、对准标记"),
    ("5 DRC 与评审", "代工厂规则检查\n机械可行性确认"),
    ("6 下单流片", "同步准备测试平台\nVNA、探针台、光路"),
    ("7 测试", "S11 / 边带比 / 截断法\n长度、周期系列"),
    ("8 校准与二轮", "实测 Q、Pπ 更新校准\n定接法与二轮设计"),
]
for k, (a, b) in enumerate(flow):
    row, col = divmod(k, 4)
    x = 0.6 + col * 3.1
    y = 1.35 + row * 2.3
    box(s, x, y, 2.75, 0.62, fill=RED, lines=[a], size=15, bold=True)
    box(s, x, y + 0.72, 2.75, 1.05, fill=WHITE, line=LRED, lines=b.split("\n"), size=14, color=DARK)
    if col < 3:
        a_ = s.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, Inches(x + 2.8), Inches(y + 0.18), Inches(0.26), Inches(0.26))
        a_.fill.solid(); a_.fill.fore_color.rgb = LRED; a_.line.fill.background()
conclusion(s, 6.05, "下单前必须确认：机械可加工性（工艺侧）、BOX ≥ 2 µm、版图带全并联保底变体", h=0.6)
order.append(s)

s = content("版图变体建议（一次流片做成扫描）",
            "一个设计一个版本风险太大，建议做成扫描。G1 是主设计，G2 是全并联保底，G3 周期系列找频率，G4 长度系列拆端部效应，G8 是 Shao 复刻结构，用来在同一批工艺上做校准。具体档位要看代工厂的设计规则。")
table(s, 0.6, 1.3, 12.13, [
    ["组", "变体", "目的", "仿真预测"],
    ["G1", "主设计：10 × 100 µm，2 串 × 5 并，汇流条 0.5 µm，周期 1.84 µm，梁 2 µm，500 nm 铝引线", "基准", "3.333 GHz；3.26 mW"],
    ["G2", "同几何，全并联（10 并）", "失谐未知时保底", "3.46–3.68 mW"],
    ["G3", "周期系列：1.84 µm 为中心，步长约 2 nm，5 档", "测 f(p) 斜率，对准目标频率", "−1.33 MHz/nm"],
    ["G4", "长度系列：0.1 / 0.2 / 0.5 / 1 / 2 mm", "Pπ 随长度、端部效应", "近似 ∝ 1/L"],
    ["G5", "段长对照：25 / 50 / 100 µm", "验证三维汇流条损失", "3.4 / 2.0 / 1.44 倍"],
    ["G6", "汇流条 0.3 / 0.5 / 0.7 µm", "线宽偏差余量", "PπL 2.53 / 2.58 / 2.79"],
    ["G7", "梁宽 1 / 2 / 4 µm；每段 / 每 2 段 / 每 5 段一根", "机械良率与声学损失折中", "每段一根 ×1.11"],
    ["G8", "Shao 2019 复刻结构（100 µm）", "本批工艺上校准", "PπL 2.36×10⁻⁶ W·m"],
    ["G9", "测试结构：无电极悬空波导、单叉指 S11、引线 open/short/thru、膜厚监测、电阻链", "光学、电学参数分开测", "过渡 0.025 dB / 个"],
], [0.6, 5.6, 3.1, 2.8], size=12, rowh=0.5, bold_col0=True)
text(s, 0.6, 6.45, 12.1, 0.4, ["具体档位受代工厂设计规则与掩模网格限制，待确认"], size=12, color=GRAY)
order.append(s)

s = content("测试方案与数据处理",
            "测试分电学和光学。电学用 VNA 测 S11，得到谐振频率、Q 和输入阻抗。光学用边带比或 MZI 测 P pi。用长度系列拆端部效应，用无电极波导扣除光学损耗。最后用实测 Q 反推 delta n，和仿真比较，更新校准系数。")
text(s, 0.6, 1.3, 6.0, 4.6, [
    [("电学（VNA）：", True), ("S11 → 谐振频率、Q（FWHM）、Re Y 与输入阻抗，与 3.333 GHz、53–57 Ω 比较", False)],
    [("光学：", True), ("相位调制边带比或 MZI 偏置法 → Pπ（或 Vπ）", False)],
    [("拆分：", True), ("G4 长度系列拆端部效应；G9 无电极波导扣除过渡与传播损耗", False)],
    [("接法决策：", True), ("以 G1 与 G2 的差别判断实际段间失谐，决定 2 串 × 5 并还是全并联", False)],
], size=15, bullet=True, spacing=10)
box(s, 6.9, 1.3, 5.83, 0.6, fill=RED, lines=["校准更新"], size=17, bold=True)
box(s, 6.9, 2.0, 5.83, 3.0, fill=WHITE, line=LRED, lines=[
    "实测 Q 代入",
    "PπL = ħω²λ² / (4 Q Lₐ Δn₀²)，Lₐ = 100 µm",
    "反推 Δn₀，与仿真比较",
    "校准系数 1.7–5.3 由 Shao 结构得到，",
    "需用 G8 在本批工艺上重新确定",
], size=19, color=DARK)
conclusion(s, 5.6, "目标：把“仿真 3.26 mW、校准后 5.5–17 mW”收敛为一个实测值，并据此定二轮设计", h=0.6)
order.append(s)

s = content("时间安排（建议）",
            "时间安排是建议值。十月底到十一月上旬确认工艺参数并重算；十一月中旬画版图；十一月下旬评审下单。代工周期按两到三个月假设，以代工厂为准。等待期间做端部、斜壁仿真和查新。二月到三月测试，四月更新校准并决定二轮。")
plan = [
    ("2026.10下–11上", "工艺参数确认", "代工厂 / 班车；A3、A7；视内存 A2、A5"),
    ("2026.11中", "版图 GDS", "主设计 + G1–G9；DRC"),
    ("2026.11下", "评审与下单", "代工厂评审；机械可行性确认"),
    ("2026.12–2027.02", "代工流片", "周期按 2–3 个月假设；同期 A4、A6、A8，搭测试平台"),
    ("2027.02–03", "测试", "电学 S11、光学 Pπ、截断法"),
    ("2027.04", "校准与二轮", "更新校准系数；定接法；二轮设计"),
]
line = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.6), Inches(3.75), Inches(12.13), Inches(0.06))
line.fill.solid(); line.fill.fore_color.rgb = LRED; line.line.fill.background()
for k, (d, a, b) in enumerate(plan):
    x = 0.6 + k * 2.04
    dot = s.shapes.add_shape(MSO_SHAPE.OVAL, Inches(x + 0.83), Inches(3.63), Inches(0.3), Inches(0.3))
    dot.fill.solid(); dot.fill.fore_color.rgb = RED; dot.line.color.rgb = WHITE
    up = k % 2 == 0
    y0 = 1.3 if up else 4.15
    box(s, x, y0, 1.95, 0.6, fill=RED, lines=[a], size=17, bold=True)
    text(s, x, y0 + 0.65, 1.95, 0.4, [d], size=15, color=RED, align=PP_ALIGN.CENTER, bold_first=True)
    text(s, x, y0 + 1.1, 1.95, 1.3, [b], size=14, color=DARK, align=PP_ALIGN.CENTER)
text(s, 0.6, 6.55, 12.1, 0.45, ["时间为建议值；代工周期与班车截止日期以代工厂为准。A2–A8 为报告中的仿真与核对任务编号。"],
     size=13, color=GRAY)
order.append(s)

order.append(end)

# ---------------- 删除未用模板页并排序 ----------------
lst = prs.slides._sldIdLst
order_ids = [sl.slide_id for sl in order]
keep_ids = set(order_ids)
for sid in list(lst):
    sl_id = int(sid.get("id"))
    if sl_id not in keep_ids:
        rid = sid.get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id")
        prs.part.drop_rel(rid)
        lst.remove(sid)
id_el = {int(e.get("id")): e for e in lst}
for e in list(lst):
    lst.remove(e)
for i in order_ids:
    lst.append(id_el[i])

prs.save(OUT)
print("saved", OUT, len(order), "slides")
