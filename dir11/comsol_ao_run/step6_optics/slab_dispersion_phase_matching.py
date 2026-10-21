# -*- coding: utf-8 -*-
import math, os
D = r'D:\comsol_ao_run\step6_optics'
lam=1550e-9; k0=2*math.pi/lam; h=500e-9; d=h/2
def fv(x,n,kind,odd):
    if x>=n: return -1
    kap=k0*math.sqrt(max(n*n-x*x,0)); gam=k0*math.sqrt(max(x*x-1,0))
    if kind=='TE':
        return (gam+kap*math.cos(kap*d)/math.sin(kap*d)) if odd else (gam-kap*math.tan(kap*d))
    else:
        F=n*n
        return (gam+kap*math.cos(kap*d)/math.sin(kap*d)/F) if odd else (gam-kap*math.tan(kap*d)/F)
def solve(n,kind,odd):
    xs=[1.0001+i*(n-1e-9-1.0001)/20000.0 for i in range(20001)]
    prev=xs[0]; fp=fv(prev,n,kind,odd); cand=[]
    for x in xs[1:]:
        fx=fv(x,n,kind,odd)
        if fp*fx<0: cand.append((prev,x))
        prev=x; fp=fx
    for (lo,hi) in cand:
        a,b=lo,hi
        for _ in range(120):
            m=(a+b)/2
            if fv(a,n,kind,odd)*fv(m,n,kind,odd)<=0: b=m
            else: a=m
        x=(a+b)/2
        if abs(fv(x,n,kind,odd))<1e2:
            return x,k0*math.sqrt(max(n*n-x*x,0)),k0*math.sqrt(max(x*x-1,0))
    return None
want={'n2211 TE0':(2.211,'TE',False),'n2211 TE1':(2.211,'TE',True),'n2211 TM0':(2.211,'TM',False),'n2211 TM1':(2.211,'TM',True),
      'n2138 TE0':(2.138,'TE',False),'n2138 TE1':(2.138,'TE',True),'n2138 TM0':(2.138,'TM',False),'n2138 TM1':(2.138,'TM',True)}
res={}
for nm,(n,kind,odd) in want.items():
    r=solve(n,kind,odd); res[nm]=r
    print(nm, 'CUTOFF' if r is None else 'neff=%.9f kappa=%.9e gamma=%.9e'%r)
rows=[['mode','neff','kappa','gamma','cutoff']]
for nm in ['n2211 TE0','n2211 TE1','n2211 TM0','n2211 TM1','n2138 TE0','n2138 TE1','n2138 TM0','n2138 TM1']:
    r=res[nm]; rows.append([nm]+(['%.9f'%r[0],'%.9e'%r[1],'%.9e'%r[2],'0'] if r else ['NA','NA','NA','1']))
K=2*math.pi/2.8526131500e-6
pm=[['mode_i','mode_j','neff_i','neff_j','delta_beta','two_beta_i','two_beta_j','K','mismatch']]
sel={'B-TE0':'n2138 TE0','B-TE1':'n2138 TE1','B-TM0':'n2211 TM0','B-TM1':'n2211 TM1'}
for a in sel:
    for b in sel:
        if a<b and res[sel[a]] and res[sel[b]]:
            ni=res[sel[a]][0]; nj=res[sel[b]][0]; db=k0*abs(ni-nj); mis=abs(db-K)/K
            pm.append([a,b,'%.9f'%ni,'%.9f'%nj,'%.6e'%db,'%.6e'%(2*k0*ni),'%.6e'%(2*k0*nj),'%.6e'%K,'%.6e'%mis])
            print(a,b,'db=%.6e mis=%.4f'%(db,mis))
rows+=pm
open(os.path.join(D,'slab_step6.csv'),'w',encoding='utf-8',newline='\n').write('\n'.join(','.join(map(str,r)) for r in rows)+'\n')
print('OK rows',len(rows),'K=%.6e'%K)
