#!/usr/bin/env python3
"""SYNTHETIC kid-style drawing with a wobbly pen hand (no real child): samples/synthetic_12/{drawing.png,voice.wav,transcript.txt}.
Same story and same first-try flaw as synthetic_11 (ship -> star, rock band, violet monster sitting ON the star = guard,
UNWINNABLE until the fixer moves it), but drawn the way a kid draws: shaky outlines that overshoot and don't close,
lumpy crayon fills with paper grain, a rocket with fins + flame, a 5-point star, a monster with legs and antennae,
doodles (sun, planet, little stars) that the reader ignores (black/yellow/light ink is not a game colour).
Deterministic (seed). Rendered at 3x then NEAREST-downscaled, so every pixel is a pure ink colour and no blended edge pixel can be
read as a game colour (e.g. black+light-blue -> dark blue = birome 'Agua'). Never rewrites synthetic_01..11."""
import math, pathlib, random, struct, wave
from PIL import Image, ImageDraw
ROOT = pathlib.Path(__file__).resolve().parents[1]; OUT = ROOT / "samples" / "synthetic_12"
TRANSCRIPT = "Mi nave tiene que llegar a la estrella sin tocar las piedras, pero hay un monstruo que la cuida"
K = 3  # supersampling
PAPER, BLACK, GRAY, VIOLET = (255, 255, 255), (30, 28, 34), (128, 128, 128), (140, 0, 200)
YELLOW, ORANGE, SKY, PINK = (255, 214, 40), (255, 150, 30), (140, 200, 255), (255, 170, 200)
R = random.Random(12)
def wobble(pts, amp=3.4, freq=3):
    """Low-frequency hand tremor along a polyline (px at 1x): each point shifted by a smooth noise of the arc length."""
    ph = [R.uniform(0, 6.28) for _ in range(4)]; out, s = [], 0.0
    for i, (x, y) in enumerate(pts):
        if i: s += math.dist(pts[i - 1], (x, y))
        n1 = math.sin(s / 23 * freq / 3 + ph[0]) + .5 * math.sin(s / 9 + ph[1]); n2 = math.sin(s / 27 + ph[2]) + .5 * math.sin(s / 11 + ph[3])
        out.append((x + amp * n1 * .7, y + amp * n2 * .7))
    return out
def dense(pts, closed=True, step=3):
    pts = list(pts) + ([pts[0]] if closed else []); out = []
    for a, b in zip(pts, pts[1:]):
        n = max(1, int(math.dist(a, b) / step)); out += [(a[0] + (b[0] - a[0]) * t / n, a[1] + (b[1] - a[1]) * t / n) for t in range(n)]
    return out + [pts[-1]]
def ellipse(cx, cy, rx, ry, n=40, lump=0.0, a0=0.0):
    ph = R.uniform(0, 6.28); return [(cx + rx * (1 + lump * math.sin(3 * a + ph)) * math.cos(a), cy + ry * (1 + lump * math.sin(3 * a + ph)) * math.sin(a))
                                     for a in (a0 + i / n * 2 * math.pi for i in range(n))]
def star_pts(cx, cy, R1, R2, rot=-math.pi / 2):
    return [(cx + (R1 if i % 2 == 0 else R2) * math.cos(rot + i * math.pi / 5), cy + (R1 if i % 2 == 0 else R2) * math.sin(rot + i * math.pi / 5)) for i in range(10)]
