#!/usr/bin/env python3
"""Validate spec(s) against specs/game-spec.schema.json + semantic checks (bounds, unique ids, win target exists).
Exit 0 = all valid, 1 = invalid. Usage: validate_spec.py specs/*.spec.json"""
import json, sys, pathlib
from jsonschema import Draft202012Validator
ROOT = pathlib.Path(__file__).resolve().parent.parent
schema = json.loads((ROOT / "specs/game-spec.schema.json").read_text())
V = Draft202012Validator(schema)
def semantic(s):
    e = []; W, H = s["grid"]["w"], s["grid"]["h"]
    ents = [s["player"]] + s.get("goals", []) + s.get("hazards", []) + s.get("characters", [])
    ids = [x["id"] for x in ents]
    if len(ids) != len(set(ids)): e.append(f"duplicate ids: {ids}")
    for x in ents + s.get("walls", []):
        w, h = x.get("w", 1), x.get("h", 1)
        if x["x"] < 0 or x["y"] < 0 or x["x"] + w > W or x["y"] + h > H: e.append(f"out of bounds: {x.get('id', x)}")
    wc = s["win_condition"]
    if wc["type"] == "reach_goal" and wc.get("target") not in [g["id"] for g in s["goals"]]: e.append(f"win target '{wc.get('target')}' not in goals")
    if wc["type"] == "survive_seconds" and not wc.get("seconds"): e.append("survive_seconds needs seconds")
    return e
bad = 0
flags = [x for x in sys.argv[1:] if x.startswith("--")]
for p in [x for x in sys.argv[1:] if not x.startswith("--")] or sorted(map(str, (ROOT / "specs").glob("*.spec.json"))):
    try: s = json.loads(pathlib.Path(p).read_text())
    except Exception as ex: print(f"FAIL {p}: invalid JSON: {ex}"); bad += 1; continue
    errs = [f"{'/'.join(map(str, er.path)) or '<root>'}: {er.message}" for er in V.iter_errors(s)]
    if not errs: errs = semantic(s)
    if not errs and "--reach" in flags:
        sys.path.insert(0, str(ROOT / "scripts")); from solver_reachability import reachability
        r = reachability(s)
        if r["win"] is False: errs.append("solver: goal unreachable (no win path)")
    print(("OK   " if not errs else "FAIL ") + p); [print("   -", x) for x in errs]; bad += bool(errs)
sys.exit(1 if bad else 0)
