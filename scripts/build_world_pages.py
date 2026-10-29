#!/usr/bin/env python3
"""Build w_<slug>[_2|_3].html for a world (offline, $0). Usage: build_world_pages.py slug synthetic_NN K [slug sample K ...]"""
import sys, json, subprocess, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[1]; a = sys.argv[1:]
for slug, s, k in zip(a[::3], a[1::3], a[2::3]):
    od = f"samples/{s}/worlds/v{k}"
    for i in (1, 2, 3):
        t = json.loads((ROOT / od / f"scene_{i}.json").read_text())["title"].replace("/", "-")
        nxt = f"w_{slug}_{i+1}.html" if i < 3 else ""; out = f"game/w_{slug}{'' if i == 1 else f'_{i}'}.html"
        r = subprocess.run([sys.executable, "scripts/build_judge_demo.py", "--sample", f"samples/{s}", "--no-browser", "--scene", f"{od}/scene_{i}.json", "--play", f"{i}/3/{nxt}/{t}", "--out", out], cwd=ROOT, capture_output=True, text=True)
        print(slug, i, r.returncode, (r.stdout.strip().splitlines() or [""])[-1], r.stderr[-300:] if r.returncode else "")
