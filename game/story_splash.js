// Opening 4-beat story for gallery + index. English default, ?lang=es Spanish.
// Tap advances, auto ~5s. Public pitch: kid drawing → Meta models → a playable world.
(function () {
  const q = new URLSearchParams(location.search);
  if (q.get('skipstory') === '1') return;
  const ES = q.get('lang') === 'es';
  const T = (en, es) => ES ? es : en;
  try { if (sessionStorage.getItem('dj_pitch_v1') === '1') return; } catch (e) {}
  const REDUCED = (() => { try { return matchMedia('(prefers-reduced-motion: reduce)').matches; } catch (e) { return false; } })();
  const MS = 5000;
  const BEATS = [
    { art: '✏️', src: 'story_1.jpg', line: T('A kid draws a world on paper.', 'Un nene dibuja un mundo en papel.') },
    { art: '✨', src: 'story_2.jpg', line: T('Then the drawing wakes up.', 'Después, el dibujo cobra vida.') },
    { art: '🪄', src: 'story_3.jpg', line: T('Creativity plus play, with Meta models to help.', 'Creatividad y juego, con modelos de Meta.') },
    { art: '🎮', src: 'story_4.jpg', line: T('Now it is your turn. Play a world!', 'Ahora es tu turno. ¡Jugá un mundo!') }
  ];
  const css = document.createElement('style');
  css.textContent = `
#pitch{position:fixed;inset:0;z-index:240;background:#07050f;color:#fffaf2;display:flex;align-items:flex-end;justify-content:center;touch-action:none;cursor:pointer;overflow:hidden;font:800 clamp(22px,5.4vw,36px)/1.25 "Comic Sans MS","Chalkboard SE",cursive;text-align:center}
#pitch .bg{position:absolute;inset:0;background:#1a1230 center/cover no-repeat;transform:scale(1.08);animation:pitchKB 16s ease-in-out infinite alternate}
#pitch .shade{position:absolute;inset:0;background:linear-gradient(180deg,#07050f55 8%,#07050e00 36%,#07050ee6 72%,#07050f 100%)}
#pitch .card{position:relative;z-index:1;width:min(92vw,560px);padding:12px 16px calc(22px + env(safe-area-inset-bottom));display:flex;flex-direction:column;align-items:center;gap:6px;pointer-events:none}
#pitch .kicker{font-size:13px;letter-spacing:.16em;text-transform:uppercase;color:#ffd27a;margin:0}
#pitch .art{font-size:52px;line-height:1;margin:2px 0 0;filter:drop-shadow(0 6px 0 #0006)}
#pitch .line{margin:0;font:800 clamp(22px,5.6vw,36px)/1.25 "Comic Sans MS","Chalkboard SE",cursive;color:#fffaf2;text-shadow:0 3px 0 #0008,0 10px 24px #000a;text-wrap:balance}
#pitch .hint{font:700 16px/1.3 system-ui,"Segoe UI",sans-serif;color:#ffd27a;margin-top:4px}
#pitch .dots{display:flex;gap:8px;margin-top:8px}
#pitch .dots b{width:10px;height:10px;border-radius:50%;background:#ffffff44;display:block;font-size:0}
#pitch .dots b.on{background:#ffd27a;box-shadow:0 0 10px #ffd27a}
html.pitching,html.pitching body{overflow:hidden!important}
@keyframes pitchKB{to{transform:scale(1.18) translate(-1.5%,-1.5%)}}
@media (prefers-reduced-motion:reduce){#pitch .bg,#pitch .art{animation:none!important;transform:none!important}}
@media (prefers-reduced-motion:no-preference){#pitch .art{animation:taleBob 1.8s ease-in-out infinite}}
@keyframes taleBob{50%{transform:translateY(-8px) scale(1.05)}}
@media (max-height:430px) and (min-width:680px){
#pitch{align-items:center}
#pitch .card{flex-direction:row;flex-wrap:wrap;justify-content:center;gap:4px 12px;width:min(94vw,760px);padding:10px 14px;text-align:left}
#pitch .kicker,#pitch .hint,#pitch .dots{flex:1 0 100%;text-align:center;margin:0}
#pitch .art{font-size:40px;margin:0}
#pitch .line{flex:1 1 280px;font-size:20px;text-align:left;margin:0}
}`;
  document.head.appendChild(css);
  document.documentElement.classList.add('pitching');
  const root = document.createElement('div');
  root.id = 'pitch';
  root.setAttribute('role', 'dialog');
  root.setAttribute('aria-label', T('Story', 'Historia'));
  let i = 0, gone = false, timer = 0;
  window.__PITCH__ = { beat: 1, total: BEATS.length, ms: MS, at: Date.now(), closed: '' };
  const paint = () => {
    const b = BEATS[i];
    const dots = BEATS.map((_, n) => '<b' + (n === i ? ' class="on"' : '') + '></b>').join('');
    root.innerHTML = '<div class="bg" style="background-image:url(\'' + b.src + '\')"></div><div class="shade"></div><div class="card"><div class="kicker">' + T('Playable Drawing', 'Dibujo Jugable') + '</div><div class="art" aria-hidden="true">' + b.art + '</div><p class="line">' + b.line + '</p><div class="hint">' + T('Tap to continue', 'Tocá para seguir') + '</div><div class="dots" aria-hidden="true">' + dots + '</div></div>';
    window.__PITCH__.beat = i + 1;
    window.__PITCH__.at = Date.now();
    window.__PITCH__.line = b.line;
    window.__PITCH__.art = b.art;
  };
  const close = (how) => {
    if (gone) return;
    gone = true;
    clearTimeout(timer);
    window.__PITCH__.closed = how;
    try { sessionStorage.setItem('dj_pitch_v1', '1'); } catch (e) {}
    document.documentElement.classList.remove('pitching');
    root.remove();
  };
  const next = (how) => {
    if (gone) return;
    if (i < BEATS.length - 1) {
      i += 1;
      paint();
      arm();
      return;
    }
    close(how);
  };
  const arm = () => {
    clearTimeout(timer);
    timer = setTimeout(() => next('auto'), MS);
  };
  root.addEventListener('pointerdown', (ev) => {
    ev.preventDefault();
    ev.stopPropagation();
    next('tap');
  });
  paint();
  document.body ? document.body.appendChild(root) : document.addEventListener('DOMContentLoaded', () => document.body.appendChild(root));
  arm();
})();
