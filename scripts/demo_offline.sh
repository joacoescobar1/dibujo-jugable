#!/usr/bin/env bash
# OFFLINE demo reel: broken level -> headless player fails -> LOCAL MOCK patch -> player wins.
# Production swaps --patcher mock for --patcher muse (Meta Muse). No API calls here.
set -e; cd "$(dirname "$0")/.."
PY=python3; [ -x .venv/bin/python ] && PY=.venv/bin/python
exec $PY agent/patch_loop.py --spec specs/broken-example.spec.json --patcher mock --browser --max 3 "$@"
