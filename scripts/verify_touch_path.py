#!/usr/bin/env python3
"""390x844 touch check: gallery -> Play -> 3 scenes -> ending.

Fails on visible Spanish without ?lang=es, video:true, a VERIFIED claim, or a Home/D-pad that does not work.
"""
import pathlib, re, sys
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parents[1]
GAME = ROOT / "game"
EV = ROOT / "evidence"
EV.mkdir(exist_ok=True)
GALLERY = (GAME / "gallery.html").resolve().as_uri()
PLAY = (GAME / "play.html").resolve().as_uri()
INDEX = (GAME / "index.html").resolve().as_uri()
ES = re.compile(
    r"[áéíóúñÁÉÍÓÚÑ¿¡]|\b(junt\w*|escenas?|puertas?|nenes|nene|nena|mariposas?|jugando|ganable|ganaste|"
    r"intentos?|dibujos?|dibuja|jugar|juego|tocá|deslizá|pasos|reiniciar|arreglo|estrellas?|huesos?|"
    r"castillo|flechas|jurado|juez|galería|sonido|pausa|arriba|abajo|izquierda|derecha|subibaja|"
    r"tobogan|nubes?|flores?|brillante|campeón|transcripción|jugable|procesando|agente|llamadas|"
    r"estado|evidencia|ganó|perdió|perdiste|salida|trabado|ilumina|recorta|en vivo)\b",
    re.I,
)
# "sin" and "contra" are too easy to false-hit inside English. Checked only with the accent/word list above.
VER = re.compile(r"\bVERIFIED\b", re.I)

def visible(pg):
    return pg.evaluate("""() => {
      const out = [];
      const shown = el => {
        for (let e = el; e && e !== document.documentElement; e = e.parentElement) {
          const cs = getComputedStyle(e);
          if (cs.display === 'none' || cs.visibility === 'hidden' || Number(cs.opacity) === 0) return false;
        }
        const r = el.getBoundingClientRect();
        return r.width >= 2 && r.height >= 2 && r.bottom > 0 && r.right > 0 && r.top < innerHeight && r.left < innerWidth;
      };
      const w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
      let n;
      while ((n = w.nextNode())) {
        const s = (n.nodeValue || '').replace(/\\s+/g, ' ').trim();
        if (!s || !n.parentElement || !shown(n.parentElement)) continue;
        out.push(s.slice(0, 240));
      }
      return out;
    }""")

def scan(pg, tag, fails):
    bits = visible(pg)
    blob = "\n".join(bits)
    es = [s for s in bits if ES.search(s)]
    ver = [s for s in bits if VER.search(s)]
    if es:
        fails.append(tag + " SPANISH: " + " | ".join(es[:8]))
    if ver:
        fails.append(tag + " VERIFIED: " + " | ".join(ver[:4]))
    print(tag, "visible", len(bits), "es", len(es), "verified", len(ver), flush=True)
    return blob

def sources_video(fails):
    for p in (GAME / "player_shell.js", GAME / "game.js", GAME / "beats.js", GAME / "stage3d.js", GAME / "gallery.html", GAME / "index.html"):
        t = p.read_text(errors="replace")
        if re.search(r"video\s*:\s*true", t):
            fails.append("video:true in " + p.name)

def dismiss(pg):
    for _ in range(5):
        note = pg.locator("#demoNote")
        if note.count() and note.is_visible():
            pg.locator("#demoNote button").tap()
            pg.wait_for_timeout(450)
            continue
        onb = pg.locator("#onb")
        if onb.count() and onb.is_visible():
            onb.tap()
            pg.wait_for_timeout(300)
            continue
        tale = pg.locator("#tale")
        if tale.count() and tale.is_visible():
            tale.tap()
            pg.wait_for_timeout(200)
            continue
        break

def pos(pg):
    return pg.evaluate("() => { const s = window.__GAME__.state().player; return [s.x, s.y, s && window.__GAME__.state().status]; }")

