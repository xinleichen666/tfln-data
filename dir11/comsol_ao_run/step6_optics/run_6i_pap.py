# -*- coding: utf-8 -*-
import subprocess, os, time
D=r'D:\comsol_ao_run\step6_optics'
CC=r'D:\COMSOL63\Multiphysics\bin\win64\comsolcompile.exe'
BAT=r'D:\COMSOL63\Multiphysics\bin\win64\comsolbatch.exe'
waited=0
while waited < 70*60:
    logs=[f for f in os.listdir(D) if f.startswith('step6i_cal_') and f.endswith('.log')]
    if len(logs)>=10: break
    time.sleep(30); waited+=30
print('first batch looks done, logs', len(logs), flush=True)
names=['PAP1','PAP1X55','PAP1C']
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
    print('run',name,q.returncode,'bytes',len(raw),flush=True)
print('ALL_DONE_PAP',flush=True)
