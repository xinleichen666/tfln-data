import pandas as pd,numpy as np
from scipy.spatial import cKDTree
base=r'D:\comsol_ao_run\convergence\mode_match\\'
def load(name):
 d=pd.read_csv(base+name,comment='%');a=d.to_numpy(float);q=a[:,:3];u=a[:,6:9];m=(q[:,1]>=-1e-12)&(q[:,1]<=500e-9+1e-12);return q[m],u[m]
xa,ua=load('refined_mode02_3.294186GHz.csv');xb,ub=load('refined4_mode02_3.290168GHz.csv');dist,idx=cKDTree(xb).query(xa);mac=(np.sum(ua*ub[idx]))**2/(np.sum(ua**2)*np.sum(ub[idx]**2));print('nodes',len(xa),len(xb),'dist_nm',np.percentile(dist*1e9,[50,95,100]),'MAC',mac)
