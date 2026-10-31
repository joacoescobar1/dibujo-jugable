#!/usr/bin/env python3
"""Touch path: gallery -> Play -> 3 scenes -> ending.

Fails on visible Spanish without ?lang=es (text plus alt, title, and aria-label), video:true,
a VERIFIED claim, or a Home/D-pad that does not work.
Pass 9: landscape 844x390 fit without scroll (HUD, D-pad, modals, story, results),
ending star count-up and finale, gallery hover/press and clearer titles.
Pass 12: fullscreen world, judge phone world fills the screen, rim/soft shadow/bloom,
particle trail, camera ease, parallax, optional challenge clock, local best time.
Pass 13: portrait 390x844 and landscape 844x390, English and Spanish, reduced motion.
Pass 18: D-pad / stick / swipe / keyboard holds clear on pointercancel, blur, pause, and transitions.
Player mode has no judge chrome. The canvas fills the viewport (no black band over 8%).
The story splash is reachable. The phone judge page is not an empty black void.
"""
import json, pathlib, re, sys
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
    r"estado|evidencia|ganó|perdió|perdiste|salida|trabado|ilumina|recorta|en vivo|"
    r"arranca|patitas|pancita|festej\w*|alegr\w*|cosquill\w*|ilusión|hacia|content[oa]s?|"
    r"el|la|los|las|hay|tiene|quiere|busca|puede|tocar|vuela|llega|llegar|entre)\b",
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
      document.body.querySelectorAll('[alt],[title],[aria-label],[placeholder]').forEach(el => {
        if (!shown(el)) return;
        ['alt', 'title', 'aria-label', 'placeholder'].forEach(a => {
          const s = (el.getAttribute(a) || '').replace(/\\s+/g, ' ').trim();
          if (s) out.push(s.slice(0, 240));
        });
      });
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
    for p in (GAME / "player_shell.js", GAME / "game.js", GAME / "beats.js", GAME / "stage3d.js", GAME / "gallery.html", GAME / "index.html", GAME / "story_splash.js"):
        t = p.read_text(errors="replace")
        if re.search(r"video\s*:\s*true", t):
            fails.append("video:true in " + p.name)
    shell = (GAME / "player_shell.js").read_text(errors="replace")
    if "const FB" in shell or "const GLUE" in shell or "const PHRASE" in shell:
        fails.append("word-level Spanish substitution is still in player_shell.js")
    for needle in ("visibilitychange", "pagehide", "lostpointercapture", "releaseHold", "__INPUT__", "__RELEASE_HOLD__"):
        if needle not in shell:
            fails.append("player_shell.js missing " + needle)
    game = (GAME / "game.js").read_text(errors="replace")
    for needle in ("__CLEAR_KEYS__", "__KEYS__", "keyup"):
        if needle not in game:
            fails.append("game.js missing " + needle)

def minigames_hidden(pg):
    return pg.evaluate("""() => {
      const shown = el => {
        if (!el) return false;
        const cs = getComputedStyle(el);
        if (cs.display === 'none' || cs.visibility === 'hidden' || Number(cs.opacity) === 0) return false;
        const r = el.getBoundingClientRect();
        return r.width >= 2 && r.height >= 2;
      };
      return { beats: shown(document.getElementById('beats')), gate: shown(document.getElementById('gate')), cards: [...document.querySelectorAll('.beat')].filter(shown).length };
    }""")

def pitch_card(pg):
    return pg.evaluate("""() => {
      const t = document.getElementById('pitch');
      if (!t) return null;
      const art = t.querySelector('.art'), line = t.querySelector('.line'), hint = t.querySelector('.hint');
      const r = t.getBoundingClientRect();
      const meta = window.__PITCH__ || {};
      const text = line ? line.textContent.trim() : '';
      const hit = (x, y) => {
        const el = document.elementFromPoint(x, y);
        return !!(el && (el.id === 'pitch' || (el.closest && el.closest('#pitch'))));
      };
      return {
        art: art ? art.textContent.trim() : '',
        line: text,
        hint: hint ? hint.textContent.trim() : '',
        ms: meta.ms || 0,
        beat: meta.beat || 0,
        total: meta.total || 0,
        closed: meta.closed || '',
        full: r.width >= innerWidth - 4 && r.height >= innerHeight - 4,
        corner: hit(8, 8),
        mid: hit(Math.round(innerWidth / 2), Math.round(innerHeight / 2))
      };
    }""")

def dismiss_pitch(pg):
    for _ in range(8):
        pitch = pg.locator("#pitch")
        if not (pitch.count() and pitch.is_visible()):
            return
        try:
            pitch.tap(force=True, timeout=2000)
        except Exception:
            pg.evaluate("""() => {
              const t = document.getElementById('pitch');
              if (!t) return;
              t.dispatchEvent(new PointerEvent('pointerdown', { bubbles: true, cancelable: true, clientX: 20, clientY: 20 }));
            }""")
        pg.wait_for_timeout(180)

def check_fullscreen(pg, fails, tag):
    info = pg.evaluate("""() => {
      const wrap = document.getElementById('wrap');
      const c3d = document.getElementById('c3d');
      const hud = document.getElementById('hud');
      const side = document.getElementById('side');
      const chips = document.getElementById('rchips');
      const vis = el => {
        if (!el) return false;
        const cs = getComputedStyle(el);
        if (cs.display === 'none' || cs.visibility === 'hidden' || Number(cs.opacity) === 0) return false;
        const r = el.getBoundingClientRect();
        return r.width >= 2 && r.height >= 2 && r.bottom > 0 && r.right > 0 && r.top < innerHeight && r.left < innerWidth;
      };
      const wr = wrap ? wrap.getBoundingClientRect() : {width:0,height:0,top:99,left:99};
      const cr = (c3d && vis(c3d)) ? c3d.getBoundingClientRect() : wr;
      return {
        vw: innerWidth, vh: innerHeight,
        w: Math.round(cr.width), h: Math.round(cr.height),
        t: Math.round(cr.top), l: Math.round(cr.left),
        lab: vis(hud) || vis(side) || vis(chips),
        play: document.body.classList.contains('play'),
        labClass: document.body.classList.contains('lab'),
        sam: ((document.body && document.body.innerText) || '').indexOf('SAM') >= 0 && vis(side)
      };
    }""")
    print("fullscreen", tag, info, flush=True)
    if not info or not info.get("play"):
        fails.append("%s player mode missing: %s" % (tag, info))
        return
    if info.get("lab") or info.get("labClass") or info.get("sam"):
        fails.append("%s judge chrome visible in player mode: %s" % (tag, info))
    chrome = pg.evaluate("""() => {
      const t = (document.body && document.body.innerText) || '';
      const needles = ['Judge tour', 'Watch the agent', 'Agent loop', 'original drawing', 'Modo juez', 'Loop del agente', 'SAM recorta', 'Vista jurado', 'Ver al agente'];
      return needles.filter(s => t.indexOf(s) >= 0);
    }""")
    if chrome:
        fails.append("%s judge chrome visible in player mode: %s" % (tag, chrome))
    gap_h = info["vh"] - info["h"]
    gap_w = info["vw"] - info["w"]
    if info["t"] > info["vh"] * 0.08 or info["l"] > info["vw"] * 0.08 or gap_h > info["vh"] * 0.08 or gap_w > info["vw"] * 0.08 or info["t"] > 4 or info["l"] > 4 or gap_w > 12 or gap_h > 12:
        fails.append("%s letterboxed play view: %s" % (tag, info))

