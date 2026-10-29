"""LOCAL MOCK patcher for offline demos ONLY. Production path = Muse via meta_client.chat (patch_loop --patcher muse).
Known fixes (minimal change, in order): (1) player spawned in a hazard -> move to nearest safe cell;
(2) hazard spans full row/column -> open 3-tile bridge; (3) walls seal the goal -> remove the one wall rect that reopens a path;
(4) player spawns on an enemy (== enemy spawned on player) -> move player to nearest cell free of walls/hazards/enemies at t=0,1;
(5) survive_seconds spawn-camp (an enemy starts within 1 tile of the player) -> move player to nearest cell >=3 tiles from every enemy;
(6) [runs before (2)/(3) so walls drawn by the kid survive] reach_goal/collect_all where an ENEMY is the blocker (spec wins with that enemy removed) -> per enemy, try in order:
    (a) shift its patrol phase (rotate the cyclic list), (b) move its spawn to the nearest free cell (BFS), keeping its patrol.
    First candidate that makes solve() succeed wins (smallest change; the kid's enemy stays in the game).
LIMITS: no fix for survive specs where the player is cornered by geometry with enemies >=2 tiles away (e.g. specs/survive-trap = designed
no-win negative control); (6) is NOT applied to survive specs (keeps survive-trap a negative control); never edits seconds;
bridge/wall fixes (2)(3) skipped for survive specs; (6b) multi-enemy: if no single-enemy edit works, greedy-then-pair search over
(phase|spawn) candidates for two enemies (phase shifts tried first), still never touching walls."""
import copy, sys, pathlib
from collections import deque
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from playtest import solve, inr, enemy_pos, enemies
def _bad(s, p): return any(inr(p, r) for r in s.get("walls", []) + s.get("hazards", []))
def _cands(s, i):
    """Edit candidates for enemy i: patrol phase shifts first, then spawn moves by BFS distance (<=12 cells)."""
    W, H = s["grid"]["w"], s["grid"]["h"]; c = s["characters"][i]; pat = c.get("patrol") or []
    pl = (s["player"]["x"], s["player"]["y"]); goals = s.get("goals", []); out = []
    for k in range(1, len(pat)): t = copy.deepcopy(c); t["patrol"] = pat[k:] + pat[:k]; out.append((t, f"enemigo {c['id']}: patrulla desfasada {k} paso(s)"))
    st = (c["x"], c["y"]); q, seen = deque([st]), {st}
    while q and len(out) < len(pat) + 12:
        p = q.popleft()
        if p != st and p != pl and not _bad(s, p) and not any(inr(p, g) for g in goals): out.append(({**c, "x": p[0], "y": p[1]}, f"enemigo {c['id']}: spawn {st}->{p}"))
        for d in ((1,0),(0,1),(-1,0),(0,-1)):
            n = (p[0]+d[0], p[1]+d[1])
            if 0 <= n[0] < W and 0 <= n[1] < H and n not in seen: seen.add(n); q.append(n)
    return out
def fix_enemy_pair(s, changes):
    """(6b) In-place: two covering guards. Try every pair of enemies x their candidate edits; walls untouched."""
    cs = s["characters"]; idx = [i for i, c in enumerate(cs) if c.get("role") == "enemy"]
    for a in range(len(idx)):
        for b in range(a + 1, len(idx)):
            i, j = idx[a], idx[b]; cj = _cands(s, j)
            for ti, ni in _cands(s, i):
                for tj, nj in cj:
                    if (ti["x"], ti["y"]) == (tj["x"], tj["y"]): continue  # never stack two guards on one cell
                    t = list(cs); t[i], t[j] = ti, tj
                    if solve({**s, "characters": t}) is not None:
                        s["characters"] = t; changes += [ni + " (abre paso)", nj + " (abre paso)"]; return True
    return False
def fix_enemy(s, changes):
    """(6) In-place: make the first single-enemy edit (patrol phase, then spawn move) that renders s winnable. Returns True if fixed."""
    W, H = s["grid"]["w"], s["grid"]["h"]; cs = s["characters"]
    pl = (s["player"]["x"], s["player"]["y"]); goals = s.get("goals", [])
    for i, c in enumerate(cs):
        if c.get("role") != "enemy": continue
        pat = c.get("patrol") or []
        for k in range(1, len(pat)):
            t = copy.deepcopy(c); t["patrol"] = pat[k:] + pat[:k]
            if solve({**s, "characters": cs[:i] + [t] + cs[i+1:]}) is not None:
                cs[i] = t; changes.append(f"enemigo {c['id']}: patrulla desfasada {k} paso(s) (deja pasar)"); return True
        st = (c["x"], c["y"]); q, seen = deque([st]), {st}
        while q:
            p = q.popleft()
            if p != st and p != pl and not _bad(s, p) and not any(inr(p, g) for g in goals):
                t = {**c, "x": p[0], "y": p[1]}
                if solve({**s, "characters": cs[:i] + [t] + cs[i+1:]}) is not None:
                    cs[i] = t; changes.append(f"enemigo {c['id']}: spawn {st}->{p} (ya no tapa el camino)"); return True
            for d in ((1,0),(0,1),(-1,0),(0,-1)):
                n = (p[0]+d[0], p[1]+d[1])
                if 0 <= n[0] < W and 0 <= n[1] < H and n not in seen: seen.add(n); q.append(n)
    return False
