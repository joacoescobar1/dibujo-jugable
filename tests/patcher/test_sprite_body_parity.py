#!/usr/bin/env python3
"""Sprite/enemy parity on phone photos: the blob game.js cuts as enemy i's sprite must be the blob the generator read as
enemy i. Before: game.js re-derived bodies with its own hard >=15% violet rule (no edge unmixing), so on photos it could
pick a different body cell or a different count -> enemy i wears the wrong scribble / none. Now build_judge_demo passes
the generator's bodies (window.__ENEMY_BODIES__) and game.js uses them; JS rule stays only as fallback.
For every synthetic sample with enemies x seeds (photoize + normalize_photo, as in the demo) this loads game/index.html in
headless Chromium twice (fallback JS rule vs generator bodies) and compares with the spec's enemy spawns.
Asserts: with bodies, 100% match and every enemy has a cut; prints the fallback mismatch rate so the gain is measured.
Usage: test_sprite_body_parity.py [--seeds N]"""
import base64, io, json, pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parents[2]; sys.path[:0] = [str(ROOT), str(ROOT / "scripts")]
from PIL import Image
import generate_from_drawing as G, photo_normalize
from photoize import photoize
from playwright.sync_api import sync_playwright
KS = float(sys.argv[sys.argv.index("--keystone") + 1]) if "--keystone" in sys.argv else 0.0
SEEDS = int(sys.argv[sys.argv.index("--seeds") + 1]) if "--seeds" in sys.argv else 3
tmp = pathlib.Path("/tmp/sprite_parity"); tmp.mkdir(exist_ok=True)
cases = []
for k, sd in enumerate(sorted((ROOT / "samples").glob("synthetic_*"))):
    img = next(sd.glob("drawing.*")); tr = (sd / "transcript.txt").read_text().strip()
    for seed in range(1, SEEDS + 1):
        p = tmp / f"{sd.name}_s{seed}.png"; photoize(Image.open(img), seed=k * 100 + seed, keystone=KS)[0].save(p)  # same fixtures as test_photo_robust
        G._LOADED.clear(); G.PHOTO_INFO.clear(); s = G.offline_spec(p, tr)
        bodies = [[c["x"], c["y"]] for c in s.get("characters", []) if c.get("role") == "enemy"]
        if not bodies: continue
        sheet, _ = photo_normalize.normalize_photo(Image.open(p)); buf = io.BytesIO(); sheet.save(buf, "PNG")
        cases.append((f"{sd.name}/s{seed}", s, bodies, "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()))
url = (ROOT / "game/index.html").as_uri(); res = {"fallback": 0, "bodies": 0}; errs = []; fails = []
with sync_playwright() as pw:
    b = pw.chromium.launch(); pg = b.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)))
    for name, s, bodies, durl in cases:
        for mode in ("fallback", "bodies"):
            init = f"window.__SPEC__ = {json.dumps(s)}; window.__DRAWING__ = {json.dumps(durl)};" + (f" window.__ENEMY_BODIES__ = {json.dumps(bodies)};" if mode == "bodies" else "")
            ctx_pg = b.new_page(); ctx_pg.on("pageerror", lambda e: errs.append(str(e))); ctx_pg.add_init_script(init); ctx_pg.goto(url)
            ctx_pg.wait_for_function("window.__CUTS__", timeout=15000); cu = ctx_pg.evaluate("window.__CUTS__"); ctx_pg.close()
            ok = cu.get("bodies") == bodies and cu.get("enemies") == len(bodies)
            res[mode] += ok
            if not ok: fails.append((mode, name, bodies, cu.get("bodies"), cu.get("enemies")))
    b.close()
n = len(cases)
print(f"cases={n} | fallback JS rule match {res['fallback']}/{n} | generator bodies match {res['bodies']}/{n} | js_errors={len(errs)}")
for f in fails: print("  mismatch", f)
assert not errs, errs; assert res["bodies"] == n, "generator bodies must always match"
print("PASS")
