#!/usr/bin/env python3
"""Generate SYNTHETIC kid-style samples (no real children). Idempotent: rewrites samples/synthetic_0N/{drawing.png,voice.wav,transcript.txt}."""
import pathlib, wave, struct, math
from PIL import Image, ImageDraw
ROOT = pathlib.Path(__file__).resolve().parents[1]
S = [("synthetic_01", "El gato tiene que llegar a la casa, no puede tocar el agua", "cat_house_river"),
     ("synthetic_02", "El perro busca el hueso y no puede tocar el fuego", "dog_bone_fire_FLAWband"),
     ("synthetic_03", "La nave llega a la estrella esquivando las piedras", "ship_star_rocks"),
     ("synthetic_04", "El gato quiere el hueso pero hay fuego", "cat_bone_fire_FLAWspawn"),
     ("synthetic_05", "El perro va a la casa y hay agua en el medio", "dog_house_river"),
     ("synthetic_06", "La nave busca la casa", "ship_house_none"),
     ("synthetic_07", "el gatito corre a la estrellita", "fuzzy_no_keywords"),
     ("synthetic_08", "El perro tiene que llegar a la estrella sin tocar las piedras", "dog_star_rocks_FLAWseal"),
     ("synthetic_09", "Un dragon vuela al castillo", "unknown_nouns"),
     ("synthetic_10", "El gato va a la casa sin tocar el agua y hay un fantasma que camina por abajo", "cat_house_river_FOEpatrol"),
     ("synthetic_11", "La nave busca la estrella esquivando las piedras pero un monstruo la cuida", "ship_star_rocks_FOEguard")]
VIOLET = (140, 0, 200)  # dedicated enemy ink read by generate_from_drawing.read_enemies
HZC = {"river": "blue", "fire": "red", "rocks": "gray"}
def draw(kind, f):
    """Kid-style drawing. ~1/3 of samples carry a realistic first-try flaw that the pixel-reading generator
    turns into an UNWINNABLE spec: FLAWband (hazard reaches the bottom edge), FLAWspawn (puddle under the player),
    FLAWseal (brown walls fully enclose the goal). The mock patcher can fix all three."""
    im = Image.new("RGB", (640, 480), "white"); d = ImageDraw.Draw(im)
    kind, _, foe = kind.partition("_FOE"); base, _, flaw = kind.partition("_FLAW"); hz = HZC.get(base.rsplit("_", 1)[-1])
    if hz:
        d.line((300, 0, 320, 480 if flaw == "band" else 340), fill=hz, width=30)   # hazard band (gap at bottom unless FLAWband)
        if flaw == "spawn": d.rectangle((0, 0, 159, 159), fill=hz)               # puddle drawn under the player
    if flaw == "seal":
        for cx in range(13, 16):
            for cy in range(9, 12):
                if (cx, cy) != (14, 10): d.rectangle((cx*40, cy*40, cx*40+39, cy*40+39), fill="saddlebrown")
    if foe == "patrol":  # ghost body at cell (5,10) + violet trail along row 10 under the river gap (winnable with timing)
        d.line((220, 420, 460, 420), fill=VIOLET, width=10); d.ellipse((205, 405, 235, 435), fill=VIOLET)
    if foe == "guard":   # FLAW: kid draws the monster ON the star (single violet blob, no trail = it never moves) -> UNWINNABLE
        d.ellipse((563, 403, 597, 437), fill=VIOLET)
    d.ellipse((40, 40, 110, 110), outline="black", width=4)            # player (top-left)
    d.rectangle((540, 380, 610, 450), outline="black", width=4)        # goal (bottom-right)
    d.text((10, 466), f"SYNTHETIC {kind}", fill="black"); im.save(f)
def tone(f, secs=1.0, hz=440, sr=16000):
    with wave.open(str(f), "w") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes(b"".join(struct.pack("<h", int(3000 * math.sin(2 * math.pi * hz * i / sr))) for i in range(int(sr * secs))))
for sid, tr, kind in S:
    d = ROOT / "samples" / sid; d.mkdir(parents=True, exist_ok=True)
    draw(kind, d / "drawing.png"); tone(d / "voice.wav"); (d / "transcript.txt").write_text(tr + "\n")
    print("wrote", d.relative_to(ROOT))
