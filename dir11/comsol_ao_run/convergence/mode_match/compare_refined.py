import pandas as pd, numpy as np, glob, re, os
from scipy.spatial import cKDTree
base=r'D:\comsol_ao_run\convergence\mode_match'
def loadset(pat):
 out=[]
 for p in sorted(glob.glob(base+'\\'+pat)):
  d=pd.read_csv(p,comment='%');a=d.to_numpy(float);xyz=a[:,:3];disp=a[:,6:9];mask=(xyz[:,1]>=-1e-12)&(xyz[:,1]<=500e-9+1e-12);out.append((p,xyz[mask],disp[mask]))
 return out
def comp(A,B,srcname):
 # use A nodes against nearest B points
 xa=A[0][1]; xb=B[0][1]; tree=cKDTree(xb); dist,idx=tree.query(xa,k=1)
 print(srcname,'node counts',len(xa),len(xb),'nearest nm p50/p95/max',np.percentile(dist*1e9,[50,95,100]))
 M=np.zeros((len(A),len(B)))
 for i,(_,_,ua) in enumerate(A):
  for j,(_,_,ub) in enumerate(B):
   va=ua;vb=ub[idx];num=np.sum(va*vb);den=np.sqrt(np.sum(va*va)*np.sum(vb*vb));M[i,j]=(num/den)**2 if den else 0
 for i in [1]:
  jj=np.argsort(M[i])[::-1][:5]
  print('A mode',i+1,[(int(j+1),round(float(M[i,j]),5),B[j][0].split('_')[-1]) for j in jj])
 return M
fine=loadset('fine_mode*.csv');ref=loadset('refined_mode*.csv')
M=comp(fine,ref,'fine->refined');
