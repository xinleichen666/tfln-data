. ../venv/bin/activate
while pgrep -f prep_coupler.py >/dev/null; do sleep 30; done
python prep_taper.py > prep_taper.log 2>&1
G0=0.2 TAG=data_g02 python prep_coupler.py > prep_g02.log 2>&1
