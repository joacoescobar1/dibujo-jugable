#!/usr/bin/env python3
"""Muse Image art for a sample: hero 3D feature-film render + empty env plate. Cached: skips outputs that exist (rule 8). $0.01/img."""
import sys, json, base64, pathlib, urllib.request
ROOT = pathlib.Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT / "agent")); import meta_client as mc
STYLE = ("polished 3D feature-film CGI animation still, like a modern animated movie: soft global illumination, warm sunlight, subsurface-lit soft materials, lush stylized grass, volumetric fluffy clouds, gentle depth of field. "
         "Stylized cartoon, NOT photorealistic, NOT flat 2D. Keep the child's exact composition, positions, proportions, colors and charming wobbly character shapes.")
JOBS = {"hero": "Turn this child's crayon drawing into a " + STYLE + " Keep every character the child drew: the butterfly, the three kids (two on the seesaw, one on the slide), the slide, the seesaw, the sun, the clouds and the flowers. No text.",
        "plate_sky": "Turn this child's crayon drawing into an EMPTY high-sky game level background above the clouds, " + STYLE + " Same sun, same palette and crayon-inspired shapes, but the camera is up in the sky: big fluffy white and pastel clouds as floating islands, soft rainbow light, no ground, no playground. No characters, no text.",
        "plate_sun": "Turn this child's crayon drawing into an EMPTY final-level game background: the child's smiling sun now huge and glowing in the center, warm golden sunset sky, sparkles and soft pastel clouds around it, celebratory and calm, " + STYLE + " No characters, no text.",
        "plate": "Turn this child's crayon drawing into an EMPTY background environment for a game level, " + STYLE + " Keep the sky, sun, clouds, grass and flowers exactly where they are, but REMOVE the butterfly, all kids, the slide and the seesaw; fill those areas with matching grass and sky. No characters, no text."}
def save(res, out):
    d = (res.get("data") or [{}])[0]
    if d.get("b64_json"): out.write_bytes(base64.b64decode(d["b64_json"]))
    elif d.get("url"): out.write_bytes(urllib.request.urlopen(d["url"], timeout=60).read())
    else: raise SystemExit(json.dumps({k: v for k, v in res.items() if k != "data"})[:500])
if __name__ == "__main__":
    sd = ROOT / sys.argv[1]; img = next(sd.glob("drawing.*")); od = ROOT / "evidence" / sd.name; od.mkdir(parents=True, exist_ok=True)
    for name in sys.argv[2:] or JOBS:
        out = od / f"image_{name}.png"
        if out.exists(): print("cached", out); continue
        r = mc.image_edit(img, JOBS[name], dry=False); save(r, out); print(name, r.get("http_status"), out)
