"""GAME_GUIDE.md (T9, Play2Code player contract): player agents read only this guide + the screen, never the spec."""
import pathlib
def guide_md(spec):
    p = spec["player"]; g = spec["goals"]; hz = spec.get("hazards", [])
    L = [f"# {spec.get('title','Juego')}", "", "## Controles / Controls",
         "- Flechas o WASD para moverte. / Arrow keys or WASD to move.", "",
         "## Objetivo / Goal", f"- Llevá a **{p.get('label', p['id'])}** hasta **{', '.join(x.get('label', x['id']) for x in g)}**.",
         f"- Take **{p.get('label', p['id'])}** to **{', '.join(x.get('label', x['id']) for x in g)}**.", "", "## Peligros / Hazards"]
    L += [f"- No toques **{h.get('label', h['id'])}**: {'perdés' if h.get('effect','lose')=='lose' else h.get('effect')}. / Don't touch **{h.get('label', h['id'])}**." for h in hz] or ["- Ninguno. / None."]
    if spec.get("walls"): L += ["- Las paredes no se pueden atravesar. / Walls block you."]
    L += ["", "## Resultado / Outcome", "Reportá uno de / Report one of: WIN | LOSE | STUCK | CRASH | TIMEOUT | INVALID", ""]
    return "\n".join(L)
def write_guide(spec, spec_path):
    f = pathlib.Path(spec_path).parent / "GAME_GUIDE.md"; f.write_text(guide_md(spec)); return f
