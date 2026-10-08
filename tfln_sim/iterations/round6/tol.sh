. ../../venv/bin/activate
run(){ [ -f $4 ] || python adc_exact.py $1 $2 $3 $4 "$5" 2>&1 | grep -vi warn | tail -1; }
run 2.65 1.26 0.25 tol_wplus50.json '{}'
run 2.55 1.16 0.35 tol_wminus50.json '{}'
run 2.6 1.21 0.33 tol_gplus30.json '{}'
run 2.6 1.21 0.27 tol_gminus30.json '{}'
run 2.6 1.21 0.3 tol_eplus20.json '{"etch":0.32}'
run 2.6 1.21 0.3 tol_eminus20.json '{"etch":0.28}'
python - <<'P'
import json,os,sys; sys.path.insert(0,".."); os.environ["OMP_NUM_THREADS"]="1"
from multiprocessing import Pool
import round_sweep as RS
C=[dict(orient="XcutZ",H=0.6,etch=e,angle=60,clad="air",wmin=1.2,wmax=2.6) for e in (0.28,0.32)]+[dict(orient="XcutZ",H=0.6,etch=0.3,angle=a,clad="air",wmin=1.2,wmax=2.6) for a in (55,65)]
if not os.path.exists("tol_taper.json"):
    with Pool(4) as p: R=p.map(RS.job,C)
    json.dump([{k:v for k,v in r.items() if k!="rows"} for r in R],open("tol_taper.json","w"),default=float)
P
echo ALLDONE
