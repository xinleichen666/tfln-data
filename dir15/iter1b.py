# polymer (TPP) mode-adapter: (i) chip-side butt joint: TFLN tip mode (polymer-clad) -> air-clad polymer core a x a ; (ii) fiber side: core D x D -> SMF-28
import json,numpy as np, modes as M
from iter1 import tip_eps, XX, YY, dx, x, y
nP=1.53; R={}
def pcore(a,XXg,YYg,yc):
    return np.where((abs(XXg)<a/2)&(abs(YYg-yc)<a/2),nP**2,1.0)
for t,w in ((0.3,0.3),(0.3,0.4),(0.6,0.4),(0.6,0.6)):
    n,V=M.solve(tip_eps(w,t,nP),dx,dx,1.9); E=V[0]; I=E**2; yc=(I*YY).sum()/I.sum()
    for a in (1.5,2.0,2.5,3.0,4.0):
        nn,VV=M.solve(pcore(a,XX,YY,yc),dx,dx,1.52); eta=M.overlap(E,VV[0])
        R[f'chip_t{t}_w{w}_a{a}']=dict(eta=eta,neff_p=float(nn[0])); print(t,w,a,round(eta,4),flush=True)
        json.dump(R,open('data/iter1b.json','w'),indent=1)
# fiber side, coarse grid
dX=0.2; xg,yg,XG,YG=M.grid(30,30,dX)
for D in (6,8,10,12):
    nn,VV=M.solve(pcore(D,XG,YG,0),dX,dX,1.52); E=VV[0]
    for wf in (5.2,):
        eta=M.overlap(E,M.gauss(XG,YG,wf)); R[f'fiber_D{D}']=dict(eta=eta); print('fiber',D,round(eta,4),flush=True)
    json.dump(R,open('data/iter1b.json','w'),indent=1)
