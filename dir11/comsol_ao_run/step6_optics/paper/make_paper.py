# -*- coding: utf-8 -*-
import os
from docx import Document
from docx.shared import Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
def EAF(r,name):
    rPr=r._element.get_or_add_rPr()
    rf=rPr.find(qn('w:rFonts'))
    if rf is None:
        rf=OxmlElement('w:rFonts'); rPr.append(rf)
    rf.set(qn('w:eastAsia'),name)


D=r'D:\comsol_ao_run\step6_optics\paper'
os.makedirs(D, exist_ok=True)
FIG=r'D:\comsol_ao_run\step6_optics\report'

doc=Document()
# global font
st=doc.styles['Normal']; st.font.name='Times New Roman'; st.font.size=Pt(10.5)
EAF_run=None  # noop

def H(t,l=0):
    p=doc.add_heading('',level=l)
    r=p.add_run(t); r.font.name='黑体'; EAF(r,'黑体'); r.font.color.rgb=RGBColor(0,0,0)
    return p
def P(t,bold=False):
    p=doc.add_paragraph(); r=p.add_run(t); r.bold=bold; return p
def CAP(t):
    p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER
    r=p.add_run(t); r.italic=True; r.font.size=Pt(9); return p
def ADDIMG(f,w=15):
    doc.add_picture(os.path.join(FIG,f), width=Cm(w))
    doc.paragraphs[-1].alignment=WD_ALIGN_PARAGRAPH.CENTER

# ---- title
p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER
r=p.add_run('毫米级长孔径分段悬空铌酸锂薄膜声光调制器：\n设计、复现校准与可制造性'); r.bold=True; r.font.size=Pt(16); EAF(r,'黑体')
P('Millimeter-scale segmented suspended thin-film lithium-niobate acousto-optic modulator: design, replication-based calibration, and manufacturability',bold=True)
p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER
p.add_run('（内部工作稿 · 仿真口径 · 未流片 · 待翻译成英文）').italic=True

# abstract
H('摘要')
P('悬空 X 切铌酸锂薄膜（TFLN）声光调制器是微波-光相干转换的有力平台，但现有器件多为百微米级单腔，长孔径化与可制造性研究不足。'
  '本文提出一种 1 mm 长、分段馈电的 TFLN 声光相位调制器：10 段 × 100 µm 叉指换能器（IDT），周期 1.84 µm，'
  '全并联或 2 串×5 并配 50 Ω，波导为 70° 斜壁脊。首先用同一套三维多物理场流程复现 Shao 等（Optica 6, 1498, 2019）的器件，'
  '五个声学模式单声子折射率变化 Δn₀ 与文献值吻合到 0.79–1.53×，半波电压-长度积 VπL = 0.058 V·cm 对实测 0.046 V·cm'
  '（模型保守 1.26×），据此给出功率校准带 0.6–1.9×。随后系统研究分段换能器的 z 向模式分裂（0.3–1 MHz）、'
  '汇流条"坏宽度"、侧壁角与制造容差。结果表明：周期 1.84 µm、段长 100 µm、汇流条 0.5 µm、脊位置容差 ±0.2 µm 为设计点，'
  '1 mm 器件驱动功率 2.85 mW（仿真）、1.7–5.4 mW（校准后）；斜壁 70° 只使功率增加约 1.7×、光学损耗不变（≤5e-4 dB/cm）。'
  '本工作为长孔径 TFLN 声光调制器提供了一套带校准误差棒、面向流片的设计规范。')

H('1. 引言')
P('声光（AO）效应在微波光子学、激光稳频与量子换能中应用广泛。悬空 TFLN 因低声损耗、强压电与电光系数，'
  '被用于实现高性能声光调制器 [S1–S2]。Shao 等 2019 年报道了 100 µm 孔径、3.33 GHz、VπL=0.046 V·cm 的器件，'
  '证明了该平台的可行性 [S1]。然而，向毫米级长孔径扩展时，叉指换能器（IDT）的馈电、沿孔径方向的模式分裂、'
  '以及斜壁刻蚀等制造约束缺乏系统性研究。本文针对这三个问题：') 
