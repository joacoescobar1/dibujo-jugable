#!/usr/bin/env python3
"""Muse plans multi-scene world for a sample (Fireboy/Watergirl style: clear scene -> door opens -> next scene -> ending).
Writes samples/<s>/scenes/scene_{1,2,3}.json + world.json. Scene 1 = existing fixed spec + door. Cached: skips if world.json exists.
Kid design rules (ages 8-10, web research 2026-10-28): one new idea per scene, visible door that opens only after the clear condition,
1 decision per gate (yes/no or 3 options from the drawing/voice), calm low-intensity ending, celebration < 5 s tap-to-skip."""
import sys, json, pathlib, re
ROOT = pathlib.Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT / "agent")); import meta_client as mc
from playtest import solve
RULES = """Sos diseñador de juegos para chicos de 8 a 10 años. Te paso el dibujo de un chico, su voz y la escena 1 (GameSpec JSON, ya ganable).
Diseñá ESCENA 2 (el cielo con nubes, después de la puerta del plaza) y ESCENA 3 (final en el sol), tipo Fireboy & Watergirl: se cumple la meta -> se abre una puerta brillante -> cambio de escena.
Reglas: cada escena es un nivel de 60-90 s con UNA sola idea nueva; la puerta brilla y se desbloquea recién al cumplir la meta; escena 2 es el pico (nubes grises patrullando, juntar 3 gotitas de arcoíris o similar sacado del dibujo); escena 3 es tranquila y corta (llegar al sol con los 3 nenes, sin enemigos difíciles) = final festejo real (después se muestra el dibujo original del chico).
Usá SOLO cosas del dibujo/voz: mariposa, 3 nenes, sol, nubes, flores, tobogán, subibaja. Nada genérico.
Cada escena tiene UNA pregunta-portón fácil (sí/no o 3 opciones) sobre el dibujo/la voz, ej: "¿A quién lleva la mariposa en su lomo?" opciones ["a los 3 nenes","a una nube","a nadie"].
Devolvé SOLO JSON: {"scenes":[S2,S3]} donde cada S tiene exactamente el formato de la escena 1 (title, genre "top-down", grid {w:16,h:12,tile:40}, player {id:"mariposa",label,x,y}, goals[{id,label,x,y,w:1,h:1}], characters[{id,label,role,x,y,patrol?}], walls[{x,y,w,h}], rules_text[], win_condition) + "door":{"id","label","x","y"} (celda libre, se abre al cumplir win) + "gate":{"q","options":[3],"answer"} + "intro" (1 frase corta para el chico). Escena 3 win_condition {"type":"reach_goal","target":"sol"} con goal id "sol"."""
def jx(s):
    s = re.sub(r"^```(json)?|```$", "", s.strip(), flags=re.M); return json.loads(s[s.index("{"):s.rindex("}") + 1])
if __name__ == "__main__":
    sd = ROOT / sys.argv[1]; od = sd / "scenes"; od.mkdir(exist_ok=True); s1 = json.load(open(sd / "spec.json"))
    raw = od / "muse_raw.json"
    if not raw.exists():
        img = next(sd.glob("drawing.*")); slim = {k: s1[k] for k in ("title", "grid", "source", "player", "goals", "characters", "walls", "rules_text", "win_condition")}
        r = mc.chat_live([{"role": "user", "content": [{"type": "text", "text": RULES + "\nESCENA 1:\n" + json.dumps(slim, ensure_ascii=False)}, mc.image_part(img)]}], note=f"playground_scenes {sd.name} scenes 2-3")
        if not r["ok"]: raise SystemExit(r)
        raw.write_text(r["content"])
    out = jx(raw.read_text())
    s1 = dict(s1, door={"id": "puerta_nube", "label": "Puerta a las nubes", "x": 14, "y": 1}, intro="¡Juntá a los 3 nenes en tu lomo!",
              gate={"q": "¿A quién lleva la mariposa en su lomo?", "options": ["A los 3 nenes", "A una nube gris", "A nadie"], "answer": "A los 3 nenes"})
    scenes = [s1] + out["scenes"]
    for i, s in enumerate(scenes, 1):
        s.setdefault("source", s1["source"]); s["scene"] = i; s["next"] = f"scene_{i+1}" if i < len(scenes) else None
        p = solve(s); print(f"scene_{i}", s["title"], "win" if p else "UNSOLVABLE", len(p or []), "door", s.get("door"))
        (od / f"scene_{i}.json").write_text(json.dumps(s, ensure_ascii=False, indent=1))
    (od / "world.json").write_text(json.dumps({"start": "scene_1", "scenes": [f"scene_{i}" for i in range(1, len(scenes) + 1)], "ending": f"scene_{len(scenes)}",
        "design": "1 idea nueva por escena; puerta visible se abre tras cumplir win; 1 decisión por portón; final tranquilo; festejo <5s tocable"}, ensure_ascii=False, indent=1))
