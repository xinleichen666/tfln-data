# One TM-pump process: x-cut, t=0.6, w=1.4, h=0.3, vertical sidewalls.
# Pump TM 0.764 um, signal TE 1.528 um, idler TM 1.528 um (energy-degenerate).
# Every neff is cached. Thickness derivative is a local central difference at 0.600 um.
import json, os, numpy as np
from geo import neff
f='data/tm_neff.json'; R=json.load(open(f)) if os.path.exists(f) else {}
def n(lam,w,pol,t,h):
    k=f'{lam:.4f}_{w:.3f}_{pol}_{t:.4f}_{h:.3f}'
    if k not in R:
        R[k]=neff(lam,w,pol,t,h,dx=0.02,dy=0.005)
        json.dump(R,open(f,'w')); print(k, R[k], flush=True)
    return R[k]
# center + thickness +/-5 nm and +/-10 nm
for t in (0.590,0.595,0.600,0.605,0.610):
    for lam,pol in ((0.764,'TM'),(1.528,'TE'),(1.528,'TM')):
        n(lam,1.4,pol,t,0.3)
# width +/-40 nm, etch +/-10 nm, at t=0.600
for w in (1.36,1.44):
    for lam,pol in ((0.764,'TM'),(1.528,'TE'),(1.528,'TM')):
        n(lam,w,pol,0.600,0.3)
for h in (0.290,0.310):
    for lam,pol in ((0.764,'TM'),(1.528,'TE'),(1.528,'TM')):
        n(lam,1.4,pol,0.600,h)
# group index: lambda +/-0.008
for lam,pol in ((0.756,'TM'),(0.772,'TM'),(1.520,'TE'),(1.536,'TE'),(1.520,'TM'),(1.536,'TM')):
    n(lam,1.4,pol,0.600,0.3)
print('done', len(R))
