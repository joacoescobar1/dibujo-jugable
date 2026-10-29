"""Headless Playwright playtest: loads game/index.html?spec=..., drives window.__GAME__ (state API),
falls back to keyboard if state API missing. Plan = BFS path; if unwinnable, optimistic() walk (route ignoring one obstacle class) so the recorded failure lands on the bug."""
import json, pathlib, sys, threading, functools, http.server, socketserver
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from playtest import solve
ROOT = pathlib.Path(__file__).resolve().parents[1]
KEYS = {(1,0):"ArrowRight",(-1,0):"ArrowLeft",(0,1):"ArrowDown",(0,-1):"ArrowUp",(0,0):" "}

def serve():
    h = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(ROOT))
    class Q(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a): pass
    h = functools.partial(Q, directory=str(ROOT))
    s = socketserver.TCPServer(("127.0.0.1", 0), h); threading.Thread(target=s.serve_forever, daemon=True).start(); return s

def greedy(spec):
    if spec["win_condition"].get("type") == "survive_seconds": return [(0, 0)] * int(spec["win_condition"].get("seconds", 1))
    p = dict(spec["player"]); g = ([g for g in spec["goals"] if g["id"] == spec["win_condition"].get("target")] or spec["goals"])[0]; out = []
    for _ in range(spec["grid"]["w"] + spec["grid"]["h"]):
        d = (1 if g["x"] > p["x"] else -1, 0) if g["x"] != p["x"] else (0, 1 if g["y"] > p["y"] else -1)
        out.append(d); p["x"] += d[0]; p["y"] += d[1]
        if (p["x"], p["y"]) == (g["x"], g["y"]): break
    return out

RELAX = (("enemies", lambda s: s.update(characters=[c for c in s.get("characters", []) if c.get("role") != "enemy"])),
         ("hazards", lambda s: s.update(hazards=[])), ("walls", lambda s: s.update(walls=[])),
         ("hazards+enemies", lambda s: s.update(hazards=[], characters=[c for c in s.get("characters", []) if c.get("role") != "enemy"])))

def optimistic(spec):
    """Unwinnable level -> the QA plan a tester would try: shortest route as if one obstacle class weren't there, so the
    walk hits the bug where it actually is (steps onto the monster / into the river / bumps the fence). Falls back to greedy.
    Returns (plan, label)."""
    if spec["win_condition"].get("type") != "survive_seconds":
        for name, f in RELAX:
            r = json.loads(json.dumps(spec)); f(r); p = solve(r)
            if p: return p, f"optimistic(ignoring {name})"
    return greedy(spec), "greedy(no path)"

def browser_playtest(spec_path, attempt=1, screenshot=None, timeline=None, use_keyboard=False):
    from playwright.sync_api import sync_playwright
    spec = json.loads(pathlib.Path(spec_path).read_text()); rel = pathlib.Path(spec_path).resolve().relative_to(ROOT)
    path = solve(spec); plan, planned_by = (path, "bfs") if path else optimistic(spec)
    srv = serve(); url = f"http://127.0.0.1:{srv.server_address[1]}/game/index.html?spec=/{rel}&attempt={attempt}"
    if timeline: url += f"&timeline=/{pathlib.Path(timeline).resolve().relative_to(ROOT)}"
    with sync_playwright() as pw:
        b = pw.chromium.launch(); pg = b.new_page(viewport={"width": 1000, "height": 620}); pg.goto(url)
        pg.wait_for_function("window.__GAME__ && window.__GAME__.ready")
        mode = "keyboard" if use_keyboard else "state_api"
        for d in plan:
            if use_keyboard: pg.keyboard.press(KEYS[tuple(d)])
            else: pg.evaluate("([a,b]) => window.__GAME__.move(a,b)", list(d))
            st = pg.evaluate("window.__GAME__.state()")
            if st["status"] != "playing" or (not path and st["events"][-1:] == ["bump"]): break  # optimistic walk hit a wall = STUCK
        st = pg.evaluate("window.__GAME__.state()")
        if screenshot: pg.screenshot(path=str(screenshot))
        b.close()
    srv.shutdown()
    return {"mode": mode, "url": url, "planned_by": planned_by, "status": st["status"],
            "won": st["status"] == "won", "steps": st["steps"], "events": st["events"][-5:], "player": st["player"]}

if __name__ == "__main__":
    import argparse; a = argparse.ArgumentParser(); a.add_argument("spec", nargs="?", default=str(ROOT/"game/spec.json"))
    a.add_argument("--keyboard", action="store_true"); a.add_argument("--shot"); a.add_argument("--summary", help="write result JSON here"); o = a.parse_args()
    r = browser_playtest(o.spec, screenshot=o.shot, use_keyboard=o.keyboard); r["screenshot"] = o.shot
    if o.summary: pathlib.Path(o.summary).write_text(json.dumps(r, indent=2, ensure_ascii=False))
    print(json.dumps(r))
