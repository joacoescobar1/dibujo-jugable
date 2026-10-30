#!/usr/bin/env python3
"""Offline Fish Home pages from the Khamkhoune village drawing.

Does not call generate_from_drawing, Meta, or Baseten. Specs are hand-authored.
The kid photo is the plate and the original-drawing panel. Solver path comes from
agent/playtest.solve and is not edited here.
"""
import base64, io, json, shutil, sys, pathlib
from PIL import Image, ImageDraw

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "agent"))
from playtest import solve, playtest

SRC = ROOT / "samples/kid_drawings/kid_02.jpg"
HOME = ROOT / "samples/kid_02"
WORLD = HOME / "worlds/v1"
ART = HOME / "art"
TRANSCRIPT = (
    "Los pececitos se salieron del estanque. Juntá los peces y llevalos a casa, "
    "después subí hasta la puerta de la casa roja."
)
CREDIT = {
    "en": "Drawing by Khamkhoune, age 11 — CC BY-SA 4.0",
    "es": "Dibujo de Khamkhoune, 11 años — CC BY-SA 4.0",
}
INTRO = {
    1: "Los pececitos se salieron del estanque. Juntá cada pez y caminá hasta la puerta.",
    2: "Subí por el muelle y las cercas. Juntá los peces y llegá a la puerta de arriba.",
    3: "La casa roja ya se ve desde el muelle. Juntá los últimos peces y entrá por la puerta.",
}
TITLE = {
    1: "Los peces del estanque",
    2: "Subí por el muelle",
    3: "La puerta de la casa roja",
}
SPARK = {"x": 10, "y": 1, "id": "spark_roof", "level": 3}
SLOW = [[1, 0], [0, 0], [0, 0], [-1, 0], [0, 0], [0, 0]]


def wall_row(y, xs):
    """Merge a row of blocked x cells into horizontal wall rects."""
    xs = sorted(xs)
    out, start, prev = [], None, None
    for x in xs:
        if start is None:
            start = prev = x
        elif x == prev + 1:
            prev = x
        else:
            out.append({"x": start, "y": y, "w": prev - start + 1, "h": 1})
            start = prev = x
    if start is not None:
        out.append({"x": start, "y": y, "w": prev - start + 1, "h": 1})
    return out


def water_row(y, xs, prefix):
    rects = wall_row(y, xs)
    out = []
    for i, r in enumerate(rects):
        out.append({**r, "id": "%s_%d" % (prefix, i), "label": "Agua", "effect": "lose"})
    return out


def fish(pairs):
    return [{"id": "pez_%d" % (i + 1), "label": "Pez", "x": x, "y": y} for i, (x, y) in enumerate(pairs)]


def base(title, intro, player, door, goals, walls, hazards, car):
    return {
        "title": title,
        "title_es": title,
        "genre": "top-down",
        "grid": {"w": 12, "h": 10, "tile": 40},
        "player": {"id": "rayo", "label": "Rayito de sol", "x": player[0], "y": player[1]},
        "goals": goals,
        "characters": [{
            "id": "auto", "label": "Auto negro", "x": car[0], "y": car[1],
            "role": "enemy", "patrol": car[2],
        }],
        "walls": walls,
        "hazards": hazards,
        "door": {"id": door[2], "label": door[3], "x": door[0], "y": door[1]},
        "win_condition": {"type": "collect_all"},
        "intro": intro,
        "rules_text": ["Pick up every fish, then step through the door. Stay off the pond."],
    }


def scenes():
    s1 = base(
        TITLE[1], INTRO[1], (1, 8), (1, 1, "puerta_muelle", "Puerta del muelle"),
        fish([(3, 7), (8, 7), (4, 3), (10, 3)]),
        wall_row(2, [6, 7, 8]) + wall_row(3, [0, 1]),
        water_row(5, [0, 2, 3, 4, 6, 7, 8, 10, 11], "agua"),
        (11, 9, [[-1, 0], [0, 0], [0, 0], [1, 0], [0, 0], [0, 0]]),
    )
    s2 = base(
        TITLE[2], INTRO[2], (1, 8), (2, 1, "puerta_muelle", "Puerta del muelle"),
        fish([(1, 6), (8, 5), (3, 3), (9, 1)]),
        wall_row(7, range(3, 12)) + wall_row(4, range(0, 8)) + wall_row(2, range(5, 12)),
        water_row(8, [10, 11], "charco"),
        (0, 9, SLOW),
    )
    s3 = base(
        TITLE[3], INTRO[3], (2, 8), (2, 1, "puerta_roja", "Puerta de la casa roja"),
        fish([(1, 6), (7, 4), (4, 3)]),
        wall_row(7, [0] + list(range(3, 12)))
        + wall_row(5, list(range(0, 6)) + list(range(8, 12)))
        + wall_row(2, [0] + list(range(3, 9)) + [11])
        + wall_row(1, range(4, 9)),
        water_row(8, [10, 11], "charco"),
        (8, 9, SLOW),
    )
    return {1: s1, 2: s2, 3: s3}


