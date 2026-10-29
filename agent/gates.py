"""On-board beats (gates) that block the grid until the kid clears a mini-game. Layered ON TOP of a spec: the spec/schema/oracle
are untouched; gates live in the demo bundle (B.gates) and in game.js only when window.__GATES__ is set.
Rules (mirrored by game.js): a LOCKED gate cell blocks the player (no tick, event 'gate:<id>', overlay opens). Clearing the beat
opens it. A fork gate has two doors (A on the solver path, B on an alternative route): picking one opens it and seals the other.
Agent: plan_gates() puts fork/question/meter on the winning path; clear_plan() returns the deterministic answer per gate;
walk() replays solve() path with gates and proves it wins only if every beat is cleared (and is STUCK if a beat is failed)."""
import math, re
from playtest import solve, inr
def said_no_touch(tr): return bool(re.search(r"sin tocar|no puede tocar|no tiene que tocar", (tr or "").lower()))
def hazard_word(tr):
    tr = (tr or "").lower(); return next((w for w in ("piedra", "agua", "fuego", "lava") if w in tr), "piedra")
METER_ZONE, METER_SPEED = (0.62, 0.82), 0.022  # needle v = (sin(k*speed)+1)/2 per frame k (beats.js uses the same)
def meter_frame():
    """First animation frame where the needle sits in the gold zone (deterministic: the agent presses then)."""
    for k in range(1, 10000):
        v = (math.sin(k * METER_SPEED) + 1) / 2
        if METER_ZONE[0] + .04 < v < METER_ZONE[1] - .04: return k
def _cells(spec, path):
    p = (spec["player"]["x"], spec["player"]["y"]); out = [p]
    W, H = spec["grid"]["w"], spec["grid"]["h"]
    for dx, dy in path:
        n = (p[0] + dx, p[1] + dy)
        if 0 <= n[0] < W and 0 <= n[1] < H and not any(inr(n, w) for w in spec.get("walls", [])): p = n
        out.append(p)
    return out
def plan_gates(spec, transcript=""):
    path = solve(spec)
    if not path: return []
    cells = _cells(spec, path); uniq = []
    for c in cells[1:-1]:
        if c not in uniq and c != cells[0]: uniq.append(c)
    if len(uniq) < 3: return []
    picks = [uniq[max(0, int(len(uniq) * f))] for f in (.2, .5, .78)]
    picks = list(dict.fromkeys(picks))
    if len(picks) < 3: picks = [uniq[0], uniq[len(uniq) // 2], uniq[-1]]
    hz = hazard_word(transcript); no = said_no_touch(transcript)
    fa = picks[0]; alt = solve({**spec, "walls": spec.get("walls", []) + [{"x": fa[0], "y": fa[1]}]})
    fb = None
    if alt:
        for c in _cells(spec, alt)[1:]:
            if c not in cells and c not in picks: fb = c; break
    hz_en = {"piedra": "the rocks", "agua": "the water", "fuego": "the fire", "lava": "the lava"}[hz]
    hz_es = {"piedra": "las piedras", "agua": "el agua", "fuego": "el fuego", "lava": "la lava"}[hz]
    fork_en = ["⬆️ This way", "↪️ The other way" if fb else "🧱 Into the wall"]
    fork_es = ["⬆️ Por acá", "↪️ Por el otro lado" if fb else "🧱 Por la pared"]
    G = [{"id": "fork", "kind": "fork", "cell": list(fa), "alt": list(fb) if fb else None, "answer": "A", "answer_es": "A",
          "prompt": "Which way do you go?", "prompt_es": "¿Por dónde seguís?", "options": fork_en, "options_es": fork_es},
         {"id": "q", "kind": "question", "cell": list(picks[1]), "answer": "No" if no else "Yes", "answer_es": "No" if no else "Sí",
          "prompt": f"Can your ship touch {hz_en}?", "prompt_es": f"¿Tu nave puede tocar {hz_es}?",
          "options": ["👍 Yes", "👎 No"], "options_es": ["👍 Sí", "👎 No"]},
         {"id": "m", "kind": "meter", "cell": list(picks[2]), "answer_frame": meter_frame(), "zone": list(METER_ZONE),
          "prompt": "Jump right on time! Stop the needle on the gold.", "prompt_es": "¡Saltá justo! Pará la aguja en lo dorado"}]
    return G
def clear_plan(gates): return {g["id"]: (g.get("answer") or "frame:%d" % g["answer_frame"]) for g in gates}
def check(g, ans):
    if g["kind"] == "meter":
        k = int(str(ans).split(":")[1]); v = (math.sin(k * METER_SPEED) + 1) / 2; return METER_ZONE[0] < v < METER_ZONE[1]
    if g["kind"] == "fork": return ans == "A" or (ans == "B" and g.get("alt") is not None)
    return ans == g["answer"]
def walk(spec, gates, answers):
    """Replay the solver path with gates. Returns {'status': won|stuck, 'cleared': [...], 'blocked_at': id|None}."""
    path = solve(spec) or []; p = (spec["player"]["x"], spec["player"]["y"]); locked = {tuple(g["cell"]): g for g in gates}
    sealed = set(); cleared = []
    for dx, dy in path:
        n = (p[0] + dx, p[1] + dy)
        if n in sealed: return {"status": "stuck", "cleared": cleared, "blocked_at": "sealed"}
        if n in locked:
            g = locked.pop(n); a = answers.get(g["id"])
            if not check(g, a): return {"status": "stuck", "cleared": cleared, "blocked_at": g["id"]}
            cleared.append(g["id"])
            if g["kind"] == "fork" and g.get("alt"): sealed.add(tuple(g["alt"]))
        if not any(inr(n, w) for w in spec.get("walls", [])) and 0 <= n[0] < spec["grid"]["w"] and 0 <= n[1] < spec["grid"]["h"]: p = n
    goal_hit = any(inr(p, gg) for gg in spec["goals"])
    return {"status": "won" if goal_hit and not locked else "stuck", "cleared": cleared, "blocked_at": None}