class Pad:
    def __init__(s): s.im = Image.new("RGB", (640 * K, 480 * K), PAPER); s.d = ImageDraw.Draw(s.im)
    def fill(s, pts, col, grain=0.12, spill=2.5, pitch=3.2):
        """Crayon colouring the way a kid does it: back-and-forth zigzag strokes (visible scribble, paper showing between
        strokes, a few skipped) clipped to the shape grown by `spill` px, so the colour goes a bit over the line."""
        m = Image.new("L", s.im.size, 0); md = ImageDraw.Draw(m); poly = [(x * K, y * K) for x, y in wobble(dense(pts), 1.2)]
        md.polygon(poly, fill=255); md.line(poly + poly[:1], fill=255, width=round(2 * spill * K))
        z = Image.new("L", s.im.size, 0); zd = ImageDraw.Draw(z); xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
        x0, x1, y0, y1 = min(xs) - 4, max(xs) + 4, min(ys) - 4, max(ys) + 4; ang = R.uniform(.5, 1.0); dx, dy = math.cos(ang), -math.sin(ang)
        L = math.hypot(x1 - x0, y1 - y0); cx, cy = (x0 + x1) / 2, (y0 + y1) / 2; zig = []; t = -L / 2; side = 1
        while t < L / 2:  # zigzag: strokes along (dx,dy), stepping perpendicular by ~pitch with jitter
            px, py = cx - dy * t, cy + dx * t; zig.append((px + dx * L / 2 * side, py + dy * L / 2 * side)); side = -side; t += pitch * R.uniform(.7, 1.3)
        for a, b in zip(zig, zig[1:]):
            if R.random() > grain: zd.line([(a[0] * K, a[1] * K), (b[0] * K, b[1] * K)], fill=255, width=round(R.uniform(3.4, 4.6) * K))
        from PIL import ImageChops
        s.im.paste(Image.new("RGB", s.im.size, col), (0, 0), ImageChops.multiply(m, z))
    def pen(s, pts, closed=True, w=3.2, col=BLACK, amp=2.2, overshoot=True):
        """Shaky pen stroke; closed shapes overshoot their start a bit (the line doesn't meet itself cleanly)."""
        p = dense(pts, closed)
        if closed and overshoot: p = p + p[1:max(2, len(p) // 9)]
        p = wobble(p, amp); s.d.line([(x * K, y * K) for x, y in p], fill=col, width=max(1, round(w * K)), joint="curve")
        r = w * K / 2
        for x, y in (p[0], p[-1]): s.d.ellipse((x * K - r, y * K - r, x * K + r, y * K + r), fill=col)
    def done(s):
        # NEAREST = every output pixel is one drawn ink sample: no blended edge (grey+white -> pink, black+sky -> birome blue)
        return s.im.resize((640, 480), Image.NEAREST)
def draw():
    P = Pad()
    # doodles first (ignored by the reader: black / yellow / light ink is not a game colour)
    P.fill(ellipse(185, 55, 26, 24, lump=.05), YELLOW); P.pen(ellipse(185, 55, 26, 24))                       # sun
    for a in range(0, 360, 40): r = math.radians(a + 8); P.pen([(185 + 33 * math.cos(r), 55 + 31 * math.sin(r)), (185 + R.uniform(42, 52) * math.cos(r), 55 + R.uniform(40, 48) * math.sin(r))], closed=False, w=2.6, overshoot=False)
    P.fill(ellipse(470, 150, 34, 34), PINK); P.pen(ellipse(470, 150, 34, 34))                                  # planet + ring
    P.pen(ellipse(470, 152, 58, 13, a0=.25)[3:18], closed=False, w=2.8, amp=1.4)
    for cx, cy, r_ in ((150, 260, 9), (420, 300, 7), (560, 70, 10), (110, 400, 8), (380, 430, 6), (520, 250, 7)):
        P.pen(star_pts(cx, cy, r_, r_ * .45), w=2.2, amp=.8)                                                    # little stars
    # rock band (Piedras): lumpy grey crayon rocks stacked down column 7-8, gap at the bottom like synthetic_11
    y = 6
    for i in range(8):
        cx = 308 + R.uniform(-5, 5); rx, ry = R.uniform(24, 29), R.uniform(22, 26); pts = ellipse(cx, y + ry, rx, ry, n=22, lump=.12)
        P.fill(pts, GRAY, grain=.08); P.pen(pts, w=2.8); y += ry * 1.55
    # the kid's rocket (player spawn cell 1,1): body, nose, window, fins, flame; slightly tilted, lines don't close
    tilt = math.radians(-12); cx0, cy0 = 60, 58
    rot = lambda pts: [(cx0 + (x - cx0) * math.cos(tilt) - (y - cy0) * math.sin(tilt), cy0 + (x - cx0) * math.sin(tilt) + (y - cy0) * math.cos(tilt)) for x, y in pts]
    body = rot([(48, 84), (47, 50), (52, 34), (60, 22), (68, 34), (73, 50), (72, 84)])
    P.fill(rot([(47, 64), (36, 86), (48, 82)]), ORANGE); P.fill(rot([(73, 64), (84, 86), (72, 82)]), ORANGE)
    P.fill(rot([(52, 86), (60, 104), (68, 86)]), ORANGE); P.fill(rot([(56, 86), (60, 97), (64, 86)]), YELLOW)
    P.pen(body); P.pen(rot([(47, 64), (36, 86), (48, 82)]), w=2.8); P.pen(rot([(73, 64), (84, 86), (72, 82)]), w=2.8)
    P.pen(rot([(52, 86), (60, 104), (68, 86)]), closed=False, w=2.6)
    P.fill(rot(ellipse(60, 52, 7, 7)), SKY); P.pen(rot(ellipse(60, 52, 7, 7)), w=2.6, amp=.8)
    # the star (goal cell 14,10): fat yellow 5-point star, outline overshoots
    st = star_pts(580, 420, 36, 16, rot=-math.pi / 2 + .12); P.fill(st, YELLOW, grain=.06); P.pen(st, w=3.2, amp=1.6)
    # the monster ON the star (flaw: guards the goal, never moves): violet lumpy body, legs, antennae, white eyes, teeth
    mb = ellipse(583, 420, 17, 15, n=26, lump=.14); P.fill(mb, VIOLET, grain=.05)
    for dx in (-9, 0, 9): P.pen([(583 + dx, 432), (583 + dx * 1.3, 438)], closed=False, w=3.4, col=VIOLET, amp=.5, overshoot=False)
    for dx in (-7, 7): P.pen([(583 + dx, 407), (583 + dx * 1.6, 399)], closed=False, w=2.6, col=VIOLET, amp=.5, overshoot=False)
    for dx in (-6, 6): P.d.ellipse(((583 + dx - 3.6) * K, (416 - 4) * K, (583 + dx + 3.6) * K, (416 + 4) * K), fill=PAPER); P.d.ellipse(((583 + dx - 1.4) * K, (417 - 1.6) * K, (583 + dx + 1.8) * K, (417 + 2) * K), fill=BLACK)
    P.pen([(575, 426), (579, 429), (583, 426), (587, 429), (591, 426)], closed=False, w=1.8, col=PAPER, amp=.3, overshoot=False)
    im = P.done(); ImageDraw.Draw(im).text((10, 466), "SYNTHETIC kid-style (no real child)", fill=BLACK); return im
def tone(f, secs=1.0, hz=440, sr=16000):
    with wave.open(str(f), "w") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes(b"".join(struct.pack("<h", int(3000 * math.sin(2 * math.pi * hz * i / sr))) for i in range(int(sr * secs))))
if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True); draw().save(OUT / "drawing.png"); tone(OUT / "voice.wav"); (OUT / "transcript.txt").write_text(TRANSCRIPT + "\n")
    print("wrote", OUT.relative_to(ROOT))
