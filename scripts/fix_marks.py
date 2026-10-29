#!/usr/bin/env python3
"""On-board marks for the judge demo (display-only, derived from data, never from prose): diff spec k vs spec k+1.
What the fixer changed in k->k+1 IS where attempt k was broken, so attempt k gets 'bug' marks (where it jams) and
attempt k+1 gets 'fix' marks (what changed: old->new spawn, opened bridge/door cells, patrol re-timed).
Mark = {kind: 'bug'|'fix', what: 'enemy'|'player'|'hazard'|'wall'|'patrol', cells: [[x,y]...], from?: [x,y], to?: [x,y], label}."""

def _cells(rects):
    return {(r["x"] + i, r["y"] + j) for r in rects for i in range(r.get("w", 1) or 1) for j in range(r.get("h", 1) or 1)}

def _ents(spec):
    out = {"__player__": spec["player"]}
    out.update({c["id"]: c for c in spec.get("characters", []) if c.get("role") == "enemy"}); return out

def diff_marks(a, b):
    """Returns (bug_marks_for_a, fix_marks_for_b)."""
    bug, fix = [], []
    ea, eb = _ents(a), _ents(b)
    for k, e in ea.items():
        f = eb.get(k)
        if not f: continue
        what = "player" if k == "__player__" else "enemy"; name = (e.get("label") or e.get("id") or what).lower()
        if (e["x"], e["y"]) != (f["x"], f["y"]):
            bug.append({"kind": "bug", "what": what, "cells": [[e["x"], e["y"]]], "label": f"🐞 {name}: tapa el camino" if what == "enemy" else f"🐞 {name}: arranca trabado"})
            fix.append({"kind": "fix", "what": what, "cells": [[f["x"], f["y"]]], "from": [e["x"], e["y"]], "to": [f["x"], f["y"]], "label": f"🔧 lo corrí"})
        elif what == "enemy" and (e.get("patrol") or []) != (f.get("patrol") or []):
            bug.append({"kind": "bug", "what": "patrol", "cells": [[e["x"], e["y"]]], "label": f"🐞 {name}: nunca deja pasar"})
            fix.append({"kind": "fix", "what": "patrol", "cells": [[f["x"], f["y"]]], "label": "🔧 otro ritmo"})
    for key, what, bl, fl in (("hazards", "hazard", "🐞 corta todo el mapa", "🔧 puente"), ("walls", "wall", "🐞 encierra la meta", "🔧 puerta")):
        gone = sorted(_cells(a.get(key, [])) - _cells(b.get(key, [])))
        if gone:
            bug.append({"kind": "bug", "what": what, "cells": [list(c) for c in gone], "label": bl})
            fix.append({"kind": "fix", "what": what, "cells": [list(c) for c in gone], "label": fl})
    return bug, fix

def marks_per_iter(specs):
    m = [[] for _ in specs]
    for k in range(len(specs) - 1):
        bug, fix = diff_marks(specs[k], specs[k + 1]); m[k] += bug; m[k + 1] += fix
    return m
