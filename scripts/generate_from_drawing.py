#!/usr/bin/env python3
"""Drawing (+voice) -> GameSpec. --mode offline: deterministic placeholder spec from transcript keywords (no vision).
--mode muse: checks /models; if Muse not listed -> LOCKED message + offline fallback. Never fabricates model output.
Usage: generate_from_drawing.py --image samples/x/drawing.png [--voice v.wav | --transcript t.txt] --out spec.json
Exit 0 = spec written + schema-valid (may be UNWINNABLE: first-try honesty); 1 = invalid.
Offline reads hazard/wall cells from drawing pixels (crude colour vision), so flawed drawings give flawed specs.
VIOLET ink = enemy characters (blob = spawn, violet trail = ping-pong patrol), see read_enemies.
Phone photos are normalised first (scripts/photo_normalize.py: deskew+crop sheet, flat-field, denoise); clean images pass through."""
import argparse, json, sys, pathlib, subprocess, hashlib
ROOT = pathlib.Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "scripts"))
def _rel_drawing(image):
    """Repo-relative drawing path. Never store an absolute machine path in a spec that can ship."""
    p = pathlib.Path(image)
    try:
        rp = p.resolve()
        if rp == ROOT or ROOT in rp.parents:
            return str(rp.relative_to(ROOT))
    except OSError:
        pass
    return p.name
LEX = {"gato": "Gato", "perro": "Perro", "nave": "Nave", "casa": "Casa", "hueso": "Hueso", "estrella": "Estrella",
       "agua": ("Agua", "#39f"), "fuego": ("Fuego", "#f33"), "piedras": ("Piedras", "#888")}
ENEMY_LEX = {"bicho": "Bicho", "fantasma": "Fantasma", "lobo": "Lobo", "araña": "Araña", "arana": "Araña", "monstruo": "Monstruo", "perro": "Perro", "gato": "Gato", "dragon": "Dragón"}
COLOR_LABEL = {"blue": ("Agua", "#39f"), "red": ("Fuego", "#f33"), "gray": ("Piedras", "#888")}
def _cls(px):
    r, g, b = px[:3]
    if b > 180 and r < 80 and g < 80: return "blue"
    if r > 180 and g < 80 and b < 80: return "red"
    if 100 < r < 160 and abs(r - g) < 12 and abs(g - b) < 12: return "gray"
    if 110 < r < 170 and 50 < g < 90 and b < 40: return "wall"
    if r > 110 and b > 150 and g < 60 and abs(r - b) < 110: return "enemy"  # violeta = bicho (cuerpo + rastro de patrulla)
    if _soft_violet(r, g, b): return "enemy"
    return "blue" if _birome_blue(r, g, b) else None
def _birome_blue(r, g, b):
    """Real birome / lapicera azul: dark, saturated blue ink (e.g. (25,45,130), (40,70,160)) that misses the pure-blue
    check (b>180). Hue 205-250 deg, saturation >= 0.25 (phone photo + JPEG drops birome ink to s~0.3-0.4), value 0.25-0.85. Black pen (s<0.2), graphite/paper (grey),
    violet (hue >= 255) and light-blue paper tint (low s) stay out. A kid hatching a river with a blue pen = Agua."""
    import colorsys
    h, s_, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
    return 205 <= h * 360 <= 250 and s_ >= 0.25 and 0.25 <= v <= 0.85
def _soft_violet(r, g, b):
    """Real lápiz/fibra violeta: soft, shaded or lavender ink (e.g. (170,120,210), (120,70,150)). Hue 255-320 deg,
    saturation >= 0.25 (paper/graphite are grey), value 0.25-0.97 (not black, not paper). Blue (hue ~200-245) and
    red/brown (hue < 40) stay out, so hazard/wall reading is unchanged."""
    import colorsys
    h, s_, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
    return 255 <= h * 360 <= 320 and s_ >= 0.25 and 0.25 <= v <= 0.97
