#!/usr/bin/env python3
"""Win-proof: BFS reachability over a GameSpec (reuses agent/playtest.solve, same rules as game.js).
Usage: solver_reachability.py SPEC [...]  -> JSON per spec; exit 0 if all winnable, 2 otherwise."""
import json, sys, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT / "agent"))
from playtest import solve
def reachability(spec):
    p = solve(spec); return {"reachable": p is not None, "win": p is not None, "steps": len(p) if p else None}
if __name__ == "__main__":
    ok = True
    for f in sys.argv[1:] or [str(ROOT / "game/spec.json")]:
        r = reachability(json.loads(pathlib.Path(f).read_text())); r["spec"] = f; print(json.dumps(r)); ok &= r["win"] is not False
    sys.exit(0 if ok else 2)
