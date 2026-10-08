import json,numpy as np,matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
d=json.load(open('res_it1.json')); A=['std','3mzi','mzix','dbl','hyb']; SC=['rand0.05','rand0.10','bias0.08']
cls=lambda n:'DFT' if n.startswith('DFT') and 'x' not in n else ('Haar' if n.startswith('Haar') else ('Perm' if n.startswith('Perm') or n=='Toffoli' or n.startswith('CNOT') else 'Kron-H'))
fl=lambda v:np.maximum(1-np.array(v),1e-12)
L=[]; rows={}
for n,r in d.items():
    b=np.array(r['bar']); fp=np.mean((b<0.1)|(b>0.9)); fe=np.mean((b>0.3)&(b<0.7))
    for s in SC:
        m={a:np.mean(fl(r[f'{s}|{a}'])) for a in A}
        rows.setdefault((cls(n),s),[]).append((m,r['nhyb']/r['K']))
        L.append((n,cls(n),s,fp,fe,m))
out=['| 类别 | 场景 | 目标数 | std | 3-MZI | MZI+X | 双MZI | 混合(冗余比例) | 3-MZI优于std的比例 |','|---|---|---|---|---|---|---|---|---|']
for (c,s),v in sorted(rows.items()):
    M={a:np.array([x[0][a] for x in v]) for a in A}; g=lambda a:f"{np.exp(np.mean(np.log(M[a]))):.1e}"
    out.append(f"| {c} | {s} | {len(v)} | {g('std')} | {g('3mzi')} | {g('mzix')} | {g('dbl')} | {g('hyb')} ({np.mean([x[1] for x in v]):.0%}) | {np.mean(M['3mzi']<M['std']):.0%} |")
open('table_it1.md','w').write('\n'.join(out)+'\n\n(几何平均不保真度 1-F，每个目标50块芯片取平均)\n'); print('\n'.join(out))
# selection rule
for s in SC:
    X=np.array([l[3]-l[4] for l in L if l[2]==s]); Y=np.array([np.log10(l[5]['3mzi']/l[5]['std']) for l in L if l[2]==s])
    pred=X>0; acc=np.mean(pred==(Y<0)); print(s,'rule acc (f_pole>f_eq => 3MZI better):',f'{acc:.2f}',len(X))
fig,ax=plt.subplots(1,2,figsize=(10,4))
col={'DFT':'C0','Haar':'C1','Perm':'C2','Kron-H':'C3'}
for i,s in enumerate(['rand0.05','rand0.10']):
    for l in L:
        if l[2]==s: ax[i].scatter(l[3]-l[4],np.log10(l[5]['3mzi']/l[5]['std']),c=col[l[1]],s=18)
    ax[i].axhline(0,c='k',lw=.5); ax[i].axvline(0,c='k',lw=.5); ax[i].set_title(f'{s}'); ax[i].set_xlabel('f_pole - f_equator (ideal settings)'); ax[i].set_ylabel('log10[(1-F)_3MZI/(1-F)_std]')
for c,k in col.items(): ax[0].scatter([],[],c=k,label=c)
ax[0].legend(); plt.tight_layout(); plt.savefig('../fig4_selection_rule.png',dpi=130)