P('(i) 提出分段 IDT + 串并联 50 Ω 匹配的长孔径架构；',bold=False)
P('(ii) 通过复现 Shao 2019 器件建立模型校准，给出误差带；')
P('(iii) 量化斜壁角、汇流条宽度与制造容差对性能的影响，形成流片设计规范。')

H('2. 器件结构与仿真方法')
P('截面（图 1）：悬空 X 切 LN 膜宽 10 µm、厚 0.8 µm（板 0.4 µm + 脊 0.4 µm），脊顶宽 0.95 µm、侧壁 70°；'
  'IDT 4 指（金 75 nm + Cr 8 nm，指宽 0.30 µm、周期 0.60 µm）——此为校准口径，与 Shao 器件一致。')
ADDIMG('fig_xsec_shao.png')
CAP('图 1  校准截面（Shao 2019 口径）')
P('设计器件（图 2）：周期回调 1.84 µm、NP=7 超胞，段长 100 µm、汇流条 0.5 µm、指端间隙 0.5 µm，'
  '沿波导方向 10 段构成 1 mm，全并联或 2 串×5 并配 50 Ω（图 3）。')
ADDIMG('fig_xsec_design.png'); CAP('图 2  设计截面（周期 1.84 µm）')
ADDIMG('fig_zseg.png'); CAP('图 3  z 向分段布局（10×100 µm，全并联）')
P('仿真采用 COMSOL 多物理场：压电本征模 + 频域驱动，耦合光弹（PE）、电光（EO）与移动边界（MB）三类折射率调制，'
  '按 Shao 定义计算单声子 Δn₀ 与 VπL；光学 TE0 模由二维模式求解得到。网格为截面自由三角形 + 沿 z 扫掠，'
  '详细口径见附录。')

H('3. 模型校准（复现 Shao 2019）')
P('用同一流程复现 Shao 器件截面，逐模对齐其结果（表 1）。五个声学模式频率差 −2.2%…+1.0%，'
  'Δn₀ 吻合 0.79–1.53×（平均 ≈1.1×）；3.24 GHz 模经场分布指纹认定为本模型 k62（电场集中于脊左侧、应变在脊内）。')
tb=doc.add_table(rows=6,cols=5); tb.style='Light Grid Accent 1'; tb.alignment=WD_TABLE_ALIGNMENT.CENTER
hdr=['文献模 (GHz)','本模型模','频率差','Δn₀ 比','备注']
data=[['1.55 (32.3)','k29 @1.535','−1.0%','1.07×','EO 主导'],
      ['2.17 (71.7)','k39 @2.140','−1.4%','1.53×','EO 主导'],
      ['2.40 (17.2)','k43 @2.348','−2.2%','0.81×',''],
      ['3.16 (65.0)','k58 @3.151','−0.3%','1.13×','PE+EO'],
      ['3.24 (102.5)','k62 @3.272','+1.0%','0.79×','场指纹认定']]
for j,h in enumerate(hdr): tb.rows[0].cells[j].text=h
for i,row in enumerate(data,1):
    for j,v in enumerate(row): tb.rows[i].cells[j].text=v
CAP('表 1  Shao 2019 五模逐模复现（Δn₀ 单位 1e-12）')
P('实测锚：VπL = 0.058 V·cm（本模型）对 0.046 V·cm（Shao 实测，3.33 GHz），模型保守 1.26×（功率 1.6×）。'
  '据此对本设计的功率预测施加 ×0.6–1.9 校准带（锚定 k62 为 ×0.63）。')

H('4. 结果')
H('4.1 分段换能器的模式分裂',1)
P('含汇流条后，原本单一主模分裂为 3.20–3.22 GHz 内间距 0.3–1 MHz 的一串模式（z 向不同阶混合），'
  '单模 Δn₀ 从 225 分散到 113–152。段长越长、汇流条越窄，分裂越弱：100 µm 段仅 1.10–1.45× 损失。'
  '发现汇流条 1 µm 为"坏宽度"（旁模合并、主峰展宽），0.5 µm 收敛且 0.3–0.7 µm 内平滑。')
