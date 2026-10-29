#!/usr/bin/env python3
"""Agent clears every interaction beat in game/demo.html (headless) -> evidence/judge_beats.png; exit 1 if any beat not clearable or JS error."""
import pathlib, sys
from playwright.sync_api import sync_playwright
ROOT = pathlib.Path(__file__).resolve().parents[1]; errs = []
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={"width": 1400, "height": 1100}); pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto((ROOT / "game/demo.html").as_uri() + "?mute=1"); pg.wait_for_timeout(500)
    done = pg.evaluate("window.__BEATS__.autoplay()"); pg.wait_for_timeout(300)
    # on-board: Modo juez walk -> agent hits the ❓ door, answers wrong once (door stays shut, red shake) -> shot -> answers right -> WIN
    pg.goto((ROOT / "game/demo.html").as_uri() + "?tour=1&mute=1"); pg.wait_for_function("document.querySelector('#gate.no')", timeout=30000); pg.wait_for_timeout(250)
    pg.screenshot(path=str(ROOT / "evidence/judge_beats.png"), full_page=True); blocked = pg.evaluate("window.__GAME__.state().events.filter(e => e.startsWith('gate'))")
    pg.wait_for_function("window.__DEMO_PLAY_DONE__ === true", timeout=30000); fin = pg.evaluate("window.__GAME__.state().status"); gates = pg.evaluate("window.__BEATS__.gates"); log = pg.evaluate("window.__BEATS__.gateLog")
    pg.screenshot(path=str(ROOT / "evidence/judge_beats_win.png"), full_page=True); b.close()
print({"beats": done, "board_events": blocked, "gate_log": log, "board_gates": gates, "final": fin, "js_errors": errs})
sys.exit(0 if all(done.get(k) for k in "fqmot") and fin == "won" and len(gates) >= 3 and all(gates.values()) and ["q", "fail"] in log and not errs else 1)