def shot_bands(path):
    from PIL import Image
    im = Image.open(path).convert("RGB")
    w, h = im.size
    px = im.load()
    def dark(p):
        r, g, b = p
        return r < 28 and g < 28 and b < 36
    def rowf(y):
        c = n = 0
        for x in range(0, w, 2):
            n += 1
            if dark(px[x, y]):
                c += 1
        return c / float(n or 1)
    def colf(x):
        c = n = 0
        for y in range(0, h, 2):
            n += 1
            if dark(px[x, y]):
                c += 1
        return c / float(n or 1)
    def edge(span, frac, rev=False):
        n = 0
        seq = range(span - 1, -1, -1) if rev else range(span)
        for i in seq:
            if frac(i) >= 0.85:
                n += 1
            else:
                break
        return n / float(span or 1)
    longest = run = 0
    for y in range(h):
        if rowf(y) >= 0.85:
            run += 1
            if run > longest:
                longest = run
        else:
            run = 0
    y0 = int(h * 0.55)
    c = n = 0
    for y in range(y0, h, 2):
        for x in range(0, w, 2):
            n += 1
            if dark(px[x, y]):
                c += 1
    return {
        "top": round(edge(h, rowf), 3),
        "bottom": round(edge(h, rowf, True), 3),
        "left": round(edge(w, colf), 3),
        "right": round(edge(w, colf, True), 3),
        "longest": round(longest / float(h or 1), 3),
        "lower": round(c / float(n or 1), 3),
    }

def assert_play_bands(fails, path, tag, limit=0.08):
    info = shot_bands(path)
    print("bands", tag, info, flush=True)
    bad = [k for k in ("top", "bottom", "left", "right", "longest") if info.get(k, 0) > limit]
    if bad:
        fails.append("%s letterbox >8%% black bands: %s" % (tag, info))

def assert_judge_filled(fails, path, tag):
    info = shot_bands(path)
    print("judge bands", tag, info, flush=True)
    if info.get("lower", 1) > 0.7:
        fails.append("%s judge page is an empty black void: %s" % (tag, info))

def check_pitch(pg, fails):
    pg.goto(GALLERY, wait_until="domcontentloaded")
    pg.evaluate("() => { try { sessionStorage.removeItem('dj_pitch_v1'); } catch (e) {} }")
    pg.reload(wait_until="domcontentloaded")
    try:
        pg.wait_for_selector("#pitch", timeout=8000)
    except Exception as ex:
        fails.append("gallery story splash missing: " + str(ex)[:140])
        return
    want = [
        ("✏️", "kid draws", "paper"),
        ("✨", "drawing wakes", "up"),
        ("🪄", "Creativity plus play", "Meta models"),
        ("🎮", "your turn", "Play a world"),
    ]
    for n, (art, a, b) in enumerate(want, 1):
        card = pitch_card(pg)
        print("pitch", n, card, flush=True)
        if not card or card.get("beat") != n or card.get("total") != 4 or card.get("ms") != 5000:
            fails.append("story beat %s shape: %s" % (n, card))
        elif not card.get("full") or not card.get("corner") or not card.get("mid"):
            fails.append("story beat %s is not fullscreen: %s" % (n, card))
        elif art not in (card.get("art") or "") or a.lower() not in (card.get("line") or "").lower() or b.lower() not in (card.get("line") or "").lower():
            fails.append("story beat %s copy: %s" % (n, card))
        elif "Tap to continue" not in (card.get("hint") or ""):
            fails.append("story beat %s hint: %s" % (n, card))
        line = card.get("line") or ""
        if ES.search(line) or VER.search(line):
            fails.append("story beat %s leak: %s" % (n, line))
        if "Grok" in line or "Persona" in line or "VERIFIED" in line:
            fails.append("story beat %s pitch leak: %s" % (n, line))
        pg.screenshot(path=str(EV / ("verify_touch_pitch%s.png" % n)))
        if n == 1:
            try:
                pg.wait_for_function("() => window.__PITCH__ && window.__PITCH__.beat === 2", timeout=7000)
            except Exception as ex:
                fails.append("story beat 1 did not auto-advance: " + str(ex)[:140])
            else:
                dt = pg.evaluate("() => Date.now() - (window.__PITCH__ && window.__PITCH__.at || 0)")
                print("pitch auto", dt, flush=True)
            continue
        tap_node(pg, "#pitch")
        pg.wait_for_timeout(220)
    pg.wait_for_timeout(200)
    if pg.locator("#pitch").count() and pg.locator("#pitch").is_visible():
        fails.append("story splash stayed up after the last tap")
        dismiss_pitch(pg)
    scan(pg, "gallery-after-pitch", fails)
    pg.goto(INDEX + "?mute=1", wait_until="domcontentloaded")
    pg.evaluate("() => { try { sessionStorage.removeItem('dj_pitch_v1'); } catch (e) {} }")
    pg.reload(wait_until="domcontentloaded")
    try:
        pg.wait_for_selector("#pitch", timeout=8000)
    except Exception as ex:
        fails.append("index story splash missing: " + str(ex)[:140])
    else:
        card = pitch_card(pg)
        print("pitch index", card, flush=True)
        if not card or card.get("beat") != 1 or not card.get("full"):
            fails.append("index story splash: %s" % card)
        pg.screenshot(path=str(EV / "verify_touch_pitch_index.png"))
        dismiss_pitch(pg)
    pg.goto(GALLERY + "?lang=es", wait_until="domcontentloaded")
    pg.evaluate("() => { try { sessionStorage.removeItem('dj_pitch_v1'); } catch (e) {} }")
    pg.reload(wait_until="domcontentloaded")
    try:
        pg.wait_for_selector("#pitch", timeout=8000)
    except Exception as ex:
        fails.append("Spanish story splash missing: " + str(ex)[:140])
    else:
        card = pitch_card(pg)
        print("pitch es", card, flush=True)
        line = (card or {}).get("line") or ""
        if not ES.search(line):
            fails.append("Spanish story splash stayed in English: " + line)
        if VER.search(line):
            fails.append("Spanish story splash claims VERIFIED")
        pg.screenshot(path=str(EV / "verify_touch_pitch_es.png"))
        dismiss_pitch(pg)
    pg.goto(GALLERY, wait_until="domcontentloaded")
    pg.evaluate("() => { try { sessionStorage.setItem('dj_pitch_v1', '1'); } catch (e) {} }")

def dismiss(pg):
    dismiss_pitch(pg)
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
    for _ in range(40):
        tale = pg.locator("#tale")
        if tale.count() and tale.is_visible():
            return True
        note = pg.locator("#demoNote")
        if note.count() and note.is_visible():
            tap_node(pg, "#demoNote button")
            pg.wait_for_timeout(200)
            continue
        onb = pg.locator("#onb")
        if onb.count() and onb.is_visible():
            tap_node(pg, "#onb")
            pg.wait_for_timeout(200)
            continue
        pg.wait_for_timeout(200)
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

def check_gallery_polish(pg, fails, min_title=20):
    if not safe_area_css(pg):
        fails.append("gallery CSS missing safe-area insets")
    rows = boxes_under(pg, "a.btn, p.note a")
    print("gallery targets", rows, flush=True)
    require_56(fails, rows, "gallery")
    css = pg.evaluate("() => [...document.querySelectorAll('style')].map(s => s.textContent).join('\\n')")
    if ".c:hover" not in css or ".c.pressed" not in css or "transform:none" not in css:
        fails.append("gallery CSS missing hover, press, or reduced-motion feedback")
    pressed = pg.evaluate("""() => {
      const card = document.querySelector('.c');
      if (!card) return null;
      const r = card.getBoundingClientRect();
      const ev = (type) => card.dispatchEvent(new PointerEvent(type, { bubbles: true, cancelable: true, clientX: r.left + 12, clientY: r.top + 12 }));
      ev('pointerdown');
      const down = card.classList.contains('pressed');
      ev('pointerup');
      return { down: down, up: card.classList.contains('pressed') };
    }""")
    print("gallery press", pressed, flush=True)
    if not pressed or not pressed.get("down") or pressed.get("up"):
        fails.append("gallery card press feedback: %s" % pressed)
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
    heads = pg.evaluate("""() => [...document.querySelectorAll('.c h2')].map(h => ({
      t: (h.textContent || '').replace(/\\s+/g, ' ').trim(),
      px: parseFloat(getComputedStyle(h).fontSize) || 0
    }))""")
    print("gallery titles", heads[:4], "min", min_title, flush=True)
    if len(heads) < 21:
        fails.append("gallery titles missing: %s" % len(heads))
    for h in heads:
        if not h["t"] or len(h["t"]) > 42 or ES.search(h["t"]):
            fails.append("gallery title unclear: %s" % h)
        if h["px"] + 0.1 < min_title:
            fails.append("gallery title smaller than %spx: %s" % (min_title, h))

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
    pg.evaluate("() => { clearTimeout(window.__TALE_TIMER__); }")
    pg.screenshot(path=str(EV / "verify_touch_story.png"), timeout=30000)
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
        pg.wait_for_selector("#tale", timeout=15000)
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
    pg.evaluate("() => { clearTimeout(window.__TALE_TIMER__); }")
    pg.screenshot(path=str(EV / ("verify_touch_story%s.png" % n)), timeout=30000)

