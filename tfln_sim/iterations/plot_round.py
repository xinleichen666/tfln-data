import json,sys,numpy as np,matplotlib;matplotlib.use("Agg");import matplotlib.pyplot as plt
d=sys.argv[1]; R=json.load(open(f"{d}/results.json"))
lab=lambda c:f"{c['orient']} H{int(c['H']*1000)} e{int(c['etch']*1000)} {c['angle']}° {c['clad']}"+(f"+{c['partial'][0]}{int(c['partial'][1]*1000)}" if c.get('partial') else "")
R=[r for r in R if r.get("valid")]; R.sort(key=lambda r:-r["g"])
fig,ax=plt.subplots(1,2,figsize=(13,0.32*len(R)+1.5))
y=np.arange(len(R))
ax[0].barh(y,[r["g"] for r in R],color="#0072B2");ax[0].set_yticks(y,[lab(r["cfg"]) for r in R],fontsize=8);ax[0].invert_yaxis();ax[0].set_xlabel("min gap Δn at TM0–TE1 anticrossing")
ax[1].barh(y,[r["L99_um"] for r in R],color="#D55E00");ax[1].set_yticks(y,[f"w×={r['wx']:.2f}µm" for r in R],fontsize=8);ax[1].invert_yaxis();ax[1].set_xscale("log");ax[1].set_xlabel("LZ linear-taper length for 99% conversion (µm)")
fig.tight_layout();fig.savefig(f"{d}/gap_and_length.png",dpi=150)
# neff vs width curves for the top 4
fig,axs=plt.subplots(1,min(4,len(R)),figsize=(16,3.6))
for a,r in zip(np.atleast_1d(axs),R[:4]):
    rows=sorted(r["rows"],key=lambda x:x["w"]); w=[x["w"] for x in rows]
    for i in range(4):
        sc=a.scatter(w,[x["neff"][i] for x in rows],c=[x["te"][i] for x in rows],cmap="coolwarm",vmin=0,vmax=1,s=8)
    a.axhline(r["slab_te"],ls=":",c="k",lw=0.8);a.axvline(r["wx"],ls="--",c="g",lw=0.8)
    a.set_title(lab(r["cfg"]),fontsize=8);a.set_xlabel("w (µm)");a.set_ylabel("neff")
    lo=r["neff_x"]-0.15;a.set_ylim(max(lo,r["slab_te"]-0.02),r["neff_x"]+0.2)
fig.colorbar(sc,ax=axs,label="TE fraction");fig.savefig(f"{d}/neff_top4.png",dpi=150,bbox_inches="tight")
