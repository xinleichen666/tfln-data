import base64,cairosvg
from PIL import Image
img=Image.open('render.png'); W,H=img.size; U=W/360.0
F='font-family="Nimbus Sans, Helvetica, Arial, sans-serif"'
M='font-family="Nimbus Roman, Times, serif" font-style="italic"'
def T(x,y,s,pt=9,a="start",fill="#1a1a1a",w="bold"):
    return f'<text x="{x}" y="{y}" {F} font-weight="{w}" font-size="{pt*U:.1f}" text-anchor="{a}" dominant-baseline="central" fill="{fill}">{s}</text>'
def m(s,pt=10): return f'<tspan {M} font-weight="normal" font-size="{pt*U:.1f}">{s}</tspan>'
def sub(s): return f'<tspan {F} font-weight="normal" font-size="{7*U:.1f}" dy="{2*U:.1f}">{s}</tspan><tspan dy="{-2*U:.1f}"> </tspan>'
def L(x1,y1,x2,y2,c="#1a1a1a",w=0.6,extra=""): return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{c}" stroke-width="{w*U:.1f}" {extra}/>'
t=[]
t.append(T(1735,700,"Ring 1"+"",9)); t.append(T(1735,410,"Ring 2",9))
t.append(T(1590,578,m("μ",10),9))
t.append(T(1105,555,"IDT",9,"middle"))
t.append(T(560,440,"RF drive",9,"middle")); t.append(T(560,530,m("Ω")+"/2π = 3.33 GHz",8,"middle",w="normal"))
t.append(T(1150,1010,"Suspended LN acoustic resonator",8,"middle",w="normal")); t.append(L(1150,975,1150,875))
t.append(T(307,700,"Input "+m("ω"),9,"middle",fill="#D55E00"))
t.append(T(2664,740,"Output "+m("ω")+" + "+m("Ω"),9,"middle",fill="#0072B2"))
t.append(T(2000,960,"Bus waveguide",8,"middle",w="normal"))
t.append(T(2560,1080,"TFLN chip",8,"middle",w="normal"))
# inset: supermode splitting
x0,y0,x1,y1=2120,40,2960,600
t.append(f'<rect x="{x0}" y="{y0}" width="{x1-x0}" height="{y1-y0}" rx="{4*U}" fill="#ffffff" stroke="#888" stroke-width="{0.5*U}"/>')
yc=(y0+y1)/2+30; d=150
lx=[2190,2330]; rx=[2620,2760]; mx=[2470,2610]
for xs,lab in [((2170,2330),"ring 1"),((2770,2930),"ring 2")]:
    t.append(L(xs[0],yc,xs[1],yc,w=1.0)); t.append(T((xs[0]+xs[1])/2,yc+55,lab,7,"middle",w="normal"))
t.append(L(2470,yc-d,2630,yc-d,"#0072B2",1.2)); t.append(L(2470,yc+d,2630,yc+d,"#D55E00",1.2))
for ys in (yc-d,yc+d):
    t.append(L(2330,yc,2470,ys,"#777",0.4,'stroke-dasharray="6,6"')); t.append(L(2630,ys,2770,yc,"#777",0.4,'stroke-dasharray="6,6"'))
t.append(T(2550,yc-d-50,m("ω")+sub("+"),9,"middle",w="normal")); t.append(T(2550,yc+d+50,m("ω")+sub("−"),9,"middle",w="normal"))
t.append(T(2250,yc-45,m("ω")+sub("0"),9,"middle",w="normal"))
# phonon wiggle arrow
import math
ax=2550; pts=" ".join(f"{ax+18*math.sin(k*math.pi/4):.1f},{yc+d-12-k*((2*d-50)/24):.1f}" for k in range(25))
t.append(f'<polyline points="{pts}" fill="none" stroke="#009E73" stroke-width="{1.0*U}"/>')
ty=yc-d+10; t.append(f'<polygon points="{ax},{ty} {ax-20},{ty+40} {ax+20},{ty+40}" fill="#009E73"/>')
t.append(T(2600,yc,"2"+m("μ")+" = "+m("Ω"),8,"start",w="normal"))
t.append(T((x0+x1)/2,y0+50,"Supermodes",8,"middle"))
b64=base64.b64encode(open('render.png','rb').read()).decode()
svg=f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="5in" height="{5*H/W:.4f}in" viewBox="0 0 {W} {H}"><rect width="{W}" height="{H}" fill="#fff"/><image width="{W}" height="{H}" xlink:href="data:image/png;base64,{b64}"/>'+"".join(t)+'</svg>'
open('fig1.svg','w').write(svg)
cairosvg.svg2pdf(bytestring=svg.encode(),write_to='../fig1_device.pdf')
cairosvg.svg2png(bytestring=svg.encode(),write_to='/tmp/f.png',dpi=600*W/3000/ (W/3000) * 3000/W*W/3000 if False else 600*W/(5*W/1.0)*5/1 /1 /1 if False else 600*(W/3000)*(3000/W)*(W/W))
im=Image.open('/tmp/f.png').convert('RGB'); im=im.resize((3000,int(3000*H/W)),Image.LANCZOS); im.save('../fig1_device.png',dpi=(600,600))
