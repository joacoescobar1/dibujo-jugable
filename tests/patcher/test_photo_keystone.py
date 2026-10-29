#!/usr/bin/env python3
"""KEYSTONE variant of test_photo_robust: same photo-ization plus a perspective tilt (top edge shrunk 3-7% per side,
as when the phone is held tilted toward the top of the sheet). Compares normalize_photo WITHOUT the keystone step
(perspective=False: deskew+crop only) vs WITH it. Same STRICT/TOLERANT definitions as below.
Asserts: with-keystone TOLERANT on every case, STRICT >= 80% and > without, STRICT on every synthetic_11 case.
--- original doc (test_photo_robust) ---
Robustness: a phone photo of the drawing must give the same game as the clean drawing.
Each synthetic sample is 'photo-ized' with fixed seeds (scripts/photoize.py: yellow paper, lighting gradient, soft
shadow, haze, rotation 1.5-5 deg, table margin, some at 1.6x scale, noise sigma 6, JPEG q70) and read by the offline
generator WITHOUT (raw) and WITH scripts/photo_normalize.normalize_photo. Compared against the clean spec:
  STRICT   = hazards, walls and enemies (spawn + patrol) identical.
  TOLERANT = same win/lose verdict from the solver; hazard+wall cell sets differ by <= 2 cells; same enemy count and
             spawn cells, each patrol's visited cells differ by <= 1. Why: a cell whose clean ink coverage sits next to
             the 15% threshold (edge of a slanted band at 16%, end of a thin violet trail at 10%) flips under a
             <=1px registration error, which no photo pipeline can promise.
Asserts: normalised TOLERANT on every case, normalised STRICT >= 85% and > raw, STRICT on every synthetic_11 case
(the judge-demo sample). Prints raw vs normalised rates so the gain is measured, not claimed.
Usage: test_photo_robust.py [--seeds N] [--keep DIR]"""
import json, pathlib, sys, tempfile
ROOT = pathlib.Path(__file__).resolve().parents[2]; sys.path[:0] = [str(ROOT), str(ROOT / "scripts")]
from PIL import Image
import generate_from_drawing as G, photo_normalize
from photoize import photoize
from agent.playtest import playtest
SEEDS = int(sys.argv[sys.argv.index("--seeds") + 1]) if "--seeds" in sys.argv else 3
KEEP = pathlib.Path(sys.argv[sys.argv.index("--keep") + 1]) if "--keep" in sys.argv else None
def cells(s):
    out = set()
    for h in s["hazards"]: out |= {(h["label"], h["x"] + i, h["y"] + j) for i in range(h["w"]) for j in range(h["h"])}
    for w in s["walls"]: out |= {("wall", w["x"] + i, w["y"] + j) for i in range(w["w"]) for j in range(w["h"])}
    return out
foes = lambda s: [(c["x"], c["y"], c["patrol"]) for c in s.get("characters", []) if c.get("role") == "enemy"]
geo = lambda s: (s["hazards"], s["walls"], foes(s))
def spec(img, tr, normalize):
    G._LOADED.clear(); G.PHOTO_INFO.clear(); real = photo_normalize.normalize_photo
    if not normalize: photo_normalize.normalize_photo = lambda im: real(im, perspective=False)
    try: return G.offline_spec(img, tr)
    finally: photo_normalize.normalize_photo = real
def trail(c):
    """enemy -> (spawn, set of cells its ping-pong patrol visits)"""
    x, y, seen = c[0], c[1], {(c[0], c[1])}
    for dx, dy in c[2]: x, y = x + dx, y + dy; seen.add((x, y))
    return (c[0], c[1]), seen
def foes_close(a, b):
    """same number of enemies, same spawn (body) cells, patrol cell sets differ by <= 1 cell each"""
    return len(a) == len(b) and all(ta[0] == tb[0] and len(ta[1] ^ tb[1]) <= 1 for ta, tb in (map(trail, p) for p in zip(a, b)))
def verdict(ref, s):
    d = len(cells(ref) ^ cells(s))
    strict = geo(ref) == geo(s)
    tol = foes_close(foes(ref), foes(s)) and d <= 2 and playtest(ref)["winnable"] == playtest(s)["winnable"]
    return strict, tol, d
fails = 0
for k in range(1, 12):  # clean digital drawings must pass through untouched (keeps their specs byte-identical)
    src = ROOT / f"samples/synthetic_{k:02d}/drawing.png"; im = Image.open(src).convert("RGB"); o, inf = photo_normalize.normalize_photo(im)
    ok = inf == {"photo": False} and o.tobytes() == im.tobytes(); fails += not ok; print(("PASS" if ok else "FAIL") + f" clean synthetic_{k:02d} passes through normalize_photo unchanged")
rows = []; tally = {"raw": [0, 0], "norm": [0, 0]}; n = 0
with tempfile.TemporaryDirectory() as td:
    td = KEEP or pathlib.Path(td); td.mkdir(parents=True, exist_ok=True)
    for k in range(1, 12):
        sid = f"synthetic_{k:02d}"; src = ROOT / f"samples/{sid}/drawing.png"; tr = (src.parent / "transcript.txt").read_text()
        ref = spec(src, tr, True)
        for seed in range(SEEDS):
            ph, info = photoize(Image.open(src), seed=k * 100 + seed, keystone=(0.03, 0.05, 0.07)[seed % 3]); p = td / f"{sid}_s{seed}.png"; ph.save(p)
            r_raw, r_norm = verdict(ref, spec(p, tr, False)), verdict(ref, spec(p, tr, True)); n += 1
            for key, r in (("raw", r_raw), ("norm", r_norm)): tally[key][0] += r[0]; tally[key][1] += r[1]
            ok = r_norm[1] and (r_norm[0] or k != 11); fails += not ok
            print(f"{'PASS' if ok else 'FAIL'} {sid} seed={k*100+seed} rot={info['angle']:+.2f} key={info['keystone']} scale={info['scale']} "
                  f"raw: strict={int(r_raw[0])} tol={int(r_raw[1])} dcells={r_raw[2]} | norm: strict={int(r_norm[0])} tol={int(r_norm[1])} dcells={r_norm[2]}")
pct = lambda a: f"{a}/{n} ({100 * a / n:.0f}%)"
print(f"DESKEW+CROP ONLY:        strict {pct(tally['raw'][0])}  tolerant {pct(tally['raw'][1])}")
print(f"WITH KEYSTONE FIX:     strict {pct(tally['norm'][0])}  tolerant {pct(tally['norm'][1])}")
if tally["norm"][0] < 0.80 * n: fails += 1; print("FAIL keystone strict rate < 80%")
if tally["norm"][0] <= tally["raw"][0]: fails += 1; print("FAIL keystone fix does not beat deskew+crop only")
print("FAILS:", fails); sys.exit(1 if fails else 0)
