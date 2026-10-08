import json,sys,numpy as np,psrlib as P
d=sys.argv[1]; R=json.load(open(f"{d}/results.json"))
for r in R:
    c=r["cfg"]; pick=None
    for c0 in r.get("cands",[]):
        tx=c0["te_x"]; nlo=c0["neff_x"]-c0["g"]/2
        c0["valid"]=bool(0.25<tx[0]<0.75 and 0.25<tx[1]<0.75 and np.isfinite(c0["alpha"]) and c0["alpha"]>0 and nlo>max(r["slab_te"],P.clad_index(c.get("clad","air"),1.55))+0.03)
        if c0["valid"] and pick is None: pick=c0
    for k in ["g","wx","alpha","L99_um","span","leak_margin","neff_x","te_x"]: r.pop(k,None)
    r["valid"]=pick is not None
    if pick:
        r.update({k:v for k,v in pick.items() if k!="valid"}); r["leak_margin"]=r["neff_x"]-r["g"]/2-r["slab_te"]
        L,S=P.lz_length(r["g"],r["alpha"]); r["L99_um"]=L; r["span"]=S
json.dump(R,open(f"{d}/results.json","w"),default=float)
for r in sorted(R,key=lambda r:-r.get("g",0)):
    c=r["cfg"]; print(c["orient"],c["H"],c["etch"],c["angle"],c["clad"],c.get("partial"),"V" if r["valid"] else "-",*(round(r[k],4) for k in ["g","wx","L99_um","leak_margin"]) if r["valid"] else "")
