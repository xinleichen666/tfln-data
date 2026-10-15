import bpy,bmesh,math,json,sys
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
argv=sys.argv[sys.argv.index('--')+1:]; RESX=int(argv[0]); SAMP=int(argv[1]); OUT=argv[2]
bpy.ops.wm.read_factory_settings(use_empty=True); sc=bpy.context.scene
def W(x,y,z=0): return Vector((x,-y,z))
def srgb(h):
    c=[int(h[i:i+2],16)/255 for i in (1,3,5)]
    return tuple(((v+0.055)/1.055)**2.4 if v>0.04045 else v/12.92 for v in c)+(1,)
def mat(n,col,metal=0,rough=0.4,trans=0,alpha=1,emit=None,es=0,coat=0):
    m=bpy.data.materials.new(n); m.use_nodes=True; b=m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value=srgb(col); b.inputs['Metallic'].default_value=metal
    b.inputs['Roughness'].default_value=rough; b.inputs['Transmission Weight'].default_value=trans
    b.inputs['Alpha'].default_value=alpha; b.inputs['Coat Weight'].default_value=coat
    if emit: b.inputs['Emission Color'].default_value=srgb(emit); b.inputs['Emission Strength'].default_value=es
    return m
def box(c,s,m,bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1,location=c); o=bpy.context.object; o.scale=s
    bpy.ops.object.transform_apply(scale=True)
    if bevel: md=o.modifiers.new('b','BEVEL'); md.width=bevel; md.segments=3
    o.data.materials.append(m); return o
def cyl(c,ax,r,L,m,v=24):
    bpy.ops.mesh.primitive_cylinder_add(vertices=v,radius=r,depth=L,location=c); o=bpy.context.object
    o.rotation_mode='QUATERNION'; o.rotation_quaternion=Vector((0,0,1)).rotation_difference(Vector(ax).normalized())
    bpy.ops.object.shade_smooth(); o.data.materials.append(m); return o
def seg(a,b,r,m): a=Vector(a);b=Vector(b); return cyl((a+b)/2,b-a,r,(b-a).length,m,16)
def torus(c,R,r,m):
    bpy.ops.mesh.primitive_torus_add(location=c,major_radius=R,minor_radius=r,major_segments=160,minor_segments=16)
    o=bpy.context.object; o.scale=(1,1,0.55); bpy.ops.object.shade_smooth(); o.data.materials.append(m); return o
mChip=mat('chip','#d9dde3',rough=0.35,coat=0.3); mSi=mat('si','#6e7480',metal=0.3,rough=0.4)
mLN=mat('ln','#f2b8d0',rough=0.12,trans=0.4,coat=1); mMem=mat('mem','#f6d6e4',rough=0.2,trans=0.5,alpha=0.85,coat=0.6)
mAu=mat('au','#e6b422',metal=1,rough=0.22); mPit=mat('pit','#3b3f47',rough=0.7)
mIn=mat('in','#D55E00',emit='#D55E00',es=2.0,rough=1); mOut=mat('out','#0072B2',emit='#0072B2',es=2.0,rough=1)
mAc=mat('ac','#009E73',emit='#009E73',es=0.4,rough=0.5,alpha=0.9)
T=6  # chip thickness top at z=0
box(W(470,215,-18),(900,400,36),mChip,bevel=4)
labels={}
YB=320; R1=(470,235); RR=72
# bus
box(W(470,YB,2),(900,8,4),mLN)
torus(W(*R1,2),RR,4.2,mLN)
R2=(470,235-2*RR-14); torus(W(*R2,2),RR,4.2,mLN)
# suspended membrane on ring-1 left arc: pit + membrane
mx0,mx1,my0,my1=360,425,180,290
box(W((mx0+mx1)/2-25,(my0+my1)/2,0.15),(mx1-mx0+50+14,my1-my0+26,0.3),mPit)
box(W((mx0+mx1)/2-25,(my0+my1)/2,0.6),(mx1-mx0+50,my1-my0+8,0.6),mMem)
# acoustic standing-wave stripes on membrane under the ring
for i in range(7):
    x=378+i*10; box(W(x,(my0+my1)/2,1.0),(3.0,my1-my0-6,0.6),mAc)
# IDT: two bus bars + interdigitated fingers, on membrane left part
ix0,ix1=318,370; yb0,yb1=my0+2,my1-2
box(W((ix0+ix1)/2,yb0,1.2),(ix1-ix0+6,7,2.4),mAu); box(W((ix0+ix1)/2,yb1,1.2),(ix1-ix0+6,7,2.4),mAu)
for i in range(9):
    x=ix0+2+i*(ix1-ix0-4)/8; top=(i%2==0)
    L=(yb1-yb0)-14; yc=yb0+3.5+L/2 if top else yb1-3.5-L/2
    box(W(x,yc,1.2),(2.4,L,2.4),mAu)
