#!/usr/bin/env python3
"""Ad-hoc measurement: greedy vs optimistic fail plan in Chromium on the 4 broken judge samples (needs runs/judge-synthetic_* from build_judge_demo)."""
import json, pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parents[2]; sys.path[:0] = [str(ROOT / "agent"), str(ROOT / "scripts")]
from browser_playtest import greedy, optimistic, serve
from fix_marks import diff_marks
from playwright.sync_api import sync_playwright
srv = serve(); port = srv.server_address[1]
with sync_playwright() as pw:
    b = pw.chromium.launch(); pg = b.new_page()
    for s in ["02", "04", "08", "11"]:
        sp = ROOT / f"runs/judge-synthetic_{s}/spec.json"; spec = json.loads(sp.read_text())
        runs = sorted([r for r in (ROOT/"runs").glob("*-mock") if (r/"iter_1.spec.json").exists() and json.loads((r/"iter_0.spec.json").read_text()) == spec])
        fixed = json.loads((runs[-1]/"iter_1.spec.json").read_text()); bug, _ = diff_marks(spec, fixed); what = bug[0]["what"] if bug else "?"
        out = {}
        for name, plan in (("greedy", greedy(spec)), ("optimistic", optimistic(spec)[0])):
            pg.goto(f"http://127.0.0.1:{port}/game/index.html?spec=/{sp.relative_to(ROOT)}&mute=1"); pg.wait_for_function("window.__GAME__ && window.__GAME__.ready")
            for d in plan:
                st = pg.evaluate("([a,b]) => window.__GAME__.move(a,b)", list(d))
                if st["status"] != "playing" or (name == "optimistic" and st["events"][-1:] == ["bump"]): break
            st = pg.evaluate("window.__GAME__.state()"); ev = (st["events"][-1:] or ["-"])[0]
            hit = {"enemy": ev.startswith("enemy:"), "hazard": ev.startswith("hazard:") and tuple((st["player"]["x"], st["player"]["y"])) in {tuple(c) for c in bug[0]["cells"]},
                   "wall": ev == "bump", "player": ev.startswith("spawn_"), "patrol": ev.startswith("enemy:")}.get(what, False)
            out[name] = (st["status"], ev, st["steps"], "ON_BUG" if hit else "elsewhere")
        print(s, what, out)
    b.close()
srv.shutdown()
