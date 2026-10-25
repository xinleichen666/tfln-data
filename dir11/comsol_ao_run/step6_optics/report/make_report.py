# -*- coding: utf-8 -*-
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

D=r'D:\comsol_ao_run\step6_optics\report'
pdfmetrics.registerFont(TTFont('MSYH', r'C:\Windows\Fonts\msyh.ttc'))
pdfmetrics.registerFont(TTFont('MSYHBD', r'C:\Windows\Fonts\msyhbd.ttc'))
st=getSampleStyleSheet()
H1=ParagraphStyle('H1',fontName='MSYHBD',fontSize=16,spaceAfter=8,textColor=colors.HexColor('#1a3a5c'))
H2=ParagraphStyle('H2',fontName='MSYHBD',fontSize=12,spaceBefore=10,spaceAfter=4,textColor=colors.HexColor('#1a3a5c'))
B=ParagraphStyle('B',fontName='MSYH',fontSize=9.5,leading=14)
TINY=ParagraphStyle('TINY',fontName='MSYH',fontSize=8,leading=11)

doc=SimpleDocTemplate(os.path.join(D,'TFLN_AOM_设计报告_v2.pdf'),pagesize=A4,
  leftMargin=16*mm,rightMargin=16*mm,topMargin=14*mm,bottomMargin=14*mm,
  title='TFLN 声光调制器设计报告')
E=[]
def P(t,s=B): E.append(Paragraph(t,s))
def IMG(f,w=170*mm):
    from PIL import Image as PILImage
    iw,ih=PILImage.open(os.path.join(D,f)).size
    E.append(Image(os.path.join(D,f),width=w,height=w*ih/iw))

P('悬空 TFLN 声光调制器：仿真设计、复现校准与流片要点（内部报告）',H1)
P('日期：2026-10-25 ｜ 口径：预测仿真，非实验；校准锚：Shao et al., Optica 6, 1498 (2019)')
E.append(Spacer(1,4*mm))

P('1. 口径声明',H2)
P('本报告全部数字来自 COMSOL 多物理场仿真（声-电-光三域），并经同一流程对 Shao 2019 器件的复现校准。'
  '未流片、无实测；所有功率数字附带校准区间（§4）。')
P('2. 器件截面',H2)
P('图 1：Shao 2019 校准截面（路A PAP1 口径）。悬空 X 切 LN 膜宽 10 µm、膜厚 0.8 µm（板 0.4 + 脊 0.4 µm），'
  '脊顶宽 0.95 µm、侧壁 70°（脊中心距左缘 2.6 µm）；4 根金指（75 nm Au + 8 nm Cr），指宽 0.30 µm、周期 0.60 µm，'
  '首指中心 5.875 µm。')
IMG('fig_xsec_shao.png')
P('图 2：本设计（Step 7）截面：周期回调 1.84 µm、NP=7 超胞（中间 3 个周期放波导）、段长 100 µm、汇流条 0.5 µm、指端 0.5 µm。')
IMG('fig_xsec_design.png')
P('图 3：z 向分段布局：1 mm = 10×100 µm 段，2 串 × 5 并配 50 Ω。')
IMG('fig_zseg.png')
P('图 4：梯形侧壁角扫（三维）：70° 为工艺最优（|Δn_eff|/V 最高、1 mm 源功率最低）。')
IMG('fig_trap.png')

P('3. 关键结果',H2)
t3=Table([
 ['项目','数值','口径'],
 ['3D 100µm 段主峰 |Δn_eff|/V','3.32e-3（矩形 90°）/ 2.18e-3（梯形 70°）','每伏指间电压'],
 ['驱动 Q','1931–2007','主峰 FWHM'],
 ['1 mm 驱动功率（仿真/匹配）','2.85 mW（2 串×5 并，48 Ω）','50 Ω 源，含失配'],
 ['1 mm 功率（路A校准后）','1.7–5.4 mW（锚定 k62：1.8 mW）','功率带 ×0.6–1.9'],
 ['梯形 70° 光学损耗','≤5e-4 dB/cm（TE0，neff 1.946）','数值底噪'],
 ['分段模化','主模分裂 0.3–1 MHz；1 µm 汇流条为"坏宽度"；0.5 µm 收敛','三维 z 模混合'],
 ['支撑梁（每段一根 2 µm + PML）','损失 1.11×，Q 不降','锚点漏能'],
 ['膜厚容差 ±10 nm','频率 ±4.4 MHz；效率 ±7%（刻蚀深）','二维 FN7'],
 ['脊位置容差','±0.4 µm 使主模族耦合降 2–40×（建议按 ±0.2 µm 控制）','路A XR 扫'],
],colWidths=[62*mm,66*mm,42*mm])
t3.setStyle(TableStyle([('FONTNAME',(0,0),(-1,-1),'MSYH'),('FONTNAME',(0,0),(-1,0),'MSYHBD'),
 ('FONTSIZE',(0,0),(-1,-1),8),('GRID',(0,0),(-1,-1),0.4,colors.grey),('VALIGN',(0,0),(-1,-1),'MIDDLE')]))
