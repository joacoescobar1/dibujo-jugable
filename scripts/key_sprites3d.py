#!/usr/bin/env python3
"""Magenta chroma-key for Muse Image 3D sprites: evidence/sprites3d/<role>_raw.png -> <role>_3d.png (transparent, cropped). Offline, $0."""
import pathlib
from PIL import Image
import numpy as np
D = pathlib.Path(__file__).resolve().parents[1] / "evidence/sprites3d"
for r in ["player", "wall", "goal", "enemy"]:
    a = np.asarray(Image.open(D / f"{r}_raw.png").convert("RGB")).astype(int); R, G, B = a[..., 0], a[..., 1], a[..., 2]
    m = np.minimum(R, B) - G  # magenta-ness
    al = np.clip(255 - (m - 40) * 3, 0, 255)
    rgb = a.copy(); sp = (m > 10) & (al > 0) & (al < 255); rgb[..., 0] = np.where(sp, np.minimum(R, G + 30), R); rgb[..., 2] = np.where(sp, np.minimum(B, G + 30), B)
    im = Image.fromarray(np.dstack([rgb, al]).astype("uint8"), "RGBA"); im = im.crop(im.getbbox()); im.save(D / f"{r}_3d.png"); print(r, im.size)
