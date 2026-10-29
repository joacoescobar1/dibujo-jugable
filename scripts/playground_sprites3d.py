#!/usr/bin/env python3
"""Crop each character from the Muse Image hero render -> Muse Image isolates it on flat magenta -> offline chroma key -> transparent 3D sprite.
evidence/<sample>/sprites3d/<name>_3d.png. Cached per output (rule 8). $0.01/img."""
import sys, pathlib, numpy as np
from PIL import Image
ROOT = pathlib.Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT / "agent")); sys.path.insert(0, str(ROOT / "scripts"))
import meta_client as mc; from playground_art import save
CROPS = {"player": (260, 140, 460, 355), "kid_1": (170, 370, 390, 675), "kid_2": (535, 230, 705, 530), "kid_3": (625, 35, 875, 500),
         "seesaw": (215, 395, 705, 715), "slide": (605, 105, 1130, 735)}
WHAT = {"player": "the yellow-and-pink butterfly", "kid_1": "the brown-haired boy", "kid_2": "the boy sitting", "kid_3": "the blonde girl in the purple dress",
        "seesaw": "the blue seesaw only (no kids)", "slide": "the pink slide with purple ladder only (no kids)"}
def key(raw, out):
    a = np.asarray(Image.open(raw).convert("RGB")).astype(int); R, G, B = a[..., 0], a[..., 1], a[..., 2]; m = np.minimum(R, B) - G
    al = np.clip(255 - (m - 40) * 3, 0, 255); im = Image.fromarray(np.dstack([a, al]).astype("uint8"), "RGBA"); im.crop(im.getbbox()).save(out)
sd = sys.argv[1]; D = ROOT / "evidence" / pathlib.Path(sd).name; S = D / "sprites3d"; S.mkdir(exist_ok=True); hero = Image.open(D / "image_hero.png").convert("RGB")
for n, box in CROPS.items():
    c, raw, out = S / f"{n}_crop.png", S / f"{n}_raw.png", S / f"{n}_3d.png"
    if not raw.exists():
        hero.crop(box).save(c)
        r = mc.image_edit(c, f"Isolate {WHAT[n]} as a single game sprite, same 3D feature-film CGI look, lighting and colors, full body, centered, on a perfectly flat solid magenta (#FF00FF) background. Remove everything else. No shadow, no text.", dry=False)
        save(r, raw); print(n, r.get("http_status"))
    key(raw, out); print(n, Image.open(out).size)
# extra board pieces cut from the empty plate (cloud -> patrolling grey cloud enemy; grass mound -> hedge wall tile)
EXTRA = {"enemy": ((320, 30, 600, 170), "Turn this cloud into a single grumpy grey storm-cloud character sprite (small frown, puffy), same 3D feature-film CGI look, centered on a perfectly flat solid magenta (#FF00FF) background. No text."),
         "flower": ((40, 700, 300, 860), "Make a single magical glowing pink flower collectible (a little sparkle around it), same 3D feature-film CGI look, centered on a perfectly flat solid magenta (#FF00FF) background. No text."),
         "cloud_block": ((320, 30, 600, 170), "Make a single fluffy white cloud platform block, soft and puffy, same 3D feature-film CGI look, centered on a perfectly flat solid magenta (#FF00FF) background. No text."),
         "door": ((320, 30, 600, 170), "Make a single glowing magic portal door made of rainbow light in an arch of cloud, same 3D feature-film CGI look, centered on a perfectly flat solid magenta (#FF00FF) background. No text."),
         "wall": ((850, 680, 1100, 860), "Make a single square chunky hedge bush block with little flowers, same 3D feature-film CGI look, seen from slightly above, centered on a perfectly flat solid magenta (#FF00FF) background. No text.")}
plate = Image.open(D / "image_plate.png").convert("RGB")
for n, (box, pr) in EXTRA.items():
    c, raw, out = S / f"{n}_crop.png", S / f"{n}_raw.png", S / f"{n}_3d.png"
    if not raw.exists(): plate.crop(box).save(c); r = mc.image_edit(c, pr, dry=False); save(r, raw); print(n, r.get("http_status"))
    key(raw, out); print(n, Image.open(out).size)
