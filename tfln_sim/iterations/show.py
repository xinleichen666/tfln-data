import json,sys
for l in open(sys.argv[1]):
  if l.startswith('{'):
    r=json.loads(l);c=r['cfg'];c={k:v for k,v in c.items() if k not in('wmin','wmax')}
    f=lambda k,n=4: round(r[k],n) if isinstance(r.get(k),(int,float)) else None
    print(c,'V' if r.get('valid') else '-',f('g'),f('wx',2),f('L99_um',0),f('leak_margin',3),r.get('err','')[:60])
