import pathlib
from playwright.sync_api import sync_playwright
u=pathlib.Path("game/play.html").resolve().as_uri(); E="evidence/player_fx_"
with sync_playwright() as p:
  b=p.chromium.launch(args=["--use-gl=angle","--use-angle=swiftshader","--enable-unsafe-swiftshader"]); pg=b.new_page(viewport={"width":1440,"height":900}); errs=[]; pg.on("pageerror",lambda e:errs.append(str(e)))
  pg.goto(u+"?mute=1"); pg.wait_for_timeout(1500)
  pg.click("#ps .big"); pg.wait_for_timeout(700); pg.click("#ps .big")
  pg.wait_for_function("!document.querySelector('#ps .scr')",timeout=40000)
  pg.wait_for_timeout(8000); pg.screenshot(path=E+"idle_arrow_7s.png",timeout=90000)
  pg.wait_for_timeout(6000); pg.screenshot(path=E+"idle_arrow_13s.png",timeout=90000)
  pg.evaluate("document.getElementById('auto').click()")
  pg.wait_for_function("window.__GAME__.state().doorOpen||window.__GAME__.state().status==='won'",timeout=120000,polling=16)
  # freeze auto-run the instant the door opens (harness no-ops further solver moves) so the heartbeat is captured before auto-win advances
  pg.evaluate("(()=>{const G=window.__GAME__;G.move=()=>({events:[]});})()")
  for i in range(4): pg.wait_for_timeout(120); pg.screenshot(path=E+f"door_flash_{i}.png",timeout=90000)
  pg.wait_for_timeout(600); print("state@heartbeat",pg.evaluate("JSON.stringify({d:window.__GAME__.state().doorOpen,s:window.__GAME__.state().status})")); pg.screenshot(path=E+"door_heartbeat.png",timeout=90000)
  print("errs",errs)
