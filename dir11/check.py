from ao_model import *
for phi in [np.pi/2,-np.pi/2]:
    p=iq_spectrum(3.68,3.68,0,-np.pi/2,phi); print(phi,{k:round(v,4) for k,v in p.items() if v>1e-4})
print(abs(acoustic_mzi(0))**2, np.angle(dc(LC_FULL/2)@[1,0]))
print(dphi_pp(1,400e-6))
