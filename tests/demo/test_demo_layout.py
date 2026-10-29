"""Layout guard for the judge demo at 1400x900: no dead half, board above the fold, 1->2->3 order."""
import json, pathlib, sys
from playwright.sync_api import sync_playwright
p = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "game/demo.html").resolve()
with sync_playwright() as pw:
    b = pw.chromium.launch(); pg = b.new_page(viewport={"width": 1400, "height": 900}); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e))); pg.goto(p.as_uri()); pg.wait_for_timeout(800)
    m = pg.evaluate("""() => { const r = s => { const e = document.querySelector(s); if (!e) return null; const b = e.getBoundingClientRect(); return {x:b.x,y:b.y,w:b.width,h:b.height,r:b.right,bt:b.bottom}; };
      const gc = document.getElementById('c').closest('.card'), gb = gc.getBoundingClientRect(); const cards = [...document.querySelectorAll('.card')].map(e => e.getBoundingClientRect());
      const right = Math.max(...cards.map(c => c.right));
      return {vw: innerWidth, vh: innerHeight, canvas: r('#c'), draw: r('#draw'), game: {x: gb.x}, used_right: right}; }""")
    b.close()
m["dead_right_px"] = round(m["vw"] - m["used_right"]); m["canvas_bottom_in_fold"] = m["canvas"]["bt"] <= m["vh"]
m["canvas_top"] = round(m["canvas"]["y"]); m["order_ok"] = m["draw"]["x"] < m["game"]["x"]; m["js_errors"] = len(errs)
print(json.dumps({k: m[k] for k in ["dead_right_px", "canvas_top", "canvas_bottom_in_fold", "order_ok", "js_errors"]} | {"canvas_wh": [round(m["canvas"]["w"]), round(m["canvas"]["h"])]}))
ok = m["dead_right_px"] < 420 and m["canvas_top"] < 320 and m["order_ok"] and not errs
sys.exit(0 if ok else 1)
