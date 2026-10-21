import pandas as pd, numpy as np, glob, os, re
from scipy.spatial import cKDTree
base=r'D:\comsol_ao_run\convergence\mode_match'
def load(p):
    d=pd.read_csv(p,comment='%')
    a=d.to_numpy(float)
    # columns: coordinate x,y,z; expression x,y,z,u,v,w
    x=a[:,:3]
    disp=a[:,6:9]
    # LN volume and below/within LN: y = 0..500nm
    mask=(x[:,1]>=-1e-12)&(x[:,1]<=500e-9+1e-12)
    return x[mask],disp[mask]
fine=[]; coarse=[]
for p in sorted(glob.glob(base+r'\fine_mode*.csv')): fine.append((p,*load(p)))
for p in sorted(glob.glob(base+r'\coarse_mode*.csv')): coarse.append((p,*load(p)))
print('counts LN',len(fine[0][1]),len(coarse[0][1]))
# Sample coarse points onto nearest fine nodes; inspect distance and MAC
xf= fine[0][1]; xc=coarse[0][1]
tree=cKDTree(xf); dist,idx=tree.query(xc,k=1)
print('nearest distance nm percentiles',np.percentile(dist*1e9,[0,25,50,75,90,95,99,100]))
# retain <150nm; compare vector MAC for all mode pairs at coarse nodes
keep=dist<=150e-9
print('kept',keep.sum(),'/',len(keep))
M=np.zeros((len(fine),len(coarse)))
for i,(_,_,uf) in enumerate(fine):
  for j,(_,_,uc) in enumerate(coarse):
    # coarse points compared with interpolated nearest fine point
    A=uf[idx[keep]]; B=uc[keep]
    num=np.sum(A*B,axis=1).sum()
    den=np.sqrt(np.sum(A*A)*np.sum(B*B))
    M[i,j]=(num/den)**2 if den else 0
for i in range(M.shape[0]):
  js=np.argsort(M[i])[::-1][:3]
  print(i+1,[(int(j+1),round(float(M[i,j]),4)) for j in js])
print('target fine mode2 best',int(np.argmax(M[1])+1),M[1].max())

