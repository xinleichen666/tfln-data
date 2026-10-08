import pickle,numpy as np,glob
CORNERS=["nom","wp50","wm50","gp30","gm30","ep20","em20","a55","a65"]; LAMS=[1.45,1.55,1.65]
_c={}
DATA="data"
def load(c,l):
    k=(DATA,c,l)
    if k not in _c: _c[k]=pickle.load(open(f"/workspace/tfln_sim/dirB/{DATA}/{c}_{l}.pkl","rb"))
    return _c[k]
def idx(D,e): return int(np.argmin(abs(D["WN"]-e)))
def ids(I):
    teA,nA,teB,nB=I["teA"],I["nA"],I["teB"],I["nB"]
    te=sorted([i for i in range(len(nA)) if teA[i]>0.8],key=lambda i:-nA[i]); tm=sorted([i for i in range(len(nA)) if teA[i]<0.2],key=lambda i:-nA[i])
    tb=sorted([i for i in range(len(nB)) if teB[i]>0.8],key=lambda i:-nB[i])
    return dict(TE0w=te[0],TE1w=te[1],TM0w=tm[0],TE0n=tb[0])
SUB=8
ADIAB_ENDS=True
from scipy.linalg import fractional_matrix_power as _fmp
_fc={}
def step(D,k):
    key=(id(D),k,SUB)
    if key not in _fc:
        T=D["T"][k]; nm=T.shape[0]
        perm=np.argmax(np.abs(T),axis=0)  # column j (mode j at k) -> row perm[j] at k+1
        if len(set(perm))<nm: perm=np.arange(nm)
        Pm=np.zeros((nm,nm)); Pm[perm,np.arange(nm)]=1
        R=Pm.T@T  # basis k -> basis k (reordered k+1)
        sg=np.exp(1j*np.angle(np.diag(R))); R=R/sg[:,None]  # remove per-mode phase (sign) of new basis
        Rf=_fmp(R,1.0/SUB) if SUB>1 else R
        n1=D["neff"][k]; n2=D["neff"][k+1][perm]
        _fc[key]=(Rf,n1,n2,Pm,sg)
    return _fc[key]
def run(D,ws,we,zfrac,L):
    ks,ke=idx(D,ws),idx(D,we); Is,Ie=D["iso"][round(ws,4)],D["iso"][round(we,4)]
    a_ids=ids(Is); b_ids=ids(Ie); k0=2*np.pi/D["lam"]; z=np.asarray(zfrac)*L
    out={}
    for src in ["TE1w","TE0w","TM0w"]:
        a=Is["inA"][a_ids[src]].astype(complex)
        if ADIAB_ENDS: j=int(np.argmax(abs(a))); a=np.zeros_like(a); a[j]=1
        for k in range(ks,ke):
            dz=(z[k-ks+1]-z[k-ks])/SUB; Rf,n1,n2,Pm,sg=step(D,k)
            for s in range(SUB):
                t=(s+0.5)/SUB; n=n1*(1-t)+n2*t
                a=Rf@(a*np.exp(-1j*k0*n*dz))
            a=Pm@(a*sg)
        for dst,M,ii in [("TE0n",Ie["outB"],b_ids["TE0n"]),("TE0w",Ie["outA"],b_ids["TE0w"]),("TE1w",Ie["outA"],b_ids["TE1w"]),("TM0w",Ie["outA"],b_ids["TM0w"])]:
            if ADIAB_ENDS: j=int(np.argmax(abs(M[ii]))); out[f"{src}->{dst}"]=float(abs(a[j])**2)
            else: out[f"{src}->{dst}"]=float(abs(M[ii]@a)**2)
    return out
def adiab(D,ws,we):
    """local nonadiabatic coupling per interval: max_j |T_ij|/|dn_ij| for the TE1w-followed mode (adjacent modes)."""
    ks,ke=idx(D,ws),idx(D,we); Is=D["iso"][round(ws,4)]; a=np.abs(Is["inA"][ids(Is)["TE1w"]])**2; i=int(np.argmax(a))
    c=[]
    for k in range(ks,ke):
        T=np.abs(D["T"][k]); i2=int(np.argmax(T[:,i])); n=D["neff"][k]
        cc=max(T[j,i]/max(abs(n[i]-n[j]),1e-4) for j in range(len(n)) if j!=i2)
        c.append(cc); i=i2
    return np.array(c)