def check_es(pg, fails):
    pg.goto(PLAY + "?lang=es&mute=1", wait_until="domcontentloaded")
    if not reach_tale(pg):
        state = pg.evaluate("""() => ({
          href: location.href.split('/').pop(),
          tale: !!document.getElementById('tale'),
          demo: !!document.getElementById('demoNote'),
          onb: !!document.getElementById('onb'),
          closed: window.__TALE__ && window.__TALE__.closed,
          level: window.__BUNDLE__ && window.__BUNDLE__.play && window.__BUNDLE__.play.level
        })""")
        print("es miss", state, flush=True)
        try:
            pg.screenshot(path=str(EV / "verify_touch_pass13_es_miss.png"))
        except Exception:
            pass
        fails.append("Spanish story card did not appear: %s" % state)
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
    pg.wait_for_timeout(300)
    try:
        pg.wait_for_function("() => window.__STAGE3D__ && window.__STAGE3D__.ok", timeout=20000)
    except Exception as ex:
        fails.append("Spanish play stage did not fill: " + str(ex)[:120])
    else:
        check_fullscreen(pg, fails, "es-play")
        pg.screenshot(path=str(EV / "verify_touch_pass13_es.png"))
        assert_play_bands(fails, EV / "verify_touch_pass13_es.png", "es-play")

def pos(pg):
    return pg.evaluate("() => { const s = window.__GAME__.state().player; return [s.x, s.y, s && window.__GAME__.state().status]; }")

def input_snap(pg):
    return pg.evaluate("""() => {
      const S = window.__GAME__.state();
      const inp = window.__INPUT__ || {};
      const st = window.__STICK__ || { x: 0, y: 0 };
      return {
        pos: [S.player.x, S.player.y],
        status: S.status,
        steps: S.steps,
        ticks: S.ticks,
        pad: inp.pad || 0,
        gap: inp.gap || 0,
        joy: inp.joy || 0,
        rec: inp.rec || 0,
        pulse: inp.pulse || 0,
        keys: (window.__KEYS__ || []).slice(),
        stick: { x: st.x || 0, y: st.y || 0 }
      };
    }""")

def fire_pad(pg, sel, typ, pid=91):
    return pg.evaluate("""({sel, typ, pid}) => {
      const btn = document.querySelector(sel);
      if (!btn) return { missing: true };
      const r = btn.getBoundingClientRect();
      const x = r.left + r.width / 2, y = r.top + r.height / 2;
      btn.dispatchEvent(new PointerEvent(typ, {
        bubbles: true, cancelable: true, composed: true,
        pointerId: pid, pointerType: 'touch',
        clientX: x, clientY: y, button: 0,
        buttons: typ === 'pointerdown' ? 1 : 0
      }));
      return window.__INPUT__ || {};
    }""", {"sel": sel, "typ": typ, "pid": pid})

def holds_live(snap):
    return bool(snap and (snap.get("pad") or snap.get("pulse") or snap.get("gap") or snap.get("joy") or snap.get("rec")))

def check_stuck_input(pg, fails):
    """pointerdown on the D-pad then cancel/blur/pause must not keep stepping."""
    if not pg.locator("#dpad").count() or not pg.locator("#dpad").is_visible():
        fails.append("stuck-input: D-pad missing")
        return
    pg.evaluate("() => { if (window.__GAME__) window.__GAME__.reset(); if (window.__RELEASE_HOLD__) window.__RELEASE_HOLD__(); }")
    pg.wait_for_timeout(80)
    moved_sel = None
    after_down = None
    for sel in ("#dpad .r", "#dpad .l", "#dpad .u", "#dpad .d"):
        pg.evaluate("() => { if (window.__GAME__) window.__GAME__.reset(); if (window.__RELEASE_HOLD__) window.__RELEASE_HOLD__(); }")
        pg.wait_for_timeout(40)
        origin = input_snap(pg)
        fire_pad(pg, sel, "pointerdown", 91)
        pg.wait_for_timeout(40)
        after_down = input_snap(pg)
        if after_down["pos"] != origin["pos"] or after_down["ticks"] != origin["ticks"]:
            moved_sel = sel
            break
        fire_pad(pg, sel, "pointercancel", 91)
        pg.evaluate("() => window.__RELEASE_HOLD__ && window.__RELEASE_HOLD__()")
    print("stuck down", moved_sel, after_down, flush=True)
    if not moved_sel or not after_down:
        fails.append("stuck-input: pointerdown on D-pad did not step")
        pg.evaluate("() => window.__RELEASE_HOLD__ && window.__RELEASE_HOLD__()")
        return
    fire_pad(pg, moved_sel, "pointercancel", 91)
    cleared = input_snap(pg)
    pg.wait_for_timeout(420)
    after_cancel = input_snap(pg)
    print("stuck cancel", after_down, cleared, after_cancel, flush=True)
    if holds_live(cleared) or holds_live(after_cancel):
        fails.append("stuck-input: hold still running after pointercancel: %s" % after_cancel)
    if after_cancel["ticks"] != cleared["ticks"]:
        fails.append("stuck-input: player kept moving after pointercancel: %s -> %s" % (cleared, after_cancel))

    pg.evaluate("() => { if (window.__GAME__) window.__GAME__.reset(); if (window.__RELEASE_HOLD__) window.__RELEASE_HOLD__(); }")
    pg.wait_for_timeout(50)
    fire_pad(pg, moved_sel, "pointerdown", 92)
    pg.wait_for_timeout(40)
    pg.evaluate("() => { window.dispatchEvent(new Event('blur')); }")
    mid = input_snap(pg)
    pg.wait_for_timeout(420)
    after_blur = input_snap(pg)
    print("stuck blur", mid, after_blur, flush=True)
    if holds_live(mid) or holds_live(after_blur):
        fails.append("stuck-input: hold still running after blur: %s" % after_blur)
    if after_blur["ticks"] != mid["ticks"]:
        fails.append("stuck-input: player kept moving after blur: %s -> %s" % (mid, after_blur))

    pg.evaluate("() => { if (window.__GAME__) window.__GAME__.reset(); if (window.__RELEASE_HOLD__) window.__RELEASE_HOLD__(); }")
    pg.wait_for_timeout(50)
    fire_pad(pg, moved_sel, "pointerdown", 93)
    pg.wait_for_timeout(40)
    pg.locator("#pz").tap()
    pg.wait_for_timeout(80)
    mid = input_snap(pg)
    pg.wait_for_timeout(420)
    after_pause = input_snap(pg)
    print("stuck pause", mid, after_pause, flush=True)
    if holds_live(mid) or holds_live(after_pause):
        fails.append("stuck-input: hold still running while paused: %s" % after_pause)
    if after_pause["ticks"] != mid["ticks"]:
        fails.append("stuck-input: player kept moving after pause: %s -> %s" % (mid, after_pause))
    if pg.locator("#pzo").count() and pg.locator("#pzo").is_visible():
        pg.locator("#pzo button").first.tap()
        pg.wait_for_timeout(150)
    else:
        fails.append("stuck-input: pause overlay did not open")

    pg.evaluate("() => { if (window.__GAME__) window.__GAME__.reset(); if (window.__CLEAR_KEYS__) window.__CLEAR_KEYS__(); }")
    pg.wait_for_timeout(50)
    pg.keyboard.down("ArrowRight")
    pg.wait_for_timeout(30)
    keys_down = pg.evaluate("() => (window.__KEYS__ || []).slice()")
    pg.evaluate("() => { window.dispatchEvent(new Event('blur')); }")
    keys_blur = pg.evaluate("() => (window.__KEYS__ || []).slice()")
    print("stuck keys", keys_down, keys_blur, flush=True)
    if "ArrowRight" not in keys_down:
        fails.append("stuck-input: keydown did not track ArrowRight: %s" % keys_down)
    if keys_blur:
        fails.append("stuck-input: keys still held after blur: %s" % keys_blur)
    try:
        pg.keyboard.up("ArrowRight")
    except Exception:
        pass
    pg.keyboard.down("ArrowLeft")
    pg.wait_for_timeout(20)
    pg.keyboard.press(" ")
    keys_space = pg.evaluate("() => (window.__KEYS__ || []).slice()")
    if keys_space:
        fails.append("stuck-input: Space left keys held: %s" % keys_space)
    try:
        pg.keyboard.up("ArrowLeft")
    except Exception:
        pass
    for k in ("ArrowRight", "ArrowLeft", "ArrowUp", "ArrowDown", " ", "w", "a", "s", "d", "W", "A", "S", "D"):
        try:
            pg.keyboard.up(k)
        except Exception:
            pass

    stick = pg.evaluate("""() => {
      const k = document.querySelector('#stick .knob');
      window.__STICK__ = { x: 0.8, y: 0.2 };
      if (k) k.style.transform = 'translate3d(20px,8px,0)';
      if (window.__RELEASE_HOLD__) window.__RELEASE_HOLD__();
      const cs = k ? getComputedStyle(k).transform : '';
      return { transform: k ? k.style.transform : '', computed: cs, stick: window.__STICK__, inp: window.__INPUT__ };
    }""")
    print("stuck stick", stick, flush=True)
    st = (stick or {}).get("stick") or {}
    if abs(st.get("x") or 0) > 0.01 or abs(st.get("y") or 0) > 0.01:
        fails.append("stuck-input: stick did not recenter: %s" % stick)
    tr = (stick or {}).get("transform") or ""
    if tr and tr not in ("none", "translate3d(0,0,0)", "translate3d(0px, 0px, 0px)", "matrix(1, 0, 0, 1, 0, 0)"):
        if "20px" in tr or "8px" in tr:
            fails.append("stuck-input: stick knob did not snap back: %s" % stick)
    pg.screenshot(path=str(EV / "verify_touch_stuck_input.png"))
    pg.evaluate("() => { if (window.__GAME__) window.__GAME__.reset(); if (window.__RELEASE_HOLD__) window.__RELEASE_HOLD__(); }")
    if pg.locator("#pzo").count() and pg.locator("#pzo").is_visible():
        pg.locator("#pzo button").first.tap()
        pg.wait_for_timeout(120)

