#!/usr/bin/env python3
"""Regression: (A) same-tick swap with an enemy = loss in BOTH playtest.py and game.js (browser);
(B) mock_patcher (6b) fixes two covering guards without touching the kid's walls; survive-trap stays unwinnable. Exit 1 on failure."""
import json, pathlib, sys, tempfile
ROOT = pathlib.Path(__file__).resolve().parents[2]; sys.path.insert(0, str(ROOT / "agent"))
from playtest import solve, playtest
from mock_patcher import mock_fix
fails = 0
def check(ok, msg):
    global fails; fails += not ok; print(("PASS " if ok else "FAIL ") + msg)
# (A) 1-wide corridor: player (1,0) -> goal (4,0); enemy at (2,0) walks left once then right. Only way past = swap -> must be unwinnable.
swap = {"title": "swap", "grid": {"w": 5, "h": 1, "tile": 40}, "player": {"id": "p", "label": "P", "x": 1, "y": 0},
        "goals": [{"id": "g", "label": "G", "x": 4, "y": 0}], "walls": [],
        "characters": [{"id": "e", "label": "E", "role": "enemy", "x": 2, "y": 0, "patrol": [[-1, 0], [1, 0]]}],
        "win_condition": {"type": "reach_goal", "target": "g"}}
check(solve(swap) is None, "solver: swap through enemy is a loss (spec unwinnable)")
try:
    from browser_playtest import browser_playtest
    with tempfile.TemporaryDirectory(dir=ROOT / "runs") as td:
        f = pathlib.Path(td) / "swap.spec.json"; f.write_text(json.dumps(swap)); b = browser_playtest(str(f))
        check(b["status"] == "lost" and "enemy:e" in b["events"] and b["player"]["x"] == 2, f"game.js: swap on tick 1 = loss in browser (parity) {b['events']}")
except ImportError as e: print("SKIP browser parity:", e)
# (B) two static guards in a 1-wide corridor
s = json.loads((ROOT / "specs/enemy-doble-guardia.spec.json").read_text()); r = playtest(s)
check(not r["winnable"] and "enemy blocks" in r["bugs"][0], "doble-guardia: violated before fix")
t = mock_fix(s, r)
check(solve(t) is not None, f"doble-guardia: winnable after fix -> {t['_patch_note']}")
check(t["walls"] == s["walls"] and len([c for c in t["characters"] if c.get("role") == "enemy"]) == 2, "doble-guardia: walls intact, both enemies kept")
en = [(c["x"], c["y"]) for c in t["characters"] if c.get("role") == "enemy"]; check(len(set(en)) == 2, f"doble-guardia: guards not stacked {en}")
trap = json.loads((ROOT / "specs/survive-trap.spec.json").read_text())
check(solve(mock_fix(trap, {})) is None, "survive-trap: still unwinnable (negative control)")
print("FAILS:", fails); sys.exit(1 if fails else 0)
