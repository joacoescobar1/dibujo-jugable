// Cinematic opening for gallery + index. English default, ?lang=es.
// Four beats (touch-path contract). The six film moments live inside them:
// lamp + pencil, the drawing wakes, the world unfolds, creativity + Meta models, your turn.
// ?skipstory=1 skips. sessionStorage dj_pitch_v1 after the first view.
// prefers-reduced-motion: still frames and a wash only. No particles, parallax, or Ken Burns.
// No network. No video. Art is the local story_*.jpg plates plus CSS/SVG.
(function () {
  const q = new URLSearchParams(location.search);
  if (q.get('skipstory') === '1') return;
  const ES = q.get('lang') === 'es';
  const T = (en, es) => (ES ? es : en);
  try { if (sessionStorage.getItem('dj_pitch_v1') === '1') return; } catch (e) {}
  if (document.getElementById('pitch')) return;

  const REDUCED = (() => {
    try { return matchMedia('(prefers-reduced-motion: reduce)').matches; } catch (e) { return false; }
  })();
  const MS = 5000;
  const BEATS = [
    {
      art: '✏️',
      src: 'story_1.jpg',
      pos: 'center 46%',
      line: T(
        'A kid draws, heart wide open.\nThe bravest world is on paper.',
        'Un nene dibuja con el corazón.\nSu mundo entero cabe en papel.'
      )
    },
    {
      art: '✨',
      src: 'story_2.jpg',
      pos: 'center 42%',
      line: T(
        'The drawing wakes up for you.\nIt wants to play right now.',
        'Tu dibujo despierta y te mira.\n¡Cobra vida y quiere jugar!'
      )
    },
    {
      art: '🪄',
      src: 'story_3.jpg',
      pos: 'center 48%',
      line: T(
        'Creativity plus play, just for you.\nMeta models believe in your lines.',
        'Creatividad y juego, de la mano.\nLos modelos de Meta te abrazan.'
      )
    },
    {
      art: '🎮',
      src: 'story_4.jpg',
      pos: 'center 40%',
      line: T(
        'This is your turn, little hero.\nPlay a world that loves you back.',
        'Ahora es tu turno, corazón.\n¡Jugá un mundo que te espera!'
      )
    }
  ];

  const css = document.createElement('style');
  css.textContent = `
#pitch{
  --ink:#1a0f08; --lamp:#ffcf8a; --paper:#fff6e4; --accent:#e25b2a; --rise:12px;
  position:fixed; inset:0; z-index:240; width:100%; height:100%;
  display:flex; flex-direction:column; justify-content:flex-end; align-items:center;
  background:var(--ink); color:var(--paper); overflow:hidden; touch-action:none;
  cursor:pointer; user-select:none; -webkit-user-select:none;
  font-family:Fredoka,"Baloo 2","Comic Neue","Comic Sans MS",system-ui,sans-serif;
  text-align:center;
}
#pitch .bg{position:absolute; inset:-8%; z-index:0; transform-origin:50% 42%}
#pitch .zoom{position:absolute; inset:0}
#pitch .layer{position:absolute; pointer-events:none}
#pitch .far,#pitch .gray{inset:-8%; background:#1a0f08 center 42%/cover no-repeat}
#pitch .gray{filter:grayscale(1) contrast(1.25); opacity:0}
#pitch .bloom{
  left:18%; right:18%; top:16%; height:46%;
  background:radial-gradient(circle,#fff6e4 0%,#ffcf8a 38%,transparent 70%);
  filter:blur(18px); mix-blend-mode:screen; opacity:0;
}
#pitch .mid{inset:-4%}
#pitch .lamp{
  position:absolute; inset:0;
  background:radial-gradient(38% 32% at 76% 14%,#ffcf8a 0%,rgba(255,207,138,.5) 28%,rgba(26,15,8,0) 66%);
  mix-blend-mode:screen; opacity:.95;
}
#pitch .grade{
  position:absolute; inset:0;
  background:linear-gradient(180deg,rgba(255,207,138,.16),rgba(26,15,8,0) 36%,rgba(26,15,8,.22));
  mix-blend-mode:soft-light;
}
#pitch .grain{
  position:absolute; inset:0; opacity:0; mix-blend-mode:multiply;
  background-image:radial-gradient(rgba(90,48,18,.45) .6px,transparent .8px);
  background-size:7px 7px;
}
#pitch[data-beat="1"] .grain{opacity:.07}
#pitch .near{inset:0; z-index:2}
#pitch .veil{
  position:absolute; inset:0; z-index:3; background:#1a0f08; opacity:0; pointer-events:none;
}
#pitch .scribble{
  display:none; position:absolute; z-index:3; left:5%; width:42%; top:5%; height:16%;
  overflow:visible; pointer-events:none;
}
#pitch .scribble path{fill:none; stroke-linecap:round; stroke-linejoin:round}
#pitch .ghost{stroke:#5c5146; stroke-width:2.4; opacity:.28}
#pitch .ink{stroke:#3a332c; stroke-width:2.6; stroke-dasharray:100; stroke-dashoffset:0; opacity:.8}
#pitch .pencil{
  display:none; position:absolute; z-index:4; left:7%; top:7%; font-size:26px;
  filter:drop-shadow(0 4px 0 rgba(90,40,10,.22)); pointer-events:none;
}
#pitch .whoosh{
  position:absolute; z-index:3; top:-10%; width:38%; height:120%; left:0; opacity:0;
  background:linear-gradient(90deg,transparent,rgba(255,207,138,.55),transparent);
  pointer-events:none;
}
#pitch .shade{
  position:absolute; inset:0; z-index:3; pointer-events:none;
  background:linear-gradient(180deg,rgba(26,15,8,.2) 0%,rgba(26,15,8,0) 20%,rgba(26,15,8,0) 46%,rgba(26,15,8,.42) 66%,rgba(26,15,8,.86) 100%);
}
#pitch .sticker{
  display:none; position:absolute; z-index:5; left:14px; top:calc(12px + env(safe-area-inset-top));
  width:112px; pointer-events:none;
}
#pitch .bug{display:block; width:100%; height:auto; overflow:visible;
  filter:drop-shadow(0 2px 0 rgba(90,40,10,.25)) drop-shadow(0 10px 14px rgba(26,15,8,.28))}
#pitch .mote,#pitch .graphite,#pitch .spark{
  position:absolute; border-radius:50%; opacity:0; pointer-events:none;
}
#pitch .mote{width:5px; height:5px; background:#ffcf8a; box-shadow:0 0 8px #ffcf8a}
#pitch .graphite{width:6px; height:6px; background:#2a241c; z-index:3}
#pitch .spark{width:8px; height:8px; background:var(--lamp); left:var(--x); top:var(--y); box-shadow:0 0 10px var(--lamp)}
#pitch .card{
  position:relative; z-index:4; width:min(940px,100%);
  padding:8px 20px calc(20px + env(safe-area-inset-bottom));
  display:flex; flex-direction:column; align-items:center; gap:16px;
  pointer-events:none;
}
#pitch .kicker{
  margin:0; font-weight:600; font-size:14px; letter-spacing:.12em; text-transform:uppercase; color:var(--lamp);
  text-shadow:0 2px 0 rgba(26,15,8,.45), 0 8px 18px rgba(26,15,8,.4);
}
#pitch .art{margin:0; line-height:0}
#pitch .mark{
  display:grid; place-items:center; width:64px; height:64px; border-radius:50%;
  background:var(--paper); color:var(--ink); font-size:32px; line-height:1;
  box-shadow:0 1px 0 rgba(255,255,255,.85) inset, 0 6px 0 rgba(176,96,28,.3), 0 14px 22px rgba(26,15,8,.3);
}
#pitch .line{
  margin:0; max-width:18em;
  font-weight:700; font-size:clamp(56px,10vw,84px); letter-spacing:-.02em; line-height:1.02;
  color:var(--paper);
  text-shadow:0 2px 0 rgba(90,40,10,.38), 0 12px 28px rgba(26,15,8,.55);
}
#pitch .ln{display:block}
#pitch .w{display:inline-block; white-space:nowrap}
#pitch .hint{
  margin:0; font-weight:600; font-size:20px; line-height:1.3; color:var(--lamp);
  text-shadow:0 2px 0 rgba(26,15,8,.35);
}
#pitch .magnet{display:inline-block; transform:translate(var(--mx,0px),var(--my,0px)); pointer-events:auto}
#pitch .cta{
  display:none; min-height:64px; min-width:200px; padding:16px 32px; border:0; border-radius:999px;
  background:var(--lamp); color:var(--ink); cursor:pointer;
  font:700 clamp(22px,4vw,32px)/1 Fredoka,"Baloo 2","Comic Neue",system-ui,sans-serif;
  letter-spacing:-.02em;
  box-shadow:0 1px 0 rgba(255,248,230,.9) inset, 0 8px 0 rgba(176,96,28,.38), 0 16px 28px rgba(26,15,8,.28);
}
#pitch[data-beat="4"] .cta{display:inline-flex; align-items:center; justify-content:center}
#pitch .dots{display:flex; gap:8px; margin:0}
#pitch .dots b{width:8px; height:8px; border-radius:99px; background:rgba(255,246,228,.35); display:block; font-size:0}
#pitch .dots b.on{width:22px; background:var(--lamp); box-shadow:0 0 0 4px rgba(255,207,138,.2)}
#pitch .skip{
  position:absolute; z-index:6; top:calc(10px + env(safe-area-inset-top)); right:calc(10px + env(safe-area-inset-right));
  min-height:56px; min-width:56px; padding:8px 18px; border:0; border-radius:999px; cursor:pointer;
  background:var(--paper); color:var(--ink);
  font:600 18px/1 Fredoka,"Baloo 2","Comic Neue",system-ui,sans-serif;
  box-shadow:0 1px 0 #fff inset, 0 6px 0 rgba(90,40,10,.22), 0 12px 20px rgba(26,15,8,.25);
  pointer-events:auto;
}
#pitch .skip:focus-visible,#pitch .cta:focus-visible{outline:3px solid var(--accent); outline-offset:3px}
#pitch .puff{
  position:absolute; z-index:7; width:8px; height:8px; margin:-4px 0 0 -4px; border-radius:50%;
  background:var(--lamp); pointer-events:none;
}
#pitch[data-beat="1"] .scribble,#pitch[data-beat="1"] .pencil{display:block}
#pitch[data-beat="1"] .lamp{background:radial-gradient(42% 36% at 78% 16%,#ffcf8a 0%,rgba(255,207,138,.62) 26%,rgba(26,15,8,0) 64%)}
#pitch[data-beat="2"] .bloom{opacity:.55}
#pitch[data-beat="2"] .sticker,#pitch[data-beat="3"] .sticker{display:block}
#pitch[data-beat="3"] .sticker{width:92px}
#pitch[data-beat="4"] .lamp{
  background:radial-gradient(48% 36% at 50% 58%,rgba(255,207,138,.95),rgba(255,207,138,.28) 42%,transparent 70%);
  opacity:.9;
}
.pitch-confetti{position:fixed; inset:0; z-index:260; pointer-events:none; overflow:hidden}
.pitch-confetti i{
  position:absolute; left:var(--x); top:36%; width:9px; height:14px; background:var(--c); border-radius:2px; opacity:0;
}
html.pitching,html.pitching body{overflow:hidden!important; height:100%}
@media (max-height:480px){
  #pitch{--rise:6px}
  #pitch .line{font-size:clamp(28px,6.6vh,40px)}
  #pitch .card{gap:10px; padding:6px 16px calc(8px + env(safe-area-inset-bottom))}
  #pitch .kicker{font-size:11px}
  #pitch .mark{width:40px; height:40px; font-size:20px}
  #pitch .hint{font-size:16px}
  #pitch .sticker{width:84px; left:10px; top:8px}
  #pitch[data-beat="3"] .sticker{width:72px}
  #pitch .cta{min-height:48px; min-width:160px; padding:8px 18px; font-size:20px}
  #pitch .scribble{top:3%; height:18%; width:30%}
  #pitch .pencil{font-size:22px; top:4%}
}
@media (prefers-reduced-motion:no-preference){
  #pitch .bg{animation:djKB 7.2s cubic-bezier(.45,0,.2,1) infinite alternate}
  #pitch .far{animation:djFar 7.6s cubic-bezier(.45,0,.2,1) infinite alternate}
  #pitch .mid{animation:djMid 6.4s cubic-bezier(.45,0,.2,1) infinite alternate}
  #pitch .near{animation:djNear 8s cubic-bezier(.45,0,.2,1) infinite alternate}
  #pitch .veil{animation:djVeil 1.2s ease-out both}
  #pitch .lamp{animation:djLamp 1.2s ease-out both}
  #pitch[data-beat="1"] .ink{animation:djDraw 1.7s ease-out both}
  #pitch[data-beat="1"] .pencil{animation:djTip 1.8s ease-in-out both}
  #pitch[data-beat="1"] .graphite{animation:djGraph .9s ease-out both; animation-delay:var(--d)}
  #pitch .mote{animation:djMote 4.2s ease-in-out infinite; animation-delay:var(--d)}
  #pitch[data-beat="2"] .zoom{animation:djWake .72s cubic-bezier(.2,1.4,.4,1) both}
  #pitch[data-beat="2"] .bloom{animation:djBloom 1.5s ease-in-out infinite}
  #pitch[data-beat="2"] .mark{animation:djWake .64s cubic-bezier(.2,1.4,.4,1) both}
  #pitch .sticker{animation:djFloat 7.4s cubic-bezier(.45,0,.2,1) infinite alternate}
  #pitch[data-beat="2"] .bug{animation:djWake .7s cubic-bezier(.2,1.4,.4,1) both}
  #pitch .wing{transform-box:view-box}
  #pitch .wing.L{transform-origin:98px 80px; animation:djFlapL 1.05s ease-in-out infinite}
  #pitch .wing.R{transform-origin:102px 80px; animation:djFlapR 1.05s ease-in-out infinite}
  #pitch .eyes{transform-box:view-box; transform-origin:100px 78px; animation:djBlink 2.6s infinite}
  #pitch[data-beat="3"] .gray{opacity:1; animation:djWipe .26s cubic-bezier(.45,0,.2,1) forwards}
  #pitch[data-beat="3"] .spark{animation:djSpark .62s ease-out both; animation-delay:var(--d)}
  #pitch[data-beat="4"] .cta{animation:djPulse 1.4s ease-in-out infinite}
  #pitch .w{animation:djWord .42s cubic-bezier(.16,.84,.2,1) both; animation-delay:calc(var(--i) * 60ms)}
  #pitch.juiced .card{animation:djJuice .28s cubic-bezier(.2,1.4,.4,1)}
  #pitch .whoosh.go{animation:djWhoosh .32s ease-out}
  #pitch .puff{animation:djPuff .36s ease-out forwards}
  #pitch .magnet{transition:transform .18s ease-out}
  #pitch .cta:active{transform:translateY(4px) scale(.98); box-shadow:0 1px 0 rgba(255,248,230,.9) inset, 0 3px 0 rgba(176,96,28,.38)}
  .pitch-confetti i{animation:djConfetti .85s ease-out forwards; animation-delay:var(--d)}
}
@keyframes djKB{from{transform:scale(1) translate3d(0,0,0)}to{transform:scale(1.12) translate3d(-3%,-2%,0)}}
@keyframes djFar{to{transform:translate3d(-2.5%,-1.5%,0)}}
@keyframes djMid{to{transform:translate3d(3.5%,2%,0)}}
@keyframes djNear{to{transform:translate3d(-4%,3%,0)}}
@keyframes djVeil{from{opacity:.22}to{opacity:0}}
@keyframes djLamp{from{opacity:0}to{opacity:.95}}
@keyframes djDraw{from{stroke-dashoffset:100}to{stroke-dashoffset:0}}
@keyframes djTip{0%{transform:translate3d(0,2vh,0)}100%{transform:translate3d(26vw,-1vh,0)}}
@keyframes djGraph{0%{opacity:0; transform:scale(.4)}28%{opacity:.85}100%{opacity:0; transform:translate3d(10px,12px,0) scale(.3)}}
@keyframes djMote{0%,100%{opacity:.2; transform:translate3d(0,8px,0)}50%{opacity:.9; transform:translate3d(8px,-18px,0)}}
@keyframes djWake{0%{transform:scale(.9)}58%{transform:scale(1.06)}100%{transform:scale(1)}}
@keyframes djFloat{to{transform:translate3d(8px,6px,0)}}
@keyframes djBloom{50%{opacity:.95}}
@keyframes djFlapL{50%{transform:rotate(8deg) scale(.96,1.03)}}
@keyframes djFlapR{50%{transform:rotate(-8deg) scale(.96,1.03)}}
@keyframes djBlink{0%,36%,46%,100%{transform:scaleY(1)}41%{transform:scaleY(.1)}}
@keyframes djWipe{from{clip-path:inset(0 0 0 0)}to{clip-path:inset(0 0 0 100%); opacity:0}}
@keyframes djSpark{0%{opacity:0; transform:translate3d(0,0,0) scale(.3)}22%{opacity:1}100%{opacity:0; transform:translate3d(var(--dx),var(--dy),0) scale(1)}}
@keyframes djPulse{50%{transform:scale(1.05)}}
@keyframes djWord{from{opacity:.9; transform:translateY(var(--rise,12px))}to{opacity:1; transform:translateY(0)}}
@keyframes djJuice{0%{transform:scale(.94)}50%{transform:scale(1.04)}100%{transform:scale(1)}}
@keyframes djWhoosh{0%{opacity:0; transform:translateX(-130%) skewX(-12deg)}35%{opacity:.8}100%{opacity:0; transform:translateX(280%) skewX(-12deg)}}
@keyframes djPuff{to{opacity:0; transform:translate3d(var(--dx),var(--dy),0) scale(.3)}}
@keyframes djConfetti{0%{opacity:1; transform:translate3d(0,0,0) rotate(0deg)}100%{opacity:0; transform:translate3d(var(--dx),46vh,0) rotate(var(--r))}}
@media (prefers-reduced-motion:reduce){
  #pitch .bg,#pitch .art,#pitch .mark,#pitch .bug,#pitch .sticker,#pitch .w,#pitch .cta{animation:none!important; transform:none!important}
  #pitch .veil,#pitch .gray,#pitch .mote,#pitch .graphite,#pitch .spark,#pitch .pencil{opacity:0!important; animation:none!important}
  #pitch .whoosh{display:none!important}
}
`;
  document.head.appendChild(css);

  const root = document.createElement('div');
  root.id = 'pitch';
  root.dataset.beat = '1';
  root.dataset.motion = REDUCED ? 'still' : 'full';
  root.setAttribute('role', 'dialog');
  root.setAttribute('aria-modal', 'true');
  root.setAttribute('aria-label', T('Story', 'Historia'));
  root.innerHTML = [
    '<div class="bg" aria-hidden="true"><div class="zoom">',
    '<div class="layer far"></div><div class="layer bloom"></div><div class="layer gray"></div>',
    '<div class="layer mid"><div class="lamp"></div><div class="grade"></div><div class="grain"></div><div class="motes"></div></div>',
    '<div class="layer near"></div></div></div>',
    '<div class="sticker" aria-hidden="true"><svg class="bug" viewBox="0 0 200 150">',
    '<circle cx="100" cy="88" r="54" fill="#fff6e4" stroke="#1a0f08" stroke-width="4"/>',
    '<g class="wing L"><path d="M92 78 C40 70 18 30 48 22 C78 16 96 48 98 74 Z" fill="#f4a3c2" stroke="#1a0f08" stroke-width="4" stroke-linejoin="round"/>',
    '<path d="M90 84 C36 100 28 132 62 128 C88 124 98 96 98 82 Z" fill="#f27d9a" stroke="#1a0f08" stroke-width="4" stroke-linejoin="round"/>',
    '<circle cx="58" cy="46" r="8" fill="#ffcf8a"/></g>',
    '<g class="wing R"><path d="M108 78 C160 70 182 30 152 22 C122 16 104 48 102 74 Z" fill="#f4a3c2" stroke="#1a0f08" stroke-width="4" stroke-linejoin="round"/>',
    '<path d="M110 84 C164 100 172 132 138 128 C112 124 102 96 102 82 Z" fill="#f27d9a" stroke="#1a0f08" stroke-width="4" stroke-linejoin="round"/>',
    '<circle cx="142" cy="46" r="8" fill="#ffcf8a"/></g>',
    '<ellipse cx="100" cy="88" rx="16" ry="26" fill="#1a0f08"/>',
    '<g class="eyes"><ellipse cx="93" cy="78" rx="5.2" ry="6.4" fill="#fff6e4"/><ellipse cx="107" cy="78" rx="5.2" ry="6.4" fill="#fff6e4"/>',
    '<circle cx="94.2" cy="79" r="2.1" fill="#1a0f08"/><circle cx="108.2" cy="79" r="2.1" fill="#1a0f08"/></g>',
    '<path d="M92 96 Q100 103 108 96" fill="none" stroke="#ffcf8a" stroke-width="2.6" stroke-linecap="round"/>',
    '<path d="M88 58 Q80 26 72 16" fill="none" stroke="#1a0f08" stroke-width="3" stroke-linecap="round"/>',
    '<path d="M112 58 Q120 26 128 16" fill="none" stroke="#1a0f08" stroke-width="3" stroke-linecap="round"/>',
    '<circle cx="72" cy="15" r="3.2" fill="#1a0f08"/><circle cx="128" cy="15" r="3.2" fill="#1a0f08"/>',
    '</svg></div>',
    '<div class="veil" aria-hidden="true"></div>',
    '<svg class="scribble" viewBox="0 0 210 110" preserveAspectRatio="xMidYMid meet" aria-hidden="true">',
    '<path class="ghost" pathLength="100" d="M8 78 C36 18 78 12 108 48 S156 96 196 36"/>',
    '<path class="ink" pathLength="100" d="M8 78 C36 18 78 12 108 48 S156 96 196 36"/>',
    '</svg>',
    '<div class="pencil" aria-hidden="true">✏️</div>',
    '<div class="whoosh" aria-hidden="true"></div>',
    '<div class="shade" aria-hidden="true"></div>',
    '<div class="sparks" aria-hidden="true"></div>',
    '<div class="card">',
    '<p class="kicker"></p>',
    '<div class="art" aria-hidden="true"><span class="mark"></span></div>',
    '<p class="line" aria-live="polite"></p>',
    '<span class="magnet"><button type="button" class="cta"></button></span>',
    '<div class="hint"></div>',
    '<div class="dots" aria-hidden="true"></div>',
    '</div>',
    '<button type="button" class="skip"></button>'
  ].join('');

  const far = root.querySelector('.far');
  const gray = root.querySelector('.gray');
  const lineEl = root.querySelector('.line');
  const mark = root.querySelector('.mark');
  const dotsEl = root.querySelector('.dots');
  const whoosh = root.querySelector('.whoosh');
  const sparkBox = root.querySelector('.sparks');
  const moteBox = root.querySelector('.motes');
  root.querySelector('.kicker').textContent = T('Playable Drawing', 'Dibujo Jugable');
  root.querySelector('.hint').textContent = T('Tap to continue', 'Tocá para seguir');
  root.querySelector('.cta').textContent = T('Play a world', '¡Jugá ya!');
  root.querySelector('.skip').textContent = T('Skip', 'Saltar');

  const MOTES = [
    [70, 8, 0], [78, 16, .4], [84, 11, .8], [74, 24, 1.1], [88, 20, 1.5],
    [64, 18, .2], [81, 30, 1.8], [90, 8, .6], [58, 12, 2.1], [76, 6, 1.3],
    [40, 22, .9], [22, 16, 1.6], [30, 10, .3], [48, 8, 2.4], [14, 20, 1.2], [52, 28, .7]
  ];
  MOTES.forEach((m) => {
    const d = document.createElement('i');
    d.className = 'mote';
    d.style.left = m[0] + '%';
    d.style.top = m[1] + '%';
    d.style.setProperty('--d', m[2] + 's');
    moteBox.appendChild(d);
  });
  [[8, 14], [14, 10], [20, 16], [26, 9], [32, 15], [38, 11], [44, 17]].forEach((g, n) => {
    const d = document.createElement('i');
    d.className = 'graphite';
    d.style.left = g[0] + '%';
    d.style.top = g[1] + '%';
    d.style.setProperty('--d', (n * 0.18) + 's');
    root.appendChild(d);
  });
  for (let n = 0; n < 12; n++) {
    const a = (Math.PI * 2 * n) / 12;
    const s = document.createElement('i');
    s.className = 'spark';
    s.style.setProperty('--x', (50 + Math.cos(a) * 10) + '%');
    s.style.setProperty('--y', (30 + Math.sin(a) * 8) + '%');
    s.style.setProperty('--dx', Math.round(Math.cos(a) * 78) + 'px');
    s.style.setProperty('--dy', Math.round(Math.sin(a) * 56) + 'px');
    s.style.setProperty('--d', (n % 6) * 18 + 'ms');
    sparkBox.appendChild(s);
  }
  sparkBox.style.cssText = 'position:absolute; inset:0; z-index:3; pointer-events:none';

  let i = 0;
  let gone = false;
  let timer = 0;
  window.__PITCH__ = { beat: 1, total: BEATS.length, ms: MS, at: Date.now(), closed: '', reduced: REDUCED };

  const fillLine = (text) => {
    lineEl.replaceChildren();
    text.split('\n').forEach((part, li) => {
      if (li) lineEl.appendChild(document.createTextNode(' '));
      const ln = document.createElement('span');
      ln.className = 'ln';
      part.split(' ').forEach((w, n) => {
        if (n) ln.appendChild(document.createTextNode(' '));
        const s = document.createElement('span');
        s.className = 'w';
        s.style.setProperty('--i', String(li * 8 + n));
        s.textContent = w;
        ln.appendChild(s);
      });
      lineEl.appendChild(ln);
    });
  };

  const paint = () => {
    const b = BEATS[i];
    root.dataset.beat = String(i + 1);
    far.style.backgroundImage = 'url("' + b.src + '")';
    gray.style.backgroundImage = 'url("' + b.src + '")';
    far.style.backgroundPosition = b.pos;
    gray.style.backgroundPosition = b.pos;
    mark.textContent = b.art;
    fillLine(b.line);
    dotsEl.replaceChildren();
    BEATS.forEach((_, n) => {
      const d = document.createElement('b');
      if (n === i) d.className = 'on';
      dotsEl.appendChild(d);
    });
    whoosh.classList.remove('go');
    if (!REDUCED) {
      void whoosh.offsetWidth;
      whoosh.classList.add('go');
    }
    window.__PITCH__.beat = i + 1;
    window.__PITCH__.at = Date.now();
    window.__PITCH__.line = b.line.replace(/\n/g, ' ');
    window.__PITCH__.art = b.art;
  };

  const arm = () => {
    clearTimeout(timer);
    timer = setTimeout(() => next('auto'), MS);
  };

  const close = (how) => {
    if (gone) return;
    gone = true;
    clearTimeout(timer);
    window.__PITCH__.closed = how;
    try { sessionStorage.setItem('dj_pitch_v1', '1'); } catch (e) {}
    document.documentElement.classList.remove('pitching');
    window.removeEventListener('keydown', onKey);
    root.remove();
  };

  const swell = () => {
    if (REDUCED) return;
    try {
      const Ctx = window.AudioContext || window.webkitAudioContext;
      if (!Ctx) return;
      const ctx = blip.ctx || (blip.ctx = new Ctx());
      if (ctx.state === 'suspended') ctx.resume().catch(() => {});
      const t = ctx.currentTime, o = ctx.createOscillator(), g = ctx.createGain();
      o.type = 'sine';
      o.frequency.setValueAtTime(180, t);
      o.frequency.exponentialRampToValueAtTime(640, t + 0.32);
      g.gain.setValueAtTime(0.0001, t);
      g.gain.exponentialRampToValueAtTime(0.045, t + 0.04);
      g.gain.exponentialRampToValueAtTime(0.0001, t + 0.36);
      o.connect(g); g.connect(ctx.destination); o.start(t); o.stop(t + 0.38);
    } catch (e) {}
  };

  const next = (how) => {
    if (gone) return;
    if (i < BEATS.length - 1) {
      i += 1;
      swell();
      paint();
      arm();
      return;
    }
    close(how);
  };

  const blip = (high) => {
    try {
      const Ctx = window.AudioContext || window.webkitAudioContext;
      if (!Ctx) return;
      const ctx = blip.ctx || (blip.ctx = new Ctx());
      if (ctx.state === 'suspended') ctx.resume().catch(() => {});
      const t = ctx.currentTime;
      const o = ctx.createOscillator();
      const g = ctx.createGain();
      o.type = high ? 'triangle' : 'sine';
      o.frequency.setValueAtTime(high ? 520 : 220, t);
      o.frequency.exponentialRampToValueAtTime(high ? 840 : 110, t + 0.12);
      g.gain.setValueAtTime(0.0001, t);
      g.gain.exponentialRampToValueAtTime(0.05, t + 0.02);
      g.gain.exponentialRampToValueAtTime(0.0001, t + 0.16);
      o.connect(g);
      g.connect(ctx.destination);
      o.start(t);
      o.stop(t + 0.18);
    } catch (e) {}
  };

  const puff = (x, y) => {
    if (REDUCED) return;
    for (let n = 0; n < 8; n++) {
      const d = document.createElement('i');
      d.className = 'puff';
      const a = (Math.PI * 2 * n) / 8;
      d.style.left = x + 'px';
      d.style.top = y + 'px';
      d.style.setProperty('--dx', Math.round(Math.cos(a) * 42) + 'px');
      d.style.setProperty('--dy', Math.round(Math.sin(a) * 32) + 'px');
      root.appendChild(d);
      setTimeout(() => d.remove(), 400);
    }
  };

  const burst = () => {
    if (REDUCED || !document.body) return;
    const layer = document.createElement('div');
    layer.className = 'pitch-confetti';
    const colors = ['#ffcf8a', '#e25b2a', '#fff6e4', '#f27d9a', '#7dce6a', '#f2c14b'];
    for (let n = 0; n < 32; n++) {
      const d = document.createElement('i');
      d.style.setProperty('--x', (6 + (n * 3.1) % 88) + '%');
      d.style.setProperty('--dx', ((n % 2 ? 1 : -1) * (10 + (n % 8) * 9)) + 'px');
      d.style.setProperty('--c', colors[n % colors.length]);
      d.style.setProperty('--d', (n % 5) * 20 + 'ms');
      d.style.setProperty('--r', (40 + n * 24) + 'deg');
      if (n % 3 === 0) d.style.borderRadius = '50%';
      layer.appendChild(d);
    }
    document.body.appendChild(layer);
    setTimeout(() => layer.remove(), 1000);
  };

  const juice = (x, y) => {
    if (REDUCED) return;
    root.classList.remove('juiced');
    void root.offsetWidth;
    root.classList.add('juiced');
    puff(x, y);
  };

  const act = (ev, how) => {
    if (gone) return;
    const x = (ev && ev.clientX) || (window.innerWidth / 2);
    const y = (ev && ev.clientY) || (window.innerHeight * 0.7);
    const last = i === BEATS.length - 1;
    juice(x, y);
    blip(last);
    try { if (navigator.vibrate) navigator.vibrate(15); } catch (e) {}
    if (last) burst();
    next(how);
  };

  function onKey(ev) {
    if (gone) return;
    if (ev.key !== ' ' && ev.key !== 'Enter' && ev.code !== 'Space') return;
    ev.preventDefault();
    const t = ev.target;
    if (t && t.closest && t.closest('.skip')) { close('skip'); return; }
    act(null, 'key');
  }

  let lastPtr = 0;
  root.addEventListener('pointerdown', (ev) => {
    if (ev.button && ev.button !== 0) return;
    ev.preventDefault();
    ev.stopPropagation();
    const now = Date.now();
    if (now - lastPtr < 320) return;
    lastPtr = now;
    const t = ev.target;
    if (t && t.closest && t.closest('.skip')) {
      try { if (navigator.vibrate) navigator.vibrate(15); } catch (e) {}
      close('skip');
      return;
    }
    act(ev, 'tap');
  }, { passive: false });

  root.addEventListener('pointermove', (ev) => {
    if (REDUCED || i !== 3) return;
    const mag = root.querySelector('.magnet');
    if (!mag) return;
    const r = mag.getBoundingClientRect();
    const dx = ev.clientX - (r.left + r.width / 2);
    const dy = ev.clientY - (r.top + r.height / 2);
    if (Math.hypot(dx, dy) > 170) {
      mag.style.setProperty('--mx', '0px');
      mag.style.setProperty('--my', '0px');
      return;
    }
    mag.style.setProperty('--mx', (dx * 0.16).toFixed(1) + 'px');
    mag.style.setProperty('--my', (dy * 0.16).toFixed(1) + 'px');
  });

  window.addEventListener('keydown', onKey);
  document.documentElement.classList.add('pitching');
  paint();
  const mount = () => document.body.appendChild(root);
  if (document.body) mount();
  else document.addEventListener('DOMContentLoaded', mount);
  arm();
  try { sessionStorage.setItem('dj_pitch_v1', '1'); } catch (e) {}

  const warm = (src) => {
    const im = new Image();
    im.decoding = 'async';
    im.src = src;
  };
  warm(BEATS[0].src);
  const later = () => BEATS.slice(1).forEach((b) => warm(b.src));
  if (window.requestAnimationFrame) requestAnimationFrame(later);
  else setTimeout(later, 0);
})();
