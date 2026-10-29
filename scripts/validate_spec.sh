#!/usr/bin/env bash
# Validate game specs (schema + semantics). No args = all specs/*.spec.json. Note: winnability is checked by the playtest, not here.
set -e; cd "$(dirname "$0")/.."
PY=python3; [ -x .venv/bin/python ] && PY=.venv/bin/python
exec $PY scripts/validate_spec.py "$@"
