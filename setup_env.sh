#!/usr/bin/env bash
# Creates a FRESH virtual environment ("venv") and installs everything (macOS / Linux)
cd "$(dirname "$0")"
PY=""
for v in 3.11 3.12 3.10 3.13; do
  if command -v python$v >/dev/null 2>&1; then PY=python$v; break; fi
done
[ -z "$PY" ] && { echo "Python 3.10-3.13 not found. Install Python 3.11 first."; exit 1; }
echo "Using $($PY --version)"
[ -d venv ] || $PY -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m ipykernel install --user --name prog_ai_lab --display-name "Python (Prog_for_AI_Lab)"
python check_env.py
echo "Done. Start working with:  source venv/bin/activate && jupyter lab"
