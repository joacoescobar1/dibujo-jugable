#!/usr/bin/env python3
"""Evidence: left card before->after render reveal, and staggered gates/beats (0 Meta spend)."""
import pathlib, json
from playwright.sync_api import sync_playwright
ROOT = pathlib.Path(__file__).resolve().parents[1]; url = (ROOT / "game/demo.html").as_uri(); out = {}
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={"width": 1400, "height": 900})
    pg.goto(url + "?mute=1"); pg.wait_for_timeout(250); pg.screenshot(path=str(ROOT / "evidence/judge_render_before.png"))
    out["t0_beats_visible"] = pg.evaluate("document.querySelectorAll('.beat:not(.hid)').length"); out["t0_gates_drawn"] = pg.evaluate("window.__GATES_DRAWN__")
    pg.wait_for_timeout(1200); pg.screenshot(path=str(ROOT / "evidence/judge_render_processing.png")); out["t1_beats_visible"] = pg.evaluate("document.querySelectorAll('.beat:not(.hid)').length")
    pg.wait_for_function("window.__RENDER_DONE__ === true"); pg.wait_for_timeout(2500); pg.screenshot(path=str(ROOT / "evidence/judge_render_after.png"))
    out["t2_beats_visible"] = pg.evaluate("document.querySelectorAll('.beat:not(.hid)').length")
    pg.click("#auto"); seen = []
    for _ in range(300):
        d = pg.evaluate("window.__GATES_DRAWN__")
        if not seen or seen[-1] != d:
            seen.append(d); pg.screenshot(path=str(ROOT / f"evidence/judge_gates_stagger_{d}.png"))
        if pg.evaluate("window.__DEMO_PLAY_DONE__ === true"): break
        pg.wait_for_timeout(100)
    out["gates_drawn_sequence"] = seen; out["final"] = pg.evaluate("window.__GAME__.state().status"); b.close()
print(json.dumps(out))
