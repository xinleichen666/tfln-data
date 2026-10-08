import clib as C,numpy as np,json,sys
C.SUB=3; C.DATA=sys.argv[1]; o=json.load(open(sys.argv[2])); Ls=[float(x) for x in sys.argv[3].split(",")]
ws,we=o["ws"],o["we"]; z=np.array(o["zf"]); R={}
for L in Ls:
    rows=[]
    for c in C.CORNERS:
        for l in C.LAMS:
            r=C.run(C.load(c,l),ws,we,z,L); rows.append((c,l,r["TE1w->TE0n"],r["TE0w->TE0n"],r["TE0w->TE0w"]))
    w=min(rows,key=lambda t:t[2]); R[L]=rows
    print(L,"worst conv %.3f dB (resid %.1f dB) at %s %s; worst TE0 xt %.1f dB"%(10*np.log10(w[2]),10*np.log10(1-w[2]),w[0],w[1],10*np.log10(max(t[3] for t in rows))),flush=True)
json.dump({str(k):v for k,v in R.items()},open(sys.argv[2].replace(".json","_val.json"),"w"))
