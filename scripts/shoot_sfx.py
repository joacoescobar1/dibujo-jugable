import pathlib,json
from playwright.sync_api import sync_playwright
u=pathlib.Path("game/play.html").resolve().as_uri(); log=[]
with sync_playwright() as p:
  b=p.chromium.launch(args=["--use-gl=angle","--use-angle=swiftshader","--enable-unsafe-swiftshader","--autoplay-policy=no-user-gesture-required"]); pg=b.new_page(viewport={"width":1440,"height":900}); errs=[]; pg.on("pageerror",lambda e:errs.append(str(e)))
  pg.goto(u); pg.evaluate("localStorage.setItem('dj_mute','0')"); pg.reload(); pg.wait_for_timeout(1500)
  pg.click("#ps .big"); pg.wait_for_timeout(700); pg.click("#ps .big")
  pg.wait_for_function("!document.querySelector('#ps .scr')",timeout=40000); pg.wait_for_timeout(600); pg.screenshot(path="evidence/story_short.png")
  print("tale", pg.evaluate("(document.getElementById('tale')||{}).innerText"))
  for n in (1,2,3):
    if n>1: pg.wait_for_url(f"**/play_{n}.html*",timeout=20000); pg.wait_for_timeout(1200)
    pg.evaluate("document.getElementById('auto').click()")
    pg.wait_for_function("window.__GAME__.state().status==='won'",timeout=120000); pg.wait_for_timeout(800)
    l=pg.evaluate("[window.__SFX_LOG__, window.AudioContext?1:0]"); print(n,l); log.append(l[0])
  pg.wait_for_timeout(2500); print("errs",errs)
json.dump(log,open("evidence/sfx_fired.json","w"),indent=1)
