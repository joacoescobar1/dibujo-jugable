#!/usr/bin/env python3
"""Deterministic 'phone photo' augmentation (pure Pillow, fixed seeds). Turns a clean synthetic drawing into what a
phone photo of a ballpoint drawing on paper looks like: yellowish paper, lighting gradient, soft cast shadow, slight
haze (ink not pure black), rotation +-5 deg, table margin around the sheet, optional upscale, gaussian-ish noise, JPEG q70.
Usage: photoize.py IN.png OUT.jpg [--seed N]   (used by tests/patcher/test_photo_robust.py)"""
import io, math, random, sys
from PIL import Image, ImageChops, ImageDraw, ImageFilter
TABLES = ((96, 70, 46), (72, 74, 80), (150, 120, 85))  # dark wood, grey desk, light wood
def _noise(size, sigma, rnd):
    """Irwin-Hall(4) of seeded uniform bytes ~ gaussian, centred 128, scaled to sigma. Deterministic (no C rand)."""
    w, h = size
    bands = [Image.frombytes("L", size, rnd.randbytes(w * h)) for _ in range(4)]
    m = ImageChops.add(ImageChops.add(bands[0], bands[1], scale=2.0), ImageChops.add(bands[2], bands[3], scale=2.0), scale=2.0)
    k = sigma / (255 / math.sqrt(12) / 2)
    return m.point(lambda v: max(0, min(255, round(128 + (v - 128) * k))))
def photoize(im, seed=0, scale=None, keystone=0.0):
    rnd = random.Random(seed); im = im.convert("RGB")
    angle = rnd.choice((-1, 1)) * rnd.uniform(1.5, 5.0)
    scale = scale if scale is not None else rnd.choice((1.0, 1.0, 1.6))
    tint = (rnd.uniform(0.97, 1.0), rnd.uniform(0.91, 0.96), rnd.uniform(0.74, 0.84))  # warm indoor light / yellowish paper
    table = TABLES[seed % len(TABLES)]
    if scale != 1.0: im = im.resize((round(im.width * scale), round(im.height * scale)), Image.BICUBIC)
    if keystone:  # phone tilted toward the top: top edge shrinks by keystone*w each side (no rnd use -> old seeds unchanged)
        from photo_normalize import homography
        w0, h0, k = im.width, im.height, keystone * im.width
        q = [(k, 0), (w0 - k, 0), (w0, h0), (0, h0)]
        im = im.transform((w0, h0), Image.PERSPECTIVE, homography(q, [(0, 0), (w0, 0), (w0, h0), (0, h0)]), Image.BICUBIC, fillcolor=table)
    im = im.rotate(angle, resample=Image.BICUBIC, expand=True, fillcolor=table)
    mx, my = rnd.randint(20, 70), rnd.randint(20, 70)
    canvas = Image.new("RGB", (im.width + 2 * mx, im.height + 2 * my), table); canvas.paste(im, (mx + rnd.randint(-10, 10), my + rnd.randint(-10, 10)))
    w, h = canvas.size
    D = math.ceil(math.hypot(w, h)); g = Image.linear_gradient("L").resize((D, D)).rotate(rnd.uniform(0, 360), resample=Image.BILINEAR)
    g = g.crop(((D - w) // 2, (D - h) // 2, (D - w) // 2 + w, (D - h) // 2 + h))  # lighting gradient, no corner fill
    lo = rnd.uniform(0.70, 0.80); light = g.point(lambda v: round(255 * (lo + (1 - lo) * v / 255)))
    sh = Image.new("L", (w, h), 255); d = ImageDraw.Draw(sh); cx, cy = rnd.choice(((0, 0), (w, 0), (0, h), (w, h)))
    r = rnd.uniform(0.35, 0.55) * max(w, h); d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=round(255 * rnd.uniform(0.62, 0.72)))  # hand/phone shadow
    sh = sh.filter(ImageFilter.GaussianBlur(radius=0.08 * max(w, h)))
    lum = ImageChops.multiply(light, sh)
    out = Image.merge("RGB", [ImageChops.multiply(b, lum.point(lambda v, t=t: round(v * t))) for b, t in zip(canvas.split(), tint)])
    haze = rnd.randint(6, 14); out = out.point(lambda v: round(haze + v * (255 - haze) / 255))  # ink never pure black
    out = Image.merge("RGB", [ImageChops.add(b, _noise((w, h), 6.0, rnd), scale=1.0, offset=-128) for b in out.split()])
    buf = io.BytesIO(); out.save(buf, "JPEG", quality=70); buf.seek(0)
    return Image.open(buf).convert("RGB"), {"seed": seed, "angle": round(angle, 2), "scale": scale, "margin": [mx, my], "tint": [round(t, 3) for t in tint], "table": table, "haze": haze, "keystone": keystone}
if __name__ == "__main__":
    seed = int(sys.argv[sys.argv.index("--seed") + 1]) if "--seed" in sys.argv else 0
    ph, info = photoize(Image.open(sys.argv[1]), seed); ph.save(sys.argv[2], quality=95); print(info)