PHOTO_INFO = {}
def load_drawing(image):
    """Open the drawing and run photo_normalize.normalize_photo (deskew/crop sheet, flat-field paper, light denoise).
    Clean digital images come back untouched (info photo=False), so their specs stay byte-identical."""
    from PIL import Image
    from photo_normalize import normalize_photo
    key = str(image)
    if key not in _LOADED:
        for c in [c for c in _COVER if c[0] == key]: del _COVER[c]  # new pixels -> stale coverage out
        im, PHOTO_INFO[key] = normalize_photo(Image.open(image))
        _LOADED[key] = _fill_hatching(im)
    return _LOADED[key]
HATCH_DIV = 60  # k=9 px on a 481 px sheet: closes pen hatching gaps, far below a 1-cell (~40 px) gap a kid leaves on purpose
def _fill_hatching(im):
    """A river hatched with a birome leaves white gaps between strokes, so per-cell coverage drops and the river breaks.
    Morphological closing of the birome-blue mask only (kernel ~1/60 of the sheet, odd, >= 5 px), painting the closed
    gaps pure blue. Pure-blue paint, other colours and images without birome-blue ink are left untouched."""
    from PIL import Image, ImageFilter
    px = im.load(); W, H = im.size
    import colorsys
    m = Image.new("L", im.size); mp = m.load(); wk = Image.new("L", im.size); wp = wk.load(); n = 0
    for x in range(W):
        for y in range(H):
            r, g, b = px[x, y][:3]
            if b > 180 and r < 80 and g < 80: continue
            if _birome_blue(r, g, b): mp[x, y] = 255; n += 1; continue
            h, s_, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
            if 200 <= h * 360 <= 255 and s_ >= 0.12 and v <= 0.95: wp[x, y] = 255
    if n < 0.002 * W * H: return im
    k = max(5, round(min(W, H) / HATCH_DIV) | 1)
    # pixel hysteresis: blurred/light edges of the pen lines (weak blue) count only within 2 px of confident birome ink
    from PIL import ImageChops
    m = ImageChops.lighter(m, ImageChops.multiply(wk, m.filter(ImageFilter.MaxFilter(5))))
    closed = m.filter(ImageFilter.MaxFilter(k)).filter(ImageFilter.MinFilter(k))
    out = im.convert("RGB").copy(); op = out.load(); cp = closed.load()
    for x in range(W):
        for y in range(H):
            if cp[x, y] and _cls(px[x, y]) in (None, "blue"): op[x, y] = (0, 0, 255)
    return out
