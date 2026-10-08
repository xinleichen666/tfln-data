# Round3: digitize Chen 2023 (arXiv 2307.11671) Fig.1d from vector path in PDF (page 2), PSD analysis.
import numpy as np, json
v=np.load('data/fig/fig1d_raw.npy')
X=0.688556*v[:,0]+271.18503; Y=0.68895*v[:,1]+180.249476
z=(X-271.18)/(452.27-271.18)*21; t=595+(255.56-Y)/(255.56-140.51)*15
np.savetxt('data/chen_fig1d_thickness.csv',np.c_[z,t],delimiter=',',header='z_mm,thickness_nm (digitized vector path, Chen 2023 Fig1d)')
dz=np.diff(z); out=dict(N=len(z),z0=z[0],z1=z[-1],dz_med=float(np.median(dz)),dz_min=float(dz.min()),dz_max=float(dz.max()),tmin=t.min(),tmax=t.max())
# uniform resample
zu=np.arange(0,21,np.median(dz)); tu=np.interp(zu,z,t)
# short-scale part: residual after smoothing with 0.2 mm boxcar
k=int(round(0.2/np.median(dz))); sm=np.convolve(tu,np.ones(k)/k,'same')
r=(tu-sm)[k:-k]; out['short_rms_nm(<0.2mm)']=float(r.std())
# point-to-point difference -> white-noise floor estimate: std(diff)/sqrt2
out['p2p_white_est_nm']=float(np.std(np.diff(tu))/np.sqrt(2))
# 5mm windows: rms after removing mean
w=int(5/np.median(dz)); rms=[np.std(tu[i:i+w]) for i in range(0,len(tu)-w,w//2)]; out['rms_5mm_windows']=[float(x) for x in rms]
# PSD
f=np.fft.rfftfreq(len(tu),zu[1]-zu[0]); P=abs(np.fft.rfft(tu-np.polyval(np.polyfit(zu,tu,1),zu)))**2
m=(f>0.2)&(f<5); sl=np.polyfit(np.log(f[m]),np.log(P[m]),1)[0]; out['psd_slope_0.2-5/mm']=float(sl)
m2=(f>5); sl2=np.polyfit(np.log(f[m2]),np.log(P[m2]+1e-30),1)[0]; out['psd_slope_>5/mm']=float(sl2)
out['nyquist_per_mm']=float(f[-1])
json.dump(out,open('data/fig1d_stats.json','w'),indent=1); print(json.dumps(out,indent=1))
