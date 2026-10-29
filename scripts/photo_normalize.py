#!/usr/bin/env python3
"""normalize_photo(): make a REAL phone photo of a pen/ballpoint drawing look like the clean scan the offline colour
vision expects (pure Pillow, deterministic, offline). Steps, each gated so a clean digital image passes through untouched:
  1. Paper finder + deskew + crop: paper = low-saturation pixels above an Otsu brightness threshold; the rotation in
     [-7, 7] deg that minimises the paper's projection-profile bounding box is undone, then the image is cropped to the
     sheet (table/background margin removed). Skipped when the sheet already fills the frame and is not rotated.
  2. Flat-field: background (paper colour + light + shadow) = per-channel morphological CLOSING (max then min, radius
     ~1/4 of the long side, so filled crayon areas up to that size count as ink, not paper) on a 4x-reduced copy, blurred
     and upsampled; out = in * 255 / background. Removes yellow tint, lighting gradients and soft shadows. A clean
     white image has background == 255 everywhere -> identity.
  3. Photo-only clean-up: 3x3 median denoise, pen-line rims snapped to black (see snap_dark_edges), 2px sheet border
     painted white.
  1b. Keystone: after deskew, the 4 sheet edges are fitted as lines (robust LSQ on first/last paper pixel per
     row/column); if any edge leans > max(3px, 0.8%) the quad is warped to a rectangle (perspective transform).
     Rotation-only photos fall below the gate and keep the plain crop.
Returns (image, info). info["photo"] False means the input object was returned as-is (byte-identical downstream)."""
import math
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageMath
def _otsu(hist):
    tot = sum(hist); sm = sum(i * h for i, h in enumerate(hist)); wb = sb = 0; best, t = -1, 128
    for i, h in enumerate(hist):
        wb += h
        if not wb or wb == tot: continue
        sb += i * h; mb, mf = sb / wb, (sm - sb) / (tot - wb); v = wb * (tot - wb) * (mb - mf) ** 2
        if v > best: best, t = v, i
    return t
def paper_mask(im, hull=True):
    hsv = im.convert("HSV"); _, s, v = hsv.split()
    low_s = s.point(lambda x: 255 if x < 90 else 0)
    t = _otsu(v.histogram(mask=low_s))
    m = ImageChops.multiply(low_s, v.point(lambda x: 255 if x > t else 0))
    m = m.filter(ImageFilter.MedianFilter(5)); return _hull_fill(m) if hull else m
