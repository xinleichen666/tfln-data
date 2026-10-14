#!/usr/bin/env bash
# From empty data/, regenerate summary.json, histories, figs.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
rm -f "$ROOT/data/summary.json" "$ROOT/data/histories.json" "$ROOT/data/examples.npz"
mkdir -p "$ROOT/data" "$ROOT/paper/fig"
python3 "$ROOT/scripts/run_protocol.py"
python3 "$ROOT/scripts/make_figs.py"
echo "regenerate complete"