def check_controls(pg, fails):
    pg.goto(PLAY + "?mute=1", wait_until="domcontentloaded")
    pg.wait_for_function("() => window.__GAME__ && window.__GAME__.ready", timeout=30000)
    pg.wait_for_timeout(400)
    scan(pg, "play-modal", fails)
    dismiss(pg)
    pg.wait_for_timeout(300)
    scan(pg, "play-hud", fails)
    check_fullscreen(pg, fails, "play-hud")
    pg.screenshot(path=str(EV / "verify_touch_fullscreen.png"))
    assert_play_bands(fails, EV / "verify_touch_fullscreen.png", "play-hud")
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
    check_stuck_input(pg, fails)
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
    hidden = minigames_hidden(pg)
    print("judge minigames", hidden, flush=True)
    if hidden.get("beats") or hidden.get("gate") or hidden.get("cards"):
        fails.append("judge mini-games still visible: %s" % hidden)
    labels = pg.evaluate("() => window.__LABELS__ || []")
    bad = [s for s in labels if ES.search(s or "")]
    print("judge labels", labels, flush=True)
    if bad:
        fails.append("judge name labels still Spanish: " + " | ".join(bad[:8]))
    pg.screenshot(path=str(EV / "verify_touch_judge.png"))
    box = pg.evaluate("""() => {
      const w = document.getElementById('wrap');
      const r = w ? w.getBoundingClientRect() : { height: 0, width: 0, top: 0 };
      return { h: Math.round(r.height), w: Math.round(r.width), top: Math.round(r.top), vh: innerHeight, vw: innerWidth };
    }""")
    print("judge phone wrap", box, flush=True)
    if not box or box["h"] < max(280, box["vh"] * 0.42):
        fails.append("judge phone world too short: %s" % box)
    else:
        try:
            pg.wait_for_function("() => [...document.querySelectorAll('#draw img')].some(i => i.naturalWidth >= 8)", timeout=8000)
        except Exception as ex:
            fails.append("judge drawing is blank: " + str(ex)[:120])
        else:
            draw = pg.evaluate("() => [...document.querySelectorAll('#draw img')].map(i => i.id + ':' + i.naturalWidth)")
            print("judge drawing", draw, flush=True)
    pg.screenshot(path=str(EV / "verify_touch_judge_phone.png"))
    assert_judge_filled(fails, EV / "verify_touch_judge_phone.png", "judge-portrait")
    pg.set_viewport_size({"width": 844, "height": 390})
    pg.goto(PLAY + "?judge=1&mute=1&norender=1", wait_until="domcontentloaded")
    try:
        pg.wait_for_function("() => window.__STAGE3D__ && (window.__STAGE3D__.ok || window.__STAGE3D__.error)", timeout=20000)
    except Exception as ex:
        fails.append("landscape judge stage did not boot: " + str(ex)[:120])
    pg.wait_for_timeout(400)
    land_box = pg.evaluate("""() => {
      const w = document.getElementById('wrap');
      const r = w ? w.getBoundingClientRect() : { height: 0, width: 0 };
      const lab = document.body.classList.contains('lab') || document.documentElement.classList.contains('lab');
      return { h: Math.round(r.height), w: Math.round(r.width), vh: innerHeight, vw: innerWidth, lab: lab };
    }""")
    print("judge land wrap", land_box, flush=True)
    land_hidden = minigames_hidden(pg)
    print("judge land minigames", land_hidden, flush=True)
    if land_hidden.get("beats") or land_hidden.get("gate") or land_hidden.get("cards"):
        fails.append("landscape judge mini-games still visible: %s" % land_hidden)
    if not land_box or not land_box.get("lab") or land_box["h"] < land_box["vh"] * 0.5:
        fails.append("landscape judge world does not fill the phone: %s" % land_box)
    pg.screenshot(path=str(EV / "verify_touch_pass13_judge_land.png"))
    assert_judge_filled(fails, EV / "verify_touch_pass13_judge_land.png", "judge-landscape")
    pg.set_viewport_size({"width": 390, "height": 844})

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
            pg.wait_for_function("() => window.__STAGE3D__ && window.__STAGE3D__.dust > 0", timeout=12000)
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
        look = pg.evaluate("""() => {
          const s = window.__STAGE3D__ || {};
          const c = document.getElementById('c3d');
          const r = c ? c.getBoundingClientRect() : { width: 0, height: 0, top: 9, left: 9 };
          return { trail: s.trail || 0, parallax: s.parallax, camEase: s.camEase, rim: s.rim, shadow: s.shadow, bloom: s.bloom || 0, cw: Math.round(r.width), ch: Math.round(r.height), ct: Math.round(r.top), cl: Math.round(r.left), vw: innerWidth, vh: innerHeight };
        }""")
        print("pass12", look, flush=True)
        if not look or look.get("trail", 0) < 1:
            fails.append("move did not leave a particle trail: %s" % look)
        if not look or look.get("parallax") != 1 or look.get("camEase") != 1 or look.get("rim") != 1 or look.get("shadow") != "pcfsoft":
            fails.append("stage look flags: %s" % look)
        if not look or (look.get("bloom") or 0) < 0.2:
            fails.append("bloom glow is off: %s" % look)
        if look and (look["ct"] > 4 or look["cl"] > 4 or look["cw"] < look["vw"] - 12 or look["ch"] < look["vh"] - 12):
            fails.append("play canvas is letterboxed: %s" % look)
        ch = pg.locator("#h3ch").inner_text().strip() if pg.locator("#h3ch").count() else ""
        print("challenge", ch, flush=True)
        if not ch.startswith("Challenge") or ES.search(ch):
            fails.append("optional challenge chip: %r" % ch)
        pg.screenshot(path=str(EV / "verify_touch_pass12.png"))
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
        pg.evaluate("""() => {
          window.__HOLD_COMBO__ = true;
          try { clearTimeout(window.__COMBO_TIMER__); } catch (e) {}
          const c = document.getElementById('combo');
          if (!c) return;
          c.classList.add('on');
          c.style.opacity = '1';
          c.style.animation = 'none';
        }""")
        pg.screenshot(path=str(EV / "verify_touch_combo.png"), timeout=30000, animations="disabled")
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
            pg.wait_for_timeout(280)
            pg.screenshot(path=str(EV / "verify_touch_wipe.png"), timeout=15000, animations="disabled")
        except Exception as ex:
            fails.append("wipe screenshot failed: " + str(ex)[:160])


