// Interaction kit (display layer, never touches game rules/parity): small "beats" the level can pick from.
// Kinds: question (from the kid's transcript), meter (stop at the right colour), order (2–3 tile puzzle), ttt (tic-tac-toe).
// window.__BEATS__.autoplay() = the agent plays every beat and verifies it can be cleared (Modo juez).
(function () {
  const ES = new URLSearchParams(location.search).get('lang') === 'es', T = (en, es) => ES ? es : en;
  const B = window.__BUNDLE__ || {}, tr = String(B.transcript || '').toLowerCase();
  const nouns = ['gato','perro','casa','agua','estrella','cohete','nave','monstruo','fantasma','piedra','puente','llave','puerta'].filter(w => tr.includes(w));
  const NOUN_EN = { gato: 'cat', perro: 'dog', casa: 'house', agua: 'water', estrella: 'star', cohete: 'rocket', nave: 'ship', monstruo: 'monster', fantasma: 'ghost', piedra: 'rock', puente: 'bridge', llave: 'key', puerta: 'door' };
  const hero = ES ? (nouns[0] || 'héroe') : (NOUN_EN[nouns[0]] || 'hero'), goal = ES ? (nouns.find(w => ['casa','estrella'].includes(w)) || 'meta') : (nouns.find(w => ['casa','estrella'].includes(w)) === 'casa' ? 'house' : nouns.find(w => ['casa','estrella'].includes(w)) === 'estrella' ? 'star' : 'goal');
  const host = document.getElementById('beats'); if (!host) return;
  let seed = 1234567; const R = () => (seed = (seed * 1103515245 + 12345) % 2147483648) / 2147483648;  // seeded -> agent verify deterministic
  const state = { done: {}, log: [] }; window.__BEATS__ = state;
  const fx = (el, ok) => { el.classList.remove('ok', 'no'); void el.offsetWidth; el.classList.add(ok ? 'ok' : 'no');
    for (let i = 0; i < (ok ? 14 : 6); i++) { const p = document.createElement('i'); p.className = 'pt' + (ok ? '' : ' r'); p.style.setProperty('--dx', (Math.random() * 160 - 80) + 'px'); p.style.setProperty('--dy', (-Math.random() * 90 - 20) + 'px'); el.appendChild(p); setTimeout(() => p.remove(), 900); } };
  const card = (id, title, sub) => { const d = document.createElement('div'); d.className = 'beat'; d.id = 'beat-' + id; d.innerHTML = `<div class="bt">${title}</div><div class="bs">${sub}</div><div class="bb"></div>`; host.appendChild(d); return d; };
  const win = (id, el, msg) => { state.done[id] = true; state.log.push([id, 'ok']); fx(el, true); el.querySelector('.bs').textContent = msg; el.classList.add('cleared'); };
  // 1) path fork A/B (both are fine paths -> the kid decides, the game adapts)
  const hz = ['piedra','agua','fuego','lava'].find(w => tr.includes(w)) || 'piedra', hzs = ES ? {piedra:'las piedras',agua:'el agua',fuego:'el fuego',lava:'la lava'}[hz] : {piedra:'the rocks',agua:'the water',fuego:'the fire',lava:'the lava'}[hz];
  const rider = tr.includes('nave') ? T('ship', 'nave') : hero;
  const f = card('f', T('Which way does the ' + rider + ' go?', '¿Por dónde va la ' + rider + '?'), T('You pick the path', 'Elegí vos el camino'));
  [[T('⬆️ Over the top', '⬆️ Por arriba'), 'arriba'], [T('⬇️ Underneath', '⬇️ Por abajo'), 'abajo']].forEach(([t, w]) => { const b = document.createElement('button'); b.textContent = t; b.onclick = () => { state.path = w; win('f', f, T('Okay! Going ' + (w === 'arriba' ? 'over the top' : 'underneath'), '¡Dale! Vamos por ' + w)); }; f.querySelector('.bb').appendChild(b); });
  // 2) question NPC: easy yes/no straight from what the kid said (8–10 años, no trivia)
  const said = /sin tocar|no puede tocar|no tiene que tocar|can't touch|cannot touch|without touching/.test(tr);
  const YES = T('👍 Yes', '👍 Sí'), NO = T('👎 No', '👎 No');
  const q = card('q', T('Can it touch ' + hzs + '?', '¿Puede tocar ' + hzs + '?'), T('From the voice that made this game', 'Según la voz que contó el juego'));
  [[YES, !said], [NO, said]].forEach(([t, ok]) => { const b = document.createElement('button'); b.textContent = t; b.onclick = () => ok ? win('q', q, T('Nice! The path opens', '¡Bien! Se abre el camino')) : (fx(q, false), q.querySelector('.bs').textContent = T('Oops! You said no 😅', '¡Uy! Vos dijiste que no 😅')); q.querySelector('.bb').appendChild(b); });
  // 2) stop-meter: hit when the needle is in the gold zone
  const m = card('m', T('Jump right on time!', '¡Saltá justo!'), T('Press Space when the needle is on the gold', 'Espacio cuando la aguja está en lo dorado')); m.querySelector('.bb').innerHTML = '<div class="meter"><span class="zone"></span><span class="needle"></span></div><button>' + T('Jump!', '¡Saltar!') + '</button>';
  const nd = m.querySelector('.needle'); let ph = 0; const tick = () => { ph += .022; const v = (Math.sin(ph) + 1) / 2; nd.style.left = (v * 100) + '%'; nd.dataset.v = v; if (!state.done.m) requestAnimationFrame(tick); }; tick();
  const jump = () => { const v = +nd.dataset.v; v > .62 && v < .82 ? win('m', m, T('Perfect! jump at ' + Math.round(v * 100) + '%', '¡Perfecto! salto en ' + Math.round(v * 100) + '%')) : (fx(m, false), m.querySelector('.bs').textContent = T('Oops, ' + Math.round(v * 100) + '% — try again', 'Uy, ' + Math.round(v * 100) + '% — de nuevo')); }; m.querySelector('button').onclick = jump; addEventListener('keydown', e => { if (e.code === 'Space' && !state.done.m) { e.preventDefault(); jump(); } });
  // 3) tiny order puzzle: put the tiles in story order
  const o = card('o', T('Build the story', 'Armá el cuento'), T('Tap: 1 drawing, 2 voice, 3 game', 'Tocá: 1 dibujo, 2 voz, 3 juego')); const seq = [T('✏️ Drawing', '✏️ Dibujo'), T('🎙️ Voice', '🎙️ Voz'), T('🎮 Game', '🎮 Juego')]; let k = 0;
  [2, 0, 1].forEach(i => { const b = document.createElement('button'); b.textContent = seq[i]; b.onclick = () => { if (i === k) { b.disabled = true; b.classList.add('on'); if (++k === 3) win('o', o, T('Story built!', '¡Cuento armado!')); } else { k = 0; o.querySelectorAll('button').forEach(z => { z.disabled = false; z.classList.remove('on'); }); fx(o, false); } }; o.querySelector('.bb').appendChild(b); });
  // 4) tic-tac-toe beat vs the monster (random but beatable: monster plays random free cell)
  const t = card('t', T('Tic-tac-toe with the monster', 'Ta-te-tí con el monstruo'), T('You are ⭐, the monster is 👾', 'Vos sos ⭐, él es 👾')); const g = document.createElement('div'); g.className = 'ttt'; t.querySelector('.bb').appendChild(g); const cells = Array(9).fill('');
  const L = [[0,1,2],[3,4,5],[6,7,8],[0,3,6],[1,4,7],[2,5,8],[0,4,8],[2,4,6]], who = s => (L.find(l => l.every(i => cells[i] === s)) ? s : null);
  const reset = () => { cells.fill(''); g.querySelectorAll('b').forEach(c => c.textContent = ''); };
  for (let i = 0; i < 9; i++) { const c = document.createElement('b'); c.onclick = () => play(i); g.appendChild(c); }
  function play(i) { if (state.done.t || cells[i]) return; cells[i] = '⭐'; g.children[i].textContent = '⭐'; if (who('⭐')) return win('t', t, T('You beat the monster!', '¡Le ganaste al monstruo!'));
    const free = cells.map((v, j) => v ? -1 : j).filter(j => j >= 0); if (!free.length) { fx(t, false); return setTimeout(reset, 500); }
    const j = free[R() * free.length | 0]; cells[j] = '👾'; g.children[j].textContent = '👾'; if (who('👾')) { fx(t, false); t.querySelector('.bs').textContent = T('The monster won 👾 — rematch', 'Te ganó 👾 — revancha'); setTimeout(reset, 700); } }
  // stagger: cards appear one at a time (timed cascade; autoplay reveals each right before playing it)
  const cards = [...host.querySelectorAll('.beat')]; cards.forEach(c => c.classList.add('hid'));
  const show = c => { if (!c.classList.contains('hid')) return; c.classList.remove('hid'); fx(c, true); };
  cards.forEach((c, i) => setTimeout(() => show(c), 900 + i * 650)); state.show = show;
  // agent autoplay: proves each beat is clearable (verification, like the solver for the board)
  state.autoplay = async () => { const sl = ms => new Promise(r => setTimeout(r, ms));
    show(f); await sl(120); f.querySelectorAll('button')[0].click(); await sl(200); show(q); await sl(120); [...q.querySelectorAll('button')].find(b => b.textContent === (said ? NO : YES)).click(); await sl(200);
    show(m); await sl(120); while (!state.done.m) { const v = +nd.dataset.v; if (v > .66 && v < .78) jump(); await sl(16); }
    show(o); await sl(120); for (const want of seq) { [...o.querySelectorAll('button')].find(b => b.textContent === want).click(); await sl(150); }
    show(t); await sl(120); for (let n = 0; n < 40 && !state.done.t; n++) { const pick = L.map(l => l.filter(i => cells[i] !== '👾')).find(l => l.length === 3 && l.some(i => !cells[i])); const i = pick ? pick.find(i => !cells[i]) : cells.indexOf(''); i >= 0 ? play(i) : reset(); await sl(120); }
    return state.done; };
})();
// ---- On-board beats (gates): window.__GATES__ from agent/gates.py. Stepping on a locked 🔀/❓/🎯 cell opens this overlay over the
// board; success opens the door (game.js openGate), a wrong answer keeps it shut (failGate: shake + red burst) -> stuck until solved.
(function () {
  const G = window.__GATES__ || [], wrap = document.getElementById('wrap'); if (!G.length || !wrap) return;
  const ES = new URLSearchParams(location.search).get('lang') === 'es', T = (en, es) => ES ? es : en;
  const ov = document.createElement('div'); ov.id = 'gate'; ov.innerHTML = '<div class="gc"><div class="gk"></div><div class="gt"></div><div class="gs"></div><div class="gb"></div></div>';
  document.body.appendChild(ov);
  const $ = s => ov.querySelector(s), st = window.__BEATS__ || (window.__BEATS__ = { done: {}, log: [] }); st.gates = {}; st.gateLog = [];
  const ICON = { fork: T('🔀 Path', '🔀 Camino'), question: T('❓ Question', '❓ Pregunta'), meter: T('🎯 Jump', '🎯 Salto') };
  let cur = null, raf = 0, frame = 0;
  const isNo = a => /^(👎\s*)?no$/i.test(String(a == null ? '' : a).trim());
  const loc = g => Object.assign({}, g, {
    prompt: ES ? (g.prompt_es || g.prompt) : g.prompt,
    options: ES ? (g.options_es || g.options || []) : (g.options || []),
    answer: ES ? (g.answer_es != null ? g.answer_es : g.answer) : g.answer
  });
  const sparks = (ok) => { for (let i = 0; i < (ok ? 22 : 10); i++) { const p = document.createElement('i'); p.className = 'pt' + (ok ? '' : ' r'); p.style.setProperty('--dx', (Math.random() * 260 - 130) + 'px'); p.style.setProperty('--dy', (-Math.random() * 140 - 20) + 'px'); $('.gc').appendChild(p); setTimeout(() => p.remove(), 900); } };
  const close = () => { cancelAnimationFrame(raf); ov.className = ''; cur = null; };
  const good = (g, side, msg) => { st.gates[g.id] = true; st.gateLog.push([g.id, 'ok']); $('.gs').textContent = msg; ov.classList.add('ok'); sparks(true); window.__GAME__.openGate(g.id, side); setTimeout(close, 650); };
  const bad = (g, msg) => { st.gateLog.push([g.id, 'fail']); $('.gs').textContent = msg; ov.classList.remove('no'); void ov.offsetWidth; ov.classList.add('no'); sparks(false); window.__GAME__.failGate(g.id); };
  const btn = (t, f) => { const b = document.createElement('button'); b.textContent = t; b.onclick = f; $('.gb').appendChild(b); return b; };
  window.__onGate = (g0) => { if (cur) return; const g = loc(g0); cur = g;
    ov.style.position = 'fixed'; ov.style.inset = '0'; ov.style.zIndex = '80'; ov.className = 'on ' + g.kind;
    $('.gk').textContent = ICON[g.kind]; $('.gt').textContent = g.prompt; $('.gb').innerHTML = ''; $('.gs').textContent = '';
    if (g.kind === 'fork') { $('.gs').textContent = T('You choose: the door you don\'t pick closes 🧱', 'Elegí vos: la puerta que no elijas se cierra 🧱');
      btn(g.options[0], () => good(g, 'A', T('Let\'s go! That path opens ✨', '¡Dale! Se abre ese camino ✨'))); btn(g.options[1], () => g.alt ? good(g, 'B', T('Let\'s take the other way! ✨', '¡Vamos por el otro lado! ✨')) : bad(g, T('Oops! There\'s a wall there — try the other one', '¡Uy! Ahí hay pared 🧱 — probá el otro'))); }
    if (g.kind === 'question') { $('.gs').textContent = T('From the voice that made this game 🎙️', 'Acordate lo que dijiste 🎙️');
      (g.options || []).forEach(o => btn(o, () => String(o).includes(g.answer) ? good(g, 'A', T('Nice! The door opens 🔓', '¡Bien! La puerta se abre 🔓')) : bad(g, isNo(g.answer) ? T('Oops! You said NO 😅', '¡Uy! Vos dijiste que NO puede 😅') : T('Oops! You said yes 😅', '¡Uy! Vos dijiste que sí 😅')))); }
    if (g.kind === 'meter') { $('.gs').textContent = T('Tap Jump! (or Space) when the needle is on the gold', 'Tocá ¡Saltar! (o Espacio) cuando la aguja está en lo dorado');
      $('.gb').innerHTML = '<div class="meter big"><span class="zone"></span><span class="needle"></span></div>'; const nd = $('.needle'); frame = 0;
      const tick = () => { frame++; const v = (Math.sin(frame * 0.022) + 1) / 2; nd.style.left = (v * 100) + '%'; nd.dataset.v = v; nd.dataset.k = frame; raf = requestAnimationFrame(tick); }; tick();
      btn(T('🦘 Jump!', '🦘 ¡Saltar!'), () => { const v = +nd.dataset.v; v > g.zone[0] && v < g.zone[1] ? good(g, 'A', T('Perfect! ' + Math.round(v * 100) + '% 🎯', '¡Perfecto! ' + Math.round(v * 100) + '% 🎯')) : bad(g, T('Oops, ' + Math.round(v * 100) + '% — try again', 'Uy, ' + Math.round(v * 100) + '% — ¡de nuevo!')); }); } };
  addEventListener('keydown', e => { if (cur && cur.kind === 'meter' && e.code === 'Space') { e.preventDefault(); e.stopImmediatePropagation(); $('.gb button').click(); } }, true);
  // agent: clear the open gate deterministically (fork A, localized answer, meter pressed in the zone); wrongFirst = show the block
  st.clearGate = async (wrongFirst) => { const sl = ms => new Promise(r => setTimeout(r, ms)); const g = cur; if (!g) return false; await sl(450);
    const bs = [...ov.querySelectorAll('.gb button')];
    if (wrongFirst && g.kind === 'question') { bs.find(b => !b.textContent.includes(g.answer)).click(); await sl(900); }
    if (g.kind === 'fork') bs[0].click(); else if (g.kind === 'question') [...ov.querySelectorAll('.gb button')].find(b => b.textContent.includes(g.answer)).click();
    else { const nd = $('.needle'); for (let n = 0; n < 2000 && cur; n++) { const v = +nd.dataset.v; if (v > g.zone[0] + .04 && v < g.zone[1] - .04) { $('.gb button').click(); break; } await sl(8); } }
    await sl(700); return !!st.gates[g.id]; };
  // side cards f/q/m now live on the board: label them
  ['f', 'q', 'm'].forEach(id => { const c = document.getElementById('beat-' + id); if (c) { const tg = document.createElement('div'); tg.className = 'onb'; tg.textContent = T('🔒 Also on the board', '🔒 también en el tablero'); c.appendChild(tg); } });
})();
