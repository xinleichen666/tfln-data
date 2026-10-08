# Round4 sensitivity: (a) analytic loss/coupling/detection -> heralding eff & coincidence factor vs L; (b) MC at L=5: chirp residual, width noise, map error
import json,numpy as np
out={}
# (a)
z_all={}
for a_s in (0.1,0.3,1.0):
  for L in (2,5,10,15,20):
    zz=np.linspace(0,L,400); Tp=10**(-2*a_s*zz/100); Ts=10**(-a_s*(L-zz)/100)
    gen=Tp.mean(); Tph=(Tp*Ts).mean()/Tp.mean()
    for ec in (0.2,0.5,0.8):
      for ed in (0.68,0.9):
        out[f'a{a_s}_L{L}_ec{ec}_ed{ed}']=dict(eta_h=ec*ed*Tph,coinc_factor=gen*(ec*ed*Tph)**2*L)
json.dump(out,open('data/sens_loss.json','w'),indent=1)
