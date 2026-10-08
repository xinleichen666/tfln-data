import json,sys,numpy as np
R=json.load(open(sys.argv[1])); L0=float(sys.argv[2]) if len(sys.argv)>2 else None
Ls=np.array(R[0]["Ls"])
if L0 is None:  # choose L maximizing worst-case TE1->TE0n
    w=np.min([r["res"]["TE1w->TE0n"] for r in R],0); L0=Ls[np.argmax(w)]
i=np.argmin(abs(Ls-L0)); print("L=",Ls[i])
for r in R:
    q=r["res"]; f=lambda k:10*np.log10(max(q[k][i],1e-9))
    print(r["lam"],"TE1->TE0n %.2f dB"%f("TE1w->TE0n"),"TE1 left %.1f"%f("TE1w->TE1w"),"| TE0->TE0n xt %.1f dB"%f("TE0w->TE0n"),"TE0 thru %.2f"%f("TE0w->TE0w"), r["n"])
