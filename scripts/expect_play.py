#!/usr/bin/env python3
"""Expect tests ($0): tests/expect/*.expect.json = {spec, actions:[R|L|U|D...] | "solve", expect:{status, player:{x,y}, steps?, frame?}}.
Simulates moves with the same rules as game.js/playtest.solve (walls block, hazards lose, goal wins) and diffs the final snapshot.
--update rewrites expect.frame/player/status from actual (review the diff!). Exit 0 all pass, 1 otherwise."""
import json, sys, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT / "agent"))
from playtest import solve, inr
D = {"R": (1, 0), "L": (-1, 0), "U": (0, -1), "D": (0, 1)}
def frame(spec, p):
    W, H = spec["grid"]["w"], spec["grid"]["h"]; rows = []
    for y in range(H):
        r = ""
        for x in range(W):
            c = "."
            if any(inr((x, y), w) for w in spec.get("walls", [])): c = "#"
            if any(inr((x, y), h) for h in spec.get("hazards", [])): c = "~"
            if any(inr((x, y), g) for g in spec["goals"]): c = "G"
            if (x, y) == p: c = "@"
            r += c
        rows.append(r)
    return rows
def run(spec, actions):
    W, H = spec["grid"]["w"], spec["grid"]["h"]; p = (spec["player"]["x"], spec["player"]["y"]); status, n = "playing", 0
    tgt = [g for g in spec["goals"] if g["id"] == spec["win_condition"].get("target")] or spec["goals"]
    for a in actions:
        if status != "playing": break
        dx, dy = D[a] if isinstance(a, str) else tuple(a); q = (p[0] + dx, p[1] + dy); n += 1
        if not (0 <= q[0] < W and 0 <= q[1] < H) or any(inr(q, w) for w in spec.get("walls", [])): continue
        p = q
        if any(inr(p, h) for h in spec.get("hazards", [])): status = "lost"
        elif any(inr(p, g) for g in tgt): status = "won"
    return {"status": status, "player": {"x": p[0], "y": p[1]}, "steps": n, "frame": frame(spec, p)}
if __name__ == "__main__":
    upd = "--update" in sys.argv; fails = 0
    files = [pathlib.Path(x) for x in sys.argv[1:] if not x.startswith("--")] or sorted((ROOT / "tests/expect").glob("*.expect.json"))
    for f in files:
        t = json.loads(f.read_text()); spec = json.loads((ROOT / t["spec"]).read_text())
        acts = solve(spec) or [] if t["actions"] == "solve" else t["actions"]
        got = run(spec, acts); exp = t.get("expect", {})
        diff = {k: {"expected": exp[k], "got": got[k]} for k in exp if exp[k] != got.get(k)}
        if upd: t["expect"] = {k: got[k] for k in ("status", "player", "frame")}; f.write_text(json.dumps(t, indent=1) + "\n"); print("UPDATED", f.name); continue
        print(("PASS " if not diff else "FAIL ") + f.name)
        for k, v in diff.items():
            if k == "frame": print("   frame expected:\n     " + "\n     ".join(v["expected"]) + "\n   got:\n     " + "\n     ".join(v["got"]))
            else: print(f"   {k}: expected {v['expected']} got {v['got']}")
        fails += bool(diff)
    sys.exit(1 if fails else 0)
