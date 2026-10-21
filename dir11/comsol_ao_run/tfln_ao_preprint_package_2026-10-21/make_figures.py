from pathlib import Path
import csv
import matplotlib.pyplot as plt
root=Path(__file__).resolve().parent
with (root/'data'/'aperture_selected_target_band.csv').open(newline='',encoding='utf-8') as f: rows=list(csv.DictReader(f))
x=[float(r['aperture_um']) for r in rows]; freq=[float(r['freq_GHz']) for r in rows]
g=[float(r['g_interior_best']) for r in rows]; ge=[float(r['g_edge_same_mode']) for r in rows]
out=root/'images'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'figure.dpi':180})
fig,ax=plt.subplots(figsize=(6.5,3.5)); ax.axhspan(3.28,3.38,color='#dcefe8',alpha=.75,label='Target band: 3.28–3.38 GHz'); ax.plot(x,freq,'o-',lw=1.8,ms=5,color='#155e75')
for xi,yi in zip(x,freq): ax.annotate(f'{yi:.3f}',(xi,yi),xytext=(0,6),textcoords='offset points',ha='center',fontsize=6.5)
ax.set(xlabel='Finger aperture, Wap (µm)',ylabel='Selected eigenfrequency (GHz)',xlim=(3.5,16.5),ylim=(3.25,3.40)); ax.grid(True,alpha=.25); ax.legend(frameon=False,loc='lower right'); fig.tight_layout(); fig.savefig(out/'frequency_vs_aperture.png',bbox_inches='tight'); plt.close(fig)
fig,ax=plt.subplots(figsize=(6.5,3.5)); ax.plot(x,g,'o-',lw=1.8,ms=5,label='Interior maximum',color='#0f766e'); ax.plot(x,ge,'s--',lw=1.5,ms=4,label='Edge maximum (same mode)',color='#c2410c'); ax.set(xlabel='Finger aperture, Wap (µm)',ylabel='Overlap proxy (J$^{-1/2}$)',xlim=(3.5,16.5),ylim=(0,80)); ax.grid(True,alpha=.25); ax.legend(frameon=False); fig.tight_layout(); fig.savefig(out/'overlap_vs_aperture.png',bbox_inches='tight'); plt.close(fig)
