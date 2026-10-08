import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt, numpy as np, math
from matplotlib.patches import FancyBboxPatch, FancyArrow
from PIL import Image
plt.rcParams.update({'font.family':'sans-serif','font.sans-serif':['Nimbus Sans','Helvetica','Arial'],
 'mathtext.fontset':'custom','mathtext.it':'Nimbus Roman:italic','mathtext.rm':'Nimbus Sans','pdf.fonttype':42})
img=np.array(Image.open('render.png').convert('RGBA')); H,W=img.shape[:2]
fw=5.0; fig=plt.figure(figsize=(fw,fw*H/W)); ax=fig.add_axes([0,0,1,1]); ax.imshow(img); ax.set_xlim(0,W); ax.set_ylim(H,0); ax.axis('off')
K='#1a1a1a'
def T(x,y,s,pt=9,ha='left',c=K,w='bold'): ax.text(x,y,s,fontsize=pt,ha=ha,va='center',color=c,fontweight=w)
T(1735,700,'Ring 1'); T(1735,410,'Ring 2'); T(1585,580,r'$\mu$',10,w='normal')
T(1105,555,'IDT',ha='center')
T(560,435,'RF drive',ha='center'); T(560,515,r'$\Omega/2\pi$ = 3.33 GHz',8,'center',w='normal')
T(1150,1010,'Suspended LN acoustic resonator',8,'center',w='normal'); ax.plot([1150,1150],[975,875],color=K,lw=0.6)
T(307,720,r'Input  $\omega$',9,'center','#D55E00')
T(2640,760,r'Output  $\omega+\Omega$',9,'center','#0072B2')
T(2000,960,'Bus waveguide',8,'center',w='normal'); T(2560,1090,'TFLN chip',8,'center',w='normal')
x0,y0,x1,y1=2080,30,2970,610
ax.add_patch(FancyBboxPatch((x0,y0),x1-x0,y1-y0,boxstyle='round,pad=0,rounding_size=30',fc='white',ec='#888',lw=0.5))
T((x0+x1)/2,y0+55,'Supermodes',8,'center')
yc=360; d=140
for a,b,lab in [(2130,2290,'Ring 1'),(2760,2920,'Ring 2')]:
    ax.plot([a,b],[yc,yc],color=K,lw=1.0); T((a+b)/2,yc+50,lab,7,'center',w='normal')
T(2210,yc-50,r'$\omega_0$',9,'center',w='normal'); T(2840,yc-50,r'$\omega_0$',9,'center',w='normal')
ax.plot([2450,2600],[yc-d]*2,color='#0072B2',lw=1.4); ax.plot([2450,2600],[yc+d]*2,color='#D55E00',lw=1.4)
for ys in (yc-d,yc+d):
    ax.plot([2290,2450],[yc,ys],color='#777',lw=0.5,ls=(0,(3,3))); ax.plot([2600,2760],[ys,yc],color='#777',lw=0.5,ls=(0,(3,3)))
T(2525,yc-d-45,r'$\omega_+$',9,'center',w='normal'); T(2525,yc+d+48,r'$\omega_-$',9,'center',w='normal')
axx=2490; ys=np.linspace(yc+d-10,yc-d+50,200); ax.plot(axx+14*np.sin((ys-ys[0])/16),ys,color='#009E73',lw=1.0)
ax.add_patch(plt.Polygon([[axx,yc-d+8],[axx-17,yc-d+52],[axx+17,yc-d+52]],color='#009E73'))
T(2535,yc,r'$2\mu=\Omega$',8,w='normal')
fig.savefig('../fig1_device.pdf'); fig.savefig('../fig1_device.png',dpi=600)
