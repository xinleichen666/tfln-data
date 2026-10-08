import sys,pickle,json,numpy as np; sys.path.insert(0,"../iterations"); import eme
prof=json.load(open("../iterations/round4/eme_results.json")); PW=np.array(prof["W"]); PZ=np.array(prof["ca_profile"])
def sub(D,lo,hi):
    i=[k for k,w in enumerate(D["W"]) if lo-1e-6<=w<=hi+1e-6]; E=dict(D); E["W"]=D["W"][i]; E["neff"]=D["neff"][i]; E["te"]=D["te"][i]; E["T"]=[D["T"][k] for k in i[:-1]]; return E
out={}
for L in [101,153,200,250,300]:
  row={}
  for c,b in [("nom",0),("wp50",.05),("wm50",-.05),("ep20",0),("em20",0),("a55",0),("a65",0)]:
    for l in [1.45,1.55,1.65]:
      D=pickle.load(open(f"../iterations/round4/D_{l}.pkl","rb")) if c in("nom","wp50","wm50") else pickle.load(open(f"taper/{c}_{l}.pkl","rb"))
      E=sub(D,1.2+b,min(2.6+b,D["W"].max()))
      z=np.interp(E["W"]-b,PW,PZ); z=(z-z[0])/(z[-1]-z[0])
      a=eme.propagate(E,z,L); row[f"{c}_{l}"]=float(a[1]/a.sum())
  out[L]=row; w=min(row,key=row.get); print(L,"worst eta %.4f (%.1f dB resid) at %s"%(row[w],10*np.log10(1-row[w]),w),flush=True)
json.dump(out,open("taper_tol.json","w"))
