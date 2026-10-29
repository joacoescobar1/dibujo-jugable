"""Play the game via state API. Pure-python BFS solver over spec (same rules as game.js, see scripts/parity_check.md).
Tick model (shared with game.js): every player action (move, bump or wait=(0,0)) is 1 tick = 1 "second".
After the player acts, enemies (characters with role=="enemy") advance one step of their cyclic `patrol` [[dx,dy],...];
a patrol step into a wall/out of bounds is skipped. Touching an enemy (player moves onto it or it moves onto player) = loss.
NPCs (role "npc" or no role) are decorative labeled sprites, not blocking.
win_condition: reach_goal (target) | survive_seconds (alive after `seconds` ticks) | collect_all (step on every goal; last pickup wins before enemies move)."""
import json, pathlib, sys
from collections import deque
def inr(p, r): return r["x"] <= p[0] < r["x"] + r.get("w", 1) and r["y"] <= p[1] < r["y"] + r.get("h", 1)
DIRS = ((1,0),(-1,0),(0,1),(0,-1),(0,0))
def enemies(spec): return [c for c in spec.get("characters", []) if c.get("role") == "enemy"]
def enemy_pos(spec, t):
    """Enemy cells after t ticks (independent of the player, so precomputable)."""
    W, H = spec["grid"]["w"], spec["grid"]["h"]; out = []
    for e in enemies(spec):
        x, y, pat = e["x"], e["y"], e.get("patrol") or []
        for i in range(t if pat else 0):
            dx, dy = pat[i % len(pat)]; n = (x+dx, y+dy)
            if 0 <= n[0] < W and 0 <= n[1] < H and not any(inr(n, w) for w in spec.get("walls", [])): x, y = n
        out.append((x, y))
    return out
def period(spec):
    import math; L = 1
    for e in enemies(spec): L = L * max(1, len(e.get("patrol") or [])) // math.gcd(L, max(1, len(e.get("patrol") or [])))
    return L
def solve(spec):
    W, H = spec["grid"]["w"], spec["grid"]["h"]; start = (spec["player"]["x"], spec["player"]["y"])
    wc = spec["win_condition"]; survive = wc.get("type") == "survive_seconds"
    goal = [g for g in spec.get("goals", []) if g["id"] == wc.get("target")] or spec.get("goals", [])
    wall = lambda p: not (0 <= p[0] < W and 0 <= p[1] < H) or any(inr(p, w) for w in spec.get("walls", []))
    haz = lambda p: any(inr(p, h) for h in spec.get("hazards", []))
    if wall(start) or haz(start) or start in enemy_pos(spec, 0): return None  # spawn death (game.js mirrors)
    N = int(wc.get("seconds", 0)); L = period(spec); cache = {}
    ep = lambda t: cache.setdefault(t, set(enemy_pos(spec, t)))
    key = lambda p, t: (p, t if survive else t % L)
    collect = wc.get("type") == "collect_all"; G = spec.get("goals", []); FULL = (1 << len(G)) - 1
    gm = lambda p: sum(1 << i for i, g in enumerate(G) if inr(p, g))
    key = lambda p, t, m: (p, t if survive else t % L, m)
    won = lambda p, t, m: (survive and t >= N) or (collect and m == FULL) or (not survive and not collect and any(inr(p, g) for g in goal))
    s0 = (start, 0, 0); q, prev = deque([s0]), {key(*s0): None}
    while q:
        p, t, m = q.popleft()
        if won(p, t, m):
            path = []; k = key(p, t, m)
            while prev[k] is not None: k, d = prev[k]; path.append(d)
            return path[::-1]
        for d in DIRS:
            n = (p[0]+d[0], p[1]+d[1])
            if wall(n): n = p  # bump = wait (still a tick)
            if haz(n) or n in ep(t): continue  # also covers same-tick swaps (player->enemy cell, enemy->player cell) = loss, like game.js
            nm = (m | gm(n)) if collect else m
            wins_now = (collect and nm == FULL) or (not survive and not collect and any(inr(n, g) for g in goal))
            if n in ep(t+1) and not wins_now: continue  # reaching goal / last pickup wins before enemies move
            k = key(n, t+1, nm)
            if k not in prev: prev[k] = (key(p, t, m), d); q.append((n, t+1, nm))
    return None
def bugs(spec):
    st = (spec["player"]["x"], spec["player"]["y"])
    if any(inr(st, h) for h in spec.get("hazards", [])): return ["player spawns inside a hazard (instant loss)"]
    if st in enemy_pos(spec, 0): return ["player spawns on an enemy (instant loss)"]
    if spec["win_condition"].get("type") == "survive_seconds": return ["cannot survive: enemies/hazards corner the player"]
    if enemies(spec) and solve({**spec, "characters": [c for c in spec.get("characters", []) if c.get("role") != "enemy"]}) is not None:
        return ["an enemy blocks every path to the goal (guards a chokepoint / patrol never lets you pass)"]
    return ["no path from player to goal avoiding hazards/walls/enemies"]
def playtest(spec):
    path = solve(spec)
    return {"winnable": path is not None, "steps": len(path) if path else None, "path": path,
            "bugs": [] if path else bugs(spec)}
if __name__ == "__main__":
    f = sys.argv[1] if len(sys.argv) > 1 else pathlib.Path(__file__).resolve().parents[1] / "game/spec.json"
    r = playtest(json.loads(pathlib.Path(f).read_text())); print(json.dumps({k: v for k, v in r.items() if k != "path"}))
