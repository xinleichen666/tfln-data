# -*- coding: utf-8 -*-
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Rectangle, FancyArrow
import numpy as np, os
plt.rcParams['font.sans-serif']=['Microsoft YaHei','SimHei']
plt.rcParams['axes.unicode_minus']=False
D=r'D:\comsol_ao_run\step6_optics\report'
os.makedirs(D, exist_ok=True)
GOLD='#d4a017'; GND='#8a8a8a'; LN='#7fb3d5'; SUB='#d5d8dc'

def ridge(ax,xc,wt,hr,hsl,ang,color=LN,label=True):
    wb=wt+2*hr/np.tan(np.radians(ang))
    ax.add_patch(Rectangle((0,0),10,hsl,color=color))
    ax.add_patch(Polygon([(xc-wb/2,hsl),(xc+wb/2,hsl),(xc+wt/2,hsl+hr),(xc-wt/2,hsl+hr)],color=color))
    if label:
        ax.annotate('%d°'%ang,(xc+wt/2+0.05,hsl+hr/2),fontsize=8,color='black')
        ax.annotate('脊顶 %.2f µm'%wt,(xc,hsl+hr+0.06),fontsize=8,ha='center')

def fingers(ax,xf0,wf,pf,n,hau,ys):
    for i in range(n):
        xc=xf0+i*pf
        ax.add_patch(Rectangle((xc-wf/2,ys),wf,hau,color=(GOLD if i%2==0 else GND)))
    ax.plot([xf0+pf/2,xf0+(n-0.5)*pf],[ys+0.1,ys+0.1],color='black',lw=0.6)
    ax.annotate('周期 %.2f µm'%pf,(xf0+(n/2-0.5)*pf,ys+0.14),fontsize=8,ha='center')

# ---- Fig 1: Shao calibration cross-section (PAP1)
fig,ax=plt.subplots(figsize=(12,3.2))
ax.add_patch(Rectangle((0,0),10,0.4,color=SUB))
ridge(ax,2.6,0.95,0.4,0.4,70)
fingers(ax,5.875,0.30,0.60,4,0.075,0.4)
ax.annotate('', xy=(2.6,0.92), xytext=(5.875,0.92), arrowprops=dict(arrowstyle='<->',color='black',lw=0.8))
ax.annotate('脊中心→首指中心 = 3.275 µm',(4.2,1.0),fontsize=8,ha='center')
ax.annotate('悬空膜宽 10 µm',(5,-0.22),fontsize=9,ha='center')
ax.plot([0,0],[-0.1,0.4],'k--',lw=0.6); ax.plot([10,10],[-0.1,0.4],'k--',lw=0.6)
ax.annotate('LN 膜 0.8 µm（板 0.4 + 脊 0.4）',(0.2,0.2),fontsize=8)
ax.annotate('金 75 nm + Cr 8 nm',(6.2,0.52),fontsize=8)
ax.set_xlim(-0.3,10.4); ax.set_ylim(-0.35,1.6)
ax.set_xlabel('x (µm)'); ax.set_ylabel('y (µm)')
ax.set_aspect('equal')
plt.tight_layout(); plt.savefig(os.path.join(D,'fig_xsec_shao.png'),dpi=200); plt.close()

# ---- Fig 2: Step 7 design cross-section
fig,ax=plt.subplots(figsize=(12,3.2))
ax.add_patch(Rectangle((0,0),12,0.4,color=SUB))
ridge(ax,2.6,0.95,0.4,0.4,70)
fingers(ax,4.5,0.46,1.84,4,0.1,0.4)
ax.annotate('设计周期 1.84 µm（NP=7 超胞，中间 3 个周期放波导）',(3.0,1.35),fontsize=8)
ax.annotate('段长 100 µm / 汇流条 0.5 µm / 指端 0.5 µm',(3.0,1.1),fontsize=8)
ax.set_xlim(-0.3,12.5); ax.set_ylim(-0.35,1.6)
ax.set_xlabel('x (µm)'); ax.set_ylabel('y (µm)')
ax.set_aspect('equal')
plt.tight_layout(); plt.savefig(os.path.join(D,'fig_xsec_design.png'),dpi=200); plt.close()

# ---- Fig 3: z-segmented layout
fig,ax=plt.subplots(figsize=(12,2.2))
ax.add_patch(Rectangle((0,0.15),100,0.7,color='#eef2f7'))
for i in range(10):
    ax.add_patch(Rectangle((i*10,0.3),10,0.4,color='#bcd4e6',alpha=0.7))
ax.plot([0,100],[0.15,0.15],'k-',lw=1)
ax.annotate('段间隙 0.5 | 信号汇流条 | 指端 0.5 | 叉指重叠区 | 指端 0.5 | 地汇流条 | 段间隙',(50,1.05),fontsize=8,ha='center')
ax.annotate('100 µm 段 ×10（1 mm），2 串 × 5 并配 50 Ω',(50,0.0),fontsize=9,ha='center')
ax.set_xlim(-3,103); ax.set_ylim(-0.2,1.3); ax.axis('off')
plt.tight_layout(); plt.savefig(os.path.join(D,'fig_zseg.png'),dpi=200); plt.close()

# ---- Fig 4: trapezoid angle sweep
ang=[60,65,70,75,90]
tot3=[1.492791e-3,1.971211e-3,2.184152e-3,1.734954e-3,3.319112e-3]
p1mm=[28.66,27.24,25.97,24.28,18.13]
fig,ax1=plt.subplots(figsize=(9,4.2))
ax1.plot(ang,tot3,'o-',color='#1f6fb2'); ax1.set_xlabel('侧壁角 θ (°)'); ax1.set_ylabel('3D |Δn_eff|/V',color='#1f6fb2')
ax1.axvline(70,color='red',ls='--',lw=1); ax1.annotate('70° 选点',(70.5,2.2e-3),fontsize=8,color='red')
ax2=ax1.twinx(); ax2.plot(ang,p1mm,'s--',color='#c0504d'); ax2.set_ylabel('1 mm nonseg 源功率 (mW)',color='#c0504d')
ax1.set_xticks(ang)
plt.tight_layout(); plt.savefig(os.path.join(D,'fig_trap.png'),dpi=200); plt.close()
print('figs done')