_LOADED = {}
_COVER = {}
def coverage(image, grid):
    """Per-cell ink coverage {(cx, cy): {class: fraction}} measured on the FULL-resolution sheet (exact cell boxes), with
    edge unmixing: a pixel the colour rules reject but that touches class-k ink (8-neighbour) and lies on the
    paper->ink_k colour line counts alpha (its ink fraction) instead of 0. Why: JPEG chroma blur, warp resampling and
    haze turn a hard ink edge into 1-3 blended pixels; the hard rules dropped them (~1 px of ink per edge), so a cell
    near the 15% threshold flipped on a phone photo. Paper/ink_k = median paper and mean class-k ink of THIS image, so
    it adapts to tint/haze; residual > max(20, 15% of |ink-paper|) = a different colour (black outline, other ink) ->
    0. Clean digital drawings have hard edges, so their coverage is the plain pixel count. Deterministic, cached."""
    im = load_drawing(image).convert("RGB"); key = (str(image), grid["w"], grid["h"])
    if key in _COVER: return _COVER[key]
    px = im.load(); W, H = im.size
    cls = [[_cls(px[x, y]) for y in range(H)] for x in range(W)]
    sums, n, paper = {}, {}, [[], [], []]
    for x in range(W):
        for y in range(H):
            k, p = cls[x][y], px[x, y]
            if k:
                s_ = sums.setdefault(k, [0, 0, 0]); n[k] = n.get(k, 0) + 1
                for i in range(3): s_[i] += p[i]
            elif (x % 4 == 0 and y % 4 == 0 and min(p) > 200):
                for i in range(3): paper[i].append(p[i])
    pap = [sorted(c)[len(c) // 2] if c else 255 for c in paper]
    ink = {k: [v / n[k] for v in s_] for k, s_ in sums.items()}
    def alpha(p, k):
        d = [ink[k][i] - pap[i] for i in range(3)]; dd = sum(v * v for v in d)
        if dd < 900: return 0.0
        q = [p[i] - pap[i] for i in range(3)]; a = max(0.0, min(1.0, sum(q[i] * d[i] for i in range(3)) / dd))
        res = sum((q[i] - a * d[i]) ** 2 for i in range(3)) ** 0.5
        return a if a >= 0.1 and res <= max(20.0, 0.15 * dd ** 0.5) else 0.0
    gw, gh = grid["w"], grid["h"]; out = {}
    for cx in range(gw):
        x0, x1 = round(cx * W / gw), round((cx + 1) * W / gw)
        for cy in range(gh):
            y0, y1 = round(cy * H / gh), round((cy + 1) * H / gh); cnt = {}
            for x in range(x0, x1):
                for y in range(y0, y1):
                    k = cls[x][y]
                    if k: cnt[k] = cnt.get(k, 0) + 1; continue
                    near = {cls[u][v] for u in range(max(0, x - 1), min(W, x + 2)) for v in range(max(0, y - 1), min(H, y + 2))} - {None}
                    if not near: continue
                    best = max(((alpha(px[x, y], c), c) for c in sorted(near)), default=(0.0, None))
                    if best[0]: cnt[best[1]] = cnt.get(best[1], 0) + best[0]
            area = max(1, (x1 - x0) * (y1 - y0)); out[(cx, cy)] = {k: v / area for k, v in cnt.items()}
    _COVER[key] = out
    return out
COVER_MIN = 0.15  # a cell is hazard/wall/enemy ink when >= 15% of its area is that ink
def read_drawing(image, grid):
    """Crude offline 'vision': per-cell colour coverage (>=15%, see coverage()) -> hazard/wall cells, merged into column runs.
    Faithful to the drawing, so a kid drawing a river to the edge or a fence around the house yields an UNWINNABLE first try."""
    try: cov = coverage(image, grid)
    except Exception: return [], []
    cells = {}
    for c, cnt in cov.items():
        k = max(cnt, key=cnt.get) if cnt else None
        if k and cnt[k] >= COVER_MIN: cells[c] = k
    runs = []  # vertical runs per column, then merge horizontally-identical runs
    for cx in range(grid["w"]):
        cy = 0
        while cy < grid["h"]:
            k = cells.get((cx, cy))
            if not k: cy += 1; continue
            y0 = cy
            while cells.get((cx, cy)) == k: cy += 1
            runs.append([k, cx, y0, 1, cy - y0])
    merged = []
    for r in runs:
        m = next((m for m in merged if m[0] == r[0] and m[1] + m[3] == r[1] and m[2] == r[2] and m[4] == r[4]), None)
        if m: m[3] += 1
        else: merged.append(r)
    rect = lambda m: {"x": m[1], "y": m[2], "w": m[3], "h": m[4]}
    return [(m[0], rect(m)) for m in merged if m[0] not in ("wall", "enemy")], [rect(m) for m in merged if m[0] == "wall"]
def read_enemies(image, grid):
    """Offline 'vision' for characters: every 4-connected VIOLET component = one enemy. The kid draws the bug (filled blob)
    plus a violet trail of where it walks. Spawn = cell with most violet ink (the body); patrol = ping-pong along the
    component's longer axis between its extremes (the trail). Single-cell component = enemy that stays put (patrol [[0,0]])."""
    try: cov = coverage(image, grid)
    except Exception: return []
    ink = {c: cnt["enemy"] for c, cnt in cov.items() if cnt.get("enemy", 0) >= COVER_MIN}
    out, seen = [], set()
    for c0 in sorted(ink):
        if c0 in seen: continue
        comp, st = [], [c0]; seen.add(c0)
        while st:
            c = st.pop(); comp.append(c)
            for d in ((1,0),(-1,0),(0,1),(0,-1)):
                n = (c[0]+d[0], c[1]+d[1])
                if n in ink and n not in seen: seen.add(n); st.append(n)
        body = max(comp, key=lambda c: (ink[c], -c[0], -c[1]))
        xs, ys = [c[0] for c in comp], [c[1] for c in comp]
        horiz = (max(xs) - min(xs)) >= (max(ys) - min(ys)); ax = 0 if horiz else 1
        lo, hi = (min(xs), max(xs)) if horiz else (min(ys), max(ys)); b = body[ax]
        unit = (1, 0) if horiz else (0, 1); neg = [-unit[0], -unit[1]]
        pat = [list(unit)] * (hi - b) + [neg] * (hi - lo) + [list(unit)] * (b - lo) if hi > lo else [[0, 0]]
        out.append({"x": body[0], "y": body[1], "patrol": pat})
    return out
def offline_spec(image, transcript):
    t = transcript.lower(); words = [w.strip(",.") for w in t.split()]
    who = next((w for w in words if w in ("gato", "perro", "nave")), "jugador")
    goal = next((w for w in words if w in ("casa", "hueso", "estrella")), "meta")
    hz = next((w for w in words if w in ("agua", "fuego", "piedras")), None)
    s = {"title": f"{LEX.get(who, who.title())} -> {LEX.get(goal, goal.title())}", "source": {"drawing": _rel_drawing(image), "voice_transcript": transcript.strip()},
         "genre": "top-down", "grid": {"w": 16, "h": 12, "tile": 40},
         "player": {"id": who, "label": LEX.get(who, who), "x": 1, "y": 1, "color": "#f90"},
         "goals": [{"id": goal, "label": LEX.get(goal, goal), "x": 14, "y": 10, "color": "#4c4"}],
         "hazards": [], "walls": [], "win_condition": {"type": "reach_goal", "target": goal},
         "rules_text": [transcript.strip()], "_generator": "offline_placeholder"}
    hz_lab = LEX[hz] if hz else None
    hzs, walls = read_drawing(image, s["grid"])
    for i, (col, r) in enumerate(hzs):
        lab, c = hz_lab or COLOR_LABEL[col]
        s["hazards"].append({"id": (hz or "peligro") if i == 0 else f"{hz or 'peligro'}_{i+1}", "label": lab, **r, "color": c, "effect": "lose"})
    s["walls"] = [r for r in walls]
    foe = next((w for w in words if w in ENEMY_LEX and w != who), None)
    for i, e in enumerate(read_enemies(image, s["grid"])):
        base = foe or "bicho"; s.setdefault("characters", []).append({"id": base if i == 0 else f"{base}_{i+1}", "label": ENEMY_LEX.get(base, "Bicho"), "role": "enemy", **e})
    if PHOTO_INFO.get(str(image), {}).get("photo"): s["_photo_normalize"] = PHOTO_INFO[str(image)]
    if s.get("characters"): s["rules_text"].append("Violeta = bicho: si te toca, perdés. Camina por su rastro ida y vuelta.")
    return s
MUSE_SPEC = {}
def muse_spec(mc, img, transcript):
    """LIVE Muse vision: drawing + transcript -> GameSpec JSON. Validated by caller; returns {} + note on failure."""
    schema = (ROOT / "specs/game-spec.schema.json").read_text(); ex = (ROOT / "specs/enemy-guardia-puerta.spec.json").read_text()
    sysm = ("Sos el generador de Dibujo Jugable. Un nene dibujó un juego en papel y lo contó con su voz. Convertí EXACTAMENTE lo que dibujó en un GameSpec JSON. "
            "Reglas: grilla 16x12 (tile 40); mapeá cada objeto a su posición relativa en la hoja (x de 0 a 15 izquierda→derecha, y de 0 a 11 arriba→abajo). "
            "Piedras/paredes/montañas dibujadas = walls (una entrada por piedra, w/h 1-2, en el lugar donde están en la hoja); agua/lava/pinches = hazards; "
            "bichos/monstruos = characters role=enemy con patrol (offsets relativos [[dx,dy],...] ida y vuelta, cerca de donde están). "
            "El protagonista de la voz = player; lo que quiere alcanzar = goals + win_condition reach_goal. Mantené ids en minúscula sin espacios. "
            "Respetá el dibujo aunque el juego quede difícil o roto: otro agente lo testea y arregla después. Devolvé SOLO el JSON.")
    user = [{"type": "text", "text": f"Schema JSON:\n{schema}\n\nEjemplo de spec válido (otro dibujo):\n{ex}\n\nTranscripción de la voz del nene: \"{transcript}\"\n\nDibujo:"}, mc.image_part(img)]
    r = mc.chat_live([{"role": "system", "content": sysm}, {"role": "user", "content": user}], m="muse-spark", note=f"generate_from_drawing {img.parent.name}", max_tokens=20000)
    if not r["ok"]: return {"_meta": {"note": f"Muse error http={r.get('http_status')} -> offline fallback", "live_meta_calls": 1}}
    try: s = mc.parse_json(r["content"])
    except Exception as e: return {"_meta": {"note": f"Muse returned non-JSON ({e}) -> offline fallback", "live_meta_calls": 1}}
    s.setdefault("source", {"drawing": _rel_drawing(img), "voice_transcript": transcript})
    s["_generator"] = "muse-spark"
    return {**s, "_meta": {"note": "LIVE Muse vision spec", "live_meta_calls": 1, "model": r["model"], "usage": r["usage"]}}
if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--image", required=True); ap.add_argument("--voice"); ap.add_argument("--transcript")
    ap.add_argument("--mode", choices=["offline", "muse"], default="offline"); ap.add_argument("--out", required=True); a = ap.parse_args()
    img = pathlib.Path(a.image); tp = pathlib.Path(a.transcript) if a.transcript else img.parent / "transcript.txt"
    meta = {"mode_requested": a.mode, "mode_used": "offline", "live_meta_calls": 0}
    if a.mode == "muse":
        from agent import meta_client as mc
        lm = mc.list_models()
        if "muse-spark" not in lm["models"]:
            meta["note"] = f"LOCKED: muse-spark not in /models (count={lm['count']}, http={lm.get('http_status')}) -> offline fallback"
        else:
            wspec = muse_spec(mc, img, tp.read_text() if tp.exists() else "")
            meta.update(wspec.pop("_meta")); 
            if wspec.get("player"): meta["mode_used"] = "muse"; MUSE_SPEC.update(wspec)
        print(meta["note"], file=sys.stderr)
    if a.voice and not tp.exists(): print(f"FAIL: no transcript for {a.voice}; STT (transcribe) needs Meta unlock", file=sys.stderr); sys.exit(1)
    spec = dict(MUSE_SPEC) if MUSE_SPEC else offline_spec(img, tp.read_text() if tp.exists() else "")
    spec["_gen_meta"] = {**meta, "input_sha256": hashlib.sha256(img.read_bytes() + (tp.read_bytes() if tp.exists() else b"")).hexdigest()[:16]}
    out = pathlib.Path(a.out); out.parent.mkdir(parents=True, exist_ok=True); out.write_text(json.dumps(spec, indent=2, ensure_ascii=False))
    from agent.game_guide import write_guide; print("guide:", write_guide(spec, out))
    v = subprocess.run([sys.executable, str(ROOT / "scripts/validate_spec.py"), str(out)], capture_output=True, text=True)
    print(v.stdout.strip() or v.stderr.strip()[-400:])
    from agent.playtest import playtest  # first-try honesty: schema-valid but possibly UNWINNABLE (loop must fix it)
    print("first_try:", "WINNABLE" if playtest(spec)["winnable"] else "UNWINNABLE (needs fix loop)"); sys.exit(v.returncode)