def check_reduced(p, fails):
    browser = p.chromium.launch(args=["--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"])
    ctx = browser.new_context(
        viewport={"width": 390, "height": 844},
        has_touch=True,
        is_mobile=True,
        device_scale_factor=2,
        locale="en-US",
        reduced_motion="reduce",
        user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
    )
    ctx.add_init_script("""
      const fsNop = () => Promise.resolve();
      try { Element.prototype.requestFullscreen = fsNop; } catch (e) {}
      try { Document.prototype.exitFullscreen = fsNop; } catch (e) {}
    """)
    pg = ctx.new_page()
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    try:
        pg.goto(GALLERY, wait_until="domcontentloaded")
        pg.evaluate("() => { try { sessionStorage.removeItem('dj_pitch_v1'); } catch (e) {} }")
        pg.reload(wait_until="domcontentloaded")
        try:
            pg.wait_for_selector("#pitch", timeout=8000)
            anim = pg.evaluate("() => { const n = document.querySelector('#pitch .bg') || document.querySelector('#pitch .art'); return n ? getComputedStyle(n).animationName : ''; }")
            print("reduced pitch anim", anim, flush=True)
            if anim and anim != "none":
                fails.append("reduced-motion story splash still moves: " + str(anim))
            pg.screenshot(path=str(EV / "verify_touch_pitch_reduced.png"))
            dismiss_pitch(pg)
        except Exception as ex:
            fails.append("reduced-motion story splash missing: " + str(ex)[:140])
        pg.goto(PLAY + "?mute=1", wait_until="domcontentloaded", timeout=60000)
        pg.wait_for_function("() => window.__GAME__ && window.__GAME__.ready && window.__STAGE3D__ && (window.__STAGE3D__.ok || window.__STAGE3D__.error)", timeout=30000)
        if pg.evaluate("() => window.__STAGE3D__.error || null"):
            fails.append("reduced-motion stage failed: " + str(pg.evaluate("() => window.__STAGE3D__.error")))
        if reach_tale(pg):
            pg.evaluate("() => { clearTimeout(window.__TALE_TIMER__); }")
            anim = pg.evaluate("() => { const n = document.querySelector('#tale .art'); return n ? getComputedStyle(n).animationName : 'missing'; }")
            print("reduced tale anim", anim, flush=True)
            if anim == "missing" or (anim and anim != "none"):
                fails.append("reduced-motion story art still moves: " + str(anim))
            pg.evaluate("() => { clearTimeout(window.__TALE_TIMER__); }")
            pg.screenshot(path=str(EV / "verify_touch_story_reduced.png"), timeout=30000)
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
        check_fullscreen(pg, fails, "reduced-play")
        pg.screenshot(path=str(EV / "verify_touch_pass13_reduced.png"))
        assert_play_bands(fails, EV / "verify_touch_pass13_reduced.png", "reduced-play")
        origin = pos(pg)
        for sel in ("#dpad .r", "#dpad .d", "#dpad .l", "#dpad .u"):
            if not pg.locator("#dpad").is_visible():
                break
            pg.locator(sel).tap()
            pg.wait_for_timeout(90)
            if pos(pg)[:2] != origin[:2]:
                break
        pg.wait_for_function("() => window.__STAGE3D__.dust > 0", timeout=12000)
        info = pg.evaluate("() => ({dust: window.__STAGE3D__.dust, travel: window.__STAGE3D__.dustTravel})")
        print("reduced dust", info, flush=True)
        if info["travel"] != 0:
            fails.append("reduced-motion dust still travels: %s" % info)
        still = pg.evaluate("() => ({trail: window.__STAGE3D__.trail || 0, parallax: window.__STAGE3D__.parallax, camEase: window.__STAGE3D__.camEase})")
        print("reduced look", still, flush=True)
        if still.get("trail") or still.get("parallax") or still.get("camEase"):
            fails.append("reduced-motion still trails, parallax, or eases the camera: %s" % still)
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
        fin = pg.evaluate("() => (window.__JUICE__ && window.__JUICE__.previewFinale) ? window.__JUICE__.previewFinale(3) : null")
        print("reduced finale", fin, flush=True)
        if not fin or not fin.get("done") or not fin.get("reduced") or fin.get("shown") != 3 or fin.get("sceneShown") != 3 or fin.get("ticked"):
            fails.append("reduced-motion finale still animates: %s" % fin)
        scan(pg, "reduced", fails)
    except Exception as ex:
        try: pg.screenshot(path=str(EV / "verify_touch_reduced_FAIL.png"))
        except Exception: pass
        fails.append("reduced-motion EXCEPTION " + str(ex)[:300])
    if errs:
        fails.append("reduced pageerror " + " | ".join(errs[:4]))
    ctx.close()
    browser.close()


def fit_no_scroll(pg, sel):
    return pg.evaluate("""(sel) => {
      const el = document.querySelector(sel);
      if (!el) return { missing: true, sel: sel };
      const kids = [];
      const vw = innerWidth, vh = innerHeight;
      for (const ch of el.querySelectorAll('*')) {
        const cs = getComputedStyle(ch);
        if (cs.display === 'none' || cs.visibility === 'hidden') continue;
        const b = ch.getBoundingClientRect();
        if (b.width < 2 || b.height < 2) continue;
        if (b.top < -1 || b.left < -1 || b.bottom > vh + 1 || b.right > vw + 1)
          kids.push((ch.id || ch.className || ch.tagName) + ' ' + Math.round(b.top) + '..' + Math.round(b.bottom));
      }
      return { sel: sel, scroll: el.scrollHeight, client: el.clientHeight, over: el.scrollHeight > el.clientHeight + 2, kids: kids.slice(0, 8) };
    }""", sel)

