#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PY="${ROOT}/.venv/bin/python"
# Allow fresh re-run from empty data/
rm -rf "${ROOT}/data"/*
mkdir -p "${ROOT}/data" "${ROOT}/paper/fig"
"$PY" "${ROOT}/scripts/run_mmd_coverage.py"
"$PY" "${ROOT}/scripts/plot_figures.py"
echo "[run_all] OK"
