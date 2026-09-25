#!/usr/bin/env bash
# Start the Flask app in a Codespace if it is not already listening.
set -euo pipefail

cd "$(dirname "$0")/.."

export HOST="${HOST:-0.0.0.0}"
export PORT="${PORT:-5000}"
export FLASK_DEBUG="${FLASK_DEBUG:-0}"

if [ ! -x ".venv/bin/python" ]; then
  echo "[codespace-start] missing .venv; run scripts/codespace-setup.sh first" >&2
  exit 1
fi

healthz() {
  ./.venv/bin/python - "$PORT" <<'PY'
import sys
import urllib.error
import urllib.request

port = sys.argv[1]
try:
    urllib.request.urlopen(f"http://127.0.0.1:{port}/healthz", timeout=2)
except (urllib.error.URLError, TimeoutError, OSError):
    raise SystemExit(1)
PY
}

if healthz; then
  echo "[codespace-start] already running on port ${PORT}"
  exit 0
fi

echo "[codespace-start] starting Flask on ${HOST}:${PORT}"
nohup ./.venv/bin/python app.py >> /tmp/chem-depth-info.log 2>&1 &

for _ in $(seq 1 40); do
  if healthz; then
    echo "[codespace-start] ready at http://127.0.0.1:${PORT}"
    exit 0
  fi
  sleep 0.25
done

echo "[codespace-start] server did not become ready; last log:" >&2
tail -n 40 /tmp/chem-depth-info.log >&2 || true
exit 1
