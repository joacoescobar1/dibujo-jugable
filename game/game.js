// Canvas grid game driven by a spec. Exposes window.__GAME__ state API for agent playtests.
// ?spec=<url> loads another spec; ?attempt=N sets HUD; ?timeline=<url> loads a timeline JSON (demo reel).
(async () => {
  const q = new URLSearchParams(location.search);
  const UI_ES = q.get('lang') === 'es', UI = (en, es) => UI_ES ? es : en;
  let spec = window.__SPEC__;
  if (!spec) { try { spec = await (await fetch(q.get('spec') || 'spec.json')).json(); } catch (e) { spec = null; } }
  if (!spec || !spec.grid) { const msg = document.createElement('p'); msg.textContent = UI('This page could not load the level.', 'Esta página no pudo cargar el nivel.'); document.body.appendChild(msg); return; }
  const T = spec.grid.tile || 40, c = document.getElementById('c'), x = c.getContext('2d'), $ = id => document.getElementById(id);
  c.width = spec.grid.w * T; c.height = spec.grid.h * T; const shownTitle = (UI_ES && spec.title_es) ? spec.title_es : spec.title; if ($('t')) $('t').textContent = (!UI_ES && window.__tr) ? window.__tr(shownTitle) : shownTitle;
  const inR = (p, r) => p.x >= r.x && p.x < r.x + (r.w || 1) && p.y >= r.y && p.y < r.y + (r.h || 1);
  // tick model shared with agent/playtest.py: every action (move/bump/wait) = 1 tick = 1 "second"; enemies then step their cyclic patrol
  const ENEMIES = (spec.characters || []).filter(c => c.role === 'enemy'), NPCS = (spec.characters || []).filter(c => c.role !== 'enemy');
  const DOOR = window.__NO_DOOR__ ? null : spec.door || null; // world scenes: win unlocks the door, stepping on it ends the scene
  const WC = spec.win_condition, SURVIVE = WC.type === 'survive_seconds', COLLECT = WC.type === 'collect_all';
  const initFoes = () => ENEMIES.map(e => ({ id: e.id, label: e.label, color: e.color, x: e.x, y: e.y, patrol: e.patrol || [] }));
  const S = { status: 'playing', steps: 0, ticks: 0, attempt: +(q.get('attempt') || 1), player: { ...spec.player }, foes: initFoes(), events: [], collected: [] };
  const GATES = (window.__GATES__ || []).map(g => ({ ...g, open: false, sealed: false }));
  const blocked = p => p.x < 0 || p.y < 0 || p.x >= spec.grid.w || p.y >= spec.grid.h || (spec.walls || []).some(w => inR(p, w));
  function move(dx, dy) { if (window.__PAUSED__) return;
    if (S.status !== 'playing') return state();
    const n = { x: S.player.x + dx, y: S.player.y + dy };
    // on-board beats (window.__GATES__, agent/gates.py mirrors): locked gate = no move, no tick, overlay opens; sealed fork door = wall
    if ((dx || dy) && GATES.length) { const hc = c => c && c[0] === n.x && c[1] === n.y;
      const sg = GATES.find(g => g.sealed && hc(g.alt)), lg = GATES.find(g => !g.open && (hc(g.cell) || (g.kind === 'fork' && hc(g.alt))));
      if (sg) { S.events.push('sealed:' + sg.id); FX.shake = Math.max(FX.shake, 4); return fin(); }
      if (lg) { S.events.push('gate:' + lg.id); FX.shake = Math.max(FX.shake, 3); if (window.__onGate) window.__onGate(lg, hc(lg.alt) ? 'B' : 'A'); return fin(); } }
    if (dx || dy) { if (blocked(n)) S.events.push('bump'); else { S.player.x = n.x; S.player.y = n.y; S.steps++; } } else S.events.push('wait');
    const p = S.player, hit = () => S.foes.find(f => f.x === p.x && f.y === p.y);
    const hz = (spec.hazards || []).find(h => inR(p, h));
    if (hz) { S.status = 'lost'; S.events.push('hazard:' + hz.id); return fin(); }
    // swap rule (parity w/ playtest.py): player stepping onto an enemy's pre-move cell loses here, so a same-tick cell swap is always a loss
    if (hit()) { S.status = 'lost'; S.events.push('enemy:' + hit().id); return fin(); }
    if (DOOR && S.doorOpen && p.x === DOOR.x && p.y === DOOR.y) { S.status = 'won'; S.events.push('door:' + DOOR.id); S.events.push('win'); return fin(); }
    if (COLLECT) { spec.goals.filter(g => inR(p, g) && !S.collected.includes(g.id)).forEach(g => { S.collected.push(g.id); S.events.push('collect:' + g.id); });
      if (S.collected.length === spec.goals.length) { if (DOOR) { if (!S.doorOpen) { S.doorOpen = true; S.events.push('door_open'); } } else { S.status = 'won'; S.events.push('win'); return fin(); } } }
    else if (!SURVIVE && spec.goals.some(g => g.id === WC.target && inR(p, g))) { if (window.__VOICE_FAIL__) { S.status = 'lost'; S.events.push('voice_rule'); return fin(); } if (DOOR) { if (!S.doorOpen) { S.doorOpen = true; S.events.push('door_open'); } } else { S.status = 'won'; S.events.push('win'); return fin(); } }
    S.foes.forEach(f => { if (!f.patrol.length) return; const [a, b] = f.patrol[S.ticks % f.patrol.length], m = { x: f.x + a, y: f.y + b }; if (!blocked(m)) { f.x = m.x; f.y = m.y; } });
    S.ticks++;
    if (hit()) { S.status = 'lost'; S.events.push('enemy:' + hit().id); }
    else if (SURVIVE && S.ticks >= WC.seconds) { S.status = 'won'; S.events.push('win'); }
    return fin();
  }
  function fin() { draw(); return state(); }
  // rules shared with agent/playtest.py (see scripts/parity_check.md): spawn inside hazard = instant loss
  function spawnCheck() { const hz = (spec.hazards || []).find(h => inR(S.player, h)); if (hz) { S.status = 'lost'; S.events.push('spawn_in_hazard:' + hz.id); }
    const f = S.foes.find(f => f.x === S.player.x && f.y === S.player.y); if (f && S.status === 'playing') { S.status = 'lost'; S.events.push('spawn_on_enemy:' + f.id); } }
  function reset() { FX.seen = { status: 'playing', col: 0 }; FX.parts = []; FX.trail = []; GATES.forEach(g => { g.open = false; g.sealed = false; g.shownAt = 0; }); Object.assign(S, { status: 'playing', steps: 0, ticks: 0, doorOpen: false, player: { ...spec.player }, foes: initFoes(), events: [], collected: [] }); spawnCheck(); draw(); }
  // ---- render layer (visual only; game rules above untouched -> parity with agent/playtest.py preserved) ----
  // "Tu dibujo cobra vida": hand-drawn doodle sprites keyed by entity name, kid's drawing faintly inked into the paper.
  const PAL = { ink: '#2b2118', paper: '#fdf6e3' };
  const rnd = s => { let h = 2166136261; for (const ch of String(s)) h = Math.imul(h ^ ch.charCodeAt(0), 16777619); return () => ((h = Math.imul(h ^ (h >>> 15), 2246822507) ^ Math.imul(h ^ (h >>> 13), 3266489909)) >>> 0) / 4294967296; };
  const KIND = id => { id = String(id || '').toLowerCase();
    for (const [k, ws] of Object.entries({ perro: ['perro','dog','perrito'], gato: ['gato','gatito','cat'], nave: ['nave','ship','cohete'], dragon: ['dragon','dragón'],
      estrella: ['estrella','star'], casa: ['casa','house','hogar'], hueso: ['hueso','bone'], castillo: ['castillo','castle'], piedras: ['piedra','rock'], agua: ['agua','rio','río','water','charco'], fuego: ['fuego','fire','lava'] }))
      if (ws.some(w => id.includes(w))) return k; return null; };
  let DRAW = null; if (window.__DRAWING__) { DRAW = new Image(); DRAW.onload = buildCuts; DRAW.src = window.__DRAWING__; }
  // "Tu dibujo cobra vida" v2 (display-only): cut the kid's REAL ink out of the photo and use it as the sprite.
  // Enemies: same violet-component rule as scripts/generate_from_drawing.py read_enemies (cell >=15% violet, 4-connected,
  // body = densest cell), so enemy i wears the monster the kid drew even after the fixer moved its spawn. Player/goals/NPCs:
  // any ink (non-paper, non-hazard) at their spawn cell. Paper keyed to transparent. No ink -> doodle sprite fallback.
  const CUT = { enemy: [], at: {}, wall: {} };
  // Art pass (display-only): lit-paper plate behind the board + Image-cleaned SAM sprites of the kid's ink, keyed by role.
  const ld = u => { const i = new Image(); i.src = u; return i; }, ok = i => i && i.complete && i.naturalWidth;
  const PLATE = window.__PLATE__ ? ld(window.__PLATE__) : null; const ART = Object.fromEntries(Object.entries(window.__ART__ || {}).map(([k, v]) => [k, ld(v)]));
  function buildCuts() { try {
    const W = spec.grid.w, H = spec.grid.h, cw = Math.max(10, Math.round(DRAW.naturalWidth / W)), ch = Math.max(10, Math.round(DRAW.naturalHeight / H));
    const o = document.createElement('canvas'); o.width = W * cw; o.height = H * ch; const ox = o.getContext('2d'); ox.drawImage(DRAW, 0, 0, o.width, o.height);
    const D = ox.getImageData(0, 0, o.width, o.height).data, P = (i) => [D[i], D[i + 1], D[i + 2]];
    const hsv = (r, g, b) => { const M = Math.max(r, g, b), m = Math.min(r, g, b), d = M - m; let h = 0; if (d) h = M === r ? ((g - b) / d) % 6 : M === g ? (b - r) / d + 2 : (r - g) / d + 4; return [(h * 60 + 360) % 360, M ? d / M : 0, M / 255]; };
    const violet = (r, g, b) => { if (r > 110 && b > 150 && g < 60 && Math.abs(r - b) < 110) return true; const [h, s_, v] = hsv(r, g, b); return h >= 255 && h <= 320 && s_ >= .25 && v >= .25 && v <= .97; };
    const hazardish = (r, g, b) => (b > 180 && r < 80 && g < 80) || (r > 180 && g < 80 && b < 80) || (100 < r && r < 160 && Math.abs(r - g) < 12 && Math.abs(g - b) < 12) || (110 < r && r < 170 && 50 < g && g < 90 && b < 40);
    const inkish = (r, g, b) => { const [, s_, v] = hsv(r, g, b); return v < .55 || (s_ > .3 && v < .98); };
    const cellCount = (cx, cy, f) => { let n = 0; for (let j = 0; j < ch; j++) for (let i = 0; i < cw; i++) { const k = ((cy * ch + j) * o.width + cx * cw + i) * 4; if (f(...P(k))) n++; } return n / (cw * ch); };
    const cut = (x0, y0, x1, y1, keep) => { const w = x1 - x0, h = y1 - y0, cc = document.createElement('canvas'); cc.width = w; cc.height = h; const cx2 = cc.getContext('2d'), img = cx2.createImageData(w, h); let n = 0;
      for (let j = 0; j < h; j++) for (let i = 0; i < w; i++) { const k = ((y0 + j) * o.width + x0 + i) * 4, q = (j * w + i) * 4, [r, g, b] = P(k); if (keep(r, g, b)) { img.data[q] = r; img.data[q + 1] = g; img.data[q + 2] = b; img.data[q + 3] = 255; n++; } }
      cx2.putImageData(img, 0, 0); return n > 12 ? cc : null; };
    // Bodies come from the SAME reader that built the spec (coverage() w/ edge unmixing) when the page has them, so a photo
    // cell at ~15% can't make JS and Python disagree on which blob is enemy i. JS rule below = fallback for plain index.html.
    const PB = Array.isArray(window.__ENEMY_BODIES__) ? window.__ENEMY_BODIES__ : null;
    if (PB) PB.forEach(body => CUT.enemy.push(cut(Math.max(0, (body[0] - .5) * cw | 0), Math.max(0, (body[1] - .5) * ch | 0), Math.min(o.width, (body[0] + 1.5) * cw | 0), Math.min(o.height, (body[1] + 1.5) * ch | 0), violet)));
    const ink = {}; if (!PB) for (let cx = 0; cx < W; cx++) for (let cy = 0; cy < H; cy++) { const f = cellCount(cx, cy, violet); if (f >= .15) ink[cx + ',' + cy] = f; }
    const JSB = [];
    const keys = Object.keys(ink).map(k => k.split(',').map(Number)).sort((a, b) => a[0] - b[0] || a[1] - b[1]), seen = new Set();
    for (const c0 of keys) { const k0 = c0.join(','); if (seen.has(k0)) continue; seen.add(k0); const comp = [], st = [c0];
      while (st.length) { const c = st.pop(); comp.push(c); for (const [dx, dy] of [[1, 0], [-1, 0], [0, 1], [0, -1]]) { const n = [c[0] + dx, c[1] + dy], nk = n.join(','); if (ink[nk] && !seen.has(nk)) { seen.add(nk); st.push(n); } } }
      const body = comp.reduce((a, b) => (ink[b.join(',')] > ink[a.join(',')] || (ink[b.join(',')] === ink[a.join(',')] && (b[0] < a[0] || (b[0] === a[0] && b[1] < a[1])))) ? b : a);
      JSB.push(body); CUT.enemy.push(cut(Math.max(0, (body[0] - .5) * cw | 0), Math.max(0, (body[1] - .5) * ch | 0), Math.min(o.width, (body[0] + 1.5) * cw | 0), Math.min(o.height, (body[1] + 1.5) * ch | 0), violet)); }
    [spec.player, ...(spec.goals || []), ...NPCS].forEach(e => { if (!e || cellCount(e.x, e.y, (r, g, b) => inkish(r, g, b) && !hazardish(r, g, b) && !violet(r, g, b)) < .06) return;
      CUT.at[e.id] = cut(Math.max(0, (e.x - .6) * cw | 0), Math.max(0, (e.y - .6) * ch | 0), Math.min(o.width, (e.x + 1.6) * cw | 0), Math.min(o.height, (e.y + 1.6) * ch | 0), (r, g, b) => inkish(r, g, b) && !hazardish(r, g, b) && !violet(r, g, b)); });  // violet = enemy ink: a monster drawn ON the star must not be baked into the star sprite (it would stay there after the fixer moves it)
    // Rocks/walls: each wall cell wears the kid's own ink found in that cell (rock drawn at that spot), else the generic tile.
    [...(spec.walls || []), ...(spec.hazards || [])].forEach(w => { for (let i = 0; i < (w.w || 1); i++) for (let j = 0; j < (w.h || 1); j++) { const gx = w.x + i, gy = w.y + j, kk = (r, g, b) => inkish(r, g, b) && !violet(r, g, b);
      if (gx >= W || gy >= H || cellCount(gx, gy, kk) < .04) continue; const c = cut(gx * cw, gy * ch, Math.min(o.width, (gx + 1) * cw), Math.min(o.height, (gy + 1) * ch), kk); if (c) CUT.wall[gx + ',' + gy] = c; } });
    window.__CUT_CANVASES__ = CUT; window.__CUTS__ = { walls: Object.keys(CUT.wall).length, src: PB ? 'spec' : 'js', bodies: PB || JSB, enemies: CUT.enemy.filter(Boolean).length, others: Object.keys(CUT.at).filter(k => CUT.at[k]).length };
  } catch (e) { window.__CUTS__ = { error: String(e) }; } }
  function cutSprite(img, role, cx, cy, s, t, seed) { // the kid's own scribble, alive: squash-stretch, wobble, crayon halo
    const sc = s * (window.__ART3D__ ? 1.3 : 1.1) / Math.max(img.width, img.height), w = img.width * sc, h = img.height * sc, k = rnd(seed)() * 6;
    const sq = 1 + Math.sin(t / 180 + k) * .06, rot = Math.sin(t / 340 + k) * (role === 'enemy' ? .09 : .045);
    x.save(); x.translate(cx, cy); x.rotate(rot); x.scale(1 / sq, sq);
    x.shadowColor = role === 'enemy' ? 'rgba(171,71,188,.55)' : role === 'goal' ? 'rgba(255,213,79,.8)' : 'rgba(66,165,245,.55)'; x.shadowBlur = 10;
    x.drawImage(img, -w / 2, -h / 2, w, h); x.shadowBlur = 0; x.globalAlpha = .9; x.drawImage(img, -w / 2, -h / 2, w, h);
    if (role === 'enemy' && !window.__ART3D__) eyes(0, -h * .08, Math.min(w, h) * .8, rnd(seed), 1); x.restore(); }
  function wob(pts, r, close = true, amp = 1.6) { // sketchy double-stroke path
    for (let pass = 0; pass < 2; pass++) { x.beginPath(); pts.forEach(([a, b], i) => { const px = a + (r() - .5) * amp, py = b + (r() - .5) * amp; i ? x.lineTo(px, py) : x.moveTo(px, py); }); if (close) x.closePath(); x.stroke(); } }
  function blob(cx, cy, rx, ry, r, n = 14, j = .12) { const p = []; for (let i = 0; i < n; i++) { const a = i / n * Math.PI * 2, k = 1 + (r() - .5) * j; p.push([cx + Math.cos(a) * rx * k, cy + Math.sin(a) * ry * k]); } return p; }
  function fillPath(pts, col) { x.beginPath(); pts.forEach(([a, b], i) => i ? x.lineTo(a, b) : x.moveTo(a, b)); x.closePath(); x.fillStyle = col; x.fill(); }
  function crayon(pts, col, r) { fillPath(pts, col); x.save(); x.clip(); x.globalAlpha = .18; x.strokeStyle = '#fff'; x.lineWidth = 1.2; // crayon grain
    const xs = pts.map(p => p[0]), ys = pts.map(p => p[1]), x0 = Math.min(...xs), x1 = Math.max(...xs), y0 = Math.min(...ys), y1 = Math.max(...ys);
    for (let k = x0 - (y1 - y0); k < x1; k += 4) { x.beginPath(); x.moveTo(k + r() * 2, y1); x.lineTo(k + (y1 - y0) + r() * 2, y0); x.stroke(); } x.restore(); }
  function shape(pts, col, r, lw = 2.4) { crayon(pts, col, r); x.strokeStyle = PAL.ink; x.lineWidth = lw; x.lineJoin = x.lineCap = 'round'; wob(pts, r); }
  function eyes(cx, cy, s, r, mood = 0) { [-1, 1].forEach(d => { x.fillStyle = '#fff'; x.beginPath(); x.ellipse(cx + d * s * .28, cy, s * .16, s * .19, 0, 0, 7); x.fill(); x.strokeStyle = PAL.ink; x.lineWidth = 1.5; x.stroke();
    x.fillStyle = PAL.ink; x.beginPath(); x.arc(cx + d * s * .28 + s * .03, cy + s * .04, Math.max(0.01, s * .08), 0, 7); x.fill();
    if (mood) { x.lineWidth = 2.2; x.beginPath(); x.moveTo(cx + d * s * .12, cy - s * .2); x.lineTo(cx + d * s * .44, cy - s * .3); x.stroke(); } }); }
  function shadow(cx, cy, w) { x.save(); x.fillStyle = '#3a2a1a'; x.globalAlpha = .18; x.beginPath(); x.ellipse(cx, cy, w * .42, w * .12, 0, 0, 7); x.fill(); x.restore(); }
  function star(cx, cy, R, r, rot = 0) { const p = []; for (let i = 0; i < 10; i++) { const a = rot - Math.PI / 2 + i * Math.PI / 5, rr = i % 2 ? R * .45 : R; p.push([cx + Math.cos(a) * rr, cy + Math.sin(a) * rr]); } return p; }
  function sprite(kind, role, cx, cy, s, seed, t) { const r = rnd(seed); x.lineCap = x.lineJoin = 'round';
    if (kind === 'perro') { shape(blob(cx, cy + s * .08, s * .42, s * .34, r), '#f4a259', r);
      shape(blob(cx - s * .38, cy - s * .12, s * .12, s * .24, r, 9), '#8d5524', r); shape(blob(cx + s * .38, cy - s * .12, s * .12, s * .24, r, 9), '#8d5524', r);
      eyes(cx, cy - s * .02, s, r); x.fillStyle = PAL.ink; x.beginPath(); x.ellipse(cx, cy + s * .17, s * .08, s * .06, 0, 0, 7); x.fill();
      x.strokeStyle = '#e57373'; x.lineWidth = 3; x.beginPath(); x.moveTo(cx, cy + s * .25); x.lineTo(cx + s * .03, cy + s * .34 + Math.sin(t / 150) * 2); x.stroke(); return; }
    if (kind === 'gato') { shape([[cx - s * .4, cy - s * .05], [cx - s * .32, cy - s * .45], [cx - s * .1, cy - s * .25], [cx + s * .1, cy - s * .25], [cx + s * .32, cy - s * .45], [cx + s * .4, cy - s * .05], [cx + s * .3, cy + s * .35], [cx - s * .3, cy + s * .35]], '#b0bec5', r);
      eyes(cx, cy, s, r); x.strokeStyle = PAL.ink; x.lineWidth = 1.2; [-1, 1].forEach(d => { for (const k of [-.04, .06]) { x.beginPath(); x.moveTo(cx + d * s * .12, cy + s * .18); x.lineTo(cx + d * s * .45, cy + s * (.15 + k)); x.stroke(); } }); return; }
    if (kind === 'nave') { shape([[cx, cy - s * .48], [cx + s * .22, cy - s * .05], [cx + s * .22, cy + s * .3], [cx - s * .22, cy + s * .3], [cx - s * .22, cy - s * .05]], '#90caf9', r);
      shape(blob(cx, cy + s * .42, s * .12, s * .1 + Math.sin(t / 90) * 2, r, 8), '#ff7043', r, 1.5); x.fillStyle = '#fff'; x.beginPath(); x.arc(cx, cy, s * .1, 0, 7); x.fill(); x.stroke(); return; }
    if (kind === 'dragon') { shape(blob(cx, cy + s * .05, s * .4, s * .32, r), '#81c784', r); shape([[cx - s * .3, cy - s * .2], [cx - s * .5, cy - s * .45], [cx - s * .15, cy - s * .3]], '#4caf50', r); eyes(cx, cy - s * .02, s, r); return; }
    if (kind === 'estrella') { const g = 1 + Math.sin(t / 300) * .06; x.save(); x.globalAlpha = .35 + Math.sin(t / 300) * .15; x.fillStyle = '#fff59d'; x.beginPath(); x.arc(cx, cy, s * .55, 0, 7); x.fill(); x.restore();
      shape(star(cx, cy, s * .46 * g, r, Math.sin(t / 900) * .15), '#ffd54f', r); eyes(cx, cy + s * .02, s * .7, r); return; }
    if (kind === 'casa') { shape([[cx - s * .38, cy - s * .02], [cx + s * .38, cy - s * .02], [cx + s * .38, cy + s * .4], [cx - s * .38, cy + s * .4]], '#ffcc80', r);
      shape([[cx - s * .48, cy], [cx, cy - s * .45], [cx + s * .48, cy]], '#e53935', r); shape([[cx - s * .1, cy + s * .15], [cx + s * .1, cy + s * .15], [cx + s * .1, cy + s * .4], [cx - s * .1, cy + s * .4]], '#6d4c41', r, 1.8); return; }
    if (kind === 'hueso') { [[-1, -1], [-1, 1], [1, -1], [1, 1]].forEach(([a, b]) => shape(blob(cx + a * s * .32, cy + b * s * .1, s * .12, s * .12, r, 8), '#fafafa', r, 2));
      shape([[cx - s * .32, cy - s * .08], [cx + s * .32, cy - s * .08], [cx + s * .32, cy + s * .08], [cx - s * .32, cy + s * .08]], '#fafafa', r, 2); return; }
    if (kind === 'castillo') { shape([[cx - s * .4, cy + s * .4], [cx - s * .4, cy - s * .3], [cx - s * .2, cy - s * .3], [cx - s * .2, cy - s * .15], [cx, cy - s * .15], [cx, cy - s * .3], [cx + s * .2, cy - s * .3], [cx + s * .2, cy - s * .15], [cx + s * .4, cy - s * .15], [cx + s * .4, cy + s * .4]], '#bdbdbd', r); return; }
    if (role === 'enemy') { const p = []; for (let i = 0; i < 16; i++) { const a = i / 16 * Math.PI * 2, k = i % 2 ? .3 : .44; p.push([cx + Math.cos(a) * s * k, cy + Math.sin(a) * s * k]); } shape(p, '#ef5350', r); eyes(cx, cy, s * .9, r, 1); return; }
    const col = { player: '#ffb74d', goal: '#aed581', npc: '#ce93d8' }[role] || '#ce93d8'; shape(blob(cx, cy, s * .4, s * .36, r), col, r); if (role !== 'goal') eyes(cx, cy, s, r); }
  function tile(kind, e, gx, gy, t) { const r = rnd(e.id + gx + ',' + gy), X = gx * T, Y = gy * T;
    if (kind === 'agua') { crayon([[X, Y], [X + T, Y], [X + T, Y + T], [X, Y + T]], '#64b5f6', r); x.strokeStyle = '#1565c0'; x.lineWidth = 2;
      for (let k = 0; k < 2; k++) { x.beginPath(); for (let i = 0; i <= T; i += 4) x.lineTo(X + i, Y + T * (.35 + k * .35) + Math.sin((i + gx * T + t / 40) / 6) * 2.5); x.stroke(); } return; }
    if (kind === 'fuego') { const f = Math.sin(t / 120 + gx + gy) * 3; shape([[X + T * .15, Y + T * .9], [X + T * .2, Y + T * .45], [X + T * .35, Y + T * .55], [X + T * .5, Y + T * .1 + f], [X + T * .65, Y + T * .5], [X + T * .8, Y + T * .35], [X + T * .85, Y + T * .9]], '#ff7043', r, 2);
      crayon([[X + T * .35, Y + T * .88], [X + T * .5, Y + T * .45 + f], [X + T * .65, Y + T * .88]], '#ffd54f', r); return; }
    // piedras / generic hazard: lumpy rocks
    [[.32, .4, .26], [.7, .62, .22], [.3, .78, .16]].forEach(([a, b, k]) => shape(blob(X + T * a, Y + T * b, T * k, T * k * .8, r, 10, .3), ['#9e9e9e', '#8d8d8d', '#bdbdbd'][Math.floor(r() * 3)], r, 1.8)); }
  function wallTile(gx, gy) { const r = rnd('w' + gx + ',' + gy), X = gx * T, Y = gy * T; shape([[X + 1, Y + 1], [X + T - 1, Y + 1], [X + T - 1, Y + T - 1], [X + 1, Y + T - 1]], '#a1887f', r, 2);
    x.strokeStyle = '#5d4037'; x.lineWidth = 1.2; for (const k of [.33, .66]) { x.beginPath(); x.moveTo(X + 3, Y + T * k); x.lineTo(X + T - 3, Y + T * k + (r() - .5) * 2); x.stroke(); } }
  function placeTags(req) { // greedy label layout: same spot if free, else nearest free slot (below/above/sideways), never off the board
    x.font = 'bold 12px "Comic Sans MS","Chalkboard SE","Comic Neue",cursive'; const placed = [], out = [];
    const hit = (b) => placed.some(q => Math.min(b.x1, q.x1) - Math.max(b.x0, q.x0) > 0 && Math.min(b.y1, q.y1) - Math.max(b.y0, q.y0) > 0);
    for (const [l, cx0, y0] of req) { if (!l) continue; const w = x.measureText(l).width + 12; let best = null;
      for (const dy of [0, 17, -17, 34, -34, 51, -51, 68, -68]) { for (const dx of [0, -(w / 2 + 4), w / 2 + 4, -w, w]) {
        const y = Math.min(Math.max(y0 + dy, 0), c.height - 17), cx = Math.min(Math.max(cx0 + dx, w / 2 + 2), c.width - w / 2 - 2), b = { x0: cx - w / 2 - 1, x1: cx + w / 2 + 1, y0: y, y1: y + 16 };
        if (!hit(b)) { best = [cx, y, b]; break; } } if (best) break; }
      if (!best) { const cx = Math.min(Math.max(cx0, w / 2 + 2), c.width - w / 2 - 2), y = Math.min(Math.max(y0, 0), c.height - 17); best = [cx, y, { x0: cx - w / 2, x1: cx + w / 2, y0: y, y1: y + 16 }]; }
      placed.push(best[2]); out.push([l, best[0], best[1]]); }
    return out; }
  function tag(text, cx, y) { if (!text) return; x.font = 'bold 12px "Comic Sans MS","Chalkboard SE","Comic Neue",cursive'; const w = x.measureText(text).width + 12; cx = Math.min(Math.max(cx, w / 2 + 2), c.width - w / 2 - 2);  // never clip a label at the board edge
    x.fillStyle = '#fffdf5e6'; x.strokeStyle = '#2b211855'; x.lineWidth = 1; x.beginPath(); x.roundRect ? x.roundRect(cx - w / 2, y, w, 16, 8) : x.rect(cx - w / 2, y, w, 16); x.fill(); x.stroke();
    x.fillStyle = PAL.ink; x.textAlign = 'center'; x.fillText(text, cx, y + 12); x.textAlign = 'left'; return { text, x0: cx - w / 2, x1: cx + w / 2, y0: y, y1: y + 16 }; }
  function paper() { x.fillStyle = PAL.paper; x.fillRect(0, 0, c.width, c.height);
    if (ok(PLATE)) { const r = Math.max(c.width / PLATE.naturalWidth, c.height / PLATE.naturalHeight), w = PLATE.naturalWidth * r, h = PLATE.naturalHeight * r; x.save(); x.globalAlpha = window.__PLATE_EMPTY__ ? 1 : .9; x.filter = 'saturate(1.15) contrast(1.05)'; x.drawImage(PLATE, (c.width - w) / 2, (c.height - h) / 2, w, h); x.restore(); }
    if (window.__PLATE_EMPTY__ && ok(PLATE)) return; // 3D film plate: no notebook lines / doodle overlay
    x.strokeStyle = '#90a4ae22'; x.lineWidth = 1; for (let j = T; j < c.height; j += T / 2) { x.beginPath(); x.moveTo(0, j); x.lineTo(c.width, j); x.stroke(); }
    x.strokeStyle = '#e5737333'; x.beginPath(); x.moveTo(T * .6, 0); x.lineTo(T * .6, c.height); x.stroke();
    if (DRAW && DRAW.complete && DRAW.naturalWidth) { x.save(); x.globalAlpha = .13; x.globalCompositeOperation = 'multiply'; x.drawImage(DRAW, 0, 0, c.width, c.height); x.restore(); } }
  // ---- juice (display-only; reads S, never writes it -> rules/parity untouched) ----
  const FX = { shake: 0, parts: [], trail: [], seen: { status: 'playing', col: 0 }, ac: null, mute: q.get('mute') === '1' };
  function blip(f, d = .09, type = 'square') { if (FX.mute) return; try { FX.ac = FX.ac || new (window.AudioContext || window.webkitAudioContext)(); const o = FX.ac.createOscillator(), g = FX.ac.createGain();
    o.type = type; o.frequency.value = f; g.gain.setValueAtTime(.06, FX.ac.currentTime); g.gain.exponentialRampToValueAtTime(.001, FX.ac.currentTime + d); o.connect(g).connect(FX.ac.destination); o.start(); o.stop(FX.ac.currentTime + d); } catch (e) { FX.mute = true; } }
  function pop(gx, gy, n, cols) { for (let i = 0; i < n; i++) { const a = Math.random() * 6.283, v = 1.5 + Math.random() * 3.5; FX.parts.push({ x: (gx + .5) * T, y: (gy + .5) * T, vx: Math.cos(a) * v, vy: Math.sin(a) * v - 2, life: 1, col: cols[i % cols.length], r: 3 + Math.random() * 4 }); } }
  function juice() { const st = S.status, col = S.collected.length, P = S.player;
    const L = FX.trail[FX.trail.length - 1]; if (!L || L[0] !== P.x || L[1] !== P.y) FX.trail.push([P.x, P.y]);
    if (col > FX.seen.col) { pop(P.x, P.y, 14, ['#ffd54f', '#ffb300', '#fff59d']); blip(880); setTimeout(() => blip(1320), 70); }
    if (st !== FX.seen.status && st === 'won') { pop(P.x, P.y, 46, ['#ffd54f', '#66bb6a', '#42a5f5', '#ec407a', '#ab47bc']); [523, 659, 784, 1047].forEach((f, i) => setTimeout(() => blip(f, .14, 'triangle'), i * 90)); }
    if (st !== FX.seen.status && st === 'lost') { FX.shake = 14; pop(P.x, P.y, 18, ['#ef5350', '#90caf9', '#2b2118']); blip(150, .25, 'sawtooth'); }
    else if (S.events[S.events.length - 1] === 'bump' && st === 'playing') FX.shake = Math.max(FX.shake, 3);
    FX.seen = { status: st, col }; }
  const MOTES = Array.from({ length: 26 }, (_, i) => { const r = rnd('m' + i); return { x: r(), y: r(), s: .5 + r() * 1.6, v: .00004 + r() * .00008, ph: r() * 6.28 }; });
  function fxLayer() { FX.parts = FX.parts.filter(p => (p.life -= .018) > 0); const t = performance.now(), Wp = spec.grid.w * T, Hp = spec.grid.h * T;
    x.save(); x.globalCompositeOperation = 'lighter';  // soft glow particles (fail/fix/win bursts) + ambient dust motes in the light
    FX.parts.forEach(p => { p.x += p.vx; p.y += p.vy; p.vy += .14; p.vx *= .985; const R = Math.max(0.01, p.r * p.life + 1), g = x.createRadialGradient(p.x, p.y, 0, p.x, p.y, R * 3);
      g.addColorStop(0, p.col); g.addColorStop(1, 'transparent'); x.globalAlpha = p.life * .9; x.fillStyle = g; x.beginPath(); x.arc(p.x, p.y, Math.max(0.01, R * 3), 0, 6.283); x.fill(); });
    MOTES.forEach(m => { const yy = ((m.y - t * m.v) % 1 + 1) % 1, xx = m.x + Math.sin(t / 1800 + m.ph) * .01; x.globalAlpha = .18 + .12 * Math.sin(t / 700 + m.ph); x.fillStyle = '#ffe9a8';
      x.beginPath(); x.arc(xx * Wp, yy * Hp, m.s, 0, 6.283); x.fill(); });
    x.restore(); x.save();  // studio lighting: warm key light from top-left + vignette, so the paper reads as a lit physical object
    const L = x.createRadialGradient(Wp * .25, -Hp * .1, 0, Wp * .25, -Hp * .1, Wp * 1.1); L.addColorStop(0, '#fff6d633'); L.addColorStop(1, 'transparent'); x.fillStyle = L; x.fillRect(0, 0, Wp, Hp);
    const V = x.createRadialGradient(Wp / 2, Hp / 2, Hp * .35, Wp / 2, Hp / 2, Wp * .75); V.addColorStop(0, 'transparent'); V.addColorStop(1, '#2b211833'); x.fillStyle = V; x.fillRect(0, 0, Wp, Hp); x.restore(); x.globalAlpha = 1; }

  // ---- agent trail + fail/fix marks (display-only; window.__MARKS__ comes from scripts/fix_marks.py = data diff spec k vs k+1) ----
  const MARKS = Array.isArray(window.__MARKS__) ? window.__MARKS__ : [];
  function trailLayer() { if (FX.trail.length < 2) return; x.save(); x.lineCap = x.lineJoin = 'round';
    const pts = FX.trail.map(([a, b]) => [(a + .5) * T, (b + .5) * T]);
    x.strokeStyle = S.status === 'lost' ? '#e5393599' : '#1e88e599'; x.lineWidth = T * .16; x.setLineDash([T * .05, T * .22]);
    x.beginPath(); pts.forEach(([a, b], i) => i ? x.lineTo(a, b) : x.moveTo(a, b)); x.stroke(); x.restore(); }
  function marksLayer(t) { if (!MARKS.length) return; const pulse = .5 + .5 * Math.sin(t / 220), lab = [];
    MARKS.forEach(m => { const bug = m.kind === 'bug', col = bug ? '#e53935' : '#2e7d32'; x.save(); x.lineWidth = 3; x.strokeStyle = col; x.setLineDash(bug ? [7, 5] : [5, 4]);
      if (m.from && m.to) { const [fx, fy] = [(m.from[0] + .5) * T, (m.from[1] + .5) * T], [tx, ty] = [(m.to[0] + .5) * T, (m.to[1] + .5) * T];
        x.globalAlpha = .55; x.beginPath(); x.arc(fx, fy, T * .42, 0, 7); x.stroke(); x.globalAlpha = 1;
        const mx = (fx + tx) / 2 + (ty - fy) * .35, my = (fy + ty) / 2 - (tx - fx) * .35; x.setLineDash([]); x.lineWidth = 3.5;
        x.beginPath(); x.moveTo(fx, fy); x.quadraticCurveTo(mx, my, tx, ty); x.stroke();
        const a = Math.atan2(ty - my, tx - mx); x.fillStyle = col; x.beginPath(); x.moveTo(tx, ty); x.lineTo(tx - Math.cos(a - .45) * 12, ty - Math.sin(a - .45) * 12); x.lineTo(tx - Math.cos(a + .45) * 12, ty - Math.sin(a + .45) * 12); x.fill();
        lab.push([m.label, fx, fy - T * .9]); }
      else { m.cells.forEach(([gx, gy]) => { const X = gx * T, Y = gy * T;
          if (bug) { x.globalAlpha = .35 + .45 * pulse; x.fillStyle = '#e5393533'; x.fillRect(X + 2, Y + 2, T - 4, T - 4); x.globalAlpha = 1; x.strokeRect(X + 2, Y + 2, T - 4, T - 4); }
          else { if (m.what === 'hazard') { x.fillStyle = '#a1887f'; for (let k = 0; k < 3; k++) x.fillRect(X + 3, Y + T * (.18 + k * .28), T - 6, T * .16); }
            x.strokeRect(X + 2, Y + 2, T - 4, T - 4); } });
        const [gx, gy] = m.cells[0]; lab.push([m.label, (gx + .5) * T, Math.max(0, gy * T - 18)]); }
      if (bug && !m.from) { const [gx, gy] = m.cells[0]; x.globalAlpha = pulse; x.beginPath(); x.arc((gx + .5) * T, (gy + .5) * T, T * (.55 + .12 * pulse), 0, 7); x.stroke(); }
      x.restore(); });
    window.__MARKS_DRAWN__ = MARKS.length; return lab; }
  const GICON = { fork: '🔀', question: '❓', meter: '🎯' };
  function gatesLayer(t) { const pulse = .5 + .5 * Math.sin(t / 240);
    const door = (cl, mode, g) => { const X = cl[0] * T, Y = cl[1] * T; x.save(); x.textAlign = 'center';
      if (mode === 'open') { x.globalAlpha = .7; x.strokeStyle = '#2fbf71'; x.lineWidth = 3; x.setLineDash([4, 4]); x.strokeRect(X + 3, Y + 3, T - 6, T - 6); x.font = `${T * .4}px sans-serif`; x.fillText('✨', X + T / 2, Y + T * .64); x.restore(); return; }
      const sealed = mode === 'sealed', gr = x.createLinearGradient(X, Y, X, Y + T); gr.addColorStop(0, sealed ? '#8d6e63' : '#7e57c2'); gr.addColorStop(1, sealed ? '#3e2723' : '#311b92');
      x.shadowColor = sealed ? '#0008' : `rgba(255,210,122,${.45 + .5 * pulse})`; x.shadowBlur = sealed ? 4 : 18; x.fillStyle = gr;
      x.beginPath(); x.roundRect ? x.roundRect(X + 3, Y + 2, T - 6, T - 4, 9) : x.rect(X + 3, Y + 2, T - 6, T - 4); x.fill(); x.shadowBlur = 0;
      x.strokeStyle = sealed ? '#2b2118' : '#ffd27a'; x.lineWidth = 2.5; x.stroke(); x.font = `${T * .46}px sans-serif`;
      x.fillText(sealed ? '🧱' : (GICON[g.kind] || '🔒'), X + T / 2, Y + T * .66); x.restore(); };
    const nx = GATES.findIndex(g => !g.open); GATES.forEach((g, i) => { if (nx >= 0 && i > nx) return; // staggered: only cleared doors + the NEXT one exist on the board
      if (!g.shownAt) g.shownAt = t; const age = t - g.shownAt; if (age < 420) { const k = age / 420, X = (g.cell[0] + .5) * T, Y = (g.cell[1] + .5) * T; x.save(); x.globalAlpha = 1 - k; x.strokeStyle = '#ffd27a'; x.lineWidth = 4; x.beginPath(); x.arc(X, Y, T * (.3 + k), 0, 7); x.stroke(); x.restore(); }
      door(g.cell, g.open ? 'open' : 'locked', g); if (g.alt) door(g.alt, g.sealed ? 'sealed' : g.open ? 'open' : 'locked', g); }); window.__GATES_DRAWN__ = nx < 0 ? GATES.length : nx + 1; }
  function render(t = performance.now()) {
    x.save(); if (FX.shake > .3) { x.translate((Math.random() - .5) * FX.shake, (Math.random() - .5) * FX.shake); FX.shake *= .86; } else FX.shake = 0;
    renderScene(t); fxLayer(); x.restore();
  }
  function renderScene(t) {
    paper(); const bob = (k) => Math.sin(t / 260 + k) * 2.5;
    const PROPS = (window.__PROPS__ || []).map(q => ({ ...q, im: q.im || (q.im = ld(q.src)) })); window.__PROPS__ = PROPS; const inProp = (cx, cy) => PROPS.some(q => cx >= q.x && cx < q.x + q.w && cy >= q.y && cy < q.y + q.h);
    (spec.walls || []).filter(w => !inProp(w.x, w.y)).forEach(w => { for (let i = 0; i < (w.w || 1); i++) for (let j = 0; j < (w.h || 1); j++) { const wc = ok(ART.wall) ? null : CUT.wall[(w.x + i) + ',' + (w.y + j)]; if (wc) { x.globalAlpha = .25; wallTile(w.x + i, w.y + j); x.globalAlpha = 1; x.drawImage(wc, (w.x + i) * T, (w.y + j) * T, T, T); } else if (ok(ART.wall)) { x.globalAlpha = window.__ART3D__ ? 0 : .3; wallTile(w.x + i, w.y + j); x.globalAlpha = 1; x.drawImage(ART.wall, (w.x + i) * T, (w.y + j) * T, T, T); } else wallTile(w.x + i, w.y + j); } });
    (spec.hazards || []).forEach(h => { const k = KIND(h.id) || KIND(h.label); for (let i = 0; i < (h.w || 1); i++) for (let j = 0; j < (h.h || 1); j++) { const wc = CUT.wall[(h.x + i) + ',' + (h.y + j)]; if (window.__ART3D__ && ok(ART.wall) && /piedra|rock|roca|stone/i.test((h.id || '') + (h.label || ''))) { const r3 = .55 + .45 * rnd(h.x * 31 + h.y * 7 + i * 13 + j)(); x.save(); x.shadowColor = '#000a'; x.shadowBlur = 8; x.drawImage(ART.wall, (h.x + i) * T - T * .08, (h.y + j) * T + T * (.02 + .04 * r3), T * 1.16, T * .86); x.restore(); } else if (wc) { x.globalAlpha = .2; tile(k, h, h.x + i, h.y + j, t); x.globalAlpha = 1; x.drawImage(wc, (h.x + i) * T, (h.y + j) * T, T, T); } else tile(k, h, h.x + i, h.y + j, t); } });
    PROPS.forEach(q => { if (ok(q.im)) { x.save(); x.shadowColor = '#0008'; x.shadowBlur = 14; const r = q.im.width / q.im.height, bw = q.w * T, bh = q.h * T, dw = Math.min(bw, bh * r), dh = dw / r; x.drawImage(q.im, q.x * T + (bw - dw) / 2, q.y * T + bh - dh, dw, dh); x.restore(); } });
    const ent = (e, role, k, ph) => { const cx = (e.x + (e.w || 1) / 2) * T, cy = (e.y + (e.h || 1) / 2) * T, s = T * 1.05; shadow(cx, cy + s * .42, s); { const ci = ok(ART['id:' + e.id]) ? ART['id:' + e.id] : ok(ART[role]) ? ART[role] : role === 'enemy' ? CUT.enemy[ENEMIES.findIndex(q => q.id === e.id)] : CUT.at[e.id]; ci ? cutSprite(ci, role, cx, cy - 2 + bob(ph), s, t, e.id) : sprite(KIND(e.id) || KIND(e.label), role, cx, cy - 2 + bob(ph), s, e.id, t); } return [cx, cy + s * .45]; };
    trailLayer(); gatesLayer(t); const mlab = marksLayer(t) || [];
    const tags = [];
    spec.goals.forEach((g, i) => { if (COLLECT && S.collected.includes(g.id)) return; tags.push([g.label, ...ent(g, 'goal', 0, i)]); });
    NPCS.forEach((n, i) => tags.push([n.label, ...ent(n, 'npc', 0, i + 2)]));
    S.foes.forEach((f, i) => tags.push([f.label, ...ent(f, 'enemy', 0, i + 4)]));
    tags.push([S.player.label, ...ent(S.player, 'player', 0, 0)]);
    (spec.hazards || []).forEach(h => { if (h.label && !/_\d+$/.test(h.id)) tags.push([h.label, (h.x + (h.w || 1) / 2) * T, (h.y + (h.h || 1)) * T - 4]); });
    // fix/bug marks first (they carry the story), then player, enemies, goals, hazards; each label takes the first free slot
    const req = [...mlab.map(([l, cx, y]) => [l, cx, Math.min(Math.max(y, 0), c.height - 17)]), ...tags.slice().reverse().map(([l, cx, y]) => [l, cx, Math.min(y, c.height - 17)])];
    window.__TAGS__ = placeTags(req).map(([l, cx, y]) => tag(l, cx, y)).filter(Boolean);
  }
  (function loop(t) { render(t); requestAnimationFrame(loop); })(performance.now());
  function GOAL_EMOJI() { const l = ((spec.goals || [])[0] || {}).label || ''; const M = [[/estrell|star/i, '⭐'], [/hueso|bone/i, '🦴'], [/castill|castle/i, '🏰'], [/tesoro|treasure|cofre/i, '💎'], [/nave|cohete|rocket/i, '🚀'], [/luna|moon/i, '🌙'], [/torta|pastel|cake/i, '🎂'], [/pelota|ball/i, '⚽']]; for (const [r, e] of M) if (r.test(l)) return e; return COLLECT ? '⭐' : '🏠'; }
  function LOSE_TEXT() { const e = S.events[S.events.length - 1] || '', id = e.split(':')[1] || '', k = KIND(id);  // name what got you (display-only)
    if (e.startsWith('enemy') || e.startsWith('spawn_on_enemy')) return UI('CAUGHT! 👾', '¡TE ATRAPÓ! 👾'); if (k === 'fuego') return UI('YOU LOSE 🔥', 'PERDISTE 🔥'); if (k === 'piedras') return UI('YOU LOSE 🪨', 'PERDISTE 🪨'); return UI('YOU LOSE 💧', 'PERDISTE 💧'); }
  function draw() {
    juice(); render();
    $('att').textContent = S.attempt; $('steps').textContent = SURVIVE ? `${S.steps} · ⏱ ${S.ticks}/${WC.seconds}s` : COLLECT ? `${S.steps} · ★ ${S.collected.length}/${spec.goals.length}` : S.steps;
    $('st').textContent = { playing: UI('playing', 'jugando'), won: UI('WON', 'GANÓ'), lost: UI('LOST', 'PERDIÓ') }[S.status];
    const ov = $('ov'); ov.className = S.status === 'playing' ? '' : S.status;
    $('ovt').textContent = S.status === 'won' ? `${UI('YOU WIN!', '¡GANASTE!')} ${GOAL_EMOJI()}` : S.status === 'lost' ? (window.__VOICE_FAIL__ ? UI('You left without the 3 kids! 0/3', '¡Te fuiste sin los 3 nenes! 0/3') : LOSE_TEXT()) : '';
  }
  function log(kind, text) { const li = document.createElement('li'); li.className = kind; li.textContent = text; $('tll').appendChild(li); }
  const K = { ArrowUp: [0, -1], ArrowDown: [0, 1], ArrowLeft: [-1, 0], ArrowRight: [1, 0], w: [0, -1], W: [0, -1], a: [-1, 0], A: [-1, 0], s: [0, 1], S: [0, 1], d: [1, 0], D: [1, 0] };
  const held = new Set();
  const reportKeys = () => { window.__KEYS__ = [...held]; };
  const clearKeys = () => { held.clear(); reportKeys(); };
  window.__CLEAR_KEYS__ = clearKeys;
  const keyBlocked = () => !!(window.__PAUSED__ || (document.body && (document.body.classList.contains('modal-open') || document.body.classList.contains('transitioning'))));
  function netHeld() {
    let x = 0, y = 0, last = null;
    held.forEach(k => { const d = K[k]; if (!d) return; x += d[0]; y += d[1]; last = d; });
    x = Math.sign(x); y = Math.sign(y);
    if (x && y) return last;
    if (x || y) return [x, y];
    return null;
  }
  addEventListener('keydown', e => {
    if (e.target && e.target.closest && e.target.closest('input,textarea,select,[contenteditable]')) return;
    if (K[e.key]) {
      if (e.repeat && !held.has(e.key)) return;
      if (keyBlocked()) return;
      held.add(e.key); reportKeys();
      const d = netHeld();
      if (d) move(...d);
      return;
    }
    if (e.key === ' ' || e.code === 'Space') {
      e.preventDefault();
      clearKeys();
      if (!keyBlocked()) move(0, 0);
      return;
    }
    if ((e.key === 'r' || e.key === 'R') && !e.metaKey && !e.ctrlKey) reset();
  });
  addEventListener('keyup', e => { if (held.delete(e.key)) reportKeys(); });
  addEventListener('blur', clearKeys);
  addEventListener('pagehide', clearKeys);
  document.addEventListener('visibilitychange', () => { if (document.hidden) clearKeys(); });
  const state = () => JSON.parse(JSON.stringify(S));
  window.__GAME__ = { spec, state, move, reset, log, gates: () => JSON.parse(JSON.stringify(GATES)), openGate: (id, side) => { const g = GATES.find(g => g.id === id); if (!g) return; g.open = true; if (g.kind === 'fork' && g.alt) { if (side === 'B') { const c0 = g.cell; g.cell = g.alt; g.alt = c0; } g.sealed = true; } S.events.push('open:' + id); pop(g.cell[0], g.cell[1], 26, ['#ffd27a', '#7dffb0', '#b388ff']); { const nn = GATES.find(q => !q.open); if (nn) setTimeout(() => { nn.shownAt = 0; pop(nn.cell[0], nn.cell[1], 18, ['#ffd27a', '#ff8ac2']); blip(880); draw(); }, 350); } blip(660); setTimeout(() => blip(990), 80); draw(); }, failGate: id => { const g = GATES.find(g => g.id === id); S.events.push('gatefail:' + id); FX.shake = 12; if (g) pop(g.cell[0], g.cell[1], 14, ['#ef5350', '#ff8a65']); blip(140, .22, 'sawtooth'); draw(); }, setAttempt: n => { S.attempt = n; draw(); }, ready: true };
  (window.__TIMELINE__ || []).forEach(e => log(e.kind, e.text));
  if (q.get('timeline')) try { (await (await fetch(q.get('timeline'))).json()).forEach(e => log(e.kind, e.text)); } catch (e) {}
  // ?realtime=1: idle clock, one wait() per second (playtests stay deterministic without it)
  if (q.get('realtime') === '1') setInterval(() => { if (S.status === 'playing') move(0, 0); }, 1000);
  spawnCheck(); draw();
})();
