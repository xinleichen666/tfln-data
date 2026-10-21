import pandas as pd, numpy as np, glob, os
from scipy.spatial import cKDTree
base=r'D:\comsol_ao_run\convergence\mode_match'
pref='fine_mode02_3.305664GHz.csv'
def read(p):
 d=pd.read_csv(p,comment='%'); a=d.to_numpy(float); xyz=a[:,:3]
 mask=(xyz[:,1]>=-1e-12)&(xyz[:,1]<=500e-9+1e-12)
 return xyz[mask],a[mask,6:9]
xe,phi=read(os.path.join(base,pref))
# drive uses real/imag for each component at expression columns 6 onward
norm=np.sum(phi**2)
vals=[]
for p in sorted(glob.glob(base+r'\driven_target_*.csv')):
 d=pd.read_csv(p,comment='%');a=d.to_numpy(float);x=a[:,:3];mask=(x[:,1]>=-1e-12)&(x[:,1]<=500e-9+1e-12);x=x[mask]
 dist,idx=cKDTree(x).query(xe,k=1)
 dd=a[mask,6:12]
 U=dd[:,0]+1j*dd[:,1];V=dd[:,2]+1j*dd[:,3];W=dd[:,4]+1j*dd[:,5]
 q=(np.sum(phi[:,0]*U)+np.sum(phi[:,1]*V)+np.sum(phi[:,2]*W))/norm
 vals.append((p.split('_')[-1].replace('GHz.csv',''),abs(q),q, np.percentile(dist*1e9,[50,95,100])))
print('eigen LN nodes',len(xe),'phi norm2',norm)
print('mapping distance nm',vals[0][3])
for name,amp,q,_ in vals: print(name,'qabs',amp,'qcomplex',q)
mx=max(v[1] for v in vals)
print('relative',[round(v[1]/mx,6) for v in vals])
