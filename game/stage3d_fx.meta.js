import * as THREE from 'three';

const mulberry32 = seed => {
  let a = seed >>> 0;
  return () => {
    a |= 0; a = (a + 0x6D2B79F5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
};
const VERT = 'varying vec2 vUv;void main(){vUv=uv;gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0);}';
const FRAG = `uniform float time;uniform float uOpacity;varying vec2 vUv;float hash(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453);}float noise(vec2 p){vec2 i=floor(p);vec2 f=fract(p);f=f*f*(3.0-2.0*f);return mix(mix(hash(i),hash(i+vec2(1.0,0.0)),f.x),mix(hash(i+vec2(0.0,1.0)),hash(i+vec2(1.0,1.0)),f.x),f.y);}void main(){vec2 p=vUv-0.5;float r=length(p)*2.0;float a=atan(p.y,p.x);float spiral=0.5+0.5*sin(a*4.0-time*3.0+r*10.0);float n=noise(vec2(a*1.5,r*4.0-time*0.8))*0.65+noise(p*9.0+vec2(time*0.35,-time*0.5))*0.35;vec3 col=mix(vec3(0.42,0.12,1.0),vec3(0.05,0.85,1.0),spiral);col=mix(col,vec3(1.0,0.72,0.18),smoothstep(0.62,0.95,n*0.55+spiral*0.45));float core=smoothstep(0.55,0.0,r);col+=vec3(0.35,0.15,0.55)*core;float alpha=smoothstep(1.0,0.12,r)*(0.35+0.65*max(spiral,n))*uOpacity;gl_FragColor=vec4(col*(0.75+n*0.7+core),alpha);}`;

export function portalDoor(iconTexture) {
  const group = new THREE.Group();
  const frame = new THREE.Group();
  const frameMat = new THREE.MeshPhysicalMaterial({ color: 0xa78bfa, emissive: 0x7c3aed, emissiveIntensity: 0.85, metalness: 0.05, roughness: 0.16, flatShading: true, transparent: true, clearcoat: 1, clearcoatRoughness: 0.12, iridescence: 1, iridescenceIOR: 1.35, iridescenceThicknessRange: [100, 400] });
  const arch = new THREE.Mesh(new THREE.TorusGeometry(0.38, 0.065, 8, 28, Math.PI), frameMat);
  arch.position.y = 0.82; arch.castShadow = true; frame.add(arch);
  const legGeo = new THREE.CylinderGeometry(0.055, 0.078, 0.84, 6);
  for (const x of [-0.38, 0.38]) {
    const leg = new THREE.Mesh(legGeo, frameMat);
    leg.position.set(x, 0.42, 0); leg.castShadow = true; frame.add(leg);
  }
  const vortexMat = new THREE.ShaderMaterial({
    uniforms: { time: { value: 0 }, uOpacity: { value: 0.95 } },
    vertexShader: VERT, fragmentShader: FRAG, transparent: true, opacity: 0.95,
    depthWrite: false, blending: THREE.AdditiveBlending, side: THREE.DoubleSide
  });
  const vortex = new THREE.Mesh(new THREE.CircleGeometry(0.36, 40), vortexMat);
  vortex.position.set(0, 0.62, -0.01); vortex.scale.set(1, 1.5, 1);
  const shardMat = new THREE.MeshStandardMaterial({ color: 0xffd98a, emissive: 0xff9d00, emissiveIntensity: 1.6, roughness: 0.25, metalness: 0.1, flatShading: true });
  const shardGeo = new THREE.OctahedronGeometry(0.05, 0);
  const shards = new THREE.Group(); const shardList = [];
  for (let i = 0; i < 6; i++) { const s = new THREE.Mesh(shardGeo, shardMat); s.castShadow = true; shardList.push(s); shards.add(s); }
  const icon = new THREE.Sprite(new THREE.SpriteMaterial({ map: iconTexture, transparent: true, depthWrite: false }));
  icon.position.set(0, 1.7, 0.08); icon.scale.set(0.38, 0.38, 1);
  const ringMat = new THREE.MeshBasicMaterial({ color: 0x8b5cf6, transparent: true, opacity: 0.55, side: THREE.DoubleSide, depthWrite: false, blending: THREE.AdditiveBlending });
  const ring = new THREE.Mesh(new THREE.RingGeometry(0.28, 0.54, 40), ringMat);
  ring.rotation.x = -Math.PI / 2; ring.position.y = 0.015;
  group.add(frame, vortex, shards, icon, ring);
  const placeShards = (t, radius) => {
    for (let i = 0; i < shardList.length; i++) {
      const a = t * 1.5 + i * Math.PI / 3, s = shardList[i];
      s.position.set(Math.cos(a) * radius, 0.68 + Math.sin(a) * radius * 0.8, Math.sin(a) * 0.16);
      s.rotation.set(t * 2 + i, t * 1.6 + i * 1.3, i);
    }
  };
  placeShards(0, 0.52);
  let appliedMode = 'locked';
  group.userData = {
    update(t = 0, mode = 'locked') {
      vortexMat.uniforms.time.value = t;
      if (mode !== appliedMode) { appliedMode = mode; frameMat.needsUpdate = true; }
      if (mode === 'sealed') {
        frame.scale.set(1, 1, 1); frame.position.y = 0; frameMat.opacity = 1; frameMat.color.set(0x8d7c68); frameMat.emissive.set(0x120d08); frameMat.emissiveIntensity = 0.04; frameMat.roughness = 0.95; frameMat.iridescence = 0; frameMat.clearcoat = 0;
        vortex.visible = false; vortexMat.opacity = 0; icon.visible = false; shardMat.color.set(0x8d7c68); shardMat.emissive.set(0x000000); shardMat.emissiveIntensity = 0;
        ringMat.color.set(0x776653); ringMat.opacity = 0.1; ring.scale.setScalar(1);
      } else {
        frameMat.color.set(0xa78bfa); frameMat.emissive.set(0x7c3aed); frameMat.roughness = 0.16; frameMat.iridescence = 1; frameMat.clearcoat = 1;
        shardMat.color.set(0xffd98a); shardMat.emissive.set(0xff9d00); shardMat.emissiveIntensity = 1.6; ringMat.color.set(0x8b5cf6);
        if (mode === 'open') {
          frame.scale.set(0.9, 0.1, 0.9); frame.position.y = 0; frameMat.opacity = 0.15; frameMat.emissiveIntensity = 0.25;
          vortex.visible = true; vortex.scale.set(2.1, 3.15, 1); vortexMat.uniforms.uOpacity.value = 0.32; vortexMat.opacity = 0.32; icon.visible = false; placeShards(t, 0.8); ringMat.opacity = 0.18; ring.scale.setScalar(1.5);
        } else {
          frame.scale.set(1, 1, 1); frame.position.y = 0; frameMat.opacity = 1; frameMat.emissiveIntensity = 0.8 + Math.sin(t * 3) * 0.35;
          vortex.visible = true; vortex.scale.set(1, 1.5, 1); vortexMat.uniforms.uOpacity.value = 0.95; vortexMat.opacity = 0.95;
          icon.visible = true; icon.position.y = 1.7 + Math.sin(t * 2) * 0.05; placeShards(t, 0.52); ringMat.opacity = 0.45 + Math.sin(t * 3) * 0.15; ring.scale.setScalar(1 + Math.sin(t * 3) * 0.04);
        }
      }
    }
  };
  return group;
}

export function rockVariant(baseMesh, seed) {
  const rand = mulberry32(seed);
  baseMesh.rotation.z = -0.35 + rand() * 0.7;
  baseMesh.scale.setScalar(0.75 + rand() * 0.5);
  baseMesh.position.x += (rand() * 2 - 1) * 0.12;
  baseMesh.position.z += (rand() * 2 - 1) * 0.12;
  let target = baseMesh.userData?.q?.isMesh ? baseMesh.userData.q : null;
  baseMesh.traverse(o => { if (!target && o.isMesh && o.userData?.q) target = o.userData.q.isMesh ? o.userData.q : o; });
  if (!target) baseMesh.traverse(o => { if (!target && o.isMesh) target = o; });
  const tint = new THREE.Color(0xcfc3b8).lerp(new THREE.Color(0xffffff), rand());
  if (target?.material) {
    if (Array.isArray(target.material)) target.material = target.material.map(m => { const c = m.clone(); if (c.color) c.color.multiply(tint); return c; });
    else { target.material = target.material.clone(); if (target.material.color) target.material.color.multiply(tint); }
  }
  return baseMesh;
}

export function winTitle(text) {
  const group = new THREE.Group();
  const label = String(text);
  const canvas = document.createElement('canvas'); canvas.width = 1024; canvas.height = 256;
  const ctx = canvas.getContext('2d');
  if (ctx) {
    let fs = 132;
    const setFont = () => { ctx.font = `900 ${fs}px "Arial Rounded MT Bold","Arial Black",Arial,sans-serif`; };
    setFont(); while (ctx.measureText(label).width > 920 && fs > 42) { fs -= 6; setFont(); }
    const grad = ctx.createLinearGradient(0, 45, 0, 210);
    grad.addColorStop(0, '#fff7ae'); grad.addColorStop(0.45, '#ffd94d'); grad.addColorStop(0.75, '#ffb300'); grad.addColorStop(1, '#ff7a00');
    ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.lineJoin = 'round';
    ctx.shadowColor = 'rgba(255,166,0,0.95)'; ctx.shadowBlur = 30; ctx.strokeStyle = '#351a00'; ctx.lineWidth = 18; ctx.strokeText(label, 512, 134);
    ctx.shadowBlur = 18; ctx.fillStyle = grad; ctx.fillText(label, 512, 134);
  }
  const texture = new THREE.CanvasTexture(canvas); texture.colorSpace = THREE.SRGBColorSpace; texture.anisotropy = 4;
  const title = new THREE.Sprite(new THREE.SpriteMaterial({ map: texture, transparent: true, depthTest: false, depthWrite: false }));
  title.scale.set(8, 2, 1); title.renderOrder = 20; group.add(title);
  const count = 300;
  const confetti = new THREE.InstancedMesh(new THREE.PlaneGeometry(0.16, 0.07), new THREE.MeshBasicMaterial({ side: THREE.DoubleSide, toneMapped: false }), count);
  confetti.instanceMatrix.setUsage(THREE.DynamicDrawUsage); confetti.frustumCulled = false; group.add(confetti);
  const rand = mulberry32(0xC0FFEE);
  const dummy = new THREE.Object3D(); const color = new THREE.Color(); const items = [];
  for (let i = 0; i < count; i++) {
    const it = { x: (rand() * 2 - 1) * 4.6, y: -2 + rand() * 5.8, z: (rand() * 2 - 1) * 1.3, speed: 0.7 + rand() * 1.5, rx: rand() * 6.283, ry: rand() * 6.283, rz: rand() * 6.283, sx: (rand() * 2 - 1) * 3, sy: (rand() * 2 - 1) * 3, sz: (rand() * 2 - 1) * 3, sway: rand() * 6.283 };
    items.push(it); confetti.setColorAt(i, color.setHSL(i / count, 1, 0.58));
    dummy.position.set(it.x, it.y, it.z); dummy.rotation.set(it.rx, it.ry, it.rz); dummy.updateMatrix(); confetti.setMatrixAt(i, dummy.matrix);
  }
  if (confetti.instanceColor) confetti.instanceColor.needsUpdate = true;
  group.userData = {
    update(t = 0, dt = 0.016) {
      const step = dt || 0.016;
      let pop = 1;
      if (t < 0.6) { const p = THREE.MathUtils.clamp(t / 0.6, 0, 1); pop = p === 0 ? 0 : Math.pow(2, -10 * p) * Math.sin((p * 10 - 0.75) * (2 * Math.PI / 3)) + 1; title.position.y = 0; }
      else title.position.y = Math.sin((t - 0.6) * 2.2) * 0.08;
      title.scale.set(8 * pop, 2 * pop, 1);
      for (let i = 0; i < items.length; i++) {
        const it = items[i]; it.y -= it.speed * step; if (it.y < -2.2) it.y += 6; it.rx += it.sx * step; it.ry += it.sy * step; it.rz += it.sz * step;
        dummy.position.set(it.x + Math.sin(t * 1.7 + it.sway) * 0.12, it.y, it.z); dummy.rotation.set(it.rx, it.ry, it.rz); dummy.updateMatrix(); confetti.setMatrixAt(i, dummy.matrix);
      }
      confetti.instanceMatrix.needsUpdate = true;
    }
  };
  return group;
}
