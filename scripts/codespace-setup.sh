#!/usr/bin/env bash
# Idempotent GitHub Codespaces install: create .venv and install runtime deps.
set -euo pipefail

cd "$(dirname "$0")/.."

if [ ! -x ".venv/bin/python" ]; then
  echo "[codespace-setup] Creating virtual environment (.venv)..."
  python3 -m venv .venv
fi

echo "[codespace-setup] Installing Python dependencies..."
./.venv/bin/pip install --upgrade pip
./.venv/bin/pip install -r requirements.txt

echo "[codespace-setup] Done."
