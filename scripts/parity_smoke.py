#!/usr/bin/env python3
"""Parity smoke: solver.winnable (Python) must equal browser WIN (real game.js in headless Chromium). Exit 2 on mismatch.
Usage: parity_smoke.py [SPEC...]  (default: specs/*.spec.json + latest eval gen specs)"""
import glob, json, pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT / "agent"))
from playtest import solve
from browser_playtest import browser_playtest
fs = sys.argv[1:] or [f for f in glob.glob(str(ROOT / "specs/*.spec.json"))] + sorted(glob.glob(str(ROOT / "runs/eval-*/gen/*/spec.json")))[-9:]
bad = 0
for f in fs:
    w = solve(json.loads(pathlib.Path(f).read_text())) is not None; b = browser_playtest(f)["won"]; bad += w != b
    print(("OK  " if w == b else "DRIFT"), pathlib.Path(f).resolve().relative_to(ROOT), "solver", w, "browser", b)
print("mismatches:", bad); sys.exit(2 if bad else 0)
