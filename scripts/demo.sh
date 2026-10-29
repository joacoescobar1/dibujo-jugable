#!/usr/bin/env bash
# Demo wrapper. MODE=offline (default; local mock patcher, zero API) | muse (Meta Muse patcher; real spend).
#   ./scripts/demo.sh            -> offline
#   ./scripts/demo.sh muse     -> smoke-checks Muse first, falls back to offline if model_not_found
set -e; cd "$(dirname "$0")/.."
PY=python3; [ -x .venv/bin/python ] && PY=.venv/bin/python
MODE="${1:-offline}"; shift || true
SPEC="${SPEC:-specs/broken-example.spec.json}"
./scripts/validate_spec.sh "$SPEC"
if [ "$MODE" = muse ]; then
  if $PY scripts/smoke_muse.py >/tmp/dj_smoke.log 2>&1; then
    echo "[demo] Muse OK -> production loop"; $PY agent/patch_loop.py --spec "$SPEC" --patcher muse --browser --max "${MAX:-5}" "$@"
  else
    echo "[demo] Muse smoke FAILED (see /tmp/dj_smoke.log) -> falling back to offline"; MODE=offline
  fi
fi
[ "$MODE" = offline ] && $PY agent/patch_loop.py --spec "$SPEC" --patcher mock --browser --max "${MAX:-3}" "$@"
$PY scripts/check_win_artifact.py
