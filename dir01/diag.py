import numpy as np, run2 as r
r.NR=4
P=r.setup('1.4_0.3'); z,q=r.weights(5,P['LAM'],0.25)
for step,err in ((0.0038,0),(0.05,0),(0.2,0),(0.2,0.1)):
    res=[]
    for k in range(4):
        dt=r.pink(z,1.59); m=r.mapped(z,dt,step,err); e=dt-m
        res.append(np.std(r.ph(z,P['St'],e)))
    print(step,err,'resid phase rms rad',np.mean(res))
print('no-adapt phase rms',np.mean([np.std(r.ph(z,P['St'],r.pink(z,1.59))) for k in range(4)]))
