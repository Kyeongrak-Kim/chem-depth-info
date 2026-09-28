#!/usr/bin/env bash
# Idempotent Cloud Agent install script for chem-depth-info.
# Safe to run repeatedly: it only installs what is missing and reuses the venv.
set -euo pipefail

cd "$(dirname "$0")/.."

# The default base image ships Python 3.12 but not the venv/ensurepip module,
# which is required to create an isolated virtual environment.
if ! dpkg -s python3.12-venv >/dev/null 2>&1; then
  echo "[cloud-setup] Installing python3.12-venv system package..."
  sudo apt-get update -qq
  sudo apt-get install -y --no-install-recommends python3.12-venv
fi

if [ ! -x ".venv/bin/python" ]; then
  echo "[cloud-setup] Creating virtual environment (.venv)..."
  python3 -m venv .venv
fi

echo "[cloud-setup] Installing Python dependencies..."
./.venv/bin/pip install --upgrade pip
./.venv/bin/pip install -r requirements.txt

echo "[cloud-setup] Done."