def check_controls(pg, fails):
    pg.goto(PLAY + "?mute=1", wait_until="domcontentloaded")
    pg.wait_for_function("() => window.__GAME__ && window.__GAME__.ready", timeout=30000)
    pg.wait_for_timeout(400)
    scan(pg, "play-modal", fails)
    dismiss(pg)
    pg.wait_for_timeout(300)
    scan(pg, "play-hud", fails)
    dpad = pg.locator("#dpad")
    if dpad.count() == 0 or not dpad.is_visible():
        fails.append("D-pad hidden after dismiss")
        return
    box = pg.locator("#dpad .r").bounding_box()
    if not box or box["width"] < 44 or box["height"] < 44:
        fails.append("D-pad button smaller than 44px: %s" % box)
    home = pg.locator("#home")
    hb = home.bounding_box() if home.count() else None
    if not hb or hb["width"] < 44 or hb["height"] < 44:
        fails.append("Home control too small or missing: %s" % hb)
    before = pos(pg)
    moved = None
    for sel in ("#dpad .r", "#dpad .l", "#dpad .u", "#dpad .d"):
        pg.locator(sel).tap()
        pg.wait_for_timeout(220)
        now = pos(pg)
        if now[:2] != before[:2]:
            moved = (sel, before, now)
            break
    print("dpad", moved, "box", box, "coarse", pg.evaluate("() => matchMedia('(pointer: coarse)').matches"), "touch", pg.evaluate("() => navigator.maxTouchPoints"), flush=True)
    if not moved:
        fails.append("D-pad taps did not move the player from %s" % (before,))
    pg.screenshot(path=str(EV / "verify_touch_dpad.png"))
    href = home.get_attribute("href") or ""
    if "gallery.html" not in href:
        fails.append("Home href is not gallery: " + href)
    home.tap()
    try:
        pg.wait_for_url("**/gallery.html*", timeout=8000)
    except Exception as ex:
        fails.append("Home tap did not open the gallery: " + str(ex)[:160])
        return
    if "lang=es" in pg.url:
        fails.append("Home added lang=es on the English path")
    scan(pg, "home-gallery", fails)
    pg.screenshot(path=str(EV / "verify_touch_home.png"))

def check_create(pg, fails):
    pg.goto(PLAY + "?create=1&mute=1", wait_until="domcontentloaded")
    pg.wait_for_selector("#ps .big", timeout=15000)
    scan(pg, "create-title", fails)
    pg.locator("#ps .big").tap()
    pg.wait_for_selector("#mic", timeout=10000)
    scan(pg, "create-mic", fails)
    pg.locator("#mic").tap()
    pg.wait_for_timeout(400)
    calls = pg.evaluate("() => window.__GUM_CALLS__ || []")
    print("gum", calls, flush=True)
    if not calls:
        fails.append("Record voice did not call getUserMedia")
    for c in calls:
        if c and c.get("video"):
            fails.append("video:true getUserMedia " + str(c))
        if not c or c.get("audio") is not True:
            fails.append("microphone was not audio:true " + str(c))
    blob = "\n".join(visible(pg))
    if VER.search(blob):
        fails.append("create flow shows VERIFIED")

def check_judge(pg, fails):
    pg.goto(PLAY + "?judge=1&mute=1&norender=1", wait_until="domcontentloaded")
    pg.wait_for_timeout(600)
    try:
        pg.wait_for_function("() => window.__STAGE3D__ && (window.__STAGE3D__.ok || window.__STAGE3D__.error)", timeout=20000)
    except Exception as ex:
        fails.append("judge stage3d did not boot: " + str(ex)[:120])
    pg.wait_for_timeout(400)
    scan(pg, "judge", fails)
    labels = pg.evaluate("() => window.__LABELS__ || []")
    bad = [s for s in labels if ES.search(s or "")]
    print("judge labels", labels, flush=True)
    if bad:
        fails.append("judge name labels still Spanish: " + " | ".join(bad[:8]))
    pg.screenshot(path=str(EV / "verify_touch_judge.png"))