def assert_fit(pg, fails, sel, tag):
    info = fit_no_scroll(pg, sel)
    print(tag, info, flush=True)
    if not info or info.get("missing") or info.get("over") or info.get("kids"):
        fails.append(tag + " does not fit without scroll: %s" % info)
    return info

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
        pg.wait_for_function("() => window.__FINALE__ && window.__FINALE__.done === true", timeout=8000)
    except Exception as ex:
        fails.append("results screen missing: " + str(ex)[:120])
        return
    fin = pg.evaluate("() => window.__FINALE__")
    print("finale", fin, flush=True)
    if not fin or fin.get("sceneStars") != 3 or fin.get("sceneShown") != 3 or not fin.get("ticked") or fin.get("reduced") or fin.get("shown") != fin.get("stars"):
        fails.append("finale count-up: %s" % fin)
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
    if not re.search(r"Best \d+:\d\d", text) or not data.get("best"):
        fails.append("results best time: %s" % res)
    best = pg.evaluate("() => window.__BEST__ || null")
    print("best", best, flush=True)
    if not best or best.get("time") != data.get("best"):
        fails.append("local best record: %s vs %s" % (best, data))
    if ES.search(text) or VER.search(text):
        fails.append("results leak: " + text)
    if res and (res["left"] < -1 or res["right"] > res["vw"] + 1 or res["top"] < -1 or res["bottom"] > res["vh"] + 1):
        fails.append("results overflow the ending screen: %s" % res)
    pg.screenshot(path=str(EV / "verify_touch_results.png"))

def check_pipo_skip(pg, fails):
    """Pipo's world: a click and Enter dismiss the story card. Mini-games stay hidden."""
    pipo = (GAME / "w_perrofuego.html").resolve().as_uri()
    pg.goto(pipo + "?mute=1", wait_until="domcontentloaded")
    if not reach_tale(pg):
        pg.goto(pipo + "?mute=1", wait_until="domcontentloaded")
        if not reach_tale(pg):
            fails.append("Pipo story did not open")
            return
    pg.evaluate("() => { clearTimeout(window.__TALE_TIMER__); }")
    pg.evaluate("""() => {
      const t = document.getElementById('tale');
      if (!t) return;
      const r = t.getBoundingClientRect();
      const card = t.querySelector('.card') || t;
      const cr = card.getBoundingClientRect();
      card.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true, clientX: cr.left + cr.width / 2, clientY: cr.top + cr.height / 2 }));
    }""")
    pg.wait_for_timeout(180)
    closed = pg.evaluate("() => ({ closed: window.__TALE__ && window.__TALE__.closed, up: !!document.getElementById('tale') })")
    print("pipo click skip", closed, flush=True)
    if not closed or closed.get("closed") != "tap" or closed.get("up"):
        fails.append("click did not skip the Pipo story: %s" % closed)
    pg.goto(pipo + "?mute=1", wait_until="domcontentloaded")
    if not reach_tale(pg):
        fails.append("Pipo story did not open for the keyboard skip")
        return
    pg.evaluate("() => { clearTimeout(window.__TALE_TIMER__); }")
    pg.keyboard.press("Enter")
    pg.wait_for_timeout(180)
    closed = pg.evaluate("() => ({ closed: window.__TALE__ && window.__TALE__.closed, up: !!document.getElementById('tale') })")
    print("pipo key skip", closed, flush=True)
    if not closed or closed.get("closed") != "key" or closed.get("up"):
        fails.append("Enter did not skip the Pipo story: %s" % closed)
    pg.keyboard.press(" ")
    hidden = minigames_hidden(pg)
    print("pipo minigames", hidden, flush=True)
    if hidden.get("beats") or hidden.get("gate") or hidden.get("cards"):
        fails.append("mini-games visible on the Pipo player path: %s" % hidden)
    scan(pg, "pipo-en", fails)
    pg.screenshot(path=str(EV / "verify_touch_pipo_en.png"))

def check_other_world(pg, fails):
    other = (GAME / "w_gato.html").resolve().as_uri()
    pg.goto(other + "?mute=1", wait_until="domcontentloaded")
    try:
        pg.wait_for_selector("#demoNote", timeout=15000)
        scan(pg, "gato-demo", fails)
        pg.locator("#demoNote button").tap()
        pg.wait_for_timeout(250)
        if pg.locator("#onb").count() and pg.locator("#onb").is_visible():
            tap_node(pg, "#onb")
        pg.wait_for_selector("#tale", timeout=4000)
        scan(pg, "gato-story", fails)
        skip_tale(pg)
    except Exception as ex:
        fails.append("other world story scan failed: " + str(ex)[:160])
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


def reach_pitch(pg, fails, tag, es=False):
    pg.goto(GALLERY + ("?lang=es" if es else ""), wait_until="domcontentloaded")
    pg.evaluate("() => { try { sessionStorage.removeItem('dj_pitch_v1'); } catch (e) {} }")
    pg.reload(wait_until="domcontentloaded")
    try:
        pg.wait_for_selector("#pitch", timeout=8000)
    except Exception as ex:
        fails.append("%s story splash missing: %s" % (tag, str(ex)[:120]))
        return
    card = pitch_card(pg)
    print("pitch", tag, card, flush=True)
    line = (card or {}).get("line") or ""
    if not card or not card.get("full") or card.get("beat") != 1 or not card.get("corner") or not card.get("mid"):
        fails.append("%s story splash not reachable: %s" % (tag, card))
    elif es and not ES.search(line):
        fails.append("%s story splash stayed in English: %s" % (tag, line))
    elif not es and (ES.search(line) or "kid draws" not in line.lower()):
        fails.append("%s story splash copy: %s" % (tag, line))
    if VER.search(line):
        fails.append("%s story splash claims VERIFIED" % tag)
    pg.screenshot(path=str(EV / ("verify_touch_pass13_pitch_%s.png" % tag)))
    dismiss_pitch(pg)

