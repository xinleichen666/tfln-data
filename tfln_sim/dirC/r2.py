import sys,json,itertools,numpy as np
sys.path.insert(0,'/workspace/tfln_sim/iterations')
from multiprocessing import Pool
import psrlib as P
def job(c):
    name,kw,wmin,wmax=c; out={}
    for lam in (1.45,1.5,1.55,1.6,1.65):
        k=dict(kw,lam=lam,nmodes=4,res=30)
        r=P.find_cross(k,wmin=wmin,wmax=wmax,step=0.1,tol=0.005)
        ns=P.slab_neff(**k)
        cs=[x for x in r['cands'] if x['alpha']==x['alpha'] and x['alpha']>0]
        if not cs: out[lam]=dict(found=False,slab=ns);continue
        x=max(cs,key=lambda x:x['g'])
        L,S=P.lz_length(x['g'],x['alpha'],lam=lam)
        out[lam]=dict(g=x['g'],wx=x['wx'],alpha=x['alpha'],S=S,neff=x['neff_x'],slabTE=ns[0],L99=float(L))
    print(name,json.dumps(out),flush=True); return name,kw,out
if __name__=='__main__':
    C=[]
    if sys.argv[1]=='C':
        for H,e in [(0.4,0.26),(0.4,0.27),(0.4,0.28),(0.4,0.29),(0.4,0.30),(0.39,0.28),(0.41,0.28)]:
            for ang in ([60] if (H,e)!=(0.4,0.28) else [55,60,65]):
                C.append((f"H{int(H*1000)}_e{int(e*1000)}_a{ang}_Y_air",dict(H=H,etch=e,angle=ang,orient='XcutY',clad='air'),1.2,2.2))
    else:
        for e in [0.28,0.30,0.32,0.34]:
            C.append((f"H600_e{int(e*1000)}_Y_Al2O3",dict(H=0.6,etch=e,orient='XcutY',clad='Al2O3'),0.5,1.6))
        C.append(("H400_e280_Y_Al2O3",dict(H=0.4,etch=0.28,orient='XcutY',clad='Al2O3'),0.5,2.4))
        C.append(("H400_e280_Y_polymer",dict(H=0.4,etch=0.28,orient='XcutY',clad='polymer'),0.5,2.4))
    with Pool(8) as p: res=p.map(job,C)
    json.dump(res,open(f'/workspace/tfln_sim/dir{sys.argv[1]}/r2_{sys.argv[1]}.json','w'),default=str)
