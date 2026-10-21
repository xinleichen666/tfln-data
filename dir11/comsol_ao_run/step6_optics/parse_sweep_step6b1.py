lines = open("step6b1_sweep2.log", encoding="utf-8", errors="ignore").read().splitlines()
hdr = [l[6:] for l in lines if l.startswith("SWHDR,")]
rows = [l[6:] for l in lines if l.startswith("SWROW,")]
assert len(hdr) == 1 and len(rows) == 131, (len(hdr), len(rows))
with open("sweep_step6b1.csv", "w", newline="\n") as f:
    f.write(hdr[0] + "\n")
    f.write("\n".join(rows) + "\n")
for l in lines:
    if l.startswith("SWEEPB1"):
        print(l)