for yy in (yb0,yb1):
    box(W(250,yy,1.0),(52,40,2.0),mAu,bevel=0.8)
    box(W((276+ix0)/2,yy,1.0),(ix0-276+2,6,2.0),mAu)
    seg(W(232,yy,3),W(170,yy,50),3.2,mSi)
labels['pad']=(W(250,235,0),0)
# photons: input wavepacket (dashed) left, output right
def pulse(xc,m,lab):
    for i in range(-5,6):
        a=math.exp(-(i/3.0)**2); h=3+16*a
        seg(W(xc+i*7,YB,5),W(xc+i*7,YB,5+0.01),1,m)
        cyl(W(xc+i*7,YB,5+h/2),(0,0,1),1.6,h,m,12)
    labels[lab]=(W(xc,YB,30),0)
pulse(90,mIn,'in'); pulse(840,mOut,'out')
def arrow(x0,x1,m):
    seg(W(x0,YB+22,3),W(x1-10,YB+22,3),2.0,m)
    bpy.ops.mesh.primitive_cone_add(vertices=24,radius1=5.5,depth=14,location=W(x1-4,YB+22,3)); o=bpy.context.object
    o.rotation_euler=(0,math.pi/2,0); o.data.materials.append(m)
arrow(45,145,mIn); arrow(795,905,mOut)
labels['r1']=W(R1[0]+RR*0.72,R1[1]-RR*0.72+4,3); labels['r2']=W(R2[0]+RR*0.72,R2[1]-RR*0.72,3)
labels['r1']=(labels['r1'],0); labels['r2']=(labels['r2'],0)
labels['mem']=(W((mx0+mx1)/2-25,my1+11,0),0); labels['idt']=(W(344,my0,2),0)
labels['bus']=(W(640,YB,3),0); labels['chip']=(W(-30,410,0),0)
labels['mu']=(W(470,235-RR-7,3),0)
cam_d=bpy.data.cameras.new('cam'); cam=bpy.data.objects.new('cam',cam_d); sc.collection.objects.link(cam); sc.camera=cam
cam.location=Vector((470,-1150,900)); tgt=Vector((450,-210,0))
cam.rotation_euler=(tgt-cam.location).to_track_quat('-Z','Y').to_euler(); cam_d.clip_end=10000; cam_d.sensor_width=36
bpy.context.view_layer.update()
cam_d.lens=50; sc.render.resolution_x=1000; sc.render.resolution_y=1000; bpy.context.view_layer.update()
xs=[];ys=[]
for o in sc.objects:
    if o.type=='MESH':
        for c in o.bound_box:
            v=world_to_camera_view(sc,cam,o.matrix_world@Vector(c)); xs.append(v.x); ys.append(v.y)
x0,x1,y0,y1=min(xs),max(xs),min(ys),max(ys); mg=0.01
wf=(x1-x0)+2*mg; hf=(y1-y0)+2*mg+0.10  # extra top room for labels
cam_d.lens=50/wf; sc.render.resolution_x=RESX; sc.render.resolution_y=int(RESX*hf/wf)
cam_d.shift_x=((x0+x1)/2-0.5)/wf; cam_d.shift_y=((y0+y1)/2+0.05-0.5)/wf
bpy.context.view_layer.update()
world=bpy.data.worlds.new('w'); sc.world=world; world.use_nodes=True
world.node_tree.nodes['Background'].inputs['Strength'].default_value=0.9
def area(loc,size,e):
    ld=bpy.data.lights.new('a','AREA'); ld.size=size; ld.energy=e; o=bpy.data.objects.new('a',ld); sc.collection.objects.link(o); o.location=loc
    o.rotation_euler=(tgt-Vector(loc)).to_track_quat('-Z','Y').to_euler()
area((100,-900,1000),1200,1.2e7); area((900,-300,1100),1000,0.8e7); area((450,500,700),900,0.3e7)
sc.render.engine='CYCLES'; cy=sc.cycles; cy.device='CPU'; cy.samples=SAMP; cy.use_denoising=True
cy.caustics_reflective=False; cy.caustics_refractive=False
sc.render.film_transparent=True; sc.view_settings.view_transform='Standard'
sc.render.image_settings.color_mode='RGBA'
out={k:[world_to_camera_view(sc,cam,p).x*sc.render.resolution_x,(1-world_to_camera_view(sc,cam,p).y)*sc.render.resolution_y] for k,(p,s) in labels.items()}
json.dump({'res':[sc.render.resolution_x,sc.render.resolution_y],'labels':out},open(OUT+'.json','w'))
sc.render.filepath=OUT+'.png'; bpy.ops.render.render(write_still=True)
