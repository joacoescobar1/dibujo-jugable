#!/usr/bin/env python3
"""Python side of on-board beats: final judge spec + gates -> agent answers clear every gate and WIN; wrong answers -> STUCK.
Usage: verify_gates.py [game/demo.html]. Exit 1 on any mismatch."""
import json, re, sys, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT / "agent"))
from gates import walk, clear_plan
html = (ROOT / (sys.argv[1] if len(sys.argv) > 1 else "game/demo.html")).read_text()
B = json.loads(re.search(r"const B = (\{.*?\});\n", html, re.S).group(1)); spec = B["iters"][-1]["spec"]; G = B.get("gates") or []
ok = len(G) >= 3 and {g["kind"] for g in G} >= {"fork", "question", "meter"}
good = walk(spec, G, clear_plan(G)); ok &= good["status"] == "won" and len(good["cleared"]) == len(G)
bad = {}
for g in G:
    wrong = dict(clear_plan(G)); wrong[g["id"]] = {"fork": "B" if not g.get("alt") else "X", "question": "Sí" if g.get("answer") == "No" else "No", "meter": "frame:1"}[g["kind"]]
    r = walk(spec, G, wrong); bad[g["id"]] = r["status"]; ok &= r["status"] == "stuck"
print(json.dumps({"gates": [(g["id"], g["kind"], g["cell"]) for g in G], "agent": good, "wrong_answer": bad, "ok": bool(ok)})); sys.exit(0 if ok else 1)
