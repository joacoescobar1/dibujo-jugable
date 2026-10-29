#!/usr/bin/env python3
"""Judge-facing legibility of the fail->fix->win story ON THE BOARD (not just in side text), headless Chromium, 0 API.
For each broken synthetic sample: build_judge_demo --out game/_legib_<s>.html (mock patcher), then measure:
  fail_played   ?iter=0, ▶ Ver al agente jugar: the agent actually walks the broken level and loses on screen (lost, steps>0 or spawn-death)
  tour_fail     ?iter=0&tour=1 (Modo juez) does the same without any click
  marks0/marksN window.__MARKS__ on the broken / fixed attempt: where the bug is, what the fix changed (old->new)
  vis_lost/vis_won  % of board pixels still readable under the end-of-game overlay (screenshot with overlay vs hidden)
Asserts all samples: fail_played, tour_fail, marks0>0, marksN>0, vis_won>=70, vis_lost>=70, 0 JS errors.
Usage: tests/demo/test_demo_legibility.py [--no-assert] [--samples 02,04,08,11,12]"""
import json, pathlib, subprocess, sys
ROOT = pathlib.Path(__file__).resolve().parents[2]
from playwright.sync_api import sync_playwright
from PIL import Image, ImageChops
PY = str(ROOT / ".venv/bin/python") if (ROOT / ".venv/bin/python").exists() else sys.executable
SAMPLES = (sys.argv[sys.argv.index("--samples") + 1] if "--samples" in sys.argv else "02,04,08,11,12").split(",")
ASSERT = "--no-assert" not in sys.argv; tmp = pathlib.Path("/tmp/demo_legib"); tmp.mkdir(exist_ok=True)

def visible(pg, tag):
    """% of #wrap pixels within 24/255 of the same frame with the overlay hidden (particles settled first)."""
    pg.wait_for_timeout(1800); a, b = tmp / f"{tag}_ov.png", tmp / f"{tag}_clean.png"
    pg.locator("#wrap").screenshot(path=str(a), animations="disabled")
    pg.evaluate("document.getElementById('ov').style.visibility='hidden'"); pg.locator("#wrap").screenshot(path=str(b), animations="disabled")
    pg.evaluate("document.getElementById('ov').style.visibility=''")
    d = ImageChops.difference(Image.open(a).convert("RGB"), Image.open(b).convert("RGB")).convert("L")
    h = d.histogram(); return round(100 * sum(h[:25]) / sum(h), 1)

def fail_on_screen(pg):  # walked into the bug (lost / dead end at the fence), or spawn-death (loses at load, visibly LOST)
    st = pg.evaluate("window.__GAME__.state()"); stuck = pg.evaluate("window.__DEMO_STUCK__ === true")
    return stuck or (st["status"] == "lost" and (st["steps"] > 0 or any(e.startswith("spawn_") for e in st["events"]))), st, stuck

rows, errs = [], []
with sync_playwright() as pw:
    br = pw.chromium.launch()
    for s in SAMPLES:
        out = f"game/_legib_{s}.html"
        r = subprocess.run([PY, "scripts/build_judge_demo.py", "--sample", f"samples/synthetic_{s}", "--out", out], cwd=ROOT, capture_output=True, text=True)
        if r.returncode: sys.exit(r.stderr)
        url = (ROOT / out).as_uri(); n = json.loads((ROOT / out).read_text().split("const B = ", 1)[1].split(";\nconst q", 1)[0])["iters"].__len__()
        row = {"sample": s, "iters": n}
        pg = br.new_page(viewport={"width": 1400, "height": 900}); pg.on("pageerror", lambda e: errs.append(f"{s}: {e}"))
        pg.goto(url + "?iter=0&mute=1"); pg.wait_for_timeout(500); row["marks0"] = pg.evaluate("(window.__MARKS__||[]).length")
        pg.click("#auto")
        try: pg.wait_for_function("window.__DEMO_PLAY_DONE__ === true", timeout=8000)
        except Exception: pass
        row["fail_played"], st, stuck = fail_on_screen(pg); row["fail_how"] = "stuck" if stuck else (st["events"][-1:] or ["-"])[0]
        row["vis_lost"] = visible(pg, f"{s}_lost") if row["fail_played"] else None
        pg.goto(url + "?iter=0&tour=1&mute=1")
        try: pg.wait_for_function("window.__DEMO_PLAY_DONE__ === true", timeout=6000)
        except Exception: pass
        row["tour_fail"] = fail_on_screen(pg)[0]
        pg.goto(url + f"?iter={n - 1}&mute=1"); pg.wait_for_timeout(500); row["marksN"] = pg.evaluate("(window.__MARKS__||[]).length")
        pg.click("#auto"); pg.wait_for_function("window.__GAME__.state().status !== 'playing'", timeout=20000)
        row["won"] = pg.evaluate("window.__GAME__.state().status") == "won"; row["vis_won"] = visible(pg, f"{s}_won")
        pg.close(); (ROOT / out).unlink(); rows.append(row); print(row)
    br.close()
k = len(rows); tot = lambda f: sum(1 for r in rows if f(r))
print(f"samples={k} | fail_played {tot(lambda r: r['fail_played'])}/{k} | tour_fail {tot(lambda r: r['tour_fail'])}/{k} | "
      f"marks0>0 {tot(lambda r: r['marks0'] > 0)}/{k} | marksN>0 {tot(lambda r: r['marksN'] > 0)}/{k} | won {tot(lambda r: r['won'])}/{k} | "
      f"vis_lost avg {sum((r['vis_lost'] or 0) for r in rows) / k:.1f}% | vis_won avg {sum(r['vis_won'] for r in rows) / k:.1f}% | js_errors={len(errs)}")
for e in errs: print("  JS", e)
if ASSERT:
    assert not errs, errs
    for r in rows:
        assert r["won"] and r["fail_played"] and r["tour_fail"] and r["marks0"] > 0 and r["marksN"] > 0, r
        assert r["vis_won"] >= 70 and (r["vis_lost"] or 0) >= 70, r
    print("PASS")
