# -*- coding: utf-8 -*-
import subprocess, os, time
D=r'D:\comsol_ao_run\step6_optics'
CC=r'D:\COMSOL63\Multiphysics\bin\win64\comsolcompile.exe'
BAT=r'D:\COMSOL63\Multiphysics\bin\win64\comsolbatch.exe'
names=['W104','T700','T900','P60','P68','R85','R105','Xn15','Xp15','W109']
t0=time.time()
for name in names:
    j=os.path.join(D,'Step6iCal%s.java'%name)
    p=subprocess.run([CC,j],cwd=D,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    print('compile',name,p.returncode,flush=True)
    if p.returncode!=0:
        print(p.stdout.decode('gb18030','replace')[-600:],flush=True); continue
    log=os.path.join(D,'step6i_cal_%s.log'%name)
    with open(log,'wb') as f:
        q=subprocess.run([BAT,'-inputfile',os.path.join(D,'Step6iCal%s.class'%name)],cwd=D,stdout=f,stderr=subprocess.STDOUT)
    raw=open(log,'rb').read()
    try: t=raw.decode('gb18030')
    except Exception: t=raw.decode('utf-8','replace')
    open(log,'w',encoding='utf-8').write(t)
    print('run',name,q.returncode,'sec',round(time.time()-t0),'bytes',len(raw),flush=True)
print('ALL_DONE sec',round(time.time()-t0),flush=True)
