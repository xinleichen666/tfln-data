import json,numpy as np
R=json.load(open('data/run5.json')); S=json.load(open('data/sens_loss.json'))
rows=[]
for L in (2,5,10,15,20):
    d=R[f'L{L}']; line=[L,round(d['eta_h'],3)]
    for k in ('none','a0.2_e0.3','a0.1_e0.3','a0.1_e0.5','a0.04_e0.3'):
        a=np.array(d[k]); p=a[:,0]; coinc=a[:,1]*d['eta_h']**2   # pairs*gen * eta_h^2 (relative)
        line.append('%.2f [%.2f–%.2f] | %.1f'%(np.median(p),np.percentile(p,10),np.percentile(p,90),np.median(p*coinc)))
    rows.append(line); print(line)
print('ideal',[ (L,round(R[f'L{L}']['ideal'][0],3)) for L in (2,5,10,15,20)])
for k in ('a0.1_L5_ec0.5_ed0.9','a0.3_L5_ec0.5_ed0.9','a1.0_L5_ec0.5_ed0.9','a1.0_L20_ec0.5_ed0.9','a0.3_L20_ec0.5_ed0.9','a0.3_L5_ec0.2_ed0.68','a0.3_L5_ec0.8_ed0.9'): print(k,S[k])
