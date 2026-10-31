#!/usr/bin/env python3
"""LIVE: kid drawing -> SAM 3.1 boxes per noun -> local alpha cutout (non-paper pixels inside box) -> sprites/*.png.
Optional --clean N: Muse Image edit on the first N cutouts (sketch -> clean sprite, same style). Logs estimated cost locally.
Usage: sam_cutouts.py samples/synthetic_12/drawing.png --nouns rocket,star,monster,rock --out runs/sam_12 [--clean 1]"""
import sys, json, pathlib, argparse, base64, subprocess
ROOT = pathlib.Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT / "agent"))
import meta_client as mc
from PIL import Image
a = argparse.ArgumentParser(); a.add_argument("image"); a.add_argument("--nouns", required=True); a.add_argument("--out", required=True); a.add_argument("--clean", type=int, default=0); o = a.parse_args()
out = pathlib.Path(o.out); (out / "sprites").mkdir(parents=True, exist_ok=True)
seg = mc.segment(o.image, o.nouns.split(",")); (out / "sam.json").write_text(json.dumps(seg, indent=2))
im = Image.open(o.image).convert("RGB"); made = []
for n, v in seg["nouns"].items():
    for k, b in enumerate(v.get("boxes", [])):
        c = im.crop(b).convert("RGBA"); px = c.load()
        for y in range(c.height):
            for x in range(c.width):
                r, g, bb, _ = px[x, y]
                if min(r, g, bb) > 225: px[x, y] = (255, 255, 255, 0)  # paper -> transparent
        f = out / "sprites" / f"{n}_{k}.png"; c.save(f); made.append(str(f))
print(json.dumps({"sam_ok": seg["ok"], "boxes": {n: v.get("boxes") for n, v in seg["nouns"].items()}, "sprites": len(made)}))
row = f"| auto | sam-3.1 x{seg['images_billed']} imgs (+${seg['images_billed']*0.0025:.4f}) {pathlib.Path(o.image).parent.name} |"
with open(out / "cost.txt", "w") as f: f.write(row + "\n")
cleaned = []
for f in made[:o.clean]:
    r = mc.image_edit(f, "Clean up this child's crayon drawing into a game sprite: keep the exact same shape, colors and wobbly hand-drawn style, white background removed, no new details.", dry=False)
    if r.get("ok") and r.get("data"):
        d = r["data"][0]
        if d.get("b64_json"): p = pathlib.Path(f).with_name(pathlib.Path(f).stem + "_clean.png"); p.write_bytes(base64.b64decode(d["b64_json"])); cleaned.append(str(p))
        else: cleaned.append(d.get("url"))
    else: cleaned.append({"error": r.get("error"), "http": r.get("http_status")})
print(json.dumps({"image_edit": cleaned}))