E.append(t3)

P('4. 模型校准（路A，Shao 2019 五模逐模对齐）',H2)
t4=Table([
 ['Shao 模 (GHz)','模型模','f','Δn0 比','备注'],
 ['1.55（tot 32.3）','k29 @1.535','−1.0%','1.07×','EO 主导'],
 ['2.17（tot 71.7）','k39 @2.140','−1.4%','1.53×（PAP1C 口径 1.37×）','EO 主导'],
 ['2.40（tot 17.2）','k43 @2.348','−2.2%','0.81×',''],
 ['3.16（tot 65.0）','k58 @3.151','−0.3%','1.13×','PE+EO'],
 ['3.24（tot 102.5）','k62 @3.272','+1.0%','0.79×','Fig.S2 场指纹认定'],
],colWidths=[34*mm,34*mm,20*mm,26*mm,56*mm])
t4.setStyle(TableStyle([('FONTNAME',(0,0),(-1,-1),'MSYH'),('FONTNAME',(0,0),(-1,0),'MSYHBD'),
 ('FONTSIZE',(0,0),(-1,-1),8),('GRID',(0,0),(-1,-1),0.4,colors.grey),('VALIGN',(0,0),(-1,-1),'MIDDLE')]))
E.append(t4)
P('实测锚：VπL = 0.058 V·cm（模型）对 0.046 V·cm（Shao 实测，3.33 GHz），模型保守 1.26×（功率 1.6×）。'
  '迁移到本设计结构时，功率按 ×0.6–1.9 区间引用（锚定 k62 为 ×0.63）。')

P('5. 设计规则与流片要点',H2)
t5=Table([
 ['参数','设计值','备注'],
 ['周期','1.84 µm','回调到 3.33 GHz；±1% → ∓25 MHz'],
 ['段长 / 拓扑','100 µm；1 mm 为 2 串×5 并','段长越长模式分裂越弱'],
 ['汇流条','0.5 µm（避开 1 µm 坏宽度）','0.3–0.7 µm 内平滑'],
 ['侧壁角','70°（工艺窗口内最优）','60–75° 已扫'],
 ['脊位置','XR=2.6 µm；对准容差 ±0.2 µm','关键尺寸，主模族对其极敏感'],
 ['膜厚','800 nm（板 400 + 脊 400）','±10 nm → ±4.4 MHz'],
 ['支撑梁','每段间隙两侧各 1 根 2 µm，信号/地同梁','损失 1.11×'],
],colWidths=[34*mm,64*mm,72*mm])
t5.setStyle(TableStyle([('FONTNAME',(0,0),(-1,-1),'MSYH'),('FONTNAME',(0,0),(-1,0),'MSYHBD'),
 ('FONTSIZE',(0,0),(-1,-1),8),('GRID',(0,0),(-1,-1),0.4,colors.grey),('VALIGN',(0,0),(-1,-1),'MIDDLE')]))
E.append(t5)

P('6. 流片前未闭环事项',H2)
P('(1) 悬空膜应力/翘曲与支撑梁机械强度（需工艺侧膜应力数据）；(2) 版图级设计冻结（空气桥、焊盘、引出线寄生）；'
  '(3) 校准可迁移性自检（在 NP=7 结构上重复场指纹一致性）；(4) UDT 单向化（约 3 dB，留作 v2 改进项）。')
P('附：数据文件（dir11/comsol_ao_run/step6_optics/，commit 166751c 及之前）：summary_routeA.md、summary_step7*.md、'
  'Step6iCal*.java、step6i_cal_*.log、Step7*.java 等。')
doc.build(E)
print('PDF built:', os.path.getsize(os.path.join(D,'TFLN_AOM_设计报告_v2.pdf')))
