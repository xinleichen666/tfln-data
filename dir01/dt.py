import json,os; from disp import *
f='data/dt.json'; D=json.load(open(f)) if os.path.exists(f) else {}
for w in (1.4,):
  for t in (0.56,0.6,0.64):
    for lam,pol in ((1.55,'TE'),(1.55,'TM'),(0.775,'TE'),(0.775,'TM')):
      k=f'{t}_{w}_{lam}_{pol}'
      if k in D: continue
      D[k]=neff(lam,w,pol,t=t); json.dump(D,open(f,'w')); print(k,D[k],flush=True)
