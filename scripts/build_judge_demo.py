#!/usr/bin/env python3
"""Judge demo builder (0 Meta spend). drawing+transcript -> generate_from_drawing (offline) -> patch_loop --patcher mock --browser
-> game/demo.html: self-contained page (drawing inlined as base64, data inlined; game.js reused) openable via file:// or http.server.
Usage: build_judge_demo.py [--sample samples/synthetic_12] [--no-browser] [--out game/demo.html]
Each iter carries the Python solver path (agent/playtest.solve, parity-checked vs game.js) so "ver al agente jugar" handles enemies/waits."""
import re, io, argparse, base64, json, pathlib, subprocess, sys
ROOT = pathlib.Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT / "agent"))
from playtest import solve
from browser_playtest import optimistic  # same plan the Chromium playtest walks when no path exists
PY = str(ROOT / ".venv/bin/python") if (ROOT / ".venv/bin/python").exists() else sys.executable
ap = argparse.ArgumentParser(); ap.add_argument("--sample", default="samples/synthetic_12"); ap.add_argument("--no-browser", action="store_true"); ap.add_argument("--run", help="replay an existing live patch_loop run dir (e.g. Muse) instead of offline gen+mock loop")
ap.add_argument("--out", default="game/demo.html", help="must live in game/ (page loads game.js relative)"); ap.add_argument("--scene", help="world scene json (samples/.../scenes/scene_N.json): final iter spec + per-scene art from world.json"); ap.add_argument("--play", help="player mode: LEVEL/TOTAL/NEXT_FILE/SCENE_NAME (e.g. 1/2/play_2.html/El patio)"); a = ap.parse_args()
sd = ROOT / a.sample; img = next(sd.glob("drawing.*")); tr = (sd / "transcript.txt").read_text().strip()
work = ROOT / "runs" / f"judge-{sd.name}"; work.mkdir(parents=True, exist_ok=True); gen = work / "spec.json"
if a.run: run = ROOT / a.run; gen = run / "iter_0.spec.json"
else:
    g = subprocess.run([PY, str(ROOT / "scripts/generate_from_drawing.py"), "--image", str(img), "--out", str(gen)], capture_output=True, text=True); print(g.stdout.strip())
    if g.returncode: sys.exit(g.stderr)
    cmd = [PY, str(ROOT / "agent/patch_loop.py"), "--spec", str(gen), "--patcher", "mock", "--max", "4"] + ([] if a.no_browser else ["--browser"])
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT); print(r.stdout.strip())
    run = ROOT / r.stdout.strip().splitlines()[-1].split()[1]
summ = json.loads((run / "summary.json").read_text())
iters = [json.loads((run / f"iter_{i}.json").read_text()) for i in range(len(summ["iterations"]))]
episode = [json.loads(l) for l in (run / "episode.jsonl").read_text().splitlines()]
# screenshots inlined as data: URIs so demo.html works on a fresh clone without runs/ (runs/ is gitignored)
shots = ["data:image/png;base64," + base64.b64encode((run / f"iter_{i}.png").read_bytes()).decode() if (run / f"iter_{i}.png").exists() else None for i in range(len(iters))]
# phone photo -> the game cuts sprites from the SAME deskewed/flat-fielded sheet the spec was read from (grid-aligned);
# the raw photo is kept only for the "🖍️ Dibujo" panel. Clean drawings pass through untouched (photo=False).
sys.path.insert(0, str(ROOT / "scripts")); from photo_normalize import normalize_photo; from PIL import Image; import io
sheet, pinfo = normalize_photo(Image.open(img)); buf = io.BytesIO(); sheet.save(buf, "PNG")
drawing_b64 = base64.b64encode(buf.getvalue() if pinfo["photo"] else img.read_bytes()).decode()
photo_src = f"data:image/{'png' if img.suffix.lower() == '.png' else 'jpeg'};base64," + base64.b64encode(img.read_bytes()).decode() if pinfo["photo"] else None
sys.path.insert(0, str(ROOT / "scripts")); from fix_marks import marks_per_iter
marks = marks_per_iter([it["spec"] for it in iters])
B = {"sample": a.sample, "transcript": tr, "drawing_b64": drawing_b64, "run": str(run.relative_to(ROOT)),
     "result": summ["result"], "iters": [{"spec": it["spec"], "voice_rule": __import__("voice_rule_check").check(it["spec"])["bugs"], "solver": it["solver"], "browser": it.get("browser"), "outcome": it.get("outcome"), "shot": shots[i], "path": solve(it["spec"]),
                "fail_path": None if solve(it["spec"]) else optimistic(it["spec"])[0], "marks": marks[i]} for i, it in enumerate(iters)],
     "episode": episode, "live_meta_calls": 0,
     # enemy i body as the generator read it (spawn BEFORE the fixer moved it) -> game.js cuts that blob for enemy i
     "enemy_bodies": [[c["x"], c["y"]] for c in json.loads(gen.read_text()).get("characters", []) if c.get("role") == "enemy"]}
