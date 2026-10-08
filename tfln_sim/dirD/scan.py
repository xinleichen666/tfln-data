import sys,json,itertools,numpy as np
sys.path.insert(0,'/workspace/tfln_sim/iterations')
from multiprocessing import Pool
import psrlib as P
def job(c):
    name,kw=c
    out={}
    for lam in (1.45,1.55,1.65):
        k=dict(kw,lam=lam,nmodes=4,res=30)
        try:
            r=P.find_cross(k,wmin=0.6,wmax=4.0,step=0.2,tol=0.01)
            ns=P.slab_neff(**k)
        except Exception as e: out[lam]=dict(err=str(e));continue
        cs=[x for x in r['cands'] if x['neff_x']>ns[1]+0.005] or r['cands']
        if not cs: out[lam]=dict(found=False,slab=ns);continue
        x=min(cs,key=lambda x:x['g']) if False else cs[0]
        L,S=P.lz_length(x['g'],x['alpha'],lam=lam) if x['alpha']>0 else (np.nan,np.nan)
        out[lam]=dict(g=x['g'],wx=x['wx'],alpha=x['alpha'],neff=x['neff_x'],slabTM=ns[1],guided=x['neff_x']>ns[1],L99=float(L))
    print(name,json.dumps({k:{a:(round(b,4) if isinstance(b,float) else b) for a,b in v.items()} for k,v in out.items()}),flush=True)
    return name,kw,out
if __name__=='__main__':
    which=sys.argv[1]; C=[]
    if which=='C':
        for o,e,cl in itertools.product(['XcutY','XcutZ'],[0.2,0.24,0.28,0.32,0.36],['air','SiO2']):
            C.append((f"H400_e{int(e*1000)}_{o}_{cl}",dict(H=0.4,etch=e,orient=o,clad=cl)))
    else:
        for o in ['XcutY','XcutZ']:
            for cl,part in [('air',None),('SiO2',None),('polymer',None),('Al2O3',None),('SiN',None),
                            ('air',('SiN',0.1)),('air',('SiN',0.2)),('air',('SiN',0.4)),('SiO2',('SiN',0.2)),('air',('Al2O3',0.3))]:
                tag=cl+('' if part is None else f"_{part[0]}{int(part[1]*1000)}")
                C.append((f"H600_e320_{o}_{tag}",dict(H=0.6,etch=0.32,orient=o,clad=cl,partial=part)))
    with Pool(4) as p: res=p.map(job,C)
    json.dump(res,open(f'/workspace/tfln_sim/dir{which}/scan_{which}.json','w'),default=str)
