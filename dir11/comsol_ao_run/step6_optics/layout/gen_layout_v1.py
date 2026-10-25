# -*- coding: utf-8 -*-
"""First-pass GDS for the segmented TFLN AOM (all-parallel wiring).
ASSUMPTIONS (to be confirmed with process):
 - all-parallel: one signal rail + one ground rail along the 1 mm device
 - GSG pads 100x100 um, pitch 150 um, placed at z>1000 (one end)
 - layers: 1 = LN ridge/etch, 2 = metal (IDT/busbar/rail/pad), 3 = release slots, 4 = alignment, 5 = air-bridge (draft)
 - suspended strip 13.5 um wide, slots 2.5 um, ridge 0.95 um top width (mask = top width, 70 deg sidewall by RIE)
"""
import gdstk, os
D=r'D:\comsol_ao_run\step6_optics\layout'
os.makedirs(D, exist_ok=True)
P=1.84; DUTY=0.5; WF=P*DUTY          # finger width/period (um)
NF=7                                  # fingers per segment
NS=10; SEG=100.0                      # 10 segments x 100 um = 1 mm
GAP=0.5; BB=2.0                       # segment gap, busbar width (z)
FEG=0.5                               # finger-end gap
OVL=SEG-GAP-BB-FEG-FEG-BB-GAP         # 94 um overlap
W_MEM=13.5; SLOT=2.5                  # suspended strip, slot width
RIDGE_W=0.95; RIDGE_X=0.0
RAIL_X=20.0; RAIL_W=8.0; LEAD_W=1.2
PAD=100.0; PAD_PITCH=150.0
L_RIDGE,L_MET,L_SLOT,L_ALIGN,L_BRG=1,2,3,4,5

lib=gdstk.Library(unit=1e-6, precision=1e-9)
dev=lib.new_cell('DEVICE')
dev.add(gdstk.rectangle((RIDGE_X-RIDGE_W/2, 0.0),(RIDGE_X+RIDGE_W/2, NS*SEG), layer=L_RIDGE))
xs=RIDGE_X-W_MEM/2
dev.add(gdstk.rectangle((xs-SLOT, 0.0),(xs, NS*SEG), layer=L_SLOT))
xe=RIDGE_X+W_MEM/2
dev.add(gdstk.rectangle((xe, 0.0),(xe+SLOT, NS*SEG), layer=L_SLOT))
cent=[RIDGE_X+(i-(NF-1)/2)*P for i in range(NF)]
sig=[i for i in range(NF) if i%2==0]; gnd=[i for i in range(NF) if i%2==1]
for s in range(NS):
    z0=s*SEG
    zb_sig=z0+GAP                        # signal busbar z start
    z_over=z0+GAP+BB+FEG                 # overlap start
    z_end=z_over+OVL                     # 94
    zb_gnd=z_end+FEG                     # ground busbar start
    for i in range(NF):
        x=cent[i]
        if i%2==0:
            dev.add(gdstk.rectangle((x-WF/2, zb_sig+BB),(x+WF/2, z_end), layer=L_MET))
        else:
            dev.add(gdstk.rectangle((x-WF/2, z_over),(x+WF/2, zb_gnd), layer=L_MET))
    xsl=min(cent[i] for i in sig)-WF/2; xsr=max(cent[i] for i in sig)+WF/2
    dev.add(gdstk.rectangle((xsl, zb_sig),(xsr, zb_sig+BB), layer=L_MET))
    xgl=min(cent[i] for i in gnd)-WF/2; xgr=max(cent[i] for i in gnd)+WF/2
    dev.add(gdstk.rectangle((xgl, zb_gnd),(xgr, zb_gnd+BB), layer=L_MET))
    dev.add(gdstk.rectangle((-RAIL_X, zb_sig+0.4),(xsl, zb_sig+0.4+LEAD_W), layer=L_MET))
    dev.add(gdstk.rectangle((xgr, zb_gnd+0.4),(RAIL_X, zb_gnd+0.4+LEAD_W), layer=L_MET))
