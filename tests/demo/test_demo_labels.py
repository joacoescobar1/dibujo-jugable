#!/usr/bin/env python3
"""Judge-facing label/sprite legibility at the two frames a judge sees (broken try LOST, fixed try WON), headless Chromium, 0 API.
For each sample: build_judge_demo --out game/_labels_<s>.html (mock patcher), play ?iter=0 (agent fails) and the last iter (agent wins), then:
  overlaps   pairs of on-board labels (window.__TAGS__ boxes) that intersect by > 2 px each way (e.g. "Nave" on "Monstruo" at the goal)
  clipped    labels whose box leaves the canvas
  ghost_px   violet (enemy-ink) pixels inside the player/goal/NPC sprites cut from the drawing: the monster ink sitting on the
             star got baked into the STAR sprite, so after the fixer moved the monster a violet copy stayed on the goal
  kid_sprites entities (player + goals + enemies) wearing a sprite cut from the kid's drawing / total entities
Asserts: overlaps 0, clipped 0, ghost_px 0, 0 JS errors, won. Usage: tests/demo/test_demo_labels.py [--no-assert] [--samples 02,04,08,11,12]"""
import json, pathlib, subprocess, sys
ROOT = pathlib.Path(__file__).resolve().parents[2]
from playwright.sync_api import sync_playwright
PY = str(ROOT / ".venv/bin/python") if (ROOT / ".venv/bin/python").exists() else sys.executable
SAMPLES = (sys.argv[sys.argv.index("--samples") + 1] if "--samples" in sys.argv else "02,04,08,11,12").split(",")
ASSERT = "--no-assert" not in sys.argv
JS_FRAME = """() => { const T = window.__TAGS__ || [], c = document.getElementById('c'); let ov = 0, cl = 0;
  for (let i = 0; i < T.length; i++) { const a = T[i]; if (a.x0 < 0 || a.y0 < 0 || a.x1 > c.width || a.y1 > c.height) cl++;
    for (let j = i + 1; j < T.length; j++) { const b = T[j]; if (Math.min(a.x1, b.x1) - Math.max(a.x0, b.x0) > 2 && Math.min(a.y1, b.y1) - Math.max(a.y0, b.y0) > 2) ov++; } }
  return { overlaps: ov, clipped: cl, labels: T.map(t => t.text) }; }"""
JS_GHOST = """() => { const C = window.__CUT_CANVASES__ || {}; let n = 0;
  for (const cv of Object.values(C.at || {})) { if (!cv) continue; const d = cv.getContext('2d').getImageData(0, 0, cv.width, cv.height).data;
    for (let i = 0; i < d.length; i += 4) { const [r, g, b, a] = [d[i], d[i + 1], d[i + 2], d[i + 3]]; if (!a) continue;
      const M = Math.max(r, g, b), m = Math.min(r, g, b), dd = M - m; let h = 0; if (dd) h = M === r ? ((g - b) / dd) % 6 : M === g ? (b - r) / dd + 2 : (r - g) / dd + 4; h = (h * 60 + 360) % 360;
      if ((r > 110 && b > 150 && g < 60 && Math.abs(r - b) < 110) || (h >= 255 && h <= 320 && M && dd / M >= .25 && M / 255 >= .25 && M / 255 <= .97)) n++; } }
  const s = window.__GAME__ && window.__CUTS__; return { ghost_px: n, cuts: window.__CUTS__ }; }"""
rows, errs = [], []
with sync_playwright() as pw:
    br = pw.chromium.launch()
    for s in SAMPLES:
        out = f"game/_labels_{s}.html"
        r = subprocess.run([PY, "scripts/build_judge_demo.py", "--sample", f"samples/synthetic_{s}", "--out", out], cwd=ROOT, capture_output=True, text=True)
        if r.returncode: sys.exit(r.stderr)
        B = json.loads((ROOT / out).read_text().split("const B = ", 1)[1].split(";\nconst q", 1)[0]); n = len(B["iters"]); last = B["iters"][-1]["spec"]
        ents = 1 + len(last.get("goals", [])) + len([c for c in last.get("characters", []) if c.get("role") == "enemy"])
        url = (ROOT / out).as_uri(); row = {"sample": s}
        pg = br.new_page(viewport={"width": 1400, "height": 900}); pg.on("pageerror", lambda e: errs.append(f"{s}: {e}"))
        pg.goto(url + "?iter=0&mute=1"); pg.wait_for_timeout(500); pg.click("#auto")
        try: pg.wait_for_function("window.__DEMO_PLAY_DONE__ === true", timeout=8000)
        except Exception: pass
        pg.wait_for_timeout(700); row["fail"] = pg.evaluate(JS_FRAME)
        pg.goto(url + f"?iter={n - 1}&mute=1"); pg.wait_for_timeout(500); pg.click("#auto"); pg.wait_for_function("window.__GAME__.state().status !== 'playing'", timeout=20000)
        pg.wait_for_timeout(700); row["won"] = pg.evaluate("window.__GAME__.state().status") == "won"; row["win"] = pg.evaluate(JS_FRAME); g = pg.evaluate(JS_GHOST)
        cuts = g["cuts"] or {}; row["ghost_px"] = g["ghost_px"]; row["kid_sprites"] = f"{(cuts.get('enemies') or 0) + (cuts.get('others') or 0)}/{ents}"
        pg.close(); (ROOT / out).unlink(); rows.append(row)
        print({"sample": s, "overlaps_fail": row["fail"]["overlaps"], "overlaps_win": row["win"]["overlaps"], "clipped": row["fail"]["clipped"] + row["win"]["clipped"],
               "ghost_px": row["ghost_px"], "kid_sprites": row["kid_sprites"], "won": row["won"], "labels_win": row["win"]["labels"]})
    br.close()
k = len(rows); ov = sum(r["fail"]["overlaps"] + r["win"]["overlaps"] for r in rows); cl = sum(r["fail"]["clipped"] + r["win"]["clipped"] for r in rows)
print(f"samples={k} | label overlaps (fail+win frames) {ov} | frames with overlap {sum((r['fail']['overlaps'] > 0) + (r['win']['overlaps'] > 0) for r in rows)}/{2 * k} | "
      f"clipped {cl} | ghost violet px in non-enemy sprites {sum(r['ghost_px'] for r in rows)} | won {sum(r['won'] for r in rows)}/{k} | js_errors={len(errs)}")
for e in errs: print("  JS", e)
if ASSERT:
    assert not errs, errs
    for r in rows: assert r["won"] and r["fail"]["overlaps"] == 0 and r["win"]["overlaps"] == 0 and r["fail"]["clipped"] + r["win"]["clipped"] == 0 and r["ghost_px"] == 0, r
    print("PASS")
