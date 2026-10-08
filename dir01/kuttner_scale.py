import json, numpy as np, run2 as r
from run2b import PB2
K=json.load(open('data/kuttner_check.json'))
C=np.loadtxt('data/chen_fig1d_thickness.csv',delimiter=','); Z,T=C[:,0],C[:,1]
A,B=0.56127258862588,-0.14438993571957118; LAM=0.0025943777213407233; S=-3.16
P=dict(A=A,B=B,b2=(0,0,0),LAM=LAM)
def med(L,f):
    z,q=r.weights(L,LAM,0.25); Ws,Wi,dW=r.grid(P,L,96); Dk=r.dk(P,Ws,Wi); tau=K['L5.0']['tau']*(5.0/L)
    vv=[]
    for z0 in np.arange(0,21-L+1e-9,4.0):
        m=(Z>=z0)&(Z<=z0+L); zz=Z[m]-z0-L/2; dt=f*np.interp(z,zz,T[m]-T[m].mean())
        vv.append(PB2(r.Phi(z,q,r.ph(z,S,dt),Dk),Ws,Wi,dW,tau)[2])
    return [round(float(np.median(vv)),3), round(float(np.min(vv)),3)]
for L in (4.0,5.0):
    for f in (0.1,0.15,0.2,0.25):
        print('L',L,'f',f,med(L,f),flush=True)
