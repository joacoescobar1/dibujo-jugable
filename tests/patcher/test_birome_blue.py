#!/usr/bin/env python3
"""Real ballpoint (birome) rivers: a kid hatches the river with a blue pen instead of painting it pure blue.
Every pure-blue pixel of each synthetic sample is recoloured to a birome tone AND thinned to diagonal hatching
(3px lines every 7px, ~43% coverage) + noise +-12. Expect TOLERANT on every case: same solver verdict (winnable or
not) as the clean spec and water cells differ by <= 2 (hatching lowers coverage, so river-edge cells that sat near the
15% threshold can drop; same caveat as test_photo_robust). STRICT (identical) is reported, not asserted.
Phone-photo pass (photoize + normalize_photo): asserts the same solver verdict; exact water cells reported (river ends
blur under JPEG, so 0-3 end cells can drop).
Also measures the old rule (b>180 only) on the same images so the gain is measured, not claimed, and checks
black pen / graphite / paper / light-blue tint / violet are NOT read as water."""
import json, pathlib, random, sys, tempfile
ROOT = pathlib.Path(__file__).resolve().parents[2]; sys.path[:0] = [str(ROOT), str(ROOT / "scripts")]
from PIL import Image
import generate_from_drawing as G
from photoize import photoize
from agent.playtest import playtest
TONES = [(25, 45, 130), (40, 70, 160), (30, 55, 115), (55, 80, 170)]
def spec(p, tr, birome=True):
    G._LOADED.clear(); G.PHOTO_INFO.clear(); real = G._birome_blue
    if not birome: G._birome_blue = lambda r, g, b: False
    try: return G.offline_spec(p, tr)
    finally: G._birome_blue = real
def cells(s):
    return {(h["label"], h["x"] + i, h["y"] + j) for h in s["hazards"] for i in range(h["w"]) for j in range(h["h"])}
def judge(ref, s):
    d = len(cells(ref) ^ cells(s)); strict = (ref["hazards"], ref["walls"]) == (s["hazards"], s["walls"])
    return strict, d <= 2 and s["walls"] == ref["walls"] and playtest(ref)["winnable"] == playtest(s)["winnable"], d
fails = 0
for px, want in [((10, 10, 10), False), ((60, 60, 60), False), ((130, 130, 130), False), ((250, 250, 245), False),
                 ((200, 215, 240), False), ((150, 90, 200), False), ((0, 0, 255), True)] + [(t, True) for t in TONES]:
    ok = (G._cls(px) == "blue") == want; fails += not ok; print(("PASS" if ok else "FAIL") + f" cls{px} blue={want}")
hit = {"old": [0, 0], "new": [0, 0]}; n = 0; photo = [0, 0, []]
with tempfile.TemporaryDirectory() as td:
    for k in range(1, 12):
        sid = f"synthetic_{k:02d}"; src = ROOT / f"samples/{sid}/drawing.png"; tr = (src.parent / "transcript.txt").read_text()
        im = Image.open(src).convert("RGB"); W, H = im.size; pix = im.load()
        if not any(pix[x, y] == (0, 0, 255) for x in range(0, W, 3) for y in range(0, H, 3)): continue
        for seed in range(3):
            rnd = random.Random(k * 10 + seed); tone = TONES[seed % len(TONES)]; out = im.copy(); o = out.load()
            for x in range(W):
                for y in range(H):
                    if pix[x, y] == (0, 0, 255):
                        o[x, y] = tuple(max(0, min(255, c + rnd.randint(-12, 12))) for c in tone) if (x + y) % 7 < 3 else (255, 255, 255)
            p = pathlib.Path(td) / f"{sid}_{seed}.png"; out.save(p); ref = spec(src, tr); n += 1
            new, old = judge(ref, spec(p, tr)), judge(ref, spec(p, tr, birome=False))
            for key, r in (("new", new), ("old", old)): hit[key][0] += r[0]; hit[key][1] += r[1]
            ph, _ = photoize(out, seed=k * 100 + seed); pp = pathlib.Path(td) / f"{sid}_{seed}_photo.png"; ph.save(pp)
            s_ph = spec(pp, tr); dph = len(cells(ref) ^ cells(s_ph)); vph = playtest(ref)["winnable"] == playtest(s_ph)["winnable"]
            photo[0] += dph == 0; photo[1] += vph; photo[2].append(dph); fails += not vph
            print(("PASS" if vph else "FAIL") + f" {sid} seed{seed} PHOTO of birome hatching: same verdict={vph} water cells_diff={dph}")
            fails += not new[1]
            print(("PASS" if new[1] else "FAIL") + f" {sid} seed{seed} tone{tone}: birome rule strict={new[0]} cells_diff={new[2]} | old rule strict={old[0]} tolerant={old[1]} cells_diff={old[2]}")
print(f"birome hatching ({n} imgs): old rule strict {hit['old'][0]}/{n} tolerant {hit['old'][1]}/{n} -> new rule strict {hit['new'][0]}/{n} tolerant {hit['new'][1]}/{n}")
print(f"phone photo of birome hatching ({n} imgs): exact water {photo[0]}/{n}, same solver verdict {photo[1]}/{n} (asserted), cells_diff {photo[2]}")
print(f"FAILS {fails}"); sys.exit(1 if fails else 0)
