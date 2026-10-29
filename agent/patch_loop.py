"""build -> play -> fix loop. Each iteration logged to runs/<ts>/ (spec, report, screenshot, timeline) = QA trail for the demo.
--patcher muse (PRODUCTION, Meta Muse via meta_client) | mock (OFFLINE demo, agent/mock_patcher.py).
--browser additionally plays every iteration headless in Chromium through window.__GAME__."""
import argparse, json, pathlib, sys, datetime
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from playtest import playtest
ROOT = pathlib.Path(__file__).resolve().parents[1]
import hashlib
from outcomes import RunOutcome, from_solver, from_browser
from game_guide import write_guide
sys.path.insert(0, str(ROOT / "scripts")); from voice_rule_check import check as voice_rule
EPISODE_N = 5  # fixer prompts read the last N episode.jsonl lines (T8, Play2Code memory)
def episode_tail(run, n=EPISODE_N):
    f = pathlib.Path(run) / "episode.jsonl"
    return [json.loads(l) for l in f.read_text().splitlines()[-n:]] if f.exists() else []
def fix_prompt(spec, report, episode):
    return (f"Este spec de juego no es ganable. Reporte QA: {json.dumps(report)}\nIntentos previos (no repitas lo que falló): {json.dumps(episode, ensure_ascii=False)}\n"
            f"Spec: {json.dumps(spec)}\nDevolvé SOLO el JSON corregido, cambio mínimo, respetando las reglas del nene.")
def muse_fix(spec, report, episode=(), chat=None):
    if chat is None: from meta_client import chat
    from meta_client import parse_json
    for k in range(3):  # Muse can spend all max_tokens reasoning and return empty content -> retry with more budget
        try: out = parse_json(chat([{"role": "system", "content": MUSE_SYS}, {"role": "user", "content": fix_prompt(spec, report, list(episode))}], max_tokens=16000 * (k + 1), note=f"patch_loop muse_fix try{k}")); break
        except (ValueError, json.JSONDecodeError):
            if k == 2: raise
    out.setdefault("_patch_note", "Muse: spec corregido"); return out
MUSE_SYS = ("Sos el agente QA+fixer de Dibujo Jugable: un nene dibujó un juego y vos lo hacés ganable SIN traicionar el dibujo. "
    "Grilla x,y desde 0, el jugador se mueve en 4 direcciones; walls bloquean, hazards matan, characters role=enemy patrullan (patrol = offsets relativos) y matan al tocar. "
    "Pensá en profundidad: simulá el camino celda por celda, identificá la causa raíz del bug del reporte, y aplicá el cambio MÍNIMO (correr un bicho, abrir un hueco/puente, mover una piedra). "
    "No borres elementos que dibujó el nene salvo que sea imprescindible. Devolvé SOLO el spec JSON completo corregido con el mismo esquema, más un campo \"_patch_note\" (1 frase en castellano rioplatense para el nene).")
def spec_sha(spec): return hashlib.sha256(json.dumps(spec, sort_keys=True).encode()).hexdigest()[:16]
if __name__ == "__main__":
    a = argparse.ArgumentParser(); a.add_argument("--spec", default=str(ROOT / "game/spec.json")); a.add_argument("--max", type=int, default=5)
    a.add_argument("--patcher", choices=["muse", "mock"], default="muse"); a.add_argument("--browser", action="store_true")
    a.add_argument("--apply", action="store_true", help="write winning spec to game/spec.json")
    o = a.parse_args(); spec = json.loads(pathlib.Path(o.spec).read_text())
    if o.patcher == "mock": from mock_patcher import mock_fix as fix
    else: fix = muse_fix
    run = ROOT / "runs" / (datetime.datetime.now().strftime("%Y%m%d-%H%M%S") + f"-{pathlib.Path(o.spec).stem.replace('.spec', '')}-{o.patcher}"); run.mkdir(parents=True, exist_ok=True)
    tl = []; tlf = run / "timeline.json"; summary = {"patcher": o.patcher, "iterations": []}
    for i in range(o.max):
        sf = run / f"iter_{i}.spec.json"; sf.write_text(json.dumps(spec, indent=2, ensure_ascii=False)); write_guide(spec, run / "x")
        r = playtest(spec); vr = voice_rule(spec)
        if vr["bugs"]: r = {**r, "winnable": False, "bugs": r.get("bugs", []) + vr["bugs"]}  # solver-winnable but betrays the kid's spoken rule = LOSE
        it = {"iter": i, **({"voice_rule": vr["bugs"]} if vr["bugs"] else {}), "solver": {k: v for k, v in r.items() if k != "path"}}
        tl.append({"kind": "win" if r["winnable"] else "fail", "text": f"#{i+1} solver: {'ganable en %d pasos' % r['steps'] if r['winnable'] else 'NO ganable'}"})
        if o.browser:
            from browser_playtest import browser_playtest
            tlf.write_text(json.dumps(tl, ensure_ascii=False))
            b = browser_playtest(sf, attempt=i+1, screenshot=run / f"iter_{i}.png", timeline=tlf); it["browser"] = b
            tl.append({"kind": "win" if b["won"] else "fail", "text": f"#{i+1} jugador headless: {b['status']} ({b['steps']} pasos, {b['events'][-1:]})"})
        (run / f"iter_{i}.json").write_text(json.dumps({"spec": spec, **it}, indent=2, ensure_ascii=False)); summary["iterations"].append(it)
        print(f"iter {i}: winnable={r['winnable']} steps={r['steps']}" + (f" browser={it['browser']['status']}" if o.browser else ""))
        it["outcome"] = (from_browser(it["browser"]) if o.browser else from_solver(r)).value
        if vr["bugs"]: tl.append({"kind": "fail", "text": f"#{i+1} regla de voz: la mariposa se fue sin los 3 nenes -> LOSE"})
        if vr["bugs"] and o.browser: it["outcome"] = "LOSE"
        if r["winnable"] and (not o.browser or it["browser"]["won"]):
            summary["result"] = RunOutcome.WIN.value; summary["spec_sha256"] = spec_sha(spec)
            with open(run / "episode.jsonl", "a") as ef: ef.write(json.dumps({"iter": i, "patch_summary": None, "outcome": it["outcome"], "bugs": []}, ensure_ascii=False) + "\n")
            if o.apply: (ROOT / "game/spec.json").write_text(json.dumps(spec, indent=2, ensure_ascii=False))
            break
        spec = fix(spec, r, episode_tail(run)) if fix is muse_fix else fix(spec, r)
        with open(run / "episode.jsonl", "a") as ef: ef.write(json.dumps({"iter": i, "patch_summary": spec.get("_patch_note", "spec corregido"), "outcome": it["outcome"], "bugs": r["bugs"]}, ensure_ascii=False) + "\n")
        tl.append({"kind": "fix", "text": f"#{i+1} patch ({o.patcher}): {spec.get('_patch_note', 'spec corregido')}"})
    else: summary["result"] = "GAVE_UP"
    tlf.write_text(json.dumps(tl, indent=2, ensure_ascii=False)); (run / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False))
    print("run:", run.relative_to(ROOT), summary["result"])