def occupied(spec):
    cells = set()
    def add(r):
        for x in range(r["x"], r["x"] + r.get("w", 1)):
            for y in range(r["y"], r["y"] + r.get("h", 1)):
                cells.add((x, y))
    for r in spec.get("walls", []) + spec.get("hazards", []):
        add(r)
    return cells


def path_cells(spec, path):
    W, H = spec["grid"]["w"], spec["grid"]["h"]
    block = occupied(spec)
    x, y = spec["player"]["x"], spec["player"]["y"]
    seen = {(x, y)}
    for dx, dy in path:
        nx, ny = x + dx, y + dy
        if 0 <= nx < W and 0 <= ny < H and (nx, ny) not in block:
            x, y = nx, ny
        seen.add((x, y))
    return seen


def reachable(spec, goal):
    W, H = spec["grid"]["w"], spec["grid"]["h"]
    block = occupied(spec)
    start = (spec["player"]["x"], spec["player"]["y"])
    if goal in block:
        return False
    q, seen = [start], {start}
    while q:
        x, y = q.pop()
        if (x, y) == goal:
            return True
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (x + dx, y + dy)
            if n in seen or not (0 <= n[0] < W and 0 <= n[1] < H) or n in block:
                continue
            seen.add(n)
            q.append(n)
    return False


def prove(specs):
    bad = False
    for n, spec in specs.items():
        r = playtest(spec)
        print("scene", n, "winnable", r["winnable"], "steps", r["steps"], "bugs", r["bugs"])
        if not r["winnable"]:
            bad = True
            continue
        if n == 3:
            walked = path_cells(spec, r["path"])
            cell = (SPARK["x"], SPARK["y"])
            door = (spec["door"]["x"], spec["door"]["y"])
            goals = {(g["x"], g["y"]) for g in spec["goals"]}
            print("spark on path", cell in walked, "reachable", reachable(spec, cell))
            if cell in walked or cell in goals or cell == door or not reachable(spec, cell):
                print("spark placement bad", cell)
                bad = True
            if any(c == door for c in goals):
                bad = True
    return not bad


def b64_png(im, mx=None):
    im = im.convert("RGBA")
    if mx:
        im.thumbnail((mx, mx))
    buf = io.BytesIO()
    im.save(buf, "PNG", optimize=True)
    return base64.b64encode(buf.getvalue()).decode()


