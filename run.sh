#!/usr/bin/env bash
# ============================================================
# NeuroCareer - one-click launcher for Linux / macOS reviewers.
# Mirrors the behaviour of run.cmd.
# ============================================================
set -e
cd "$(dirname "$0")"

echo
echo "=== NeuroCareer launcher ==="
echo

# 1. Locate Python 3.10+
PY_CMD=""
for cand in python3.12 python3.11 python3.10 python3 python; do
    if command -v "$cand" >/dev/null 2>&1; then
        if "$cand" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)' 2>/dev/null; then
            PY_CMD="$cand"
            break
        fi
    fi
done
if [ -z "$PY_CMD" ]; then
    echo "[ERROR] Python 3.10 or newer not found."
    echo "  Install from https://www.python.org/downloads/ then re-run this script."
    exit 1
fi
echo "Found Python: $($PY_CMD --version)"

# 2. Create venv if missing
if [ ! -x ".venv/bin/python" ]; then
    echo "Creating virtual environment in .venv ..."
    "$PY_CMD" -m venv .venv
fi

PY=".venv/bin/python"
PIP=".venv/bin/pip"

# 3. Install requirements (idempotent)
if [ ! -f ".venv/.installed" ]; then
    echo "Upgrading pip ..."
    "$PY" -m pip install --upgrade pip --quiet --disable-pip-version-check
    echo "Installing dependencies (3-5 minutes the first time) ..."
    "$PIP" install --quiet --disable-pip-version-check -r requirements.txt
    : > ".venv/.installed"
    echo "Dependencies installed."
fi

# 4. Launch
echo
echo "Starting Streamlit on http://localhost:8501 ..."
echo "Press Ctrl+C to stop."
echo
exec "$PY" -m streamlit run app.py --server.port 8501
