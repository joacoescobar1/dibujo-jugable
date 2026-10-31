// Cinematic Three.js stage (display-only). Rules stay in game.js; this reads window.__GAME__.state()/gates() each frame.
import * as THREE from 'three';
import { EffectComposer } from 'three/examples/jsm/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/examples/jsm/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/examples/jsm/postprocessing/UnrealBloomPass.js';
import { portalDoor, rockVariant, winTitle } from './stage3d_fx.meta.js';
import { OutputPass } from 'three/examples/jsm/postprocessing/OutputPass.js';
import { ShaderPass } from 'three/examples/jsm/postprocessing/ShaderPass.js';

function boot() {
  const G = window.__GAME__, c2 = document.getElementById('c'), wrap = document.getElementById('wrap');
  if (!G || !G.ready || !c2) return setTimeout(boot, 60);
  // wait for the inline bundle (sets __BUNDLE__/__PLATE__/__ART__ after this script) so play mode + plate ground are never skipped by a race
  if (!window.__BUNDLE__ && (boot.n = (boot.n || 0) + 1) < 40) return setTimeout(boot, 50);
  // player_shell.js (after this file) sets __tr. A timer can run in that gap and stamp Spanish name cards.
  if (typeof window.__tr !== 'function' && (boot.trN = (boot.trN || 0) + 1) < 40) return setTimeout(boot, 50);
  const COARSE = (() => { try { return matchMedia('(pointer: coarse)').matches; } catch (e) { return false; } })();
  const REDUCED = (() => { try { return matchMedia('(prefers-reduced-motion: reduce)').matches; } catch (e) { return false; } })();
  const STILL = new URLSearchParams(location.search).get('still') === '1' || REDUCED;
  const PLAYM = !!(window.__BUNDLE__ && window.__BUNDLE__.play && new URLSearchParams(location.search).get('judge') !== '1');
  let gl; try { gl = new THREE.WebGLRenderer({ antialias: !COARSE, alpha: false, preserveDrawingBuffer: true, powerPreference: COARSE ? 'low-power' : 'default' }); } catch (e) { window.__STAGE3D__ = { error: String(e) }; return; }
  const spec = G.spec, W = spec.grid.w, H = spec.grid.h, ART = window.__ART__ || {};
  gl.setPixelRatio(Math.min(devicePixelRatio || 1, (PLAYM && COARSE) ? 1.25 : 2)); gl.shadowMap.enabled = true; gl.shadowMap.type = THREE.PCFSoftShadowMap;
  gl.toneMapping = THREE.ACESFilmicToneMapping; gl.toneMappingExposure = 1.12; gl.outputColorSpace = THREE.SRGBColorSpace;
  const cv = gl.domElement; cv.id = 'c3d'; cv.style.cssText = 'position:absolute;left:0;top:0;width:100%;height:100%;border-radius:0;pointer-events:none;touch-action:none;z-index:2';
  wrap.insertBefore(cv, c2.nextSibling); c2.style.opacity = '0'; document.body.classList.add('s3d');
  const scene = new THREE.Scene(); scene.background = new THREE.Color('#8ebfff'); scene.fog = new THREE.Fog('#c9e4ff', 18, 46);
  const sky = new THREE.Mesh(new THREE.SphereGeometry(90, COARSE ? 16 : 28, COARSE ? 12 : 18), new THREE.MeshBasicMaterial({ color: '#8ebfff', side: THREE.BackSide, fog: false }));
  scene.add(sky);
  let SKYM = false;
  const cam = new THREE.PerspectiveCamera(50, 4 / 3, .1, 120);
  // lights: warm key, soft fill, cool rim, pink kicker (the fringe that reads on a phone)
  scene.add(new THREE.HemisphereLight('#fff1d0', '#243056', 1.12));
  const key = new THREE.DirectionalLight('#ffcf8a', 2.55); key.position.set(-7, 14, 8); key.castShadow = true; key.shadow.mapSize.set(COARSE ? 512 : 1024, COARSE ? 512 : 1024);
  Object.assign(key.shadow.camera, { left: -W, right: W, top: H, bottom: -H, near: .5, far: 40 }); key.shadow.bias = -.0006; key.shadow.normalBias = .02; key.shadow.radius = COARSE ? 3 : 8; scene.add(key);
  const rim = new THREE.DirectionalLight('#8eb6ff', 1.65); rim.position.set(7, 5.5, -12); scene.add(rim);
  const rimPink = new THREE.DirectionalLight('#ff8ad4', .42); rimPink.position.set(-9, 3, -6); scene.add(rimPink);
  const fill = new THREE.DirectionalLight('#ffd6ea', .48); fill.position.set(5, 2.5, 10); scene.add(fill);
  const tl = new THREE.TextureLoader(), tex = u => { if (!u) return null; const t = tl.load(u); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = COARSE ? 2 : 8; return t; };
  const X = gx => gx + .5 - W / 2, Z = gy => gy + .5 - H / 2;
  const lamp = new THREE.PointLight('#ffcf8a', STILL ? .9 : 1.45, 14, 1.8);
  lamp.position.set(X(spec.player.x), 5.6, Z(spec.player.y) + 1.1); scene.add(lamp);
  // ground = Meta film plate, plus a dark stage apron around it
  const apron = new THREE.Mesh(new THREE.PlaneGeometry(W * 8, H * 8), new THREE.MeshStandardMaterial({ color: '#8cc46a', roughness: 1 }));
  apron.rotation.x = -Math.PI / 2; apron.position.y = -.02; apron.receiveShadow = true; scene.add(apron);
  const grassT = (() => { const k = document.createElement('canvas'); k.width = k.height = COARSE ? 128 : 256; const x = k.getContext('2d'); x.fillStyle = '#e8e8e8'; x.fillRect(0, 0, k.width, k.height); for (let i = 0; i < (COARSE ? 700 : 2600); i++) { const v = 170 + Math.random() * 85 | 0; x.strokeStyle = `rgba(${v},${v},${v},.55)`; x.lineWidth = 1 + Math.random() * 1.5; const a = Math.random() * k.width, b = Math.random() * k.height; x.beginPath(); x.moveTo(a, b); x.lineTo(a + (Math.random() - .5) * 4, b - 3 - Math.random() * 6); x.stroke(); } const t = new THREE.CanvasTexture(k); t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(W * 2, H * 2); t.anisotropy = COARSE ? 2 : 8; return t; })();
  apron.material.map = grassT; apron.material.map.repeat.set(W * 6, H * 6); apron.material.needsUpdate = true;
  const ground = new THREE.Mesh(new THREE.PlaneGeometry(W, H), new THREE.MeshStandardMaterial({ color: '#000', transparent: true, opacity: 0, depthWrite: false }));
  ground.rotation.x = -Math.PI / 2; ground.receiveShadow = true; scene.add(ground);
  // immersive world: plate as a huge curved backdrop + ground tint sampled from the plate's bottom edge (no floating board / frame)
  if (window.__PLATE__) tl.load(window.__PLATE__, t => { t.colorSpace = THREE.SRGBColorSpace; const D0 = Math.max(W, H), a = t.image.height / t.image.width, bw = D0 * 4.2;
    const bd = new THREE.Mesh(new THREE.CylinderGeometry(bw * .9, bw * .9, bw * a, 48, 1, true, -Math.PI * .32, Math.PI * .64), new THREE.MeshBasicMaterial({ map: t, side: THREE.BackSide, fog: false }));
    bd.rotation.y = Math.PI; bd.position.set(0, bw * a * .5 - D0 * .5, bw * .9 - H * .5 - D0 * .4); scene.add(bd);
    try { const k = document.createElement('canvas'); k.width = 32; k.height = 4; const x = k.getContext('2d'); x.drawImage(t.image, 0, t.image.height * .88, t.image.width, t.image.height * .12, 0, 0, 32, 4); const d = x.getImageData(0, 0, 32, 4).data; let r = 0, g = 0, b = 0; for (let i = 0; i < d.length; i += 4) { r += d[i]; g += d[i + 1]; b += d[i + 2]; } const n = d.length / 4, c = new THREE.Color(`rgb(${r / n | 0},${g / n | 0},${b / n | 0})`); const L0 = (.2126 * r + .7152 * g + .0722 * b) / n / 255, SKY = L0 > .6; if (SKY) { /* bright sky plate: cloud-sea floor, keep saturation, no white wash */ const hsl = {}; c.getHSL(hsl); c.set('#e9dcff'); const cl = document.createElement('canvas'); cl.width = cl.height = 256; const cx = cl.getContext('2d'); cx.fillStyle = '#f4ecff'; cx.fillRect(0, 0, 256, 256); for (let i = 0; i < 140; i++) { const x0 = Math.random() * 256, y0 = Math.random() * 256, r0 = 10 + Math.random() * 34, gr = cx.createRadialGradient(x0, y0, 0, x0, y0, r0); gr.addColorStop(0, 'rgba(255,255,255,.55)'); gr.addColorStop(1, 'rgba(255,255,255,0)'); cx.fillStyle = gr; for (const ox of [-256, 0, 256]) for (const oy of [-256, 0, 256]) { cx.save(); cx.translate(ox, oy); cx.fillRect(x0 - r0, y0 - r0, r0 * 2, r0 * 2); cx.restore(); } } const ct = new THREE.CanvasTexture(cl); ct.wrapS = ct.wrapT = THREE.RepeatWrapping; ct.repeat.set(W / 2.5, H / 2.5); ct.colorSpace = THREE.SRGBColorSpace; apron.material.map = ct; apron.material.needsUpdate = true; gl.toneMappingExposure = .96; bloom.threshold = .8; scene.fog.near = 18; scene.fog.far = 55; scene.background.set('#9fc4ff'); SKYM = true; } else { c.multiplyScalar(1.3); scene.fog.near = 8; scene.fog.far = 24; } apron.material.color.copy(c); scene.fog.color.copy(c); const hk = document.createElement('canvas'); hk.width = 4; hk.height = 128; const hx = hk.getContext('2d'), hg = hx.createLinearGradient(0, 128, 0, 0); hg.addColorStop(0, c.getStyle()); hg.addColorStop(.45, c.getStyle()); hg.addColorStop(1, 'rgba(0,0,0,0)'); hx.fillStyle = hg; hx.fillRect(0, 0, 4, 128); const ht = new THREE.CanvasTexture(hk); const hz = new THREE.Mesh(new THREE.CylinderGeometry(D0 * 2.6, D0 * 2.6, D0 * .9, 48, 1, true), new THREE.MeshBasicMaterial({ map: ht, transparent: true, side: THREE.BackSide, fog: false, depthWrite: false })); hz.position.set(0, D0 * .2, 0); scene.add(hz); } catch (e) { } });
  // emoji / text textures
  const ctex = (draw, w = 256, h = 256) => { const k = document.createElement('canvas'); k.width = w; k.height = h; draw(k.getContext('2d'), w, h); const t = new THREE.CanvasTexture(k); t.colorSpace = THREE.SRGBColorSpace; return t; };
  const emoji = (e, col) => ctex((x, w, h) => { const g = x.createRadialGradient(w / 2, h / 2, 10, w / 2, h / 2, w / 2); g.addColorStop(0, col); g.addColorStop(1, '#0000'); x.fillStyle = g; x.fillRect(0, 0, w, h); x.font = `${w * .55}px sans-serif`; x.textAlign = 'center'; x.textBaseline = 'middle'; x.fillText(e, w / 2, h / 2 + 8); });
  const label = s => ctex((x, w, h) => { x.font = 'bold 56px "Comic Sans MS","Chalkboard SE",cursive'; const tw = Math.min(w - 8, x.measureText(s).width + 36); x.fillStyle = '#fffaf0ee'; x.beginPath(); x.roundRect((w - tw) / 2, 10, tw, 76, 38); x.fill(); x.strokeStyle = '#ffd27a'; x.lineWidth = 4; x.stroke(); x.fillStyle = '#2b2118'; x.textAlign = 'center'; x.fillText(s, w / 2, 66, w - 40); }, 768, 96);
  const blobT = ctex((x, w, h) => { const g = x.createRadialGradient(w / 2, h / 2, 0, w / 2, h / 2, w / 2); g.addColorStop(0, '#000a'); g.addColorStop(1, '#0000'); x.fillStyle = g; x.fillRect(0, 0, w, h); }, 128, 128);
  const glowT = ctex((x, w, h) => { const g = x.createRadialGradient(w / 2, h / 2, 0, w / 2, h / 2, w / 2); g.addColorStop(0, '#fff'); g.addColorStop(.25, '#fffa'); g.addColorStop(1, '#fff0'); x.fillStyle = g; x.fillRect(0, 0, w, h); }, 64, 64);
  const FALL = { player: '🦋', goal: '⭐', enemy: '👾', npc: '🙂', wall: '🪨', door: '🚪' }, COL = { player: '#6fe3ffaa', goal: '#ffd54faa', enemy: '#ab47bcaa', npc: '#ce93d8aa', wall: '#8888', door: '#ffd27aaa' };
  const artTex = {}; const roleTex = r => artTex[r] || (artTex[r] = ART[r] ? tex(ART[r]) : emoji(FALL[r] || '❔', COL[r] || '#fff5'));
  const RIMS = [];
  function fresnelCard(map, col, size) {
    const mat = new THREE.ShaderMaterial({
      uniforms: { map: { value: map }, color: { value: new THREE.Color(col) }, pulse: { value: 1 } },
      vertexShader: 'varying vec2 vUv;void main(){vUv=uv;gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0);}',
      fragmentShader: 'uniform sampler2D map;uniform vec3 color;uniform float pulse;varying vec2 vUv;void main(){float a=texture2D(map,vUv).a;vec2 e=vec2(.02,.02);float n=(texture2D(map,vUv+vec2(e.x,0.)).a+texture2D(map,vUv-vec2(e.x,0.)).a+texture2D(map,vUv+vec2(0.,e.y)).a+texture2D(map,vUv-vec2(0.,e.y)).a)*.25;float edge=smoothstep(.08,.6,a)*(1.-smoothstep(.25,.95,n));float halo=smoothstep(0.,.25,a)*(1.-smoothstep(.2,.65,a));float rad=length((vUv-.5)*vec2(1.15,1.35));float fres=pow(smoothstep(.15,.72,rad),1.6)*smoothstep(.12,.45,a);float rim=clamp(max(max(edge,halo*.75),fres*.9)*pulse,0.,1.);if(rim<.04)discard;gl_FragColor=vec4(color,rim);}',
      transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, side: THREE.DoubleSide, toneMapped: false, fog: false
    });
    const mesh = new THREE.Mesh(new THREE.PlaneGeometry(size * 1.1, size * 1.1), mat);
    mesh.position.set(0, size / 2, .03); mesh.renderOrder = 4; RIMS.push(mat); return mesh;
  }
  // character = upright billboard with real alpha shadow + contact blob + glow halo + name card
  function actor(role, name, size = 1.25, id) {
    const mp = id && ART['id:' + id] ? (artTex['id:' + id] || (artTex['id:' + id] = tex(ART['id:' + id]))) : roleTex(role);
    const g = new THREE.Group(), m = new THREE.MeshStandardMaterial({ map: mp, transparent: false, alphaTest: .5, side: THREE.DoubleSide, roughness: .55, emissive: '#ffffff', emissiveIntensity: .08 });
    m.emissiveMap = m.map; const q = new THREE.Mesh(new THREE.PlaneGeometry(size, size), m); q.castShadow = true; q.position.y = size / 2; q.customDepthMaterial = new THREE.MeshDepthMaterial({ map: m.map, alphaTest: .35, depthPacking: THREE.RGBADepthPacking });
    const sh = new THREE.Mesh(new THREE.PlaneGeometry(size * 1.25, size * .62), new THREE.MeshBasicMaterial({ map: blobT, transparent: true, depthWrite: false, opacity: .85 })); sh.rotation.x = -Math.PI / 2; sh.position.y = .012;
    const rimCol = { player: '#9be7ff', goal: '#ffe27a', enemy: '#ff8ad9', npc: '#ffd0ef', door: '#fff1b0', wall: '#d7c4ff' }[role] || '#fff4d2';
    let rimMat = null;
    if (role === 'wall') {
      const rimCard = new THREE.Mesh(new THREE.PlaneGeometry(size * 1.08, size * 1.08), new THREE.MeshBasicMaterial({ color: rimCol, transparent: true, opacity: .28, depthWrite: false, blending: THREE.AdditiveBlending, side: THREE.DoubleSide, toneMapped: false, fog: false }));
      rimCard.position.set(0, size / 2, -.06); g.add(rimCard);
    } else { const rimMesh = fresnelCard(mp, rimCol, size); g.add(rimMesh); rimMat = rimMesh.material; }
    const halo = new THREE.Sprite(new THREE.SpriteMaterial({ map: glowT, color: { player: '#6fe3ff', goal: '#ffd54f', enemy: '#d05cff', npc: '#ffb3e6' }[role] || '#fff', blending: THREE.AdditiveBlending, depthWrite: false, fog: false, opacity: role === 'goal' ? .9 : .45 }));
    halo.scale.setScalar(size * 1.6); halo.position.y = size * .5;
    g.add(sh, q); halo.position.z = -.4; if (role === 'goal' || role === 'door' || role === 'player') g.add(halo); g.userData = { q, halo, role, size, rimMat };
    if (name && !PLAYM) { const nm = window.__tr ? window.__tr(name) : name; (window.__LABELS__ = window.__LABELS__ || []).push(nm); const L = new THREE.Sprite(new THREE.SpriteMaterial({ map: label(nm), depthTest: false, transparent: true })); L.scale.set(4.2, .52, 1); L.position.y = size + .35; L.renderOrder = 10; g.add(L); g.userData.L = L; }
    scene.add(g); return g;
  }
  const wallM = ART.wall ? null : new THREE.MeshStandardMaterial({ color: '#8d6e63', roughness: .8 });
  const cells = (r, f) => { for (let i = 0; i < (r.w || 1); i++) for (let j = 0; j < (r.h || 1); j++) f(r.x + i, r.y + j); };
  const PROPS = window.__PROPS__ || [], underProp = (gx, gy) => PROPS.some(p => gx >= p.x && gx < p.x + p.w && gy >= p.y && gy < p.y + p.h);
  PROPS.forEach(p => { const tx = tex(p.src); const m = new THREE.MeshStandardMaterial({ map: tx, transparent: false, alphaTest: .5, side: THREE.DoubleSide, roughness: .6 });
    const wd = p.w * 1.05, ht = Math.max(p.h * .75, 2.2), q = new THREE.Mesh(new THREE.PlaneGeometry(wd, ht), m); q.castShadow = true; q.customDepthMaterial = new THREE.MeshDepthMaterial({ map: tx, alphaTest: .3, depthPacking: THREE.RGBADepthPacking });
    const g = new THREE.Group(); q.position.y = ht / 2; g.add(q); g.position.set(X(p.x + (p.w - 1) / 2), 0, Z(p.y + p.h - 1) + .2); g.userData = { q, prop: true }; scene.add(g);
    tl.load(p.src, t => { const a = t.image.height / t.image.width; q.scale.y = Math.min(1.6, (wd * a) / ht); q.position.y = ht * q.scale.y / 2; }); });
  (spec.walls || []).forEach(w => cells(w, (gx, gy) => { if (underProp(gx, gy)) return; if (wallM) { const b = new THREE.Mesh(new THREE.BoxGeometry(.92, .7, .92), wallM); b.position.set(X(gx), .35, Z(gy)); b.castShadow = b.receiveShadow = true; scene.add(b); } else { const a = actor('wall', null, 1.05); a.position.set(X(gx), 0, Z(gy)); rockVariant(a, gx * 97 + gy * 29 + 3); } }));
  const HZ = [];
  (spec.hazards || []).forEach(h => { const rock = /piedra|rock|roca|stone/i.test((h.id || '') + (h.label || '')), water = /agua|rio|río|water|charco/i.test((h.id || '') + (h.label || ''));
    cells(h, (gx, gy) => { if (rock) { const a = actor('wall', null, .95); a.position.set(X(gx), 0, Z(gy)); rockVariant(a, gx * 131 + gy * 17 + 7); return; }
      const m = new THREE.Mesh(new THREE.PlaneGeometry(.96, .96), new THREE.MeshStandardMaterial({ color: water ? '#42a5f5' : '#ff7043', emissive: water ? '#0d47a1' : '#ff3d00', emissiveIntensity: water ? .4 : 1.4, transparent: true, opacity: .82, roughness: .1, metalness: .3 }));
      m.rotation.x = -Math.PI / 2; m.position.set(X(gx), .02, Z(gy)); m.userData.haz = water ? 'w' : 'f'; scene.add(m); HZ.push(m); }); });
  const goals = spec.goals.map(g => { const a = actor('goal', g.label, 1.6, g.id); a.position.set(X(g.x + ((g.w || 1) - 1) / 2), 0, Z(g.y + ((g.h || 1) - 1) / 2)); a.userData.id = g.id; return a; });
  const npcs = (spec.characters || []).filter(c => c.role !== 'enemy' && !/^(sol|sun)$/i.test(c.id)).map(n => { const a = actor('npc', n.label, 1.1, n.id); a.position.set(X(n.x), 0, Z(n.y)); return a; });
  let doorA = null; if (spec.door) { doorA = actor('door', spec.door.label, 2.1, 'door'); doorA.position.set(X(spec.door.x), 0, Z(spec.door.y)); if (ART.door) { const dm = tex(ART.door); doorA.userData.q.material.map = dm; doorA.userData.q.material.emissiveMap = dm; if (doorA.userData.rimMat) doorA.userData.rimMat.uniforms.map.value = dm; } doorA.userData.halo.material.color.set('#ffe9a0'); dressDoor(doorA); }
  function dressDoor(g) {
    const archMat = new THREE.MeshBasicMaterial({ color: '#ffd56a', toneMapped: false });
    const arch = new THREE.Mesh(new THREE.TorusGeometry(1.05, .12, 8, 28, Math.PI), archMat);
    arch.position.set(0, 1.18, .16); g.add(arch);
    const postGeo = new THREE.CylinderGeometry(.1, .12, 1.22, 6);
    [-1.05, 1.05].forEach(x => { const p = new THREE.Mesh(postGeo, archMat); p.position.set(x, .61, .16); g.add(p); });
    const beamT = ctex((x, w, h) => { const gr = x.createLinearGradient(0, h, 0, 0); gr.addColorStop(0, 'rgba(255,200,70,0)'); gr.addColorStop(.18, 'rgba(255,214,110,.28)'); gr.addColorStop(.58, 'rgba(255,246,210,.9)'); gr.addColorStop(1, 'rgba(255,255,255,0)'); x.fillStyle = gr; x.fillRect(0, 0, w, h); }, 16, 128);
    const beam = new THREE.Mesh(new THREE.CylinderGeometry(.12, .62, 6.6, 12, 1, true), new THREE.MeshBasicMaterial({ map: beamT, color: '#fff4c0', transparent: true, opacity: .5, depthWrite: false, blending: THREE.AdditiveBlending, side: THREE.DoubleSide, toneMapped: false, fog: false }));
    beam.position.y = 4.05; g.add(beam);
    const pad = new THREE.Mesh(new THREE.RingGeometry(.7, 1.08, 32), new THREE.MeshBasicMaterial({ color: '#ffe27a', transparent: true, opacity: .75, depthWrite: false, blending: THREE.AdditiveBlending, side: THREE.DoubleSide, toneMapped: false, fog: false }));
    pad.rotation.x = -Math.PI / 2; pad.position.y = .045; g.add(pad);
    const light = new THREE.PointLight('#ffd27a', 3.6, 10, 1.35); light.position.set(0, 1.8, .25); g.add(light);
    Object.assign(g.userData, { archMat, beam, pad, light, flash: 0 });
  }
  const foes = {}; const player = actor('player', spec.player.label, 2.0);
  // fail/fix marks from the agent (window.__MARKS__): red pulsing bug tiles, green fix tiles, arcs for moved spawns
  const MK = []; (window.__MARKS__ || []).forEach(m => { const bug = m.kind === 'bug', col = bug ? '#ff3b3b' : '#35e07a';
    if (m.from && m.to) { const a = new THREE.Vector3(X(m.from[0]), .05, Z(m.from[1])), b = new THREE.Vector3(X(m.to[0]), .05, Z(m.to[1])), mid = a.clone().lerp(b, .5); mid.y = 1.6;
      const tube = new THREE.Mesh(new THREE.TubeGeometry(new THREE.QuadraticBezierCurve3(a, mid, b), 40, .05, 8), new THREE.MeshBasicMaterial({ color: col })); scene.add(tube); MK.push(tube); }
    else (m.cells || []).forEach(([gx, gy]) => { const t = new THREE.Mesh(new THREE.RingGeometry(.32, .46, 4, 1, Math.PI / 4), new THREE.MeshBasicMaterial({ color: col, transparent: true, side: THREE.DoubleSide })); t.rotation.x = -Math.PI / 2; t.position.set(X(gx), .04, Z(gy)); t.scale.setScalar(1.35); t.userData.bug = bug; scene.add(t); MK.push(t); }); });
  // gates: glowing crystal doors with icon, pop in when staggered
  const GI = { fork: '🔀', question: '❓', meter: '🎯' }, gateMesh = {};
  function door(icon) { const pd = portalDoor(emoji(icon, '#ffd27a88')); pd.scale.setScalar(.001); pd.userData.born = 0; pd.userData.portal = true; scene.add(pd); return pd; }
  function doorOld(icon) { const g = new THREE.Group(), body = new THREE.Mesh(new THREE.BoxGeometry(.8, 1.1, .2), new THREE.MeshPhysicalMaterial({ color: '#7e57c2', emissive: '#5e35b1', emissiveIntensity: .9, roughness: .15, transmission: .3, thickness: .5, clearcoat: 1 }));
    body.position.y = .55; body.castShadow = true; const ic = new THREE.Sprite(new THREE.SpriteMaterial({ map: emoji(icon, '#ffd27a88'), depthTest: false })); ic.position.y = 1.5; ic.scale.setScalar(.8); ic.renderOrder = 9;
    const ring = new THREE.Mesh(new THREE.TorusGeometry(.55, .04, 8, 48), new THREE.MeshBasicMaterial({ color: '#ffd27a' })); ring.rotation.x = Math.PI / 2; ring.position.y = .03;
    g.add(body, ic, ring); g.userData = { body, ic, ring, born: 0 }; g.scale.setScalar(.001); scene.add(g); return g; }
  // One instanced pool for every burst. Dead slots stay at scale 0, so a collect or a door opening does not add draw calls.
  const NP = Math.min(300, COARSE ? 120 : 280);
  const starT = ctex((x, w, h) => {
    const g = x.createRadialGradient(w / 2, h / 2, 0, w / 2, h / 2, w * .48);
    g.addColorStop(0, '#fff'); g.addColorStop(.32, '#fff8'); g.addColorStop(1, '#fff0');
    x.fillStyle = g; x.fillRect(0, 0, w, h); x.save(); x.translate(w / 2, h / 2); x.fillStyle = '#fff'; x.beginPath();
    for (let i = 0; i < 8; i++) { const a = -Math.PI / 2 + i * Math.PI / 4, r = (i % 2 ? .2 : .46) * w, px = Math.cos(a) * r, py = Math.sin(a) * r; i ? x.lineTo(px, py) : x.moveTo(px, py); }
    x.closePath(); x.fill(); x.restore();
  }, 64, 64);
  // Optional sparkle star (playground scene 1). Display only: it never blocks a cell.
  let sparkA = null;
  const SPK = (window.__SPARK__ && window.__SPARK__.cell && Number.isFinite(+window.__SPARK__.cell.x) && Number.isFinite(+window.__SPARK__.cell.y)) ? window.__SPARK__.cell : null;
  if (SPK) {
    sparkA = new THREE.Group();
    const star = new THREE.Sprite(new THREE.SpriteMaterial({ map: starT, color: '#ffe56a', transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, toneMapped: false, fog: false }));
    star.scale.set(1.25, 1.25, 1); star.position.y = 1.15; star.renderOrder = 6;
    const halo = new THREE.Sprite(new THREE.SpriteMaterial({ map: glowT, color: '#fff4c0', transparent: true, opacity: .8, depthWrite: false, blending: THREE.AdditiveBlending, toneMapped: false, fog: false }));
    halo.scale.set(2.4, 2.4, 1); halo.position.y = 1.15; halo.renderOrder = 5;
    const ring = new THREE.Mesh(new THREE.RingGeometry(.26, .48, 5), new THREE.MeshBasicMaterial({ color: '#ffe27a', side: THREE.DoubleSide, transparent: true, opacity: .95, depthWrite: false, toneMapped: false }));
    ring.rotation.x = -Math.PI / 2; ring.position.y = .06;
    const light = new THREE.PointLight('#ffd56a', STILL ? .8 : 1.6, 5, 2); light.position.y = 1.3;
    sparkA.add(halo, star, ring, light);
    sparkA.position.set(X(+SPK.x), 0, Z(+SPK.y));
    sparkA.userData = { star, halo, ring, light, bye: null, popped: false };
    scene.add(sparkA);
  }
  const pMesh = new THREE.InstancedMesh(new THREE.PlaneGeometry(1, 1), new THREE.MeshBasicMaterial({ map: starT, color: '#ffffff', transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, toneMapped: false, fog: false, side: THREE.DoubleSide }), NP);
  pMesh.instanceMatrix.setUsage(THREE.DynamicDrawUsage); pMesh.frustumCulled = false; pMesh.count = NP; pMesh.renderOrder = 4; scene.add(pMesh);
  const pDummy = new THREE.Object3D(), pColor = new THREE.Color();
  const PX = new Float32Array(NP), PY = new Float32Array(NP), PZ = new Float32Array(NP), PVX = new Float32Array(NP), PVY = new Float32Array(NP), PVZ = new Float32Array(NP);
  const PLIFE = new Float32Array(NP), PROT = new Float32Array(NP), PSPIN = new Float32Array(NP), PSC = new Float32Array(NP), PR = new Float32Array(NP), PG = new Float32Array(NP), PB = new Float32Array(NP);
  let pi = 0, spawned = 0;
  const hideP = k => { pDummy.position.set(0, -40, 0); pDummy.scale.setScalar(0); pDummy.rotation.set(0, 0, 0); pDummy.updateMatrix(); pMesh.setMatrixAt(k, pDummy.matrix); pMesh.setColorAt(k, pColor.setRGB(0, 0, 0)); };
  for (let k = 0; k < NP; k++) hideP(k);
  pMesh.instanceMatrix.needsUpdate = true;
  function burst(x, z, n, cols, up = 1, y0 = .7, spread = 1, exact = false) {
    if (!exact && COARSE) n = Math.max(3, n >> 2);
    if (STILL) n = Math.min(n, 16);
    spawned += n;
    for (let i = 0; i < n; i++) {
      const k = pi++ % NP, a = Math.random() * 6.283, v = (.04 + Math.random() * .11) * spread;
      pColor.set(cols[i % cols.length]);
      PX[k] = x; PY[k] = y0 + Math.random() * .3; PZ[k] = z;
      PVX[k] = Math.cos(a) * v; PVY[k] = (.055 + Math.random() * .14) * up; PVZ[k] = Math.sin(a) * v;
      PLIFE[k] = .75 + Math.random() * .4; PROT[k] = Math.random() * 6.28; PSPIN[k] = (Math.random() - .5) * .4;
      PSC[k] = .18 + Math.random() * .42; PR[k] = pColor.r; PG[k] = pColor.g; PB[k] = pColor.b;
    }
  }
  function tickParts() {
    let alive = 0;
    for (let k = 0; k < NP; k++) {
      if (PLIFE[k] <= 0) { hideP(k); continue; }
      alive++; PLIFE[k] -= .016; PVY[k] -= .0036;
      PX[k] += PVX[k]; PY[k] = Math.max(.05, PY[k] + PVY[k]); PZ[k] += PVZ[k]; PROT[k] += PSPIN[k];
      const fade = Math.max(0, Math.min(1, PLIFE[k]));
      pDummy.position.set(PX[k], PY[k], PZ[k]); pDummy.quaternion.copy(cam.quaternion); pDummy.rotateZ(PROT[k]); pDummy.scale.setScalar(PSC[k] * (.7 + fade));
      pDummy.updateMatrix(); pMesh.setMatrixAt(k, pDummy.matrix); pMesh.setColorAt(k, pColor.setRGB(PR[k] * fade, PG[k] * fade, PB[k] * fade));
    }
    pMesh.instanceMatrix.needsUpdate = true; if (pMesh.instanceColor) pMesh.instanceColor.needsUpdate = true;
    return alive;
  }
  // dust motes drifting in the warm lamp (frozen in place when motion is reduced)
  const NM = Math.min(120, COARSE ? 40 : 96), mg = new THREE.BufferGeometry(), mp = new Float32Array(NM * 3), mote0 = new Float32Array(NM * 3);
  const moteX = X(spec.player.x), moteZ = Z(spec.player.y);
  for (let i = 0; i < NM; i++) { const a = Math.random() * 6.283, rad = .25 + Math.random() * 2.3; mote0.set([Math.cos(a) * rad, Math.random() * 3.1, Math.sin(a) * rad], i * 3); mp.set([moteX + mote0[i * 3], .4 + mote0[i * 3 + 1], moteZ + mote0[i * 3 + 2]], i * 3); }
  mg.setAttribute('position', new THREE.BufferAttribute(mp, 3)); scene.add(new THREE.Points(mg, new THREE.PointsMaterial({ size: COARSE ? .09 : .07, map: glowT, color: '#ffcf8a', transparent: true, opacity: STILL ? .4 : .82, blending: THREE.AdditiveBlending, depthWrite: false, toneMapped: false })));
  // distant clouds slide slower than the camera so a tall phone still has a sky
  const cloudT = ctex((x, w, h) => { x.clearRect(0, 0, w, h); for (let i = 0; i < 6; i++) { const cx = w * (.12 + i * .15), cy = h * (.48 + (i % 3) * .06), r = h * (.28 + (i % 2) * .1); const g = x.createRadialGradient(cx, cy, 4, cx, cy, r); g.addColorStop(0, 'rgba(255,255,255,.9)'); g.addColorStop(1, 'rgba(255,255,255,0)'); x.fillStyle = g; x.beginPath(); x.arc(cx, cy, r, 0, 6.283); x.fill(); } }, 512, 220);
  const para = [];
  for (let i = 0; i < 4; i++) {
    const m = new THREE.Mesh(new THREE.PlaneGeometry(16, 5.4), new THREE.MeshBasicMaterial({ map: cloudT, transparent: true, depthWrite: false, fog: false, opacity: .38 + (i % 2) * .18, side: THREE.DoubleSide }));
    m.position.set(-12 + i * 8, 6.1 + (i % 2) * 1.35, -7 - i * 1.5); m.frustumCulled = false; scene.add(m);
    para.push({ m, k: .14 + i * .08, bx: m.position.x, by: m.position.y, bz: m.position.z });
  }
  // pooled foot rings (fixed draw calls; the moving hero used to allocate a mesh per step)
  const STEP_N = 16, steps = []; let si = 0;
  for (let i = 0; i < STEP_N; i++) { const s = new THREE.Mesh(new THREE.CircleGeometry(.12, 10), new THREE.MeshBasicMaterial({ color: '#6fe3ff', transparent: true, opacity: 0, depthWrite: false })); s.rotation.x = -Math.PI / 2; s.visible = false; scene.add(s); steps.push(s); }
  // post: bloom + vignette/grade
  const comp = new EffectComposer(gl); comp.addPass(new RenderPass(scene, cam)); const bloom = new UnrealBloomPass(new THREE.Vector2(COARSE ? 256 : 512, COARSE ? 192 : 384), COARSE ? .64 : .78, COARSE ? .36 : .46, .8); comp.addPass(bloom);
  const bloomSet = bloom.setSize.bind(bloom), capX = COARSE ? 256 : 512, capY = COARSE ? 192 : 384;
  bloom.setSize = (w, h) => bloomSet(Math.max(16, Math.min(w, capX)), Math.max(16, Math.min(h, capY)));
  const grade = new ShaderPass({ uniforms: { tDiffuse: { value: null }, t: { value: 0 }, flash: { value: 0 }, tint: { value: new THREE.Color(1, 1, 1) }, grain: { value: COARSE ? 0 : .035 } },
    vertexShader: 'varying vec2 v;void main(){v=uv;gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.);}',
    fragmentShader: 'uniform sampler2D tDiffuse;uniform float t,flash,grain;uniform vec3 tint;varying vec2 v;float h(vec2 p){return fract(sin(dot(p,vec2(12.9898,78.233))+t)*43758.5453);}void main(){vec2 o=(v-.5)*(grain>0.0?0.0025:0.0);vec4 c=vec4(texture2D(tDiffuse,v+o).r,texture2D(tDiffuse,v).g,texture2D(tDiffuse,v-o).b,1.);float d=distance(v,vec2(.5,.45));c.rgb*=smoothstep(.85,.3,d)*.6+.4;c.rgb=mix(c.rgb,c.rgb*vec3(1.05,.98,1.08),.5);c.rgb=mix(c.rgb,c.rgb*tint,.6)+flash*vec3(.55,.3,.08);c.rgb+=(h(v*900.)-.5)*grain;gl_FragColor=c;}' });
  comp.addPass(grade); comp.addPass(new OutputPass());
  function size() {
    const vv = window.visualViewport;
    const vw = Math.max(64, Math.round(window.innerWidth || 0), Math.round(document.documentElement.clientWidth || 0), Math.round((vv && vv.width) || 0));
    const vh = Math.max(48, Math.round(window.innerHeight || 0), Math.round(document.documentElement.clientHeight || 0), Math.round((vv && vv.height) || 0));
    const narrow = vw < 980;
    const pin = (el, pos, w, h) => {
      if (!el) return;
      el.style.setProperty('position', pos, 'important');
      el.style.setProperty('inset', '0px', 'important');
      el.style.setProperty('margin', '0px', 'important');
      el.style.setProperty('max-width', 'none', 'important');
      el.style.setProperty('max-height', 'none', 'important');
      el.style.setProperty('aspect-ratio', 'auto', 'important');
      el.style.setProperty('width', w + 'px', 'important');
      el.style.setProperty('height', h + 'px', 'important');
    };
    let w, h;
    if (PLAYM) {
      w = vw; h = vh;
      pin(wrap, 'fixed', w, h); pin(c2, 'fixed', w, h); pin(cv, 'fixed', w, h);
      const r = cv.getBoundingClientRect();
      if (r.height < vh * 0.92 || r.width < vw * 0.92) { w = vw; h = vh; pin(cv, 'fixed', w, h); }
    } else if (narrow && wrap) {
      wrap.style.setProperty('width', '100%', 'important');
      wrap.style.setProperty('max-width', 'none', 'important');
      wrap.style.setProperty('aspect-ratio', 'auto', 'important');
      wrap.style.removeProperty('height');
      let r = wrap.getBoundingClientRect();
      const minH = Math.round(vh * (vh > vw ? 0.55 : 0.62));
      if (r.height < minH) wrap.style.setProperty('min-height', minH + 'px', 'important');
      r = wrap.getBoundingClientRect();
      w = Math.max(64, Math.round(r.width || vw));
      h = Math.max(48, Math.round(r.height || minH));
      pin(cv, 'absolute', w, h);
    } else {
      const r = c2.getBoundingClientRect();
      w = Math.max(64, Math.round(r.width)); h = Math.max(48, Math.round(r.height));
      cv.style.left = c2.offsetLeft + 'px'; cv.style.top = c2.offsetTop + 'px';
    }
    if (cv._w !== w || cv._h !== h) { cv._w = w; cv._h = h; gl.setSize(w, h, false); comp.setSize(w, h); cam.aspect = w / Math.max(1, h); cam.updateProjectionMatrix(); if (PLAYM) pin(cv, 'fixed', w, h); }
    const fx = window.__STAGE3D__; if (fx) { fx.viewW = w; fx.viewH = h; }
  }
  const seen = { st: 'playing', col: 0, px: spec.player.x, py: spec.player.y, ev: 0, got: new Set() }; let WT = null, shake = 0, flash = 0, bloomKick = 0, heroPulse = 0, tintT = new THREE.Color(1, 1, 1), winT = 0;
  const nudge = n => { if (!STILL) shake = Math.max(shake, n); };
  const pp = new THREE.Vector3(X(spec.player.x), 0, Z(spec.player.y)); let hop = 0, land = 0, dolly = 1.2, idleT = 0, lastMv = 0;
  const RING_N = 8, ringPool = []; let ri = 0;
  for (let i = 0; i < RING_N; i++) { const m = new THREE.Mesh(new THREE.RingGeometry(.15, .28, 20), new THREE.MeshBasicMaterial({ color: '#fff6e0', transparent: true, opacity: 0, depthWrite: false, side: THREE.DoubleSide })); m.rotation.x = -Math.PI / 2; m.visible = false; scene.add(m); ringPool.push(m); }
  function ring(x, z, col = '#fff6e0', sp = 1.09) { const m = ringPool[ri++ % RING_N]; m.visible = true; m.position.set(x, .04, z); m.scale.setScalar(1); m.material.color.set(col); m.material.opacity = .75; m.userData.sp = sp; }
  // Landing dust: soft ground puffs. Reduced motion keeps one still puff (no travel).
  const DUST_N = 28;
  const dustT = ctex((x, w, h) => { const g = x.createRadialGradient(w / 2, h / 2, 2, w / 2, h / 2, w / 2); g.addColorStop(0, 'rgba(255,248,230,.95)'); g.addColorStop(.35, 'rgba(222,196,150,.62)'); g.addColorStop(1, 'rgba(170,140,90,0)'); x.fillStyle = g; x.fillRect(0, 0, w, h); }, 64, 64);
  const dusts = [];
  for (let i = 0; i < DUST_N; i++) { const m = new THREE.Mesh(new THREE.PlaneGeometry(.7, .7), new THREE.MeshBasicMaterial({ map: dustT, transparent: true, opacity: 0, depthWrite: false, fog: false })); m.visible = false; m.renderOrder = 3; scene.add(m); dusts.push(m); }
  let di = 0;
  function puffDust(x, z) {
    const fx = window.__STAGE3D__; const n = STILL ? 1 : (COARSE ? 5 : 8);
    fx.dust = (fx.dust || 0) + n; fx.dustTravel = STILL ? 0 : 1;
    for (let i = 0; i < n; i++) {
      const m = dusts[di++ % DUST_N], a = (i / n) * 6.283 + (STILL ? 0 : Math.random() * .35), sp = STILL ? 0 : (.55 + Math.random() * .7);
      m.visible = true; m.position.set(x + Math.cos(a) * .08, .07, z + Math.sin(a) * .08);
      m.material.opacity = STILL ? .7 : .9; m.scale.setScalar(STILL ? .85 : .35);
      m.userData.vx = Math.cos(a) * sp; m.userData.vz = Math.sin(a) * sp; m.userData.life = STILL ? .45 : (.5 + Math.random() * .28); m.userData.grow = STILL ? 0 : (1.1 + Math.random() * .7);
    }
  }
  function tickDust() {
    let live = 0;
    for (const m of dusts) {
      if (!m.visible) continue; live++; const ud = m.userData; ud.life -= .016;
      if (!STILL) { m.position.x += ud.vx * .016; m.position.z += ud.vz * .016; m.position.y = .06; m.scale.setScalar(Math.min(1.55, m.scale.x + ud.grow * .016)); ud.vx *= .9; ud.vz *= .9; }
      m.material.opacity = Math.max(0, ud.life * 1.7); m.quaternion.copy(cam.quaternion);
      if (ud.life <= 0) m.visible = false;
    }
    window.__STAGE3D__.dustLive = live;
  }
  // Wide double-thump so a slow phone frame still catches the beat (the old spike was ~35ms).
  function heartBeat(now) {
    const u = (now % .92) / .92;
    const lobe = (c, half, flat) => {
      let d = Math.abs(u - c); if (d > .5) d = 1 - d;
      if (d <= flat) return 1; if (d >= half) return 0;
      return Math.cos(((d - flat) / (half - flat)) * Math.PI * .5);
    };
    return Math.min(1, lobe(.12, .22, .08) + lobe(.38, .14, .04) * .72);
  }
  const juiceLight = new THREE.PointLight('#ffd54f', 0, 7.5, 2); juiceLight.position.set(0, -4, 0); scene.add(juiceLight);
  const hint = new THREE.Mesh(new THREE.ConeGeometry(.35, .7, 4), new THREE.MeshStandardMaterial({ color: '#ffe27a', emissive: '#ffb300', emissiveIntensity: 1.2 })); hint.rotation.x = Math.PI; hint.visible = false; scene.add(hint);
  const hintG = new THREE.Mesh(new THREE.RingGeometry(.55, .8, 32), new THREE.MeshBasicMaterial({ color: '#ffe27a', transparent: true, opacity: .6, depthWrite: false, blending: THREE.AdditiveBlending })); hintG.rotation.x = -Math.PI / 2; hintG.visible = false; scene.add(hintG);
  const clock = new THREE.Clock(); window.__STAGE3D__ = { ok: true, engine: 'three r' + THREE.REVISION, frames: 0, pixelRatio: gl.getPixelRatio(), fx: COARSE ? 'low' : 'full', particles: 'instanced', pool: NP, reduced: REDUCED, dust: 0, dustLive: 0, dustTravel: 0, heartbeat: 0, heartbeatMax: 0, doorOpen: false, doorScale: 0, doorScaleMin: null, doorScaleMax: 0, confetti: 0, spark: sparkA ? 1 : 0, sparkOn: sparkA ? 1 : 0, sparkSpin: 0, trail: 0, parallax: STILL ? 0 : 1, camEase: STILL ? 0 : 1, rim: 1, fresnel: RIMS.length ? 1 : 0, shadow: 'pcfsoft', tone: 'ACESFilmic', output: 'srgb', bloomThreshold: .8, lights: 'hemi+key+back', camK: STILL ? 0 : .08, idleAmp: STILL ? 0 : .005, dprCap: 2, lamp: 1 };
  const camTgt = new THREE.Vector3(), lookTgt = new THREE.Vector3(), camHold = new THREE.Vector3(), lookHold = new THREE.Vector3();
  let camReady = false, slowStreak = 0, lite = false, stamp = performance.now();
  // Composer resets the draw-call counter on every pass, so keep the main scene pass.
  let sceneCalls = 0; const renderScene = gl.render.bind(gl);
  gl.render = (s, c) => { renderScene(s, c); if (s === scene) sceneCalls = gl.info.render.calls; };
  let freeze = 0;
  function frame() { requestAnimationFrame(frame); size(); const now = clock.getElapsedTime(); if (freeze > 0) { freeze--; comp.render(); window.__STAGE3D__.frames++; return; } const t = STILL ? 2 : now, S = G.state(), gates = G.gates ? G.gates() : [];
    // juice from state deltas
    const P = S.player; if (P.x !== seen.px || P.y !== seen.py) { hop = 1; const s = steps[si++ % STEP_N]; s.visible = true; s.position.set(X(seen.px), .03, Z(seen.py)); s.scale.setScalar(1); s.material.opacity = .55; seen.px = P.x; seen.py = P.y; if (!STILL) burst(X(P.x), Z(P.y), 6, ['#bdf3ff', '#fff'], .4); }
    if (S.collected.length < seen.col) { seen.col = S.collected.length; seen.got = new Set(S.collected); goals.forEach(g => { if (!S.collected.includes(g.userData.id)) { g.userData.bye = null; g.scale.setScalar(1); } }); }
    const fresh = (S.collected || []).filter(id => !seen.got.has(id));
    if (fresh.length) { fresh.forEach(id => { const g = goals.find(q => q.userData.id === id); const x = g ? g.position.x : X(P.x), z = g ? g.position.z : Z(P.y); if (g) g.userData.bye = now; burst(x, z, 72, ['#ffd54f', '#ffb300', '#fff59d', '#fff'], 1.35, .9, 1.15); burst(x, z, 28, ['#ffffff', '#ffe082'], 2.5, 1.2, .8); ring(x, z, '#ffd54f', 1.16); juiceLight.position.set(x, 1.3, z); }); juiceLight.intensity = 8; heroPulse = 1; bloomKick = Math.max(bloomKick, .9); flash = Math.max(flash, .24); nudge(.2); if (!STILL) freeze = 2; seen.col = S.collected.length; seen.got = new Set(S.collected); }
    if (S.events.length < seen.ev) seen.ev = 0;
    for (let i = seen.ev; i < S.events.length; i++) { const e = S.events[i]; if (e === 'bump' || e.startsWith('gate:') || e.startsWith('sealed:')) nudge(.12); if (e === 'door_open' && doorA) { burst(doorA.position.x, doorA.position.z, 150, ['#fff6c2', '#ffd27a', '#7dffb0', '#b388ff', '#fff'], 1.7, .85, 1.45); burst(doorA.position.x, doorA.position.z, 70, ['#fff', '#ffe082', '#fff6c2'], 2.8, 1.3, .85); ring(doorA.position.x, doorA.position.z, '#fff6c2', 1.12); ring(doorA.position.x, doorA.position.z, '#ffd27a', 1.2); doorA.userData.flash = 1; juiceLight.position.set(doorA.position.x, 1.7, doorA.position.z); juiceLight.intensity = 12; bloomKick = Math.max(bloomKick, 1.2); flash = Math.max(flash, .3); tintT.set(1.12, 1.02, .86); setTimeout(() => tintT.set(1, 1, 1), 900); if (!STILL) freeze = 3; nudge(.18); dolly = 1; }
      if (e.startsWith('gatefail:')) { nudge(.4); tintT.set(1.4, .6, .6); } if (e.startsWith('open:')) { const g = gates.find(q => 'open:' + q.id === e); if (g) burst(X(g.cell[0]), Z(g.cell[1]), 80, ['#ffd27a', '#7dffb0', '#b388ff']); flash = Math.max(flash, .12); bloomKick = Math.max(bloomKick, .4); } }
    seen.ev = S.events.length;
    if (S.status !== seen.st) { if (S.status === 'won') { if (!WT) { const winEs = new URLSearchParams(location.search).get('lang') === 'es'; window.__WIN_TITLE__ = winEs ? '¡GANASTE!' : 'YOU WIN!'; WT = winTitle(window.__WIN_TITLE__); scene.add(WT); } WT.visible = true; WT.position.set(0, 3.2, 0); WT.userData.t0 = t; winT = t; flash = .22; bloomKick = Math.max(bloomKick, .7); if (!STILL) freeze = 5; for (let k = 0; k < 4; k++) burst(X(P.x) + (Math.random() - .5) * 3, Z(P.y) + (Math.random() - .5) * 2, 70, ['#ffd54f', '#66bb6a', '#42a5f5', '#ec407a', '#ab47bc'], 1.5); tintT.set(1.15, 1.05, .9); }
      else if (S.status === 'lost') { nudge(.55); if (!STILL) freeze = 4; burst(X(P.x), Z(P.y), 80, ['#ef5350', '#90caf9', '#2b2118']); tintT.set(1.3, .65, .7); } else { if (WT) WT.visible = false; tintT.set(1, 1, 1); steps.forEach(s => { s.visible = false; }); winT = 0; } seen.st = S.status; }
    if (!STILL && Math.random() < (COARSE ? .04 : .1)) burst(pp.x + (Math.random() - .5) * .4, pp.z + .2, 1, ['#ff9ad5', '#ffe27a', '#9be7ff'], .25);
    // actors
    const trailFromX = player.userData._tx == null ? pp.x : player.userData._tx, trailFromZ = player.userData._tz == null ? pp.z : player.userData._tz;
    pp.lerp(new THREE.Vector3(X(P.x), 0, Z(P.y)), .28); if (hop > .05 && hop * .86 <= .05) { land = 1; ring(pp.x, pp.z); puffDust(pp.x, pp.z); } hop *= .86; land *= .8; player.position.set(pp.x, Math.sin((1 - hop) * Math.PI) * hop * .5, pp.z);
    if (!STILL && (Math.abs(pp.x - trailFromX) + Math.abs(pp.z - trailFromZ) > .012) && ((t * 12 | 0) !== player.userData._tf)) {
      player.userData._tf = t * 12 | 0;
      burst(trailFromX, trailFromZ, COARSE ? 2 : 3, ['#fff6c8', '#ffc2ea', '#b9f3ff'], .22, .32, .32, true);
      window.__STAGE3D__.trail += COARSE ? 2 : 3;
    }
    player.userData._tx = pp.x; player.userData._tz = pp.z;
    const lampTo = new THREE.Vector3(pp.x * .7, 5.5, pp.z + 1.05);
    if (STILL) lamp.position.copy(lampTo); else lamp.position.lerp(lampTo, .08);
    const sq = (1 + Math.sin(t * 5) * .04) * (1 - land * .25) * (1 + hop * .15); player.userData.q.scale.set(1 / sq, sq, 1); player.userData.q.rotation.z = Math.sin(t * 2.3) * .05;
    player.userData.q.material.emissiveIntensity = .08 + heroPulse * 2.2; player.userData.q.material.emissive.set(heroPulse > .04 ? '#ffe7a0' : '#ffffff'); heroPulse *= .9; juiceLight.intensity *= .88; if (juiceLight.intensity < .05) juiceLight.intensity = 0;
    if (S.status === 'won') { player.position.y += Math.min(3, (t - winT) * 1.2); player.rotation.y = (t - winT) * 4; }
    if (S.status === 'lost') player.userData.q.rotation.z = Math.min(1.5, player.userData.q.rotation.z + .2);
    if (sparkA) {
      const got = !!(window.__SPARK__ && window.__SPARK__.got), ud = sparkA.userData;
      if (!got) { ud.bye = null; ud.popped = false; }
      else if (ud.bye == null) { ud.bye = now; if (!ud.popped) { ud.popped = true; if (!STILL) burst(sparkA.position.x, sparkA.position.z, 36, ['#fff6c2', '#ffd54f', '#fff'], 1.3, 1.05, .65); } }
      const age = ud.bye == null ? -1 : now - ud.bye, popping = !STILL && age >= 0 && age < .32;
      sparkA.visible = !got || popping;
      const bob = STILL ? 0 : Math.sin(t * 3) * .18, pulse = STILL ? 1 : (1 + Math.sin(t * 4.2) * .1), popK = popping ? (1 + Math.sin((age / .32) * Math.PI) * .45) : 1;
      ud.star.position.y = 1.15 + bob; ud.halo.position.y = 1.15 + bob;
      ud.star.scale.set(1.25 * pulse * popK, 1.25 * pulse * popK, 1);
      ud.halo.material.opacity = (STILL ? .65 : (.5 + Math.sin(t * 5) * .22)) * (popping ? Math.max(0, 1 - age / .32) : 1);
      ud.ring.rotation.z = STILL ? 0 : t * 1.1;
      ud.light.intensity = STILL ? .8 : (1.3 + Math.sin(t * 5) * .5);
    }
    goals.forEach((g, i) => { const got = S.collected.includes(g.userData.id); if (!got) g.userData.bye = null; else if (g.userData.bye == null) g.userData.bye = now; const age = g.userData.bye == null ? -1 : now - g.userData.bye; const popping = !STILL && age >= 0 && age < .38; g.visible = !got || popping; if (popping) { const k = age / .38; g.scale.setScalar(1 + Math.sin(k * Math.PI) * .55); g.userData.q.material.emissive.set('#ffe27a'); g.userData.q.material.emissiveIntensity = .3 + (1 - k) * 2.4; g.userData.halo.material.opacity = 1; g.userData.q.position.y = g.userData.size / 2 + .25; } else if (!got) { if (g.scale.x !== 1) g.scale.setScalar(1); g.userData.q.material.emissiveIntensity = .08; g.userData.q.material.emissive.set('#ffffff'); g.userData.q.position.y = g.userData.size / 2 + .15 + Math.sin(t * 2 + i) * .12; g.userData.q.rotation.y = Math.sin(t * 1.3 + i) * .5; g.userData.halo.material.opacity = .6 + Math.sin(t * 3 + i) * .3; } });
    npcs.forEach((n, i) => n.userData.q.position.y = n.userData.size / 2 + Math.abs(Math.sin(t * 3 + i)) * .1);
    const live = new Set(); S.foes.forEach((f, i) => { live.add(f.id); const a = foes[f.id] || (foes[f.id] = (() => { const z = actor('enemy', f.label, 1.9, f.id); z.position.set(X(f.x), 0, Z(f.y)); return z; })());
      a.visible = true; a.position.lerp(new THREE.Vector3(X(f.x), 0, Z(f.y)), .2); a.userData.q.rotation.z = Math.sin(t * 4 + i) * .12; a.userData.halo.material.opacity = .35 + Math.sin(t * 6 + i) * .2; });
    Object.keys(foes).forEach(k => { if (!live.has(k)) foes[k].visible = false; });
    if (doorA) { const o = !!S.doorOpen, ud = doorA.userData, hb = (!STILL && o) ? heartBeat(now) : 0, pulse = STILL ? (o ? 1 : .75) : (o ? (.35 + hb) : (.5 + .5 * Math.sin(now * 2.2))), beat = hb, near = Math.hypot(doorA.position.x - pp.x, doorA.position.z - pp.z) < 3.2 ? 1.7 : 1; ud.halo.material.opacity = (o ? .92 : .72) + pulse * .12; ud.halo.scale.setScalar((o ? 4.2 : 3.15) + pulse * .75); ud.q.material.color.set('#ffffff'); ud.q.material.emissive.set('#fff1c2'); ud.q.material.emissiveIntensity = (o ? 1.05 : .75) + pulse * .5 + (ud.flash || 0) * 1.5; ud.q.position.y = ud.size / 2 + (STILL ? 0 : Math.sin(now * 2.2) * .06); if (ud.light) ud.light.intensity = (o ? 6.4 : 3.5) + pulse * (o ? 3.4 : 2.2) + (ud.flash || 0) * 8; if (ud.beam) { ud.beam.material.opacity = (o ? .58 : .4) + pulse * .2; const bs = .92 + pulse * .2; ud.beam.scale.set(bs, 1, bs); } if (ud.pad) { ud.pad.scale.setScalar(1 + pulse * .16 + beat * .18 * near); ud.pad.material.opacity = .42 + pulse * .4; } if (ud.archMat) ud.archMat.color.set(o ? '#fff8d8' : '#ffd56a'); if (ud.flash) ud.flash *= .9; doorA.scale.setScalar(1 + (o ? .06 : .028) * pulse + beat * (o ? .22 * near : 0)); ud.hb = beat; ud.sc = doorA.scale.x; if (o && !STILL && beat > .72 && (ud._puff || 0) !== (now * 2 | 0)) { ud._puff = now * 2 | 0; burst(doorA.position.x, doorA.position.z, 6, ['#fff6c2', '#ffd27a'], .55, .4, .6); } else if (o && !STILL && Math.random() < (COARSE ? .03 : .08)) burst(doorA.position.x + (Math.random() - .5) * .5, doorA.position.z, 2, ['#fff6c2', '#ffd27a'], .8, 1.4, .45); }
    HZ.forEach((m, i) => { m.material.emissiveIntensity = m.userData.haz === 'f' ? 1.2 + Math.sin(t * 9 + i) * .5 : .35 + Math.sin(t * 2 + i) * .15; });
    MK.forEach((m, i) => { if (m.userData.bug !== undefined) { m.rotation.z = t * (m.userData.bug ? 1.5 : -.8); m.material.opacity = m.userData.bug ? .5 + .5 * Math.sin(t * 6) : .85; } });
    // gates: cleared + NEXT one only (mirrors game.js stagger)
    const nx = gates.findIndex(g => !g.open); gates.forEach((g, i) => { const show = nx < 0 || i <= nx; [['a', g.cell, g.open ? 'open' : 'locked'], ['b', g.alt, g.sealed ? 'sealed' : g.open ? 'open' : 'locked']].forEach(([s, cl, mode]) => { if (!cl) return; const k = g.id + s; let d = gateMesh[k];
      if (!d) d = gateMesh[k] = door(GI[g.kind] || '🔒'); d.visible = show; if (!show) { d.userData.born = 0; d.scale.setScalar(.001); return; } if (!d.userData.born) { d.userData.born = t; burst(X(cl[0]), Z(cl[1]), 40, ['#ffd27a', '#ff8ac2']); }
      const age = t - d.userData.born, el = Math.min(1, age / .6), pop = el < 1 ? 1 + Math.sin(el * Math.PI) * .35 : 1; d.position.set(X(cl[0]), 0, Z(cl[1])); d.scale.setScalar(Math.max(.001, el * pop * 1.15)); d.userData.update(t, mode); }); });
    if (!STILL) { for (let i = 0; i < NM; i++) { const y = (mote0[i * 3 + 1] + t * .16) % 3.2; mp[i * 3] = lamp.position.x + mote0[i * 3] + Math.sin(t * .7 + i) * .05; mp[i * 3 + 1] = .35 + y; mp[i * 3 + 2] = lamp.position.z + mote0[i * 3 + 2] + Math.cos(t * .5 + i) * .04; } mg.attributes.position.needsUpdate = true; }
    ringPool.forEach(m => { if (!m.visible) return; m.scale.multiplyScalar(m.userData.sp || 1.09); m.material.opacity *= .9; if (m.material.opacity < .03 || m.scale.x > 8) m.visible = false; });
    steps.forEach(s => { if (!s.visible) return; s.material.opacity *= .94; s.scale.multiplyScalar(1.02); if (s.material.opacity < .04) s.visible = false; });
    if (P.x !== seen.hx || P.y !== seen.hy) { seen.hx = P.x; seen.hy = P.y; lastMv = t; } idleT = t - lastMv;
    { let tg = null; if (S.status === 'playing' && idleT > 5) { const gl = goals.filter(g => g.visible); if (gl.length) tg = gl.reduce((a, b) => (a.position.distanceTo(pp) < b.position.distanceTo(pp) ? a : b)); else if (doorA && S.doorOpen) tg = doorA; }
      hint.visible = hintG.visible = !!tg; if (tg) { hintG.position.set(tg.position.x, .05, tg.position.z); hintG.scale.setScalar(1.2 + Math.abs(Math.sin(t * 4)) * .6 * (idleT > 10 ? 1.6 : 1)); hintG.material.opacity = .45 + Math.sin(t * 8) * .25; if (!STILL && Math.random() < (COARSE ? .05 : .14)) burst(tg.position.x, tg.position.z, 2, ['#ffe27a', '#fff'], .8); hint.position.set(tg.position.x, 2.6 + Math.abs(Math.sin(t * 4)) * .5, tg.position.z); hint.rotation.y = t * 2; hint.scale.setScalar((idleT > 10 ? 1.6 : 1.2) * (1 + Math.pow(Math.max(0, Math.sin(t * 6)), 6) * .25)); } }
    const win = S.status === 'won' ? Math.min(1, (t - winT) / 2) : 0;
    const tx = pp.x, tz = pp.z, drift = STILL ? 0 : 1;
    const portrait = (cam.aspect || 1) < .92;
    const back = portrait ? 8.2 : 7.4, camY = (portrait ? 3.85 : 3.35) + win * 2.2;
    const easeIn = STILL ? 1 : Math.min(1, t / .85), ease = easeIn * easeIn * (3 - 2 * easeIn);
    dolly = STILL ? 0 : dolly * .96;
    cam.fov = (portrait ? 50 : 46) + (1 - ease) * 12 - dolly * 6 + (S.status === 'won' ? 3 : 0);
    cam.updateProjectionMatrix();
    const amp = (portrait ? 8.2 : 7.4) * .005 * drift;
    camTgt.set(tx * .5 + Math.sin(t * .65) * amp, camY + Math.sin(t * .5) * amp, tz + back + win * 1.15);
    lookTgt.set(tx * .78, .9 + win * 1.05, tz - .85);
    if (!camReady || STILL) { camHold.copy(camTgt); lookHold.copy(lookTgt); camReady = true; }
    else { camHold.lerp(camTgt, .08); lookHold.lerp(lookTgt, .08); }
    cam.position.copy(camHold);
    if (!STILL && shake > .005) { cam.position.x += (Math.random() - .5) * shake; cam.position.y += (Math.random() - .5) * shake * .65; shake *= .82; } else shake = 0;
    cam.lookAt(lookHold);
    if (!STILL) para.forEach(L => { L.m.position.x = L.bx + cam.position.x * L.k; L.m.position.y = L.by + Math.sin(t * .25 + L.k * 8) * .12; L.m.position.z = L.bz + cam.position.z * L.k * .2; });
    // billboards face camera (yaw only)
    scene.traverse(o => { if (o.userData && o.userData.q && !(o === player && S.status === 'won')) o.rotation.y = Math.atan2(cam.position.x - o.position.x, cam.position.z - o.position.z); });
    flash *= .9; grade.uniforms.flash.value = flash; grade.uniforms.t.value = t; grade.uniforms.tint.value.lerp(tintT, .06);
    const baseB = COARSE ? .64 : .78;
    bloom.strength = Math.min(.9, baseB + Math.min(.2, bloomKick * .18) + (S.status === 'won' ? .06 : 0));
    bloom.threshold = Math.max(.74, .8 - bloomKick * .04); bloomKick *= .9;
    if (!STILL && RIMS.length) { const p = .84 + Math.sin(t * 2.1) * .16; for (let i = 0; i < RIMS.length; i++) RIMS[i].uniforms.pulse.value = p; }
    if (!STILL && S.status === 'won' && t - winT < 2.5 && Math.random() < (COARSE ? .12 : .4)) burst(pp.x + (Math.random() - .5) * 4, pp.z + (Math.random() - .5) * 2, 8, ['#ff5c8a', '#ffd54f', '#6fe3ff', '#7dffb0', '#c38bff'], 1.6);
    if (WT && WT.visible) WT.userData.update(t - WT.userData.t0, 1 / 60);
    tickDust();
    const alive = tickParts();
    comp.render();
    const fx = window.__STAGE3D__; fx.frames++; fx.bloom = +bloom.strength.toFixed(3); fx.shake = STILL ? 0 : +shake.toFixed(3); fx.doorLight = doorA && doorA.userData.light ? +doorA.userData.light.intensity.toFixed(2) : 0; fx.alive = alive; fx.spawned = spawned; fx.calls = sceneCalls;
    const hbv = doorA && doorA.userData ? (doorA.userData.hb || 0) : 0, scv = doorA && doorA.userData && doorA.userData.sc ? doorA.userData.sc : 0;
    fx.heartbeat = +hbv.toFixed(3); fx.doorOpen = !!(S && S.doorOpen); fx.doorScale = +scv.toFixed(4); fx.reduced = REDUCED;
    fx.spark = sparkA ? 1 : 0; fx.sparkOn = sparkA && sparkA.visible ? 1 : 0; fx.sparkSpin = (sparkA && !STILL && !(window.__SPARK__ && window.__SPARK__.got)) ? 1 : 0;
    fx.parallax = STILL ? 0 : (para.length ? 1 : 0); fx.camEase = STILL ? 0 : 1; fx.rim = 1; fx.fresnel = RIMS.length ? 1 : 0; fx.shadow = 'pcfsoft'; fx.trail = fx.trail || 0; fx.tone = 'ACESFilmic'; fx.output = 'srgb'; fx.bloomThreshold = +bloom.threshold.toFixed(3); fx.lights = 'hemi+key+back'; fx.camK = STILL ? 0 : .08; fx.idleAmp = STILL ? 0 : .005; fx.dprCap = 2; fx.pool = NP; fx.lamp = 1;
    const nowMs = performance.now(), dtMs = nowMs - stamp; stamp = nowMs;
    if (fx.frames > 24 && dtMs > 22 && dtMs < 280) slowStreak++; else slowStreak = Math.max(0, slowStreak - 1);
    if (!lite && slowStreak > 20 && gl.getPixelRatio() > 1) { lite = true; gl.setPixelRatio(1); cv._w = 0; fx.fx = 'lite'; fx.pixelRatio = 1; }
    if (fx.doorOpen && !STILL && scv) { fx.heartbeatMax = Math.max(fx.heartbeatMax || 0, hbv); fx.doorScaleMin = fx.doorScaleMin == null ? scv : Math.min(fx.doorScaleMin, scv); fx.doorScaleMax = Math.max(fx.doorScaleMax || 0, scv); }
    fx.confetti = WT && WT.userData ? (WT.userData.count || 0) : (fx.confetti || 0);
  }
  frame();
  G.render_game_to_text = () => { const S = G.state(); return JSON.stringify({ engine: 'three', status: S.status, player: [S.player.x, S.player.y], foes: S.foes.map(f => [f.id, f.x, f.y]), collected: S.collected, gates: (G.gates ? G.gates() : []).map(g => [g.id, g.open]) }); }; window.render_game_to_text = G.render_game_to_text;
}
setTimeout(boot, 0);