def check_landscape(pg, fails):
    restore_window(pg)
    pg.set_viewport_size({"width": 844, "height": 390})
    reach_pitch(pg, fails, "land", es=False)
    pg.goto(GALLERY, wait_until="domcontentloaded")
    pg.wait_for_timeout(250)
    dismiss_pitch(pg)
    bad = layout_overflow(pg)
    print("land gallery", bad, flush=True)
    if bad:
        fails.append("landscape gallery overflow: " + " | ".join(bad[:8]))
    scan(pg, "land-gallery", fails)
    check_gallery_polish(pg, fails, 18)
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
    pg.evaluate("() => { try { localStorage.removeItem('dj_onboard_v2'); localStorage.removeItem('dj_onboard_v1'); } catch (e) {} }")
    pg.reload(wait_until="domcontentloaded")
    pg.wait_for_function("() => window.__GAME__ && window.__GAME__.ready", timeout=30000)
    pg.wait_for_selector("#demoNote", timeout=15000)
    assert_fit(pg, fails, "#demoNote", "land demo")
    pg.locator("#demoNote button").tap()
    pg.wait_for_timeout(250)
    onb = pg.locator("#onb")
    if onb.count() == 0 or not onb.is_visible():
        fails.append("landscape onboarding hint did not show")
    else:
        assert_fit(pg, fails, "#onb", "land onboard")
        tap_node(pg, "#onb")
    pg.wait_for_selector("#tale", timeout=4000)
    assert_fit(pg, fails, "#tale", "land story")
    card = story_card(pg)
    print("land story", card, flush=True)
    if not card or not card.get("full") or not card.get("corner") or not card.get("mid"):
        fails.append("landscape story card is not full-screen: %s" % card)
    pg.screenshot(path=str(EV / "verify_touch_story_land.png"))
    skip_tale(pg)
    pg.wait_for_timeout(200)
    check_fullscreen(pg, fails, "land-play")
    bad = layout_overflow(pg)
    print("land play", bad, flush=True)
    if bad:
        fails.append("landscape play overflow: " + " | ".join(bad[:8]))
    rows = boxes_under(pg, "#pz, #mu, #home, #dpad button")
    print("land targets", rows, flush=True)
    require_56(fails, rows, "landscape")
    hit = pg.evaluate("""() => {
      const a = document.getElementById('h3c'), b = document.getElementById('dpad');
      if (!a || !b) return { missing: true };
      const ar = a.getBoundingClientRect(), br = b.getBoundingClientRect();
      const overlap = ar.left < br.right - 1 && ar.right > br.left + 1 && ar.top < br.bottom - 1 && ar.bottom > br.top + 1;
      return { hit: overlap, goal: [Math.round(ar.left), Math.round(ar.top), Math.round(ar.right), Math.round(ar.bottom)], pad: [Math.round(br.left), Math.round(br.top), Math.round(br.right), Math.round(br.bottom)] };
    }""")
    print("land hud pad", hit, flush=True)
    if not hit or hit.get("missing") or hit.get("hit"):
        fails.append("landscape goal banner overlaps the D-pad: %s" % hit)
    scan(pg, "land-play", fails)
    pg.screenshot(path=str(EV / "verify_touch_play_land.png"))
    assert_play_bands(fails, EV / "verify_touch_play_land.png", "land-play")
    pg.locator("#pz").tap()
    pg.wait_for_timeout(200)
    if not pg.locator("#pzo").is_visible():
        fails.append("landscape pause menu did not open")
    else:
        assert_fit(pg, fails, "#pzo", "land pause")
        require_56(fails, boxes_under(pg, "#pzo button, #pzo a"), "landscape pause")
        scan(pg, "land-pause", fails)
        pg.screenshot(path=str(EV / "verify_touch_pause_land.png"))
        pg.locator("#pzo button").first.tap()
        pg.wait_for_timeout(150)
    reach_pitch(pg, fails, "land-es", es=True)
    pg.goto(PLAY + "?lang=es&mute=1", wait_until="domcontentloaded")
    if not reach_tale(pg):
        fails.append("landscape Spanish story did not open")
    else:
        tale = story_card(pg) or {}
        print("land es story", tale, flush=True)
        if not ES.search(tale.get("line") or ""):
            fails.append("landscape Spanish story stayed in English: %s" % tale)
        if not tale.get("full"):
            fails.append("landscape Spanish story is not full screen: %s" % tale)
        pg.screenshot(path=str(EV / "verify_touch_pass13_story_land_es.png"))
        skip_tale(pg)
    pg.wait_for_timeout(250)
    try:
        pg.wait_for_function("() => window.__STAGE3D__ && window.__STAGE3D__.ok", timeout=20000)
    except Exception as ex:
        fails.append("landscape Spanish stage did not fill: " + str(ex)[:120])
    else:
        check_fullscreen(pg, fails, "land-es-play")
        pg.screenshot(path=str(EV / "verify_touch_pass13_land_es.png"))
        assert_play_bands(fails, EV / "verify_touch_pass13_land_es.png", "land-es-play")
    restore_window(pg)
    pg.wait_for_timeout(150)
    pg.set_viewport_size({"width": 390, "height": 844})

def full_path(pg, fails):
    pg.goto(GALLERY, wait_until="domcontentloaded")
    pg.wait_for_timeout(300)
    dismiss_pitch(pg)
    scan(pg, "gallery", fails)
    check_gallery_polish(pg, fails)
    pg.screenshot(path=str(EV / "verify_touch_gallery.png"))
    pg.locator('a.btn', has_text="Play").first.tap()
    pg.wait_for_url("**/play.html*", timeout=15000)
    pg.wait_for_function("() => window.__GAME__ && window.__GAME__.ready", timeout=30000)
    dismiss(pg)
    hud_ok(pg, fails, 1)
    scan(pg, "scene1", fails)
    check_fullscreen(pg, fails, "scene1")
    pg.screenshot(path=str(EV / "verify_touch_scene1.png"))
    pg.screenshot(path=str(EV / "verify_touch_fullscreen_scene1.png"))
    assert_play_bands(fails, EV / "verify_touch_fullscreen_scene1.png", "scene1")
    scene_fit = layout_overflow(pg)
    print("scene1 fit", scene_fit, flush=True)
    if scene_fit:
        fails.append("portrait play overflow: " + " | ".join(scene_fit[:8]))
    check_spark(pg, fails)
    juice_scene(pg, fails)
    for n, nxt in ((1, "play_2.html"), (2, "play_3.html")):
        pg.evaluate("() => { window.__HOLD_FX__ = 3500 }")
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
        pg.screenshot(path=str(EV / ("verify_touch_scene%s.png" % (n + 1))))
        check_fullscreen(pg, fails, "scene%s" % (n + 1))
        assert_play_bands(fails, EV / ("verify_touch_scene%s.png" % (n + 1)), "scene%s" % (n + 1))
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
    restore_window(pg)
    pg.set_viewport_size({"width": 844, "height": 390})
    pg.wait_for_timeout(200)
    pg.evaluate("() => { const s = document.querySelector('#ps .scr'); if (s) s.scrollTop = 0; window.scrollTo(0, 0); }")
    assert_fit(pg, fails, "#ps .scr", "land results")
    scan(pg, "ending-land", fails)
    pg.screenshot(path=str(EV / "verify_touch_ending_land.png"))
    restore_window(pg)
    pg.set_viewport_size({"width": 390, "height": 844})

def check_viewport_sources(fails):
    need = ["play.html", "index.html", "gallery.html", "w_gato.html", "w_fishhome.html", "demo.template.html"]
    for name in need:
        t = (GAME / name).read_text(errors="replace")[:1500]
        if 'name="viewport"' not in t or "width=device-width" not in t:
            fails.append("viewport meta missing width=device-width in " + name)

def check_fish_solver(fails):
    sys.path.insert(0, str(ROOT / "agent"))
    from playtest import solve
    for n in (1, 2, 3):
        spec = json.loads((ROOT / "samples/kid_02/worlds/v1" / ("scene_%d.json" % n)).read_text())
        path = solve(spec)
        print("fish solve", n, None if path is None else len(path), flush=True)
        if not path:
            fails.append("fish home scene %s is not solver-green" % n)
        if len(spec.get("goals") or []) < 3 or len(spec.get("goals") or []) > 5:
            fails.append("fish home scene %s fish count %s" % (n, len(spec.get("goals") or [])))

