#!/usr/bin/env python3
"""Regression for mock_patcher fix (6) + offline enemy vision. Exit 1 on any failure.
(a) enemy specs are UNWINNABLE as written and the solver blames the enemy; (b) after mock_fix they are winnable,
the patch touches the enemy (not the kid's walls); (c) survive-trap stays a negative control; (d) generate_from_drawing
reads violet ink as enemy characters with patrols (synthetic_10 trail, synthetic_11 static guard on the goal)."""
import json, pathlib, subprocess, sys, tempfile
ROOT = pathlib.Path(__file__).resolve().parents[2]; sys.path.insert(0, str(ROOT / "agent"))
from playtest import solve, playtest
from mock_patcher import mock_fix
fails = 0
def check(ok, msg):
    global fails; fails += not ok; print(("PASS " if ok else "FAIL ") + msg)
for name in ("enemy-guardia-puerta", "enemy-pasillo-sincro"):
    s = json.loads((ROOT / f"specs/{name}.spec.json").read_text()); r = playtest(s)
    check(not r["winnable"] and "enemy blocks" in r["bugs"][0], f"{name}: violated before fix ({r['bugs'][0][:40]}...)")
    t = mock_fix(s, r)
    check(solve(t) is not None, f"{name}: held after fix -> {t['_patch_note']}")
    check(t.get("walls") == s.get("walls") and "enemigo" in t["_patch_note"], f"{name}: walls intact, enemy edited")
trap = json.loads((ROOT / "specs/survive-trap.spec.json").read_text())
check(solve(mock_fix(trap, {})) is None, "survive-trap: still unwinnable after mock (negative control)")
py = str(ROOT / ".venv/bin/python") if (ROOT / ".venv/bin/python").exists() else sys.executable
with tempfile.TemporaryDirectory() as td:
    for sid, want_patrol, want_first in (("synthetic_10", True, True), ("synthetic_11", False, False)):
        o = pathlib.Path(td) / sid / "spec.json"
        subprocess.run([py, str(ROOT / "scripts/generate_from_drawing.py"), "--image", str(ROOT / f"samples/{sid}/drawing.png"), "--out", str(o)], capture_output=True, check=True)
        s = json.loads(o.read_text()); en = [c for c in s.get("characters", []) if c.get("role") == "enemy"]
        check(len(en) == 1 and (en[0]["patrol"] != [[0, 0]]) == want_patrol, f"{sid}: 1 violet enemy detected, patrol={'trail' if want_patrol else 'static'} ({en[:1]})")
        check((solve(s) is not None) == want_first, f"{sid}: first_try winnable={want_first}")
        check(solve(mock_fix(s, {})) is not None, f"{sid}: winnable after mock loop")
print("FAILS:", fails); sys.exit(1 if fails else 0)
