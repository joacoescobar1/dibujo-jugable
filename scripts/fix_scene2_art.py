#!/usr/bin/env python3
"""Scene-2 art fix: empty sky plate edited from the already-empty plate (not the drawing, which leaks characters) + solid cloud wall tile. $0.01/img."""
import sys, pathlib; ROOT = pathlib.Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT/"agent")); sys.path.insert(0, str(ROOT/"scripts"))
import meta_client as mc; from playground_art import save, STYLE; from PIL import Image
D = ROOT/"evidence"/"playground_01"; S = D/"sprites3d"
SKY = ("Repaint this as an EMPTY high-sky game level background far above the ground: " + STYLE + " Only open pastel-blue sky, soft sun glow in the upper corner, and large soft volumetric clouds near the bottom and edges, the center left clear and open. "
       "Absolutely no grass, no ground, no playground, no slide, no seesaw, no butterfly, no people, no animals, no objects, no characters, no text.")
CLOUD = ("Make a single solid square cloud wall block for a platform game: a chunky dense cube of packed white cumulus with flat top and flat sides, firm and solid like a stone block made of cloud, slight blue shading underneath, "
         "same 3D feature-film CGI look, filling most of the frame, centered on a perfectly flat solid magenta (#FF00FF) background. No text, no face.")
if "sky" in sys.argv: r = (Image.open(D/"image_plate.png").convert("RGB").save("/tmp/plate_in.png"), mc.image_edit(pathlib.Path("/tmp/plate_in.png"), SKY, dry=False))[1]; save(r, D/"image_plate_sky.png"); print("sky", r.get("http_status"))
if "cloud" in sys.argv:
    r = (Image.open(S/"cloud_block_crop.png").convert("RGB").save("/tmp/cb_in.png"), mc.image_edit(pathlib.Path("/tmp/cb_in.png"), CLOUD, dry=False))[1]; save(r, S/"cloud_block_raw.png"); print("cloud", r.get("http_status"))
    import numpy as np; a = np.asarray(Image.open(S/"cloud_block_raw.png").convert("RGB")).astype(int); m = np.minimum(a[...,0], a[...,2]) - a[...,1]
    al = np.clip(255 - (m - 40) * 3, 0, 255); im = Image.fromarray(np.dstack([a, al]).astype("uint8"), "RGBA"); im.crop(im.getbbox()).save(S/"cloud_block_3d.png"); print(im.getbbox())
