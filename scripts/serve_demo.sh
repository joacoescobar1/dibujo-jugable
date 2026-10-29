#!/usr/bin/env bash
# Fresh-clone judge demo: (re)build game/demo.html if missing (0 Meta spend, mock patcher), then serve game/ locally.
# Usage: scripts/serve_demo.sh [PORT] [--rebuild]
set -euo pipefail
cd "$(dirname "$0")/.."
PORT="${1:-8000}"; PY=.venv/bin/python; [ -x "$PY" ] || PY=python3
if [ ! -f game/demo.html ] || [[ " $* " == *" --rebuild "* ]]; then
  "$PY" scripts/build_judge_demo.py || "$PY" scripts/build_judge_demo.py --no-browser
fi
echo "Demo: http://localhost:$PORT/demo.html  (también funciona con file://game/demo.html)"
exec "$PY" -m http.server "$PORT" -d game --bind 127.0.0.1
