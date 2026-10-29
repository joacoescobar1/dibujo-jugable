#!/usr/bin/env python3
"""Goal gate: exit 0 only if the newest runs/*/summary.json has result WIN, a winning screenshot exists, and (freshness, T6)
the WIN summary + screenshot are newer than every file under the watched paths (default: game/, agent/, specs/*.spec.json).
Override watched paths with DJ_FRESH_PATHS="game agent specs/*.spec.json"; DJ_FRESH=0 disables (logged). Used by .muse/hooks.json."""
import json, sys, os, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
runs = sorted((p for p in (ROOT / "runs").glob("*/summary.json") if not p.parent.name.startswith("eval-")), key=lambda p: p.stat().st_mtime)
if not runs: print("BLOCK: no runs/*/summary.json — run a playtest first"); sys.exit(2)
s = json.loads(runs[-1].read_text())
if s.get("result") != "WIN": print(f"BLOCK: latest run {runs[-1].parent.name} result={s.get('result')} (need WIN)"); sys.exit(2)
pngs = list(runs[-1].parent.glob("*.png"))
if not pngs: print(f"BLOCK: {runs[-1].parent.name} WIN but no screenshot"); sys.exit(2)
if os.environ.get("DJ_FRESH", "1") != "0":
    def files(pat):
        p = ROOT / pat
        it = p.rglob("*") if p.is_dir() else ROOT.glob(pat)
        return (f for f in it if f.is_file() and "__pycache__" not in f.parts)
    watched = [f for pat in os.environ.get("DJ_FRESH_PATHS", "game agent specs/*.spec.json").split() for f in files(pat)]
    if watched:
        newest = max(watched, key=lambda f: f.stat().st_mtime); art = min([runs[-1]] + pngs, key=lambda f: f.stat().st_mtime)
        if newest.stat().st_mtime > art.stat().st_mtime:
            print(f"BLOCK: stale WIN {runs[-1].parent.name} — {newest.relative_to(ROOT)} changed after the winning artifact; re-run the playtest"); sys.exit(2)
else: print("WARN: freshness check disabled (DJ_FRESH=0)")
print(f"OK: winning artifact {runs[-1].parent.relative_to(ROOT)}")