def sprite_sun():
    im = Image.new("RGBA", (128, 128), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    cx = cy = 64
    for i in range(12):
        import math
        a = i * math.pi / 6
        x2, y2 = cx + math.cos(a) * 58, cy + math.sin(a) * 58
        d.line((cx, cy, x2, y2), fill=(255, 179, 0, 255), width=10)
    d.ellipse((30, 30, 98, 98), fill=(255, 224, 64, 255))
    d.ellipse((46, 44, 70, 66), fill=(255, 249, 196, 255))
    return im


def sprite_fish():
    im = Image.new("RGBA", (128, 128), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.polygon([(18, 64), (46, 36), (46, 92)], fill=(255, 112, 67, 255))
    d.ellipse((40, 34, 112, 94), fill=(255, 152, 0, 255))
    d.ellipse((78, 50, 96, 68), fill=(255, 255, 255, 255))
    d.ellipse((86, 56, 94, 64), fill=(33, 33, 33, 255))
    return im


def sprite_car():
    im = Image.new("RGBA", (128, 128), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((16, 48, 112, 92), radius=16, fill=(33, 33, 33, 255))
    d.rounded_rectangle((36, 28, 92, 58), radius=12, fill=(55, 55, 55, 255))
    d.rectangle((44, 36, 84, 54), fill=(144, 202, 249, 255))
    d.ellipse((24, 78, 48, 102), fill=(20, 20, 20, 255))
    d.ellipse((80, 78, 104, 102), fill=(20, 20, 20, 255))
    return im


def sprite_door():
    im = Image.new("RGBA", (128, 128), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.polygon([(8, 48), (64, 8), (120, 48)], fill=(198, 40, 40, 255))
    d.rectangle((20, 46, 108, 118), fill=(183, 28, 28, 255))
    d.rounded_rectangle((50, 68, 78, 116), radius=6, fill=(255, 213, 79, 255))
    d.ellipse((70, 88, 76, 94), fill=(93, 64, 55, 255))
    return im


def sprite_wall():
    im = Image.new("RGBA", (128, 128), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rectangle((8, 8, 120, 120), fill=(141, 110, 99, 255))
    d.rectangle((18, 18, 34, 110), fill=(109, 76, 65, 255))
    d.rectangle((58, 18, 74, 110), fill=(109, 76, 65, 255))
    d.rectangle((96, 18, 112, 110), fill=(109, 76, 65, 255))
    return im


def thumb(src):
    im = Image.open(src).convert("RGB")
    # cover-crop toward the pond and houses
    w, h = im.size
    target = 4 / 3
    if w / h > target:
        nw = int(h * target)
        left = (w - nw) // 2
        im = im.crop((left, 0, left + nw, h))
    else:
        nh = int(w / target)
        top = max(0, (h - nh) // 5)
        im = im.crop((0, top, w, min(h, top + nh)))
    im = im.resize((640, 480), Image.Resampling.LANCZOS)
    out = ROOT / "game/thumb_fishhome.jpg"
    im.save(out, "JPEG", quality=82, optimize=True)
    return out


def write_pages(specs, art, plate_b64, drawing_b64, photo_src):
    tpl = (ROOT / "game/demo.template.html").read_text()
    pages = {
        1: ("w_fishhome.html", "w_fishhome_2.html"),
        2: ("w_fishhome_2.html", "w_fishhome_3.html"),
        3: ("w_fishhome_3.html", ""),
    }
    for n, spec in specs.items():
        solved = playtest(spec)
        name, nxt = pages[n]
        it = {
            "spec": spec,
            "solver": {"winnable": True, "steps": solved["steps"], "bugs": []},
            "path": solved["path"],
            "fail_path": None,
            "voice_rule": [],
            "marks": [],
            "shot": None,
            "browser": None,
            "outcome": "WIN",
        }
        B = {
            "sample": "samples/kid_02",
            "transcript": TRANSCRIPT,
            "drawing_b64": drawing_b64,
            "photo_src": photo_src,
            "title_b64": plate_b64,
            "plate_b64": plate_b64,
            "plate_empty": True,
            "art3d": False,
            "art": art,
            "run": "offline/fishhome",
            "result": "WIN",
            "iters": [it],
            "episode": [{"iter": 0, "outcome": "WIN", "bugs": [], "patch_summary": ""}],
            "live_meta_calls": 0,
            "enemy_bodies": [[spec["characters"][0]["x"], spec["characters"][0]["y"]]],
            "gates": [],
            "scene_intro": spec["intro"],
            "play": {"level": n, "total": 3, "next": nxt, "scene": spec["title"]},
            "credit": CREDIT,
        }
        if n == 3:
            B["spark"] = SPARK
        raw = json.dumps(B, ensure_ascii=False).replace("</", "<\\/")
        out = ROOT / "game" / name
        out.write_text(tpl.replace("/*__BUNDLE__*/null", raw))
        print("wrote", out.relative_to(ROOT), "steps", solved["steps"])


def main():
    if not SRC.exists():
        sys.exit("missing " + str(SRC))
    HOME.mkdir(parents=True, exist_ok=True)
    WORLD.mkdir(parents=True, exist_ok=True)
    ART.mkdir(parents=True, exist_ok=True)
    drawing = HOME / "drawing.jpg"
    shutil.copyfile(SRC, drawing)
    (HOME / "transcript.txt").write_text(TRANSCRIPT + "\n")
    specs = scenes()
    if not prove(specs):
        sys.exit("Fish Home is not solver-green")
    for n, spec in specs.items():
        (WORLD / ("scene_%d.json" % n)).write_text(json.dumps(spec, ensure_ascii=False, indent=2) + "\n")
    sprites = {
        "player": sprite_sun(),
        "goal": sprite_fish(),
        "enemy": sprite_car(),
        "door": sprite_door(),
        "wall": sprite_wall(),
    }
    art = {}
    rel = {}
    for role, im in sprites.items():
        p = ART / (role + ".png")
        im.save(p, "PNG")
        art[role] = b64_png(im, 256)
        rel[role] = str(p.relative_to(ROOT))
    photo = Image.open(drawing).convert("RGB")
    plate = photo.copy()
    plate.thumbnail((800, 800), Image.Resampling.LANCZOS)
    plate_path = HOME / "plate.png"
    plate.save(plate_path, "PNG", optimize=True)
    plate_b64 = b64_png(Image.open(plate_path))
    drawing_b64 = plate_b64
    photo_src = "data:image/jpeg;base64," + base64.b64encode(drawing.read_bytes()).decode()
    world = {
        "title": "Fish Home",
        "sample": "samples/kid_02",
        "start": "scene_1",
        "scenes": ["scene_1", "scene_2", "scene_3"],
        "ending": "scene_3",
        "solvable": ["win", "win", "win"],
        "credit": CREDIT,
        "license": "https://creativecommons.org/licenses/by-sa/4.0/",
        "art": {
            "door": rel["door"],
            "player": rel["player"],
            "scene_1": {"plate": str(plate_path.relative_to(ROOT))},
            "scene_2": {"plate": str(plate_path.relative_to(ROOT))},
            "scene_3": {"plate": str(plate_path.relative_to(ROOT))},
        },
    }
    (WORLD / "world.json").write_text(json.dumps(world, ensure_ascii=False, indent=2) + "\n")
    thumb(drawing)
    write_pages(specs, art, plate_b64, drawing_b64, photo_src)
    print("fish home offline build ok")


if __name__ == "__main__":
    main()