# Muse Image lit-paper plate + Image-cleaned SAM sprites (display-only art; evidence/ assets generated live earlier)
def _b64png(f, mx):
    from PIL import Image as _I; im = _I.open(f).convert("RGBA"); im.thumbnail((mx, mx)); bb = io.BytesIO(); im.save(bb, "PNG"); return base64.b64encode(bb.getvalue()).decode()
_nn = re.sub(r"\D", "", pathlib.Path(a.sample).name)[-2:]
_plate = ROOT / f"evidence/image_plate_{_nn}.png"
_paper = ROOT / f"evidence/image_synthetic_{_nn}_paper.png"  # Muse Image lit render of the whole sheet (4:3, matches the board)
_empty, _hero = ROOT / f"evidence/image_plate_{_nn}_disney_empty.png", ROOT / f"evidence/image_render_{_nn}_disney.png"  # 3D feature-film look: env-only plate (no characters -> no doubling) + full hero render for the story card
if _empty.exists(): B["plate_b64"] = _b64png(_empty, 1280); B["plate_empty"] = True
if _hero.exists(): B["title_b64"] = _b64png(_hero, 1280)
if "plate_b64" in B: pass
elif _paper.exists(): B["plate_b64"] = B["title_b64"] = _b64png(_paper, 1280)
elif _plate.exists(): B["plate_b64"] = _b64png(_plate, 1280)
_sd = ROOT / f"evidence/sam_{_nn}/sprites"; _art = {}
for role, noun in {"player": "rocket", "goal": "star", "enemy": "monster", "wall": "rock"}.items():
    for cand in (f"{noun}_0_clean.png", f"{noun}_0.png"):
        if (_sd / cand).exists(): _art[role] = _b64png(_sd / cand, 256); break
for role in ("player", "goal", "enemy", "wall"):  # 3D feature-film sprites (Muse Image isolated from the hero render, magenta-keyed) win over flat SAM cuts
    _f = ROOT / f"evidence/sprites3d/{role}_3d.png"
    if _f.exists() and (ROOT / f"evidence/image_plate_{_nn}_disney_empty.png").exists(): _art[role] = _b64png(_f, 256); B["art3d"] = True
_pd = ROOT / "evidence" / sd.name; _s3 = _pd / "sprites3d"  # per-sample Muse Image set (playground_01): hero, empty plate, per-character 3D sprites, props
if (_pd / "image_plate.png").exists():
    B["plate_b64"] = _b64png(_pd / "image_plate.png", 1280); B["plate_empty"] = True; B["art3d"] = True
    if (_pd / "image_hero.png").exists(): B["title_b64"] = _b64png(_pd / "image_hero.png", 1280)
    _art = {k: _b64png(_s3 / f"{k}_3d.png", 256) for k in ("player", "enemy", "wall") if (_s3 / f"{k}_3d.png").exists()}
    _kids = sorted(iters[-1]["spec"]["goals"], key=lambda g: g["x"])
    for n, g in enumerate(_kids[:3]):
        if (_s3 / f"kid_{n+1}_3d.png").exists(): _art["id:" + g["id"]] = _b64png(_s3 / f"kid_{n+1}_3d.png", 256)
    if (_s3 / "kid_1_3d.png").exists(): _art["goal"] = _b64png(_s3 / "kid_1_3d.png", 256)
    _art["id:sol"] = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="  # sun already lit in the plate
    _PROPS = json.loads((sd / "props.json").read_text()) if (sd / "props.json").exists() else []
    B["props"] = [{**q, "src": "data:image/png;base64," + _b64png(_s3 / f"{q['name']}_3d.png", 512)} for q in _PROPS if (_s3 / f"{q['name']}_3d.png").exists()]
