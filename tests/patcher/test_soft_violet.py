#!/usr/bin/env python3
"""Regression: offline enemy vision survives a REAL violet pencil, not just pure synthetic violet.
Recolours the violet ink of synthetic_10/11 into soft lavender / shaded pencil tones with per-pixel noise and
checks the same enemies (spawn + patrol) come out; also checks blue/red/brown/paper/graphite are never 'enemy'."""
import json, pathlib, random, subprocess, sys, tempfile
ROOT = pathlib.Path(__file__).resolve().parents[2]; sys.path.insert(0, str(ROOT / "scripts"))
from PIL import Image
from generate_from_drawing import _cls
fails = 0
def check(ok, msg):
    global fails; fails += not ok; print(("PASS " if ok else "FAIL ") + msg)
for px, want in (((170,120,210),"enemy"),((120,70,150),"enemy"),((150,95,190),"enemy"),((200,160,225),"enemy"),
                 ((40,90,220),"not"),((60,140,230),"not"),((230,40,40),"not"),((140,70,30),"not"),
                 ((250,248,240),"not"),((90,90,95),"not"),((20,15,25),"not")):
    got = _cls(px); check((got == "enemy") == (want == "enemy"), f"_cls{px} -> {got}")
py = str(ROOT / ".venv/bin/python") if (ROOT / ".venv/bin/python").exists() else sys.executable
TONES = ((170,120,210),(120,70,150),(150,95,190))
def gen(img, out):
    subprocess.run([py, str(ROOT / "scripts/generate_from_drawing.py"), "--image", str(img), "--out", str(out)], capture_output=True, check=True)
    return [c for c in json.loads(out.read_text()).get("characters", []) if c.get("role") == "enemy"]
with tempfile.TemporaryDirectory() as td:
    for sid in ("synthetic_10", "synthetic_11"):
        src = ROOT / f"samples/{sid}/drawing.png"; im = Image.open(src).convert("RGB"); p = im.load(); rnd = random.Random(7)
        for x in range(im.width):
            for y in range(im.height):
                if _cls(p[x, y]) == "enemy":
                    t = rnd.choice(TONES); p[x, y] = tuple(max(0, min(255, c + rnd.randint(-12, 12))) for c in t)
        soft = pathlib.Path(td) / f"{sid}_soft.png"; im.save(soft)
        a, b = gen(src, pathlib.Path(td) / "a.json"), gen(soft, pathlib.Path(td) / "b.json")
        strip = lambda e: [(c["x"], c["y"], c["patrol"]) for c in e]
        check(len(b) == len(a) >= 1 and strip(a) == strip(b), f"{sid}: soft pencil violet -> same enemies {strip(b)[:1]}")
print("FAILS:", fails); sys.exit(1 if fails else 0)