def check_index(pg, fails):
    pg.goto(INDEX + "?mute=1", wait_until="domcontentloaded")
    pg.wait_for_timeout(500)
    scan(pg, "index", fails)

def full_path(pg, fails):
    pg.goto(GALLERY, wait_until="domcontentloaded")
    pg.wait_for_timeout(300)
    scan(pg, "gallery", fails)
    pg.screenshot(path=str(EV / "verify_touch_gallery.png"))
    pg.locator('a.btn', has_text="Play").first.tap()
    pg.wait_for_url("**/play.html*", timeout=15000)
    pg.wait_for_function("() => window.__GAME__ && window.__GAME__.ready", timeout=30000)
    dismiss(pg)
    scan(pg, "scene1", fails)
    pg.screenshot(path=str(EV / "verify_touch_scene1.png"))
    for n, nxt in ((1, "play_2.html"), (2, "play_3.html")):
        pg.evaluate("document.getElementById('auto').click()")
        pg.wait_for_function("() => window.__GAME__ && window.__GAME__.state().status === 'won'", timeout=180000)
        title = pg.evaluate("() => window.__WIN_TITLE__ || ''")
        print("scene", n, "win title", title, flush=True)
        if title != "YOU WIN!":
            fails.append("scene %s win title %r" % (n, title))
        scan(pg, "won%s" % n, fails)
        pg.wait_for_url("**/" + nxt + "*", timeout=20000)
        pg.wait_for_function("() => window.__GAME__ && window.__GAME__.ready", timeout=30000)
        pg.wait_for_timeout(900)
        dismiss(pg)
        scan(pg, "scene%s" % (n + 1), fails)
        pg.screenshot(path=str(EV / ("verify_touch_scene%s.png" % (n + 1))))
    pg.evaluate("document.getElementById('auto').click()")
    pg.wait_for_function("() => window.__GAME__ && window.__GAME__.state().status === 'won'", timeout=180000)
    title = pg.evaluate("() => window.__WIN_TITLE__ || ''")
    print("scene 3 win title", title, flush=True)
    if title != "YOU WIN!":
        fails.append("scene 3 win title %r" % (title,))
    pg.wait_for_function("() => document.body.innerText.includes('You did it')", timeout=20000)
    pg.wait_for_timeout(400)
    scan(pg, "ending", fails)
    pg.screenshot(path=str(EV / "verify_touch_ending.png"))
    if "You did it" not in "\n".join(visible(pg)):
        fails.append("ending screen did not show You did it")

def main():
    fails = []
    sources_video(fails)
    with sync_playwright() as p:
        browser = p.chromium.launch(args=["--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"])
        ctx = browser.new_context(
            viewport={"width": 390, "height": 844},
            has_touch=True,
            is_mobile=True,
            device_scale_factor=2,
            locale="en-US",
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
        )
        ctx.add_init_script("""
          window.__GUM_CALLS__ = [];
          const md = navigator.mediaDevices || (navigator.mediaDevices = {});
          md.getUserMedia = async function (c) {
            let snap = null;
            try { snap = JSON.parse(JSON.stringify(c)); } catch (e) { snap = { bad: true }; }
            window.__GUM_CALLS__.push(snap);
            const err = new Error('blocked-in-test');
            err.name = 'NotAllowedError';
            throw err;
          };
        """)
        pg = ctx.new_page()
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        try:
            check_controls(pg, fails)
            check_create(pg, fails)
            check_judge(pg, fails)
            check_index(pg, fails)
            full_path(pg, fails)
        except Exception as ex:
            try: pg.screenshot(path=str(EV / "verify_touch_FAIL.png"))
            except Exception: pass
            fails.append("EXCEPTION " + str(ex)[:400])
        if errs:
            fails.append("pageerror " + " | ".join(errs[:6]))
        browser.close()
    print("FAILS", len(fails), flush=True)
    for f in fails:
        print(" -", f, flush=True)
    return 1 if fails else 0

if __name__ == "__main__":
    sys.exit(main())
