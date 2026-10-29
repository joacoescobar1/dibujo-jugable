#!/usr/bin/env python3
"""Screenshot game/demo_playground.html (file://) in headless Chromium -> evidence/judge_playground_win.png (final iter after the agent plays it)
and evidence/judge_playground_fail.png (?iter=0 after the agent tries it). Fails (exit 1) on any JS error, if the broken first try
does not end LOST on screen, or if the final autoplay does not reach WIN."""
import pathlib, sys
from playwright.sync_api import sync_playwright
ROOT = pathlib.Path(__file__).resolve().parents[1]; url = (ROOT / "game/demo_playground.html").as_uri(); errs = []
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={"width": 1400, "height": 900}); pg.on("pageerror", lambda e: errs.append(str(e)))
    # broken first try: the agent actually walks it (same optimistic plan as the Chromium playtest) and fails ON the bug, marks on the bug
    pg.goto(url + "?iter=0&mute=1"); pg.wait_for_timeout(400); pg.click("#auto"); pg.wait_for_function("window.__DEMO_PLAY_DONE__ === true", timeout=20000); fail_st = pg.evaluate("window.__DEMO_STUCK__ ? 'stuck' : window.__GAME__.state().status"); pg.wait_for_timeout(1200); pg.screenshot(path=str(ROOT / "evidence/judge_playground_fail.png"), full_page=True)
    pg.goto(url + "?mute=1"); pg.wait_for_timeout(400); pg.click("#auto"); pg.wait_for_function("window.__GAME__.state().status !== 'playing'", timeout=20000)
    pg.wait_for_function("window.__DEMO_PLAY_DONE__ === true", timeout=30000); st = pg.evaluate("window.__GAME__.state().status"); gates = pg.evaluate("(window.__BEATS__ && window.__BEATS__.gates) || {}"); pg.wait_for_timeout(1500); pg.screenshot(path=str(ROOT / "evidence/judge_playground_win.png"), full_page=True)
    b.close()
print({"first_try_status": fail_st, "final_status": st, "board_gates_cleared": gates, "js_errors": errs}); sys.exit(0 if st == "won" and fail_st in ("lost", "stuck") and len(gates) >= 3 and all(gates.values()) and not errs else 1)
