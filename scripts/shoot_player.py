import pathlib
from playwright.sync_api import sync_playwright
u=pathlib.Path("game/play.html").resolve().as_uri(); E="evidence/player_"
def play(pg,tag):
  pg.evaluate("document.getElementById('auto').click()"); pg.wait_for_function("window.__GAME__.state().doorOpen||window.__GAME__.state().status==='won'",timeout=120000); pg.wait_for_timeout(700); pg.screenshot(path=E+tag+"_door_open.png")
  pg.wait_for_function("window.__GAME__.state().status==='won'",timeout=60000); pg.wait_for_timeout(2500); 
  try: pg.screenshot(path=E+tag+"_wipe.png", timeout=5000)
  except Exception as e: print("wipe shot skip",tag)
with sync_playwright() as p:
  b=p.chromium.launch(args=["--use-gl=angle","--use-angle=swiftshader","--enable-unsafe-swiftshader"]); pg=b.new_page(viewport={"width":1440,"height":900}); errs=[]; pg.on("pageerror",lambda e:errs.append(str(e)))
  pg.goto(u+"?mute=1"); pg.wait_for_timeout(1500); pg.screenshot(path=E+"1_title.png")
  pg.click("#ps .big"); pg.wait_for_timeout(700); pg.screenshot(path=E+"2_upload.png")
  pg.click("#ps .big"); pg.wait_for_timeout(4300); pg.screenshot(path=E+"3_agent_oops.png")
  pg.wait_for_function("!document.querySelector('#ps .scr')",timeout=40000); pg.wait_for_timeout(1500); pg.screenshot(path=E+"4_scene1.png")
  play(pg,"5s1")
  for n in (2,3):
    pg.wait_for_url(f"**/play_{n}.html*",timeout=20000); pg.wait_for_timeout(300); pg.screenshot(path=E+f"6_arrive{n}.png"); pg.wait_for_timeout(2500); pg.screenshot(path=E+f"7_scene{n}.png"); play(pg,f"8s{n}")
  pg.wait_for_timeout(1500); pg.screenshot(path=E+"9_ending.png"); print("errs",errs)