def check_fishhome(pg, fails):
    check_fish_solver(fails)
    pg.goto(GALLERY, wait_until="domcontentloaded")
    pg.wait_for_timeout(250)
    dismiss_pitch(pg)
    card = pg.evaluate("""() => {
      const c = document.querySelector('[data-demo="fishhome"]');
      if (!c) return null;
      const h = c.querySelector('h2'), p = c.querySelector('p'), s = c.querySelector('small'), a = c.querySelector('a.btn');
      const link = s && s.querySelector('a');
      return {
        title: h ? h.textContent.replace(/\\s+/g, ' ').trim() : '',
        line: p ? p.textContent.replace(/\\s+/g, ' ').trim() : '',
        small: s ? s.innerText.replace(/\\s+/g, ' ').trim() : '',
        href: a ? a.getAttribute('href') : '',
        link: link ? link.getAttribute('href') : ''
      };
    }""")
    print("fish card", card, flush=True)
    if not card or card.get("title") != "Fish Home":
        fails.append("fish home card missing: %s" % card)
    else:
        blob = card["title"] + "\n" + card["line"] + "\n" + card["small"]
        if "Khamkhoune" not in card["small"] or "CC BY-SA 4.0" not in card["small"]:
            fails.append("fish home credit missing on card: %s" % card["small"])
        if "creativecommons.org/licenses/by-sa/4.0" not in (card.get("link") or ""):
            fails.append("fish home license link missing: %s" % card)
        if card.get("href") != "w_fishhome.html":
            fails.append("fish home play link: %s" % card.get("href"))
        if ES.search(blob) or VER.search(blob):
            fails.append("fish home card leak on English gallery: " + blob)
    pg.locator('[data-demo="fishhome"]').scroll_into_view_if_needed()
    pg.screenshot(path=str(EV / "verify_touch_fishhome_gallery.png"))
    fish = (GAME / "w_fishhome.html").resolve().as_uri()
    pg.goto(fish + "?mute=1", wait_until="domcontentloaded")
    if not reach_tale(pg):
        fails.append("fish home scene 1 story did not open")
    else:
        tale = story_card(pg)
        print("fish story", tale, flush=True)
        line = (tale or {}).get("line") or ""
        low = line.lower()
        if "fish" not in low and "pond" not in low:
            fails.append("fish home story missing fish or pond: " + line)
        if ES.search(line) or VER.search(line) or "LEAK" in line:
            fails.append("fish home story leak: " + line)
        if (tale or {}).get("art") != "🐟":
            fails.append("fish home story art: %s" % tale)
    skip_tale(pg)
    pg.wait_for_timeout(200)
    hud_ok(pg, fails, 1)
    obj = pg.locator("#h3c .obj").inner_text() if pg.locator("#h3c .obj").count() else ""
    if "fish" not in obj.lower():
        fails.append("fish home goal does not mention fish: " + obj)
    check_fullscreen(pg, fails, "fish-scene1")
    info = pg.evaluate("""() => ({
      cell: window.__SPARK__ && window.__SPARK__.cell,
      spark: (window.__STAGE3D__ && window.__STAGE3D__.spark) || 0,
      credit: (window.__BUNDLE__ && window.__BUNDLE__.credit) || null,
      calls: window.__BUNDLE__ && window.__BUNDLE__.live_meta_calls
    })""")
    print("fish scene1 spark", info, flush=True)
    if info.get("cell") or info.get("spark"):
        fails.append("fish home scene 1 shows the bonus star: %s" % info)
    if (info.get("credit") or {}).get("en") != "Drawing by Khamkhoune, age 11 — CC BY-SA 4.0":
        fails.append("fish home English credit string: %s" % info.get("credit"))
    if (info.get("credit") or {}).get("es") != "Dibujo de Khamkhoune, 11 años — CC BY-SA 4.0":
        fails.append("fish home Spanish credit string: %s" % info.get("credit"))
    if info.get("calls") not in (0, None):
        fails.append("fish home live calls: %s" % info.get("calls"))
    scan(pg, "fish-scene1", fails)
    pg.screenshot(path=str(EV / "verify_touch_fishhome_scene1.png"))
    assert_play_bands(fails, EV / "verify_touch_fishhome_scene1.png", "fish-scene1")
    pg.goto(fish + "?lang=es&mute=1", wait_until="domcontentloaded")
    if not reach_tale(pg):
        closed = pg.evaluate("() => window.__TALE__ && window.__TALE__.closed")
        if closed:
            print("fish story es already closed", closed, flush=True)
        else:
            fails.append("fish home Spanish story did not open")
    else:
        tale = story_card(pg) or {}
        print("fish story es", tale, flush=True)
        line = tale.get("line") or ""
        if not re.search(r"pez|estanque", line, re.I):
            fails.append("fish home Spanish story: " + line)
    skip_tale(pg)
    pg.wait_for_timeout(200)
    es_obj = pg.locator("#h3c .obj").inner_text() if pg.locator("#h3c .obj").count() else ""
    print("fish hud es", es_obj, flush=True)
    if not re.search(r"peces|pez", es_obj, re.I):
        fails.append("fish home Spanish goal: " + es_obj)
    fish3 = (GAME / "w_fishhome_3.html").resolve().as_uri()
    pg.goto(fish3 + "?go=1&mute=1", wait_until="domcontentloaded")
    pg.wait_for_function("() => window.__GAME__ && window.__GAME__.ready && window.__STAGE3D__ && (window.__STAGE3D__.ok || window.__STAGE3D__.error)", timeout=30000)
    dismiss(pg)
    pg.wait_for_timeout(250)
    roof = pg.evaluate("""() => ({
      cell: window.__SPARK__ && window.__SPARK__.cell,
      spark: (window.__STAGE3D__ && window.__STAGE3D__.spark) || 0
    })""")
    print("fish roof", roof, flush=True)
    cell = (roof or {}).get("cell") or {}
    if cell.get("x") != 10 or cell.get("y") != 1 or not roof.get("spark"):
        fails.append("bonus star missing on the blue roof: %s" % roof)
    check_fullscreen(pg, fails, "fish-scene3")
    scan(pg, "fish-scene3", fails)
    pg.screenshot(path=str(EV / "verify_touch_fishhome_scene3.png"))
    assert_play_bands(fails, EV / "verify_touch_fishhome_scene3.png", "fish-scene3")
    pg.evaluate("document.getElementById('auto').click()")
    try:
        pg.wait_for_function("() => window.__GAME__ && window.__GAME__.state().status === 'won'", timeout=60000)
        pg.wait_for_function("() => !!document.getElementById('credit') || ((document.body.innerText || '').indexOf('Khamkhoune') >= 0)", timeout=20000)
    except Exception as ex:
        try:
            pg.screenshot(path=str(EV / "verify_touch_fishhome_ending.png"))
        except Exception:
            pass
        fails.append("fish home ending did not show credit: " + str(ex)[:160])
    else:
        cred = pg.locator("#credit").inner_text() if pg.locator("#credit").count() else ""
        print("fish credit", cred, flush=True)
        blob = cred or "\n".join(visible(pg))
        if "Drawing by Khamkhoune, age 11 — CC BY-SA 4.0" not in blob:
            fails.append("ending credit sentence: " + (cred or blob)[:180])
        href = ""
        if pg.locator("#credit a").count():
            href = pg.locator("#credit a").get_attribute("href") or ""
        if "creativecommons.org/licenses/by-sa/4.0" not in href:
            fails.append("ending license link missing")
        scan(pg, "fish-ending", fails)
        pg.screenshot(path=str(EV / "verify_touch_fishhome_ending.png"))
    restore_window(pg)
    try:
        pg.goto(GALLERY + "?lang=es", wait_until="domcontentloaded", timeout=30000)
    except Exception as ex:
        fails.append("fish home Spanish gallery: " + str(ex)[:160])
        return
    pg.wait_for_timeout(250)
    dismiss_pitch(pg)
    es_card = pg.evaluate("""() => {
      const c = document.querySelector('[data-demo="fishhome"]');
      if (!c) return '';
      return (c.innerText || '').replace(/\\s+/g, ' ').trim();
    }""")
    print("fish card es", es_card, flush=True)
    if "Dibujo de Khamkhoune, 11 años" not in es_card or "CC BY-SA 4.0" not in es_card:
        fails.append("Spanish gallery credit missing: " + es_card)
    if "Los peces vuelven a casa" not in es_card:
        fails.append("Spanish gallery title missing: " + es_card)

def main():
    fails = []
    sources_video(fails)
    check_viewport_sources(fails)
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
            check_pitch(pg, fails)
            check_story(pg, fails)
            check_controls(pg, fails)
            check_create(pg, fails)
            check_judge(pg, fails)
            check_index(pg, fails)
            full_path(pg, fails)
            check_es(pg, fails)
            check_other_world(pg, fails)
            check_pipo_skip(pg, fails)
            check_fishhome(pg, fails)
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
        try:
            check_reduced(p, fails)
        except Exception as ex:
            fails.append("reduced-motion EXCEPTION " + str(ex)[:300])
    print("FAILS", len(fails), flush=True)
    for f in fails:
        print(" -", f, flush=True)
    return 1 if fails else 0

if __name__ == "__main__":
    sys.exit(main())