def _hull_fill(m):
    """A sheet of paper is convex: fill the convex hull of the mask. Closes ink holes and, above all, a deep hand/phone
    shadow that drops a corner of the sheet under the global Otsu threshold (it used to bite the corner off, so the
    deskew angle and crop came out wrong). Hull from the first/last white pixel of each row (monotone chain)."""
    w, h = m.size; buf = m.point(lambda v: 255 if v > 127 else 0).tobytes(); ff = b"\xff"; pts = []
    for y in range(h):
        row = buf[y * w:(y + 1) * w]; a = row.find(ff)
        if a >= 0: pts += [(a, y), (row.rfind(ff), y)]
    if len(pts) < 6: return m
    pts = sorted(set(pts)); cross = lambda o, a, b: (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lo, hi = [], []
    for p in pts:
        while len(lo) >= 2 and cross(lo[-2], lo[-1], p) <= 0: lo.pop()
        lo.append(p)
    for p in reversed(pts):
        while len(hi) >= 2 and cross(hi[-2], hi[-1], p) <= 0: hi.pop()
        hi.append(p)
    out = Image.new("L", m.size, 0); ImageDraw.Draw(out).polygon(lo[:-1] + hi[:-1], fill=255, outline=255); return out
EDGE = 2  # px of sheet/table blend painted paper-white after the crop (thinner than one sampling step)
def _span(profile, frac=0.5):
    """first/last index whose fill >= frac * max (sub-pixel ends via linear interpolation of the crossing)."""
    mx = max(profile) or 1; th = frac * mx; idx = [i for i, p in enumerate(profile) if p >= th]
    if not idx: return 0.0, float(len(profile))
    a, b = idx[0], idx[-1]
    fa = a - (profile[a] - th) / (profile[a] - profile[a - 1]) if a > 0 and profile[a] > profile[a - 1] else float(a)
    fb = b + (profile[b] - th) / (profile[b] - profile[b + 1]) if b + 1 < len(profile) and profile[b] > profile[b + 1] else float(b)
    return max(0.0, fa + 0.5), min(float(len(profile)), fb + 0.5)
def _bbox(mask):
    w, h = mask.size
    rows = _flat(mask.resize((1, h), Image.BOX)); cols = _flat(mask.resize((w, 1), Image.BOX))
    (y0, y1), (x0, x1) = _span(rows), _span(cols); return x0, y0, x1, y1
def _flat(im): return list(im.get_flattened_data()) if hasattr(im, "get_flattened_data") else list(im.getdata())
def _sharpness(mask):
    """Projection-profile edge energy: sum of squared steps of the row and column fill profiles. Peaks when the sheet's
    edges (and the ink drawn parallel to them) are axis-aligned."""
    w, h = mask.size; e = 0.0
    for prof in (_flat(mask.resize((1, h), Image.BOX)), _flat(mask.resize((w, 1), Image.BOX))):
        e += sum((a - b) ** 2 for a, b in zip(prof, prof[1:])) / 255.0 ** 2
    return e
def find_sheet(im):
    """-> (angle_deg, (x0,y0,x1,y1) as fractions of the frame rotated by angle with expand=True).
    The mask gets a 2px black border so a sheet that fills the frame still has sharp outer edges at 0 deg."""
    sm = im.copy(); sm.thumbnail((400, 400), Image.BOX); m = paper_mask(sm)
    pad = Image.new("L", (m.width + 4, m.height + 4), 0); pad.paste(m, (2, 2))
    score = lambda a: (-_sharpness(pad.rotate(a, resample=Image.BILINEAR, expand=True)), abs(a), a)
    best = min(score(a / 2) for a in range(-14, 15))[2]
    best = min(score(best + d / 20) for d in range(-10, 11))[2]
    big = im.copy(); big.thumbnail((900, 900), Image.BOX); mb = paper_mask(big)  # final 0.01 deg pass at higher resolution
    padb = Image.new("L", (mb.width + 4, mb.height + 4), 0); padb.paste(mb, (2, 2))
    best = min((-_sharpness(padb.rotate(best + d / 100, resample=Image.BILINEAR, expand=True)), abs(best + d / 100), best + d / 100) for d in range(-5, 6))[2]
    r = m.rotate(best, resample=Image.NEAREST, expand=True); W, H = r.size; x0, y0, x1, y1 = _bbox(r)
    return best, (x0 / W, y0 / H, x1 / W, y1 / H)
def homography(src, dst):
    """8 coeffs (a..h) of the projective map src[i] -> dst[i] (4 point pairs), Pillow PERSPECTIVE order. Pillow maps
    OUTPUT -> INPUT, so pass src = output corners, dst = input corners. Plain Gauss-Jordan, no numpy."""
    A = []
    for (x, y), (u, v) in zip(src, dst):
        A.append([x, y, 1, 0, 0, 0, -u * x, -u * y, u]); A.append([0, 0, 0, x, y, 1, -v * x, -v * y, v])
    for c in range(8):
        p = max(range(c, 8), key=lambda r: abs(A[r][c])); A[c], A[p] = A[p], A[c]
        for r in range(8):
            if r != c and A[r][c]:
                f = A[r][c] / A[c][c]; A[r] = [a - f * b for a, b in zip(A[r], A[c])]
    return [A[i][8] / A[i][i] for i in range(8)]
def _fit(pts):
    """robust line q = a*t + b over (t, q): deterministic consensus over point pairs (one from each half, 24x24 grid)
    keeps the line with most points within 2px, then least squares on those inliers. Ink touching the sheet edge
    (a crayon block in a corner can cover a third of a side) pulls those rows inward; consensus ignores them.
    -> (a, b, inlier fraction)."""
    def ls(ps):
        n = len(ps); st = sum(t for t, _ in ps); sq = sum(q for _, q in ps); stt = sum(t * t for t, _ in ps); stq = sum(t * q for t, q in ps)
        d = n * stt - st * st or 1e-9; a = (n * stq - st * sq) / d; return a, (sq - a * st) / n
    n = len(pts); h = n // 2; A, B = pts[:h], pts[h:]; best = (-1, 0.0, 0.0)
    for i in range(0, len(A), max(1, len(A) // 24)):
        for j in range(0, len(B), max(1, len(B) // 24)):
            (t1, q1), (t2, q2) = A[i], B[j]
            if t2 == t1: continue
            a = (q2 - q1) / (t2 - t1); b = q1 - a * t1; c = sum(abs(q - a * t - b) <= 2.0 for t, q in pts)
            if c > best[0]: best = (c, a, b)
    _, a, b = best; inl = [(t, q) for t, q in pts if abs(q - a * t - b) <= 2.0]
    a, b = ls(inl); return a, b, len(inl) / n
def find_quad(mask, box):
    """Sheet edges as 4 lines fitted to the first/last paper pixel of each row/column inside the inner 80% of box.
    -> (corners TL,TR,BR,BL, max edge deviation from axis-aligned in px)."""
    w, h = mask.size; x0, y0, x1, y1 = box; m = mask.point(lambda v: 255 if v > 127 else 0)
    rows = m.tobytes(); cols = m.transpose(Image.TRANSPOSE).tobytes(); ff = b"\xff"
    def edges(buf, stride, lo, hi, a, b):
        L, R = [], []
        for i in range(int(lo), int(hi)):
            line = buf[i * stride + int(a): i * stride + int(b)]; f = line.find(ff)
            if f >= 0: L.append((i, a // 1 + f)); R.append((i, a // 1 + line.rfind(ff) + 1))
        return L, R
    iy0, iy1 = y0 + 0.1 * (y1 - y0), y1 - 0.1 * (y1 - y0); ix0, ix1 = x0 + 0.1 * (x1 - x0), x1 - 0.1 * (x1 - x0)
    lft, rgt = edges(rows, w, iy0, iy1, 0, w); top, bot = edges(cols, h, ix0, ix1, 0, h)
    if min(len(lft), len(top)) < 16: return None, 0.0
    (al, bl, fl), (ar, br, fr), (at, bt, ft), (ab, bb, fb) = map(_fit, (lft, rgt, top, bot))
    if min(fl, fr, ft, fb) < 0.4: return None, 0.0  # an edge mostly covered by ink: no trustworthy quad, keep plain crop
    def meet(av, bv, ah, bh):  # x = av*y + bv  and  y = ah*x + bh
        x = (av * bh + bv) / (1 - av * ah); return (x, ah * x + bh)
    quad = [meet(al, bl, at, bt), meet(ar, br, at, bt), meet(ar, br, ab, bb), meet(al, bl, ab, bb)]
    dev = max(max(abs(al), abs(ar)) * (y1 - y0), max(abs(at), abs(ab)) * (x1 - x0))
    return quad, dev
def flat_field_bg(im):
    f = max(1, round(max(im.size) / 160)); s = im.reduce(f) if f > 1 else im.copy(); r = max(2, math.ceil(max(s.size) / 4))
    for _ in range(r): s = s.filter(ImageFilter.MaxFilter(3))
    for _ in range(r): s = s.filter(ImageFilter.MinFilter(3))
    s = s.filter(ImageFilter.GaussianBlur(2))
    return s.resize(im.size, Image.BILINEAR)
def snap_dark_edges(im):
    """Blur + JPEG turn the rim of a black pen line into mid-grey pixels, which the colour vision reads as grey 'Piedras'.
    Photo-only: a low-saturation mid-tone pixel (lum 85-180) with near-black ink (lum < 70) within 2px is part of that
    line -> painted black. Filled grey crayon areas have no black core next to them, so they are kept."""
    _, s, _ = im.convert("HSV").split(); L = im.convert("L")
    near_black = L.filter(ImageFilter.MinFilter(5)).point(lambda v: 255 if v < 70 else 0)
    mid = ImageChops.multiply(L.point(lambda v: 255 if 85 <= v <= 180 else 0), s.point(lambda v: 255 if v < 60 else 0))
    return Image.composite(Image.new("RGB", im.size, (0, 0, 0)), im, ImageChops.multiply(near_black, mid))
def normalize_photo(im, perspective=True):
    im = im.convert("RGB"); info = {"photo": False}; out = im
    angle, (fx0, fy0, fx1, fy1) = find_sheet(im)
    margin = max(fx0, fy0, 1 - fx1, 1 - fy1)
    if abs(angle) >= 0.5 or margin > 0.015:
        r = im.rotate(angle, resample=Image.BICUBIC, expand=True, fillcolor=(0, 0, 0)) if abs(angle) >= 0.5 else im
        # refine the crop at full resolution on the deskewed frame; sub-pixel box so the grid registers to the sheet
        pm = paper_mask(r); x0, y0, x1, y1 = _bbox(pm)
        quad, dev = find_quad(paper_mask(r, hull=False), (x0, y0, x1, y1)) if perspective else (None, 0.0)
        if quad and dev > max(3.0, 0.008 * max(x1 - x0, y1 - y0)):
            # keystone (phone not parallel to the sheet): warp the fitted quad to a rectangle of its mean side lengths
            (a, b, c, d) = quad; dist = lambda p, q: math.hypot(p[0] - q[0], p[1] - q[1])
            W, H = round((dist(a, b) + dist(d, c)) / 2), round((dist(a, d) + dist(b, c)) / 2)
            out = r.transform((W, H), Image.PERSPECTIVE, homography([(0, 0), (W, 0), (W, H), (0, H)], quad), Image.BICUBIC, fillcolor=(255, 255, 255))
            info.update(perspective=[[round(v, 1) for v in p] for p in quad], keystone_px=round(dev, 1))
        else:
            out = r.resize((round(x1 - x0), round(y1 - y0)), Image.BICUBIC, box=(x0, y0, x1, y1))
        info.update(photo=True, angle=round(angle, 2), crop=[round(v) for v in (x0, y0, x1, y1)], frame=list(r.size))
    bg = flat_field_bg(out)
    lo = min(b[0] for b in bg.getextrema())
    if lo < 250 or info["photo"]:
        bands = [ImageMath.lambda_eval(lambda e: e["a"] * 255.0 / (e["b"] + 0.5), a=a, b=b).convert("L") for a, b in zip(out.split(), bg.split())]
        out = snap_dark_edges(Image.merge("RGB", bands).filter(ImageFilter.MedianFilter(3)))
        if "crop" in info: ImageDraw.Draw(out).rectangle((0, 0, out.width - 1, out.height - 1), outline=(255, 255, 255), width=EDGE)
        info.update(photo=True, bg_min=lo)
    return (out if info["photo"] else im), info
if __name__ == "__main__":
    import sys
    o, inf = normalize_photo(Image.open(sys.argv[1])); print(inf)
    if len(sys.argv) > 2: o.save(sys.argv[2])
