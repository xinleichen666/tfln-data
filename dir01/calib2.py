import json,os,numpy as np; from geo2 import neff
f='data/calib2.json'; R=json.load(open(f)) if os.path.exists(f) else {}
def db(t,h,w,th,lp=1.58):
    v=[]
    for l in (lp,lp/2):
        k=f'{t:.3f}_{h:.3f}_{w:.3f}_{th}_{l}'
        if k not in R: R[k]=neff(l,w,'TE',t,h,th); json.dump(R,open(f,'w'))
        v.append(R[k])
    return 2*np.pi*(v[1]/(lp/2)-2*v[0]/lp)
out={}
for th in (90,75,65,60):
    d=0.01
    out[th]=dict(dt=(db(.303+d,.154,.85,th)-db(.303-d,.154,.85,th))/(2*d),
                 dh=(db(.303,.154+d,.85,th)-db(.303,.154-d,.85,th))/(2*d),
                 dw=(db(.303,.154,.85+.02,th)-db(.303,.154,.85-.02,th))/.04)
    print(th,out[th],'paper dt -4.018 dh 1.842 dw -0.485',flush=True)
    json.dump(out,open('data/calib2_result.json','w'),indent=1)
