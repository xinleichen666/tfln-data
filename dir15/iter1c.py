import json,numpy as np, modes as M
R=json.load(open('data/iter1b.json')); nP=1.53
dX=0.2; xg,yg,XG,YG=M.grid(30,30,dX)
for D in (6,8,10,12):
    E=M.solve(np.where((abs(XG)<D/2)&(abs(YG)<D/2),nP**2,1.0),dX,dX,1.6)[1][0]
    eta=M.overlap(E,M.gauss(XG,YG,5.2)); R[f'fiber_D{D}']=dict(eta=eta); print(D,round(eta,4),flush=True)
json.dump(R,open('data/iter1b.json','w'),indent=1)
