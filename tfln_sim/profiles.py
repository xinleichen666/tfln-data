import numpy as np,matplotlib;matplotlib.use("Agg");import matplotlib.pyplot as plt
import modes_lib as M
for w,tag in [(3.0,"before"),(3.5,"anticrossing"),(4.0,"after")]:
    d=M.build(w,False).solve()
    fig,ax=plt.subplots(1,3,figsize=(13,3))
    for m in range(3):
        I=(abs(d.Ex.isel(mode_index=m,f=0))**2+abs(d.Ey.isel(mode_index=m,f=0))**2).squeeze()
        I.T.plot(ax=ax[m],x="x",cmap="magma",add_colorbar=False)
        ax[m].set_xlim(-3,3);ax[m].set_ylim(-0.5,1.2);ax[m].set_aspect("equal")
        ax[m].set_title(f"mode {m}: neff={float(d.n_eff[0,m]):.4f}, TE={float(d.pol_fraction.te[0,m]):.2f}")
    fig.suptitle(f"Air-clad, w={w} µm ({tag})");fig.savefig(f"profiles_air_w{w}.png",dpi=150,bbox_inches="tight");plt.close()
