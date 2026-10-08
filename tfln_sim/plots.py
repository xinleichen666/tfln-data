import json,numpy as np,matplotlib;matplotlib.use("Agg");import matplotlib.pyplot as plt
import modes_lib as M
fig,ax=plt.subplots(1,2,figsize=(11,4.2),sharey=True)
for a,k,t in [(ax[0],"clad","SiO2 upper cladding"),(ax[1],"air","Air upper cladding")]:
    rows=json.load(open("modes.json"))[k]+json.load(open("modes_wide.json"))[k]
    w=np.array([r["w"] for r in rows]);n=np.array([r["neff"] for r in rows]);te=np.array([r["te"] for r in rows])
    for i in range(4):
        sc=a.scatter(w,n[:,i],c=te[:,i],cmap="coolwarm",vmin=0,vmax=1,s=12)
    a.set_title(t);a.set_xlabel("Top-level width w (µm)");a.set_ylim(1.76,1.97)
ax[0].set_ylabel("n_eff");fig.colorbar(sc,ax=ax,label="TE fraction (red=TE, blue=TM)")
fig.savefig("neff_vs_width.png",dpi=200,bbox_inches="tight")
