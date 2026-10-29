# Evidence: agent-theater step chips + kid HUD (star pips) + pause menu. Offline, no API.
import pathlib
from playwright.sync_api import sync_playwright
u=pathlib.Path("game/play.html").resolve().as_uri()
with sync_playwright() as p:
  b=p.chromium.launch(args=["--use-gl=angle","--use-angle=swiftshader","--enable-unsafe-swiftshader"]); pg=b.new_page(viewport={"width":1440,"height":900})
  errs=[]; pg.on("pageerror",lambda e:errs.append(str(e)))
  pg.goto(u+"?mute=1"); pg.wait_for_timeout(1500)
  pg.click("#ps .big"); pg.wait_for_timeout(700); pg.click("#ps .big")
  pg.wait_for_function("document.querySelector('#ps .steps b.bad, #ps .steps b.fix')",timeout=20000); pg.wait_for_timeout(300)
  pg.screenshot(path="evidence/theater_steps.png"); print("steps",pg.evaluate("[...document.querySelectorAll('#ps .steps b')].map(b=>b.className+':'+b.textContent)"))
  pg.wait_for_function("!document.querySelector('#ps .scr')",timeout=40000); pg.wait_for_timeout(5000)
  pg.click("#pz"); pg.wait_for_timeout(400); pg.screenshot(path="evidence/hud_pause.png")
  print("hud",pg.evaluate("document.getElementById('h3c').innerText"),"pause",pg.evaluate("document.getElementById('pzo').innerText"))
  pg.click("#pzo button"); print("paused",pg.evaluate("window.__PAUSED__")); print("errs",errs)