dev.add(gdstk.rectangle((-RAIL_X-RAIL_W/2, 0.0),(-RAIL_X+RAIL_W/2, NS*SEG), layer=L_MET))
dev.add(gdstk.rectangle((RAIL_X-RAIL_W/2, 0.0),(RAIL_X+RAIL_W/2, NS*SEG), layer=L_MET))
ZP=NS*SEG
dev.add(gdstk.rectangle((-RAIL_W/2, ZP),(RAIL_W/2, ZP+60.0), layer=L_MET))
dev.add(gdstk.rectangle((RAIL_X-RAIL_W/2, ZP),(RAIL_X+RAIL_W/2, ZP+60.0), layer=L_MET))
dev.add(gdstk.rectangle((-PAD/2, ZP+50),(PAD/2, ZP+50+PAD), layer=L_MET))
for sgn in (-1,1):
    dev.add(gdstk.rectangle((sgn*PAD_PITCH-PAD/2, ZP+50),(sgn*PAD_PITCH+PAD/2, ZP+50+PAD), layer=L_MET))
dev.add(gdstk.rectangle((0.0, ZP+10),(0.0, ZP+50), layer=L_MET))  # placeholder
for x in (RIDGE_X-RAIL_X-20, RIDGE_X+RAIL_X+20):
    for z in (-40.0, ZP+200.0):
        dev.add(gdstk.rectangle((x-3,z-0.5),(x+3,z+0.5), layer=L_ALIGN))
        dev.add(gdstk.rectangle((x-0.5,z-3),(x+0.5,z+3), layer=L_ALIGN))
lib.write_gds(os.path.join(D,'aom_1mm_allparallel_v1.gds'))
dev.write_svg(os.path.join(D,'aom_1mm_allparallel_v1.svg'), scaling=4.0)
spec=[]
spec.append('# 版图 first-pass 规格（全并联）\n')
spec.append('| 参数 | 值 |'); spec.append('|---|---|')
for k,v in [('周期 P',f'{P} um'),('指宽/占空',f'{WF:.2f} um / {DUTY}'),('每段指数',f'{NF}'),('段数×段长',f'{NS} × {SEG:.0f} um = 1 mm'),
            ('段间隙 / 总线宽',f'{GAP} / {BB} um'),('指端间隙',f'{FEG} um'),('叉指重叠',f'{OVL:.1f} um'),
            ('悬空带宽 / 槽宽',f'{W_MEM} / {SLOT} um'),('脊顶宽',f'{RIDGE_W} um (掩模=顶宽, 70° RIE)'),
            ('信号/地总线',f'x=±{RAIL_X:.0f} um, 宽 {RAIL_W:.0f} um'),('引出线宽',f'{LEAD_W} um'),
            ('GSG 焊盘',f'{PAD:.0f}×{PAD:.0f} um, pitch {PAD_PITCH:.0f} um')]:
    spec.append(f'| {k} | {v} |')
spec.append('\n## 层定义\n')
spec.append('| 层 | 用途 |'); spec.append('|---|---|')
for a,b in [(L_RIDGE,'LN 脊/刻蚀掩模（顶宽 0.95）'),(L_MET,'金属：指/总线/轨/焊盘'),(L_SLOT,'释放槽'),(L_ALIGN,'对准标记'),(L_BRG,'空气桥（草稿，未布线）')]:
    spec.append(f'| {a} | {b} |')
spec.append('\n## 未决事项（画最终版前必须确认）\n')
spec.append('1. 引出线/轨跨越释放槽：全并联需要信号/地轨在悬空区外，但每段引出线必须跨槽 → 需支撑梁走线或空气桥；本版为草稿直连。')
spec.append('2. 左侧地焊盘与信号焊盘之间的跨线：GSG 布局要求地-信号-地，引入线交叉需空气桥层；本版未处理交叉。')
spec.append('3. 工艺层映射（GDS layer → 实际掩模层）与 DRC 规则待流片平台确认。')
spec.append('4. 悬空带宽度 13.5 um、槽宽 2.5 um、焊盘位置为假设值。')
open(os.path.join(D,'layout_spec_v1.md'),'w',encoding='utf-8').write('\n'.join(spec)+'\n')
# DRC-ish report
print('polygons:', len(dev.polygons))
print('bbox:', dev.bounding_box())
print('min widths: ridge %.2f, finger %.2f, busbar %.1f, rail %.1f, lead %.1f' % (RIDGE_W,WF,BB,RAIL_W,LEAD_W))
print('min gaps: finger %.2f, slot %.1f, segment %.1f' % (P-WF,SLOT,GAP))
print('written GDS/SVG/spec')