def mock_fix(spec, report):
    s = copy.deepcopy(spec); W, H = s["grid"]["w"], s["grid"]["h"]; changes = []
    pl = s["player"]; st = (pl["x"], pl["y"])
    if _bad(s, st):
        q, seen = deque([st]), {st}
        while q:
            p = q.popleft()
            if not _bad(s, p): pl["x"], pl["y"] = p; changes.append(f"player {st}->{p} (fuera del peligro)"); break
            for d in ((1,0),(0,1),(-1,0),(0,-1)):
                n = (p[0]+d[0], p[1]+d[1])
                if 0 <= n[0] < W and 0 <= n[1] < H and n not in seen: seen.add(n); q.append(n)
    def relocate(ok, why):
        q, seen = deque([st]), {st}
        while q:
            p = q.popleft()
            if ok(p): pl["x"], pl["y"] = p; changes.append(f"player {st}->{p} ({why})"); return p
            for d in ((1,0),(0,1),(-1,0),(0,-1)):
                n = (p[0]+d[0], p[1]+d[1])
                if 0 <= n[0] < W and 0 <= n[1] < H and n not in seen: seen.add(n); q.append(n)
    e0, e1 = set(enemy_pos(s, 0)), set(enemy_pos(s, 1)); st = (pl["x"], pl["y"])
    if st in e0: st = relocate(lambda p: not _bad(s, p) and p not in e0 and p not in e1, "no nacer sobre un enemigo") or st
    if solve(s) is None and s["win_condition"].get("type") == "survive_seconds" and any(abs(e[0]-st[0]) + abs(e[1]-st[1]) <= 1 for e in e0):
        relocate(lambda p: not _bad(s, p) and all(abs(e[0]-p[0]) + abs(e[1]-p[1]) >= 3 for e in e0), "lejos del enemigo al arrancar")
    surv = s["win_condition"].get("type") == "survive_seconds"  # (2)/(3) are path fixes: never applied to survive specs
    if solve(s) is None and not surv and enemies(s) and solve({**s, "characters": [c for c in s.get("characters", []) if c.get("role") != "enemy"]}) is not None:
        fix_enemy(s, changes) or fix_enemy_pair(s, changes)
    if solve(s) is None and not surv: bridge_where_drowned(s, changes)
    if solve(s) is None and not surv:
        for h in list(s.get("hazards", [])):
            if h["y"] + h.get("h", 1) >= H and h.get("h", 1) > 1 and h["y"] < H - 3:  # touches bottom edge -> bridge on last 3 rows
                old = h.get("h", 1); h["h"] = H - 3 - h["y"]; changes.append(f"hazard {h['id']}: h {old}->{h['h']} (puente abajo)")
            elif h["x"] == 0 and h.get("w", 1) >= W: h["w"] = W - 3; changes.append(f"hazard {h['id']}: w {W}->{W-3} (puente)")
    if solve(s) is None and not surv:
        for i, w in enumerate(s.get("walls", [])):
            t = {**s, "walls": s["walls"][:i] + s["walls"][i+1:]}
            if solve(t) is not None: s["walls"] = t["walls"]; changes.append(f"wall {w} removida (puerta a la meta)"); break
    s["title"] = s["title"].replace(" (ROTO)", "")
    s.pop("_bug_note", None); s["_patch_note"] = "mock_patcher: " + "; ".join(changes or ["no known fix"])
    return s

def bridge_where_drowned(s, changes):
    """(2a) Bridge at the cell where the QA walk (browser_playtest.optimistic, the same plan the demo plays) falls in the river,
    so the 🐞 (drown cell) and the 🔧 (bridge) coincide. Splits that hazard rect around a 1-cell gap; kept only if it makes the level winnable."""
    import json as _j
    from browser_playtest import optimistic
    plan, _ = optimistic(_j.loads(_j.dumps(s))); p = (s["player"]["x"], s["player"]["y"]); W, H = s["grid"]["w"], s["grid"]["h"]
    wall = lambda q: not (0 <= q[0] < W and 0 <= q[1] < H) or any(w["x"] <= q[0] < w["x"] + w.get("w", 1) and w["y"] <= q[1] < w["y"] + w.get("h", 1) for w in s.get("walls", []))
    for d in plan or []:
        n = (p[0] + d[0], p[1] + d[1]); p = p if wall(n) else n
        for i, h in enumerate(s.get("hazards", [])):
            x0, y0, w, hh = h["x"], h["y"], h.get("w", 1), h.get("h", 1)
            if not (x0 <= p[0] < x0 + w and y0 <= p[1] < y0 + hh): continue
            parts = ([{**h, "y": y0, "h": p[1] - y0}, {**h, "id": h["id"] + "_b", "y": p[1] + 1, "h": y0 + hh - p[1] - 1}] if hh >= w else
                     [{**h, "x": x0, "w": p[0] - x0}, {**h, "id": h["id"] + "_b", "x": p[0] + 1, "w": x0 + w - p[0] - 1}])
            parts = [q for q in parts if q.get("h", 1) > 0 and q.get("w", 1) > 0]
            t = {**s, "hazards": s["hazards"][:i] + parts + s["hazards"][i + 1:]}
            if solve(t) is not None:
                s["hazards"] = t["hazards"]; changes.append(f"hazard {h['id']}: puente en {p} (donde se cayó)"); return True
            return False
    return False