H('4.2 设计规则与制造容差',1)
tb2=doc.add_table(rows=7,cols=3); tb2.style='Light Grid Accent 1'
hdr2=['参数','设计值','备注']
data2=[['周期','1.84 µm','回调到 3.33 GHz；±1% → ∓25 MHz'],
       ['段长/拓扑','100 µm；全并联（2串×5并备用）','段长越长分裂越弱'],
       ['汇流条','0.5 µm（避开 1 µm）','0.3–0.7 µm 平滑'],
       ['脊位置','XR=2.6 µm，对准 ±0.2 µm','主模族对其极敏感（+0.4 µm 掉 2–40×）'],
       ['膜厚','800 nm（板 400+脊 400）','±10 nm → ±4.4 MHz'],
       ['侧壁角','70°','60–75° 已扫，70° 最优']]
for j,h in enumerate(hdr2): tb2.rows[0].cells[j].text=h
for i,row in enumerate(data2,1):
    for j,v in enumerate(row): tb2.rows[i].cells[j].text=v
CAP('表 2  设计规则与容差')
H('4.3 梯形侧壁',1)
P('侧壁角扫（60–75°）表明：70° 为可加工斜壁内的最优（图 4）；相对矩形（90°），3D 耦合降为 0.66×、'
  '1 mm 功率增 1.72×（2.85→4.91 mW），但光学损耗不变（≤5e-4 dB/cm，neff 1.946）。')
ADDIMG('fig_trap.png'); CAP('图 4  梯形侧壁角扫（三维 |Δn_eff|/V 与 1 mm 源功率）')
H('4.4 功率预算',1)
P('1 mm 器件（周期 1.84 µm、0.5 µm 汇流条、全并联）：仿真 2.85 mW，计入校准 1.7–5.4 mW；'
  '计入每段一根支撑梁（1.11×）与引线（1.03×）后仍在该带内。段间失谐 σ=1 MHz 时全并联功率仅 ×1.08，'
  '比串联拓扑稳健。')

H('5. 讨论')
P('与 Shao 2019 对比：同流程、同段长下本设计 P·L 为其 0.77–0.87×（略优，同量级）；主要区别是'
  '长孔径分段架构与匹配馈电，而非效率数量级。局限：本文为仿真口径，校准锚为 Shao 器件的仿真值加一个实测 VπL 点；'
  '校准因子向本设计结构迁移的假设尚未独立验证；应力/翘曲与支撑梁机械强度待工艺数据。'
  '单向换能器（约 3 dB）留作 v2 改进项。')

H('6. 结论')
P('本文给出了一套 1 mm 长、分段馈电的悬空 TFLN 声光调制器设计：经复现 Shao 2019 校准后，'
  '1 mm 驱动功率 1.7–5.4 mW、VπL 与文献同量级，并量化了分段模化、斜壁代价与制造容差。'
  '结果为长孔径 TFLN 声光调制器的流片提供了带误差棒的设计规范。')

H('参考文献（节选）')
P('[S1] L. Shao, et al., "Microwave-to-optical conversion using lithium niobate thin-film acoustic resonators," Optica 6, 1498 (2019).')
P('[S2] L. Shao, et al., "Integrated microwave acousto-optic frequency shifter on thin-film lithium niobate," Opt. Express 28, 23728 (2020).')
P('[S3] Hassanien, et al., 谐振型 TFLN 声光调制器（Vπ 0.54 V, 45 µm）。')
P('注：正文数字全部来自内部仿真与复现校准，未流片、无实验；外部引用前须补全文献条目并按目标期刊改写英文。')

doc.save(os.path.join(D,'TFLN_AOM_论文初稿.docx'))
# markdown source for reference
md=open(os.path.join(D,'manuscript_draft.md'),'w',encoding='utf-8')
md.write('# 论文初稿（中文）\n\n见 docx；此文件为占位。')
md.close()
print('docx saved')
