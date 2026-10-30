#!/usr/bin/env python3
"""390x844 touch check: gallery -> Play -> 3 scenes -> ending.

Fails on visible Spanish without ?lang=es, video:true, a VERIFIED claim, or a Home/D-pad that does not work.
Also checks the story card, scene pill, objective, pause, first-time hint, gallery taglines, and 56px targets.
Pass 8: playground sparkle star (optional, off the solver path), results screen (stars + time),
and layout overflow at 390x844 and 844x390.
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
            # Reduced motion removes #tale on pointerdown before Playwright
            # finishes the tap, then retries until timeout. A detach means it closed.
            try:
                tale.tap(force=True, timeout=2500)
            except Exception:
                pg.evaluate("""() => {
                  const t = document.getElementById('tale');
                  if (!t) return;
                  t.dispatchEvent(new PointerEvent('pointerdown', { bubbles: true, cancelable: true }));
                  t.remove();
                }""")
            pg.wait_for_timeout(200)
            continue
        break

STORY_JS = r"""() => {
  const t = document.getElementById('tale');
  if (!t) return null;
  const art = t.querySelector('.art'), line = t.querySelector('.line'), hint = t.querySelector('.hint');
  const r = t.getBoundingClientRect();
  const meta = window.__TALE__ || {};
  const text = line ? line.textContent.trim() : '';
  const hit = (x, y) => {
    const el = document.elementFromPoint(x, y);
    return !!(el && (el.id === 'tale' || (el.closest && el.closest('#tale'))));
  };
  return {
    art: art ? art.textContent.trim() : '',
    line: text,
    hint: hint ? hint.textContent.trim() : '',
    ms: meta.ms || 0,
    between: !!meta.between,
    scene: meta.scene || 0,
    closed: meta.closed || '',
    ends: (text.match(/[.!?]/g) || []).length,
    full: r.width >= innerWidth - 4 && r.height >= innerHeight - 4,
    corner: hit(8, 8),
    mid: hit(Math.round(innerWidth / 2), Math.round(innerHeight / 2))
  };
}"""

def story_card(pg):
    return pg.evaluate(STORY_JS)

def tap_node(pg, sel):
    node = pg.locator(sel)
    try:
        node.tap(force=True, timeout=2500)
    except Exception:
        pg.evaluate("""(sel) => {
          const t = document.querySelector(sel);
          if (!t) return;
          t.dispatchEvent(new PointerEvent('pointerdown', { bubbles: true, cancelable: true, clientX: 20, clientY: 20 }));
        }""", sel)
    pg.wait_for_timeout(180)

def reach_tale(pg):
    pg.wait_for_function("() => window.__GAME__ && window.__GAME__.ready", timeout=30000)
    for _ in range(8):
        tale = pg.locator("#tale")
        if tale.count() and tale.is_visible():
            return True
        note = pg.locator("#demoNote")
        if note.count() and note.is_visible():
            tap_node(pg, "#demoNote button")
            continue
        onb = pg.locator("#onb")
        if onb.count() and onb.is_visible():
            tap_node(pg, "#onb")
            continue
        pg.wait_for_timeout(180)
    return False

def skip_tale(pg):
    tale = pg.locator("#tale")
    try:
        tale.tap(position={"x": 8, "y": 8}, force=True, timeout=2500)
    except Exception:
        pg.evaluate("""() => {
          const t = document.getElementById('tale');
          if (!t) return;
          t.dispatchEvent(new PointerEvent('pointerdown', { bubbles: true, cancelable: true, clientX: 8, clientY: 8 }));
        }""")
    pg.wait_for_timeout(120)

def hud_ok(pg, fails, n):
    try:
        pg.wait_for_function("() => { const o = document.querySelector('#h3c .obj'); return !!(o && o.textContent.trim()); }", timeout=4000)
    except Exception as ex:
        fails.append("scene %s objective missing: %s" % (n, str(ex)[:120]))
        return
    pill = pg.locator("#h3s").inner_text().strip()
    obj = pg.locator("#h3c .obj").inner_text().strip()
    print("hud", n, pill, obj, flush=True)
    if pill != "Scene %s/3" % n:
        fails.append("scene pill %r" % (pill,))
    if not obj:
        fails.append("scene %s objective empty" % n)
    if ES.search(pill) or ES.search(obj):
        fails.append("HUD Spanish on scene %s: %s | %s" % (n, pill, obj))

def boxes_under(pg, sel):
    return pg.evaluate("""(sel) => [...document.querySelectorAll(sel)].map(el => {
      const r = el.getBoundingClientRect();
      return { t: (el.textContent || '').replace(/\\s+/g, ' ').trim().slice(0, 48), w: Math.round(r.width), h: Math.round(r.height) };
    })""", sel)

def require_56(fails, rows, tag):
    for row in rows:
        if row["w"] < 56 or row["h"] < 56:
            fails.append("%s target under 56px: %s" % (tag, row))

def safe_area_css(pg):
    return pg.evaluate("""() => {
      const css = [...document.querySelectorAll('style')].map(s => s.textContent).join('\\n');
      return ['safe-area-inset-top', 'safe-area-inset-right', 'safe-area-inset-bottom', 'safe-area-inset-left'].every(k => css.includes(k));
    }""")

def check_gallery_polish(pg, fails):
    if not safe_area_css(pg):
        fails.append("gallery CSS missing safe-area insets")
    rows = boxes_under(pg, "a.btn, p.note a")
    print("gallery targets", rows, flush=True)
    require_56(fails, rows, "gallery")
    lines = pg.evaluate("""() => [...document.querySelectorAll('.c p')].map(p => (p.textContent || '').replace(/\\s+/g, ' ').trim())""")
    if len(lines) < 21:
        fails.append("gallery taglines missing: %s" % len(lines))
    for line in lines:
        body = re.sub(r"[\U0001F000-\U0001FAFF\u2600-\u27BF\uFE0F\u200D]", "", line)
        marks = re.findall(r"[.!?]", body)
        if len(marks) != 1:
            fails.append("gallery tagline is not one sentence: " + line)
        if not re.search(r"[\U0001F000-\U0001FAFF\u2600-\u27BF]", line):
            fails.append("gallery tagline missing emoji: " + line)
        if ES.search(line):
            fails.append("gallery tagline Spanish: " + line)

def check_story(pg, fails):
    pg.goto(PLAY + "?mute=1", wait_until="domcontentloaded")
    pg.evaluate("() => { try { localStorage.removeItem('dj_onboard_v2'); localStorage.removeItem('dj_onboard_v1'); } catch (e) {} }")
    pg.reload(wait_until="domcontentloaded")
    pg.wait_for_function("() => window.__GAME__ && window.__GAME__.ready", timeout=30000)
    pg.wait_for_selector("#demoNote", timeout=15000)
    pg.locator("#demoNote button").tap()
    pg.wait_for_timeout(250)
    onb = pg.locator("#onb")
    if onb.count() == 0 or not onb.is_visible():
        fails.append("first-time onboarding hint did not show")
    else:
        text = onb.inner_text()
        print("onb", text.replace("\n", " | "), flush=True)
        low = text.lower()
        if "first time here" not in low or "tap anywhere to start" not in low:
            fails.append("onboarding copy changed: " + text.replace("\n", " | ")[:180])
        if ES.search(text):
            fails.append("onboarding Spanish on the English path")
        if pg.locator("#tale").count() and pg.locator("#tale").is_visible():
            fails.append("story card covered the first-time hint")
        pg.screenshot(path=str(EV / "verify_touch_onboard.png"))
        tap_node(pg, "#onb")
    pg.wait_for_selector("#tale", timeout=4000)
    card = story_card(pg)
    print("story1", card, flush=True)
    if not card or card.get("scene") != 1 or card.get("between"):
        fails.append("opening story card: %s" % card)
    elif card.get("ends") != 1 or card.get("ms") != 4000 or not card.get("full") or not card.get("corner") or not card.get("mid"):
        fails.append("opening story shape: %s" % card)
    elif "Tap anywhere to skip" not in (card.get("hint") or "") or "magic door" not in (card.get("line") or "") or "🦋" not in (card.get("art") or ""):
        fails.append("opening story copy: %s" % card)
    pg.screenshot(path=str(EV / "verify_touch_story.png"))
    skip_tale(pg)
    closed = pg.evaluate("() => ({ closed: window.__TALE__ && window.__TALE__.closed, up: !!document.getElementById('tale') })")
    print("skip", closed, flush=True)
    if not closed or closed.get("closed") != "tap" or closed.get("up"):
        fails.append("tap anywhere did not skip the story: %s" % closed)
    pg.reload(wait_until="domcontentloaded")
    pg.wait_for_function("() => window.__GAME__ && window.__GAME__.ready", timeout=30000)
    pg.wait_for_selector("#demoNote", timeout=15000)
    pg.locator("#demoNote button").tap()
    pg.wait_for_timeout(300)
    if pg.locator("#onb").count() and pg.locator("#onb").is_visible():
        fails.append("onboarding showed again after the first visit")
    try:
        pg.wait_for_selector("#tale", timeout=4000)
    except Exception as ex:
        fails.append("story card missing on the second visit: " + str(ex)[:120])
        return
    try:
        pg.wait_for_function("() => window.__TALE__ && window.__TALE__.closed === 'auto' && !document.getElementById('tale')", timeout=8000)
    except Exception as ex:
        fails.append("story card did not auto-skip: " + str(ex)[:140])
    else:
        dt = pg.evaluate("() => Date.now() - (window.__TALE__ && window.__TALE__.at || 0)")
        print("auto ms", dt, flush=True)
        if dt < 3400 or dt > 7000:
            fails.append("story auto-skip was %sms, expected about 4000" % dt)
    hud_ok(pg, fails, 1)
    if not safe_area_css(pg):
        fails.append("play shell missing safe-area insets")
    require_56(fails, boxes_under(pg, "#pz, #mu, #home"), "hud")
    pg.screenshot(path=str(EV / "verify_touch_hud.png"))
    pg.locator("#pz").tap()
    pg.wait_for_timeout(250)
    if not pg.locator("#pzo").is_visible():
        fails.append("pause button did not open the pause menu")
    else:
        require_56(fails, boxes_under(pg, "#pzo button, #pzo a"), "pause")
        scan(pg, "pause", fails)
        pg.screenshot(path=str(EV / "verify_touch_pause.png"))
        pg.locator("#pzo button").first.tap()
        pg.wait_for_timeout(200)
        if pg.locator("#pzo").is_visible():
            fails.append("Keep playing did not close pause")

def check_between(pg, fails, n):
    try:
        pg.wait_for_selector("#tale", timeout=5000)
    except Exception as ex:
        fails.append("scene %s story card missing between scenes: %s" % (n, str(ex)[:120]))
        return
    card = story_card(pg)
    print("between", n, card, flush=True)
    if not card or not card.get("between") or card.get("scene") != n:
        fails.append("scene %s was not a between-scene story: %s" % (n, card))
    elif card.get("ends") != 1 or card.get("ms") != 4000 or not card.get("full") or "Tap anywhere to skip" not in (card.get("hint") or ""):
        fails.append("scene %s story shape: %s" % (n, card))
    else:
        want = "cloud" if n == 2 else "sun"
        mark = "☁" if n == 2 else "☀"
        if want not in (card.get("line") or "").lower() or mark not in (card.get("art") or ""):
            fails.append("scene %s story copy: %s" % (n, card))
    pg.screenshot(path=str(EV / ("verify_touch_story%s.png" % n)))

def check_es(pg, fails):
    pg.goto(PLAY + "?lang=es&mute=1", wait_until="domcontentloaded")
    if not reach_tale(pg):
        fails.append("Spanish story card did not appear")
        return
    card = story_card(pg)
    pill = pg.locator("#h3s").inner_text().strip()
    print("es", pill, card, flush=True)
    if pill != "Escena 1/3":
        fails.append("Spanish scene pill %r" % (pill,))
    line = (card or {}).get("line") or ""
    if not ES.search(line):
        fails.append("Spanish story card stayed in English: " + line)
    if VER.search(line):
        fails.append("Spanish story claims VERIFIED")
    pg.screenshot(path=str(EV / "verify_touch_story_es.png"))
    dismiss(pg)

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
    if not box or box["width"] < 56 or box["height"] < 56:
        fails.append("D-pad button smaller than 56px: %s" % box)
    home = pg.locator("#home")
    hb = home.bounding_box() if home.count() else None
    if not hb or hb["width"] < 56 or hb["height"] < 56:
        fails.append("Home control too small or missing: %s" % hb)
    hud_ok(pg, fails, 1)
    require_56(fails, boxes_under(pg, "#pz, #mu"), "play")
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

COLLECT_JS = r"""() => {
  const G = window.__GAME__;
  G.reset();
  const sp = G.spec;
  const sparkK = (window.__SPARK__ && window.__SPARK__.cell) ? (window.__SPARK__.cell.x + ',' + window.__SPARK__.cell.y) : '';
  let hitSpark = false;
  const wall = new Set();
  const block = (x, y, w, h) => { for (let i = 0; i < (w || 1); i++) for (let j = 0; j < (h || 1); j++) wall.add((x + i) + ',' + (y + j)); };
  (sp.walls || []).forEach(w => block(w.x, w.y, w.w, w.h));
  (sp.hazards || []).forEach(w => block(w.x, w.y, w.w, w.h));
  (G.gates ? G.gates() : []).forEach(g => { if (g.cell) wall.add(g.cell[0] + ',' + g.cell[1]); if (g.alt) wall.add(g.alt[0] + ',' + g.alt[1]); });
  const W = sp.grid.w, H = sp.grid.h;
  const foeAt = (x, y) => (G.state().foes || []).some(f => f.x === x && f.y === y);
  function pathTo(tx, ty) {
    const S = G.state();
    const start = S.player.x + ',' + S.player.y;
    const prev = {}; prev[start] = null;
    const Q = [[S.player.x, S.player.y]];
    const doorK = sp.door ? (sp.door.x + ',' + sp.door.y) : '';
    const target = tx + ',' + ty;
    let found = false;
    while (Q.length) {
      const [x, y] = Q.shift();
      if (x === tx && y === ty) { found = true; break; }
      for (const [dx, dy] of [[1, 0], [-1, 0], [0, 1], [0, -1]]) {
        const nx = x + dx, ny = y + dy, k = nx + ',' + ny;
        if (nx < 0 || ny < 0 || nx >= W || ny >= H || wall.has(k) || k in prev) continue;
        if (doorK && k === doorK && k !== target) continue;
        if (foeAt(nx, ny)) continue;
        prev[k] = [x, y, dx, dy];
        Q.push([nx, ny]);
      }
    }
    if (!found) return null;
    const mv = []; let k = target;
    while (prev[k]) { const row = prev[k]; mv.unshift([row[2], row[3]]); k = row[0] + ',' + row[1]; }
    return mv;
  }
  const goals = (sp.goals || []).slice();
  for (const g of goals) {
    if ((G.state().collected || []).indexOf(g.id) >= 0) continue;
    const mv = pathTo(g.x, g.y);
    if (!mv) return { ok: false, why: 'no path', id: g.id, at: [G.state().player.x, G.state().player.y], status: G.state().status };
    for (const m of mv) {
      const st = G.state();
      if (st.status !== 'playing') return { ok: false, why: 'stopped', status: st.status, events: (st.events || []).slice(-4) };
      if (st.doorOpen && sp.door && st.player.x + m[0] === sp.door.x && st.player.y + m[1] === sp.door.y) {
        return { ok: false, why: 'would step on open door', at: [st.player.x, st.player.y] };
      }
      G.move(m[0], m[1]);
      const pp = G.state().player;
      if (sparkK && pp.x + ',' + pp.y === sparkK) hitSpark = true;
    }
    const after = G.state();
    if (after.status !== 'playing') return { ok: false, why: 'after goal', id: g.id, status: after.status, events: (after.events || []).slice(-4) };
  }
  const S = G.state();
  const need = (sp.goals || []).length;
  return { ok: S.status === 'playing' && S.collected.length >= Math.min(2, need) && (!sp.door || !!S.doorOpen), collected: S.collected.length, need: need, door: !!S.doorOpen, status: S.status, pos: [S.player.x, S.player.y], hitSpark: hitSpark, stars: (window.__RUN__ && window.__RUN__.stars) || 0 };
}"""


def juice_scene(pg, fails):
    """Landing dust, collect combo, unlocked-door heartbeat. Leaves the level reset."""
    origin = pos(pg)
    moved = False
    for sel in ("#dpad .r", "#dpad .d", "#dpad .l", "#dpad .u"):
        pg.locator(sel).tap()
        pg.wait_for_timeout(90)
        if pos(pg)[:2] != origin[:2]:
            moved = True
            break
    if not moved:
        fails.append("could not step the hero to spawn landing dust")
    else:
        try:
            pg.wait_for_function("() => window.__STAGE3D__ && window.__STAGE3D__.dust > 0", timeout=5000)
        except Exception as ex:
            fails.append("landing dust did not spawn: " + str(ex)[:140])
        else:
            info = pg.evaluate("() => ({dust: window.__STAGE3D__.dust, travel: window.__STAGE3D__.dustTravel, live: window.__STAGE3D__.dustLive, reduced: !!window.__STAGE3D__.reduced})")
            print("dust", info, flush=True)
            if info["reduced"]:
                fails.append("main touch path unexpectedly has reduced motion")
            if not info["dust"]:
                fails.append("dust counter stayed at 0")
            if info["travel"] != 1:
                fails.append("landing dust should travel when motion is allowed: %s" % info)
        pg.wait_for_timeout(160)
        pg.screenshot(path=str(EV / "verify_touch_dust.png"))
    pg.evaluate("() => window.__GAME__.reset()")
    pg.wait_for_timeout(120)
    walked = pg.evaluate(COLLECT_JS)
    print("walk", walked, flush=True)
    if not walked or not walked.get("ok") or not walked.get("door"):
        fails.append("combo/door setup failed: %s" % walked)
    else:
        try:
            pg.wait_for_function("() => { const c = document.getElementById('combo'); return !!(c && c.classList.contains('on') && /Combo/i.test(c.textContent || '') && /[2-9]/.test(c.textContent || '')); }", timeout=3000)
        except Exception as ex:
            fails.append("combo popup missing: " + str(ex)[:160])
        combo = pg.evaluate("() => { const c = document.getElementById('combo'); return { text: c ? c.textContent : '', n: window.__JUICE__ && window.__JUICE__.combo }; }")
        print("combo", combo, flush=True)
        if ES.search(combo.get("text") or ""):
            fails.append("combo popup is Spanish on the English path: " + (combo.get("text") or ""))
        if not combo.get("n") or combo["n"] < 2:
            fails.append("combo count did not reach 2: %s" % combo)
        pg.screenshot(path=str(EV / "verify_touch_combo.png"), timeout=8000, animations="disabled")
        seen = pg.evaluate("() => { const c = document.getElementById('combo'); if (!c) return null; const cs = getComputedStyle(c); return { on: c.classList.contains('on'), op: cs.opacity, text: c.textContent }; }")
        print("combo seen", seen, flush=True)
        if not seen or seen.get("op") == "0" or not seen.get("on"):
            fails.append("combo popup faded before the screenshot: %s" % seen)
        pg.evaluate("() => { const s = window.__STAGE3D__; s.heartbeatMax = 0; s.doorScaleMin = null; s.doorScaleMax = 0; }")
        try:
            pg.wait_for_function("() => window.__STAGE3D__ && window.__STAGE3D__.doorOpen && window.__STAGE3D__.heartbeatMax > 0.55 && (window.__STAGE3D__.doorScaleMax - window.__STAGE3D__.doorScaleMin) > 0.04", timeout=8000)
        except Exception as ex:
            snap = pg.evaluate("() => window.__STAGE3D__ && ({hb: window.__STAGE3D__.heartbeat, max: window.__STAGE3D__.heartbeatMax, min: window.__STAGE3D__.doorScaleMin, maxs: window.__STAGE3D__.doorScaleMax, open: window.__STAGE3D__.doorOpen})")
            fails.append("unlocked door did not heartbeat: %s %s" % (snap, str(ex)[:80]))
        else:
            print("heart", pg.evaluate("() => ({max: window.__STAGE3D__.heartbeatMax, span: +(window.__STAGE3D__.doorScaleMax - window.__STAGE3D__.doorScaleMin).toFixed(3)})"), flush=True)
            pg.screenshot(path=str(EV / "verify_touch_heartbeat.png"))
    pg.evaluate("""() => {
      const c = document.getElementById('combo'); if (c) c.remove();
      if (window.__GAME__) window.__GAME__.reset();
      window.__DOOR_WALK__ = false;
    }""")
    pg.wait_for_timeout(180)
    st = pg.evaluate("() => window.__GAME__.state().status")
    if st != "playing":
        fails.append("juice left the scene in status %s" % st)


def transition_state(pg):
    return pg.evaluate("""() => {
      const d = document.getElementById('dpad');
      const w = document.getElementById('wipe');
      const cs = d ? getComputedStyle(d) : null;
      const btn = d ? d.querySelector('button') : null;
      const hidden = !d || d.hidden || !!(cs && (cs.display === 'none' || cs.visibility === 'hidden' || cs.pointerEvents === 'none'));
      const disabled = !d || d.getAttribute('aria-disabled') === 'true' || !!(btn && btn.disabled);
      return { hidden: hidden, disabled: disabled, fx: w && w.dataset ? (w.dataset.fx || '') : '', on: !!(w && w.classList.contains('on')), transitioning: document.body.classList.contains('transitioning') };
    }""")


def check_transition(pg, fails, n):
    try:
        pg.wait_for_function("() => document.body.classList.contains('transitioning')", timeout=8000)
    except Exception as ex:
        fails.append("scene %s did not start a scene transition: %s" % (n, str(ex)[:120]))
        return
    fx = transition_state(pg)
    print("transition", n, fx, flush=True)
    if fx.get("fx") not in ("iris", "wipe"):
        fails.append("scene %s transition was %r, expected iris or wipe" % (n, fx.get("fx")))
    if not fx.get("hidden") or not fx.get("disabled"):
        fails.append("D-pad stayed usable during the scene %s transition: %s" % (n, fx))
    if n == 1:
        try:
            pg.screenshot(path=str(EV / "verify_touch_wipe.png"), timeout=8000, animations="disabled")
        except Exception as ex:
            fails.append("wipe screenshot failed: " + str(ex)[:160])


def check_reduced(browser, fails):
    ctx = browser.new_context(
        viewport={"width": 390, "height": 844},
        has_touch=True,
        is_mobile=True,
        device_scale_factor=2,
        locale="en-US",
        reduced_motion="reduce",
        user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
    )
    pg = ctx.new_page()
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    try:
        pg.goto(PLAY + "?mute=1", wait_until="domcontentloaded")
        pg.wait_for_function("() => window.__GAME__ && window.__GAME__.ready && window.__STAGE3D__ && (window.__STAGE3D__.ok || window.__STAGE3D__.error)", timeout=30000)
        if pg.evaluate("() => window.__STAGE3D__.error || null"):
            fails.append("reduced-motion stage failed: " + str(pg.evaluate("() => window.__STAGE3D__.error")))
        if reach_tale(pg):
            anim = pg.evaluate("() => getComputedStyle(document.querySelector('#tale .art')).animationName")
            print("reduced tale anim", anim, flush=True)
            if anim and anim != "none":
                fails.append("reduced-motion story art still moves: " + str(anim))
            pg.screenshot(path=str(EV / "verify_touch_story_reduced.png"))
        else:
            fails.append("reduced-motion story card did not appear")
        dismiss(pg)
        if not pg.evaluate("() => !!window.__STAGE3D__.reduced"):
            fails.append("prefers-reduced-motion did not freeze stage motion")
        spark = pg.evaluate("() => ({spark: window.__STAGE3D__.spark || 0, on: window.__STAGE3D__.sparkOn || 0, spin: window.__STAGE3D__.sparkSpin || 0})")
        print("reduced spark", spark, flush=True)
        if spark.get("spark") != 1 or spark.get("on") != 1 or spark.get("spin") != 0:
            fails.append("reduced-motion sparkle star still moves or is hidden: %s" % spark)
        pg.screenshot(path=str(EV / "verify_touch_spark_reduced.png"))
        origin = pos(pg)
        for sel in ("#dpad .r", "#dpad .d", "#dpad .l", "#dpad .u"):
            if not pg.locator("#dpad").is_visible():
                break
            pg.locator(sel).tap()
            pg.wait_for_timeout(90)
            if pos(pg)[:2] != origin[:2]:
                break
        pg.wait_for_function("() => window.__STAGE3D__.dust > 0", timeout=5000)
        info = pg.evaluate("() => ({dust: window.__STAGE3D__.dust, travel: window.__STAGE3D__.dustTravel})")
        print("reduced dust", info, flush=True)
        if info["travel"] != 0:
            fails.append("reduced-motion dust still travels: %s" % info)
        pg.screenshot(path=str(EV / "verify_touch_reduced_dust.png"))
        walked = pg.evaluate(COLLECT_JS)
        print("reduced walk", walked, flush=True)
        if not walked or not walked.get("door"):
            fails.append("reduced-motion door setup failed: %s" % walked)
        else:
            pg.evaluate("() => { const s = window.__STAGE3D__; s.heartbeatMax = 0; s.doorScaleMin = null; s.doorScaleMax = 0; }")
            pg.wait_for_timeout(1100)
            snap = pg.evaluate("() => ({hb: window.__STAGE3D__.heartbeat, max: window.__STAGE3D__.heartbeatMax, min: window.__STAGE3D__.doorScaleMin, maxs: window.__STAGE3D__.doorScaleMax})")
            print("reduced heart", snap, flush=True)
            span = 0 if snap["min"] is None else abs((snap["maxs"] or 0) - snap["min"])
            if snap["hb"] or snap["max"]:
                fails.append("reduced-motion door still heartbeats: %s" % snap)
            if span > 0.02:
                fails.append("reduced-motion door scale still moves: %s" % snap)
            pg.screenshot(path=str(EV / "verify_touch_reduced_door.png"))
        pg.evaluate("() => window.__JUICE__ && window.__JUICE__.playConfetti && window.__JUICE__.playConfetti()")
        pg.wait_for_timeout(150)
        cele = pg.evaluate("() => ({n: window.__JUICE__ && window.__JUICE__.confetti, reduced: window.__JUICE__ && window.__JUICE__.confettiReduced, shapes: (window.__JUICE__ && window.__JUICE__.shapes) || [], canvas: !!document.getElementById('winconfetti')})")
        print("reduced confetti", cele, flush=True)
        if not cele["canvas"] or not cele["reduced"] or (cele["n"] or 0) < 36:
            fails.append("reduced-motion win confetti was not a still burst: %s" % cele)
        if "star" not in cele["shapes"] or "ribbon" not in cele["shapes"]:
            fails.append("win confetti shapes missing star/ribbon: %s" % cele["shapes"])
        pg.screenshot(path=str(EV / "verify_touch_reduced_confetti.png"))
        scan(pg, "reduced", fails)
    except Exception as ex:
        try: pg.screenshot(path=str(EV / "verify_touch_reduced_FAIL.png"))
        except Exception: pass
        fails.append("reduced-motion EXCEPTION " + str(ex)[:300])
    if errs:
        fails.append("reduced pageerror " + " | ".join(errs[:4]))
    ctx.close()


def layout_overflow(pg):
    return pg.evaluate("""() => {
      const bad = [];
      const vw = innerWidth, vh = innerHeight;
      const root = document.documentElement;
      if (root.scrollWidth > vw + 2) bad.push('scrollWidth ' + root.scrollWidth);
      const fixedIds = { home: 1, pz: 1, mu: 1, dpad: 1, hud3: 1, h3c: 1, h3s: 1, h3spark: 1 };
      for (const el of document.querySelectorAll('#home,#pz,#mu,#dpad,#hud3,#h3c,#h3s,#h3spark,h1,h2')) {
        if (el.hidden) continue;
        const cs = getComputedStyle(el);
        if (cs.display === 'none' || cs.visibility === 'hidden' || Number(cs.opacity) === 0) continue;
        const r = el.getBoundingClientRect();
        if (r.width < 2 || r.height < 2) continue;
        const name = el.id || el.tagName;
        if (r.left < -1 || r.right > vw + 1) bad.push(name + ' x ' + Math.round(r.left) + '..' + Math.round(r.right));
        if (fixedIds[el.id] && (r.top < -1 || r.bottom > vh + 1)) bad.push(name + ' y ' + Math.round(r.top) + '..' + Math.round(r.bottom));
      }
      return bad;
    }""")

def check_spark(pg, fails):
    """Bonus star on playground scene 1: visible, off the blocking grid, score +1, solver path unchanged."""
    try:
        pg.wait_for_function("() => window.__STAGE3D__ && window.__STAGE3D__.ok && window.__SPARK__ && window.__SPARK__.cell", timeout=15000)
    except Exception as ex:
        fails.append("sparkle star did not mount: " + str(ex)[:140])
        return
    info = pg.evaluate("""() => {
      const s = window.__STAGE3D__ || {}, k = window.__SPARK__ || {}, spec = window.__GAME__.spec, c = k.cell;
      const hit = (list) => (list || []).some(r => c && c.x >= r.x && c.x < r.x + (r.w || 1) && c.y >= r.y && c.y < r.y + (r.h || 1));
      const goal = (spec.goals || []).some(g => c && g.x === c.x && g.y === c.y);
      const door = !!(spec.door && c && spec.door.x === c.x && spec.door.y === c.y);
      const start = !!(c && spec.player.x === c.x && spec.player.y === c.y);
      return { spark: s.spark || 0, on: s.sparkOn || 0, spin: s.sparkSpin || 0, cell: c, blocked: !c || hit(spec.walls) || hit(spec.hazards) || goal || door || start, goals: (spec.goals || []).map(g => g.id) };
    }""")
    print("spark", info, flush=True)
    pg.screenshot(path=str(EV / "verify_touch_spark.png"))
    if not info or info.get("spark") != 1 or info.get("on") != 1:
        fails.append("playground sparkle star is not visible: %s" % info)
        return
    if info.get("blocked"):
        fails.append("sparkle star blocks or sits on a rule cell: %s" % info)
        return
    if info.get("spin") != 1:
        fails.append("sparkle star should twinkle when motion is allowed: %s" % info)
    took = pg.evaluate("""() => {
      const g = window.__GAME__, cell = window.__SPARK__.cell;
      g.reset();
      const before = g.state();
      const col = (before.collected || []).slice();
      let guard = 0;
      while (guard++ < 8) {
        const S = g.state();
        if (S.status !== 'playing') return { ok: false, why: 'status', status: S.status };
        if (S.player.x === cell.x && S.player.y === cell.y) break;
        const dx = Math.sign(cell.x - S.player.x), dy = Math.sign(cell.y - S.player.y);
        const step = Math.abs(cell.x - S.player.x) >= Math.abs(cell.y - S.player.y) ? [dx || 0, 0] : [0, dy || 0];
        if (!step[0] && !step[1]) return { ok: false, why: 'stuck', pos: [S.player.x, S.player.y] };
        g.move(step[0], step[1]);
      }
      if (window.__WATCH_SPARK__) window.__WATCH_SPARK__();
      const S = g.state();
      const same = S.collected.join(',') === col.join(',');
      return { ok: !!(window.__SPARK__.got) && (window.__RUN__ && window.__RUN__.stars) === 1 && S.status === 'playing' && same && S.collected.indexOf('spark_patio') < 0, stars: window.__RUN__ && window.__RUN__.stars, got: window.__SPARK__.got, status: S.status, collected: S.collected, pos: [S.player.x, S.player.y], goals: g.spec.goals.length };
    }""")
    print("spark took", took, flush=True)
    pg.screenshot(path=str(EV / "verify_touch_spark_got.png"))
    if not took or not took.get("ok"):
        fails.append("picking up the sparkle star changed the rules: %s" % took)
        return
    popped = pg.evaluate("() => { const c = document.getElementById('sparkpop'); return c ? c.textContent : ''; }")
    if popped and ES.search(popped):
        fails.append("bonus star popup is Spanish on the English path: " + popped)
    walked = pg.evaluate(COLLECT_JS)
    print("spark path", walked, flush=True)
    if not walked or not walked.get("ok") or not walked.get("door"):
        fails.append("solver walk failed after the bonus star: %s" % walked)
    elif walked.get("hitSpark"):
        fails.append("solver path stepped on the bonus star: %s" % walked)
    elif walked.get("stars") != 1:
        fails.append("bonus score did not stay a cosmetic +1: %s" % walked)
    pg.evaluate("""() => { if (window.__GAME__) window.__GAME__.reset(); window.__DOOR_WALK__ = false; }""")
    try:
        pg.wait_for_function("() => window.__SPARK__ && window.__SPARK__.got && window.__STAGE3D__ && window.__STAGE3D__.sparkOn === 0 && window.__RUN__ && window.__RUN__.stars === 1 && window.__GAME__.state().status === 'playing' && !window.__GAME__.state().doorOpen", timeout=3000)
    except Exception as ex:
        hidden = pg.evaluate("() => ({on: window.__STAGE3D__ && window.__STAGE3D__.sparkOn, got: window.__SPARK__ && window.__SPARK__.got, stars: window.__RUN__ && window.__RUN__.stars, status: window.__GAME__.state().status, door: !!window.__GAME__.state().doorOpen})")
        fails.append("reset did not keep the cosmetic star and a closed door: %s %s" % (hidden, str(ex)[:80]))
    else:
        print("spark after reset", pg.evaluate("() => ({on: window.__STAGE3D__.sparkOn, got: window.__SPARK__.got, stars: window.__RUN__.stars})"), flush=True)

def check_results(pg, fails):
    try:
        pg.wait_for_selector("#results", timeout=4000)
    except Exception as ex:
        fails.append("results screen missing: " + str(ex)[:120])
        return
    res = pg.evaluate("""() => {
      const el = document.getElementById('results');
      el.scrollIntoView({ block: 'center', inline: 'nearest' });
      const r = el.getBoundingClientRect();
      return { text: (el.innerText || '').replace(/\\s+/g, ' ').trim(), data: window.__RESULTS__ || null, top: Math.round(r.top), bottom: Math.round(r.bottom), left: Math.round(r.left), right: Math.round(r.right), vh: innerHeight, vw: innerWidth };
    }""")
    print("results", res, flush=True)
    text = (res or {}).get("text") or ""
    data = (res or {}).get("data") or {}
    if data.get("stars") != 1 or ("Stars collected: %s" % data.get("stars")) not in text:
        fails.append("results stars: %s" % res)
    if not re.search(r"Time: \d+:\d\d", text):
        fails.append("results time: %s" % text)
    if ES.search(text) or VER.search(text):
        fails.append("results leak: " + text)
    if res and (res["left"] < -1 or res["right"] > res["vw"] + 1 or res["top"] < -1 or res["bottom"] > res["vh"] + 1):
        fails.append("results overflow the ending screen: %s" % res)
    pg.screenshot(path=str(EV / "verify_touch_results.png"))

def check_other_world(pg, fails):
    other = (GAME / "w_gato.html").resolve().as_uri()
    pg.goto(other + "?mute=1", wait_until="domcontentloaded")
    try:
        pg.wait_for_function("() => window.__STAGE3D__ && (window.__STAGE3D__.ok || window.__STAGE3D__.error) && window.__SPARK__", timeout=30000)
    except Exception as ex:
        fails.append("other world stage did not boot: " + str(ex)[:140])
        return
    info = pg.evaluate("() => ({cell: window.__SPARK__ && window.__SPARK__.cell, spark: window.__STAGE3D__.spark || 0, sample: (window.__BUNDLE__ && window.__BUNDLE__.sample) || ''})")
    print("nospark", info, flush=True)
    if info.get("cell") or info.get("spark"):
        fails.append("sparkle star leaked outside playground_01: %s" % info)
    pg.screenshot(path=str(EV / "verify_touch_nospark.png"))

def restore_window(pg):
    """Fullscreen from the demo Play tap blocks later viewport resizes."""
    try:
        pg.evaluate("""() => {
          const d = document;
          if (d.fullscreenElement && d.exitFullscreen) return d.exitFullscreen();
        }""")
    except Exception:
        pass
    try:
        cdp = pg.context.new_cdp_session(pg)
        info = cdp.send("Browser.getWindowForTarget")
        cdp.send("Browser.setWindowBounds", {
            "windowId": info["windowId"],
            "bounds": {"windowState": "normal"},
        })
        try:
            cdp.detach()
        except Exception:
            pass
    except Exception:
        pass


def check_landscape(pg, fails):
    restore_window(pg)
    pg.set_viewport_size({"width": 844, "height": 390})
    pg.goto(GALLERY, wait_until="domcontentloaded")
    pg.wait_for_timeout(250)
    bad = layout_overflow(pg)
    print("land gallery", bad, flush=True)
    if bad:
        fails.append("landscape gallery overflow: " + " | ".join(bad[:8]))
    scan(pg, "land-gallery", fails)
    pg.screenshot(path=str(EV / "verify_touch_gallery_land.png"))
    pg.goto(INDEX + "?mute=1", wait_until="domcontentloaded")
    pg.wait_for_timeout(300)
    bad = layout_overflow(pg)
    print("land index", bad, flush=True)
    if bad:
        fails.append("landscape lab overflow: " + " | ".join(bad[:8]))
    scan(pg, "land-index", fails)
    pg.screenshot(path=str(EV / "verify_touch_index_land.png"))
    pg.goto(PLAY + "?mute=1", wait_until="domcontentloaded")
    pg.wait_for_function("() => window.__GAME__ && window.__GAME__.ready", timeout=30000)
    dismiss(pg)
    pg.wait_for_timeout(250)
    bad = layout_overflow(pg)
    print("land play", bad, flush=True)
    if bad:
        fails.append("landscape play overflow: " + " | ".join(bad[:8]))
    rows = boxes_under(pg, "#pz, #mu, #home, #dpad button")
    print("land targets", rows, flush=True)
    require_56(fails, rows, "landscape")
    scan(pg, "land-play", fails)
    pg.screenshot(path=str(EV / "verify_touch_play_land.png"))
    restore_window(pg)
    pg.wait_for_timeout(150)
    pg.set_viewport_size({"width": 390, "height": 844})

def full_path(pg, fails):
    pg.goto(GALLERY, wait_until="domcontentloaded")
    pg.wait_for_timeout(300)
    scan(pg, "gallery", fails)
    check_gallery_polish(pg, fails)
    pg.screenshot(path=str(EV / "verify_touch_gallery.png"))
    pg.locator('a.btn', has_text="Play").first.tap()
    pg.wait_for_url("**/play.html*", timeout=15000)
    pg.wait_for_function("() => window.__GAME__ && window.__GAME__.ready", timeout=30000)
    dismiss(pg)
    hud_ok(pg, fails, 1)
    scan(pg, "scene1", fails)
    pg.screenshot(path=str(EV / "verify_touch_scene1.png"))
    scene_fit = layout_overflow(pg)
    print("scene1 fit", scene_fit, flush=True)
    if scene_fit:
        fails.append("portrait play overflow: " + " | ".join(scene_fit[:8]))
    check_spark(pg, fails)
    juice_scene(pg, fails)
    for n, nxt in ((1, "play_2.html"), (2, "play_3.html")):
        pg.evaluate("() => { window.__HOLD_FX__ = 1800 }")
        pg.evaluate("document.getElementById('auto').click()")
        pg.wait_for_function("() => window.__GAME__ && window.__GAME__.state().status === 'won'", timeout=180000)
        pg.wait_for_timeout(280)
        conf = pg.evaluate("() => (window.__STAGE3D__ && window.__STAGE3D__.confetti) || 0")
        print("scene", n, "confetti3d", conf, flush=True)
        if conf < 40:
            fails.append("scene %s win confetti count %s" % (n, conf))
        if n == 1:
            pg.screenshot(path=str(EV / "verify_touch_win_confetti.png"))
        title = pg.evaluate("() => window.__WIN_TITLE__ || ''")
        print("scene", n, "win title", title, flush=True)
        if title != "YOU WIN!":
            fails.append("scene %s win title %r" % (n, title))
        scan(pg, "won%s" % n, fails)
        check_transition(pg, fails, n)
        pg.wait_for_url("**/" + nxt + "*", timeout=20000)
        pg.wait_for_function("() => window.__GAME__ && window.__GAME__.ready", timeout=30000)
        check_between(pg, fails, n + 1)
        dismiss(pg)
        hud_ok(pg, fails, n + 1)
        scan(pg, "scene%s" % (n + 1), fails)
        pg.screenshot(path=str(EV / ("verify_touch_scene%s.png" % (n + 1))))
        arrived = pg.evaluate("() => { const w = document.getElementById('wipe'); return w && w.dataset ? (w.dataset.fx || '') : ''; }")
        expect = "wipe" if (n + 1) % 2 == 0 else "iris"
        print("arrived", n + 1, arrived, flush=True)
        if arrived != expect:
            fails.append("scene %s arrival transition was %r, expected %s" % (n + 1, arrived, expect))
        try:
            pg.wait_for_function("() => !document.body.classList.contains('transitioning')", timeout=4000)
        except Exception as ex:
            fails.append("scene %s transition did not finish: %s" % (n + 1, str(ex)[:100]))
        if not pg.locator("#dpad").is_visible():
            fails.append("D-pad still hidden after scene %s transition" % (n + 1))
    pg.evaluate("document.getElementById('auto').click()")
    pg.wait_for_function("() => window.__GAME__ && window.__GAME__.state().status === 'won'", timeout=180000)
    pg.wait_for_timeout(280)
    conf = pg.evaluate("() => (window.__STAGE3D__ && window.__STAGE3D__.confetti) || 0")
    print("scene 3 confetti3d", conf, flush=True)
    if conf < 40:
        fails.append("scene 3 win confetti count %s" % conf)
    title = pg.evaluate("() => window.__WIN_TITLE__ || ''")
    print("scene 3 win title", title, flush=True)
    if title != "YOU WIN!":
        fails.append("scene 3 win title %r" % (title,))
    pg.wait_for_function("() => document.body.innerText.includes('You did it')", timeout=20000)
    try:
        pg.wait_for_function("() => !!document.getElementById('winconfetti')", timeout=4000)
    except Exception as ex:
        fails.append("ending confetti canvas missing: " + str(ex)[:120])
    cele = pg.evaluate("() => ({n: window.__JUICE__ && window.__JUICE__.confetti, shapes: (window.__JUICE__ && window.__JUICE__.shapes) || []})")
    print("ending confetti", cele, flush=True)
    if (cele.get("n") or 0) < 40:
        fails.append("ending confetti too small: %s" % cele)
    if "star" not in cele.get("shapes", []) or "ribbon" not in cele.get("shapes", []):
        fails.append("ending confetti missing star or ribbon: %s" % cele)
    pg.wait_for_timeout(280)
    scan(pg, "ending", fails)
    check_results(pg, fails)
    pg.evaluate("() => { const h = document.querySelector('#ps h1'); if (h) h.scrollIntoView({ block: 'start' }); }")
    pg.wait_for_timeout(150)
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
          // Demo Play calls requestFullscreen. That maximizes the Chromium
          // window and the next set_viewport_size throws. Keep the call, no-op it.
          const fsNop = () => Promise.resolve();
          try { Element.prototype.requestFullscreen = fsNop; } catch (e) {}
          try { Document.prototype.exitFullscreen = fsNop; } catch (e) {}
        """)
        pg = ctx.new_page()
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        try:
            check_story(pg, fails)
            check_controls(pg, fails)
            check_create(pg, fails)
            check_judge(pg, fails)
            check_index(pg, fails)
            full_path(pg, fails)
            check_reduced(browser, fails)
            check_es(pg, fails)
            check_other_world(pg, fails)
            check_landscape(pg, fails)
            pg.goto(GALLERY, wait_until="domcontentloaded")
            pg.wait_for_timeout(200)
            fit = layout_overflow(pg)
            print("portrait gallery", fit, flush=True)
            if fit:
                fails.append("portrait gallery overflow: " + " | ".join(fit[:8]))
            pg.screenshot(path=str(EV / "verify_touch_gallery_portrait.png"))
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
