"""Gallery -> each wave8 demo card -> scenes 1..3 auto-played to the ending. Evidence: evidence/gallery_<demo>_*.png. Offline, $0."""
import pathlib, sys
from playwright.sync_api import sync_playwright
G = pathlib.Path("game/gallery.html").resolve().as_uri(); E = "evidence/gallery_"; D = sys.argv[1:] or ["gato", "dragon", "perro", "nave"]
def play(pg):
    pg.evaluate("document.getElementById('auto').click()"); pg.wait_for_function("window.__GAME__.state().status==='won'", timeout=180000)
def run(pg, d, errs):
        pg.goto(G); pg.wait_for_timeout(500); pg.screenshot(path=E + "0_index.png")
        pg.click(f'[data-demo="{d}"] a.btn:not(.alt)'); pg.wait_for_url(f"**/w_{d}.html*", timeout=20000); pg.wait_for_timeout(1500); pg.screenshot(path=E + f"{d}_1_title.png")
        pg.click("#ps .big"); pg.wait_for_timeout(900); pg.click("#ps .big"); pg.wait_for_timeout(4000)
        pg.wait_for_function("!document.querySelector('#ps .scr')", timeout=90000); pg.wait_for_timeout(1500); pg.screenshot(path=E + f"{d}_2_scene1.png"); play(pg)
        for n in (2, 3):
            pg.wait_for_url(f"**/w_{d}_{n}.html*", timeout=30000); pg.wait_for_timeout(3000); pg.screenshot(path=E + f"{d}_3_scene{n}.png"); play(pg)
        pg.wait_for_timeout(2000); pg.screenshot(path=E + f"{d}_4_ending.png")
with sync_playwright() as p:
    b = p.chromium.launch(args=["--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"]); res = {}
    for d in D:
        pg = b.new_page(viewport={"width": 1440, "height": 900}); errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
        try: run(pg, d, errs)
        except Exception as ex: pg.screenshot(path=E + f"{d}_FAIL.png"); errs.append("FAIL " + str(ex)[:150])
        res[d] = errs or "green"; print(d, res[d], flush=True); pg.close()
    print("RESULT", res)