if _art: B["art"] = _art
if photo_src: B.update(photo_src=photo_src, photo_normalize=pinfo)
from gates import plan_gates
B["gates"] = plan_gates(iters[-1]["spec"], tr) if summ["result"] == "WIN" else []  # on-board beats on the winning iter (agent/gates.py)
if a.scene:
    _sp = ROOT / a.scene; _sc = json.loads(_sp.read_text()); _w = json.loads((_sp.parent / "world.json").read_text()); _art_w = _w.get("art", {}); _sa = _art_w.get(_sp.stem, {})
    _fin = dict(B["iters"][-1]); _fin.update(spec=_sc, path=solve(_sc), fail_path=None, marks=[], voice_rule=[]); B["iters"] = B["iters"] if _sp.stem == _w["start"] else []; B["iters"] = B["iters"][:-1] + [_fin] if B["iters"] else [_fin]
    if _sa.get("plate"): B["plate_b64"] = _b64png(ROOT / _sa["plate"], 1280); B["plate_empty"] = True
    B.setdefault("art", {})
    for _r in ("goal", "wall", "player", "enemy"):
        if _sa.get(_r): B["art"][_r] = _b64png(ROOT / _sa[_r], 256)
    if _sp.stem == _w["start"] and (_s3 / "kid_1_3d.png").exists():  # scene goal ids can differ from the muse spec's (nena_/nene_derecha): re-key kid sprites by scene goals
        [B["art"].pop(k) for k in [k for k in B["art"] if k.startswith("id:") and k != "id:sol"]]
        for n, g in enumerate(sorted(_sc.get("goals", []), key=lambda g: g["x"])[:3]):
            if (_s3 / f"kid_{n+1}_3d.png").exists(): B["art"]["id:" + g["id"]] = _b64png(_s3 / f"kid_{n+1}_3d.png", 256)
    if _sp.stem != _w["start"]:
        B["props"] = []; [B["art"].pop(k) for k in [k for k in B["art"] if k.startswith("id:") and k != "id:sol"]]
        _kids = sorted([c for c in _sc.get("characters", []) if c.get("role") != "enemy" and c["id"].startswith(("nene", "nena"))], key=lambda c: c["x"])
        for n, c in enumerate(_kids[:3]):  # scene 3: the 3 kids keep their scene-1 3D sprites (art parity)
            if (_s3 / f"kid_{n+1}_3d.png").exists(): B["art"]["id:" + c["id"]] = _b64png(_s3 / f"kid_{n+1}_3d.png", 256)
    if _art_w.get("door"): B["art"]["door"] = _b64png(ROOT / _art_w["door"], 512)
    _gq = _sc.get("gate"); _pg = [g for g in plan_gates(_sc, tr) if g["kind"] == "question"]
    B["gates"] = [{**_pg[0], "prompt": _gq["q"], "options": _gq["options"], "answer": _gq["answer"]}] if _gq and _pg else []
    B["scene_intro"] = _sc.get("intro", "")
if a.play: _l, _t, _n, _sn = (a.play.split("/") + ["", "", "", ""])[:4]; B["play"] = {"level": int(_l), "total": int(_t), "next": _n, "scene": _sn}
tpl = (ROOT / "game/demo.template.html").read_text()
out = ROOT / a.out; out.write_text(tpl.replace("/*__BUNDLE__*/null", json.dumps(B, ensure_ascii=False).replace("</", "<\\/")))
print("demo:", out.relative_to(ROOT), "| run:", B["run"], "|", B["result"], f"in {len(iters)} iter(s)")
