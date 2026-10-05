/* =====================================================================
   Motion Studio – engine (motion.js)
   Každé video je čistá funkcia času: window.seek(t) nakreslí frame t.
   Žiadne CSS transitions, setTimeout, requestAnimationFrame v renderi,
   žiadny stav medzi frame-ami, žiadne Math.random (len M.rng(seed)).
   ===================================================================== */
(function () {
  const M = {};

  /* ---------- Základ ---------- */
  M.clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
  M.lerp = (a, b, p) => a + (b - a) * p;
  M.map = (x, a, b, c = 0, d = 1) => M.lerp(c, d, M.clamp((x - a) / (b - a)));
  M.TAU = Math.PI * 2;

  /* ---------- Pružiny (closed-form, deterministické) ----------
     spring(t) ide z 0 do 1. t < 0 => 0.                           */
  M.spring = function (t, k = 170, d = 26) {
    if (t <= 0) return 0;
    const w0 = Math.sqrt(k), z = d / (2 * w0);
    if (z < 1) {
      const wd = w0 * Math.sqrt(1 - z * z);
      return 1 - Math.exp(-z * w0 * t) * (Math.cos(wd * t) + (z * w0 / wd) * Math.sin(wd * t));
    }
    return 1 - Math.exp(-w0 * t) * (1 + w0 * t);
  };
  // Presety: [stiffness, damping]
  M.SPRINGS = {
    snappy: [320, 30],   // UI, tlačidlá, prepínače, predné hrany
    base: [170, 26],     // karty, kontajnery, kamera
    heavy: [110, 22],    // veľký text, 3D, logá
    playful: [220, 13],  // maskoti, nálepky – viditeľný overshoot
    soft: [60, 16],      // pomalé plávanie, pozadie
  };
  M.sp = (t, preset = 'base') => { const [k, d] = M.SPRINGS[preset] || preset; return M.spring(t, k, d); };

  // Hodnota s viacerými cieľmi: jedna pružina za každú zmenu (nereštartuje sa).
  // keys: [[čas, hodnota], ...] zoradené podľa času
  M.track = function (t, keys, preset = 'base') {
    let v = keys[0][1];
    for (let i = 1; i < keys.length; i++) v += (keys[i][1] - keys[i - 1][1]) * M.sp(t - keys[i][0], preset);
    return v;
  };
  // To isté pre [x,y] alebo ľubovoľné pole čísel
  M.trackN = function (t, keys, preset = 'base') {
    const out = keys[0][1].slice();
    for (let i = 1; i < keys.length; i++) {
      const s = M.sp(t - keys[i][0], preset);
      for (let j = 0; j < out.length; j++) out[j] += (keys[i][1][j] - keys[i - 1][1][j]) * s;
    }
    return out;
  };

  // Bezšvový LOOP: posledná hodnota v keys musí byť rovnaká ako prvá.
  // Pružiny, ktoré sa nestihli usadiť pred koncom, "dobehnú" na začiatku ďalšieho kola → posledný frame = prvý.
  M.loopTrack = function (t, keys, dur, preset = 'base') {
    let v = keys[0][1];
    for (let i = 1; i < keys.length; i++) {
      const d = keys[i][1] - keys[i - 1][1];
      v += d * (M.sp(t - keys[i][0], preset) + M.sp(t + dur - keys[i][0], preset) - 1);
    }
    return v;
  };
  M.loopTrackN = (t, keys, dur, preset = 'base') => keys[0][1].map((_, j) => M.loopTrack(t, keys.map(k => [k[0], k[1][j]]), dur, preset));

  /* ---------- Easing (len keď pružina nedáva zmysel) ---------- */
  M.ease = {
    linear: p => p,
    inOut: p => p < .5 ? 4 * p * p * p : 1 - Math.pow(-2 * p + 2, 3) / 2,
    out: p => 1 - Math.pow(1 - p, 3),
    in: p => p * p * p,
    expoOut: p => p === 1 ? 1 : 1 - Math.pow(2, -10 * p),
    expoInOut: p => p === 0 ? 0 : p === 1 ? 1 : p < .5 ? Math.pow(2, 20 * p - 10) / 2 : (2 - Math.pow(2, -20 * p + 10)) / 2,
  };
  // Progres 0..1 v okne [a, a+dur] s easingom
  M.prog = (t, a, dur, e = M.ease.out) => e(M.clamp((t - a) / dur));

  // Alfa okno: nábeh po tIn, odchod pred tOut
  M.window = (t, tIn, tOut, fadeIn = 0.12, fadeOut = 0.1) =>
    Math.min(M.clamp((t - tIn) / fadeIn), M.clamp((tOut - t) / fadeOut));

  /* ---------- Náhoda so seedom (nikdy Math.random) ---------- */
  M.rng = function (seed) {
    return function () {
      seed |= 0; seed = seed + 0x6D2B79F5 | 0;
      let t = Math.imul(seed ^ seed >>> 15, 1 | seed);
      t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t;
      return ((t ^ t >>> 14) >>> 0) / 4294967296;
    };
  };
  // Hash -> 0..1 (stabilná náhoda pre index)
  M.hash = (n, seed = 1) => { const r = M.rng((n * 374761393 + seed * 668265263) | 0); r(); return r(); };
  // Plynulý 1D šum (value noise)
  M.noise = function (x, seed = 1) {
    const i = Math.floor(x), f = x - i, u = f * f * (3 - 2 * f);
    return M.lerp(M.hash(i, seed), M.hash(i + 1, seed), u) * 2 - 1;
  };

  /* ---------- Farby ---------- */
  M.hex = function (h) { if (Array.isArray(h)) return h; if (h.startsWith('rgb')) return h.match(/[\d.]+/g).slice(0, 3).map(Number); h = h.replace('#', ''); if (h.length === 3) h = h.split('').map(c => c + c).join('');
    return [parseInt(h.slice(0, 2), 16), parseInt(h.slice(2, 4), 16), parseInt(h.slice(4, 6), 16)]; };
  M.mix = function (a, b, p) { const A = M.hex(a), B = M.hex(b);
    return 'rgb(' + A.map((v, i) => Math.round(M.lerp(v, B[i], M.clamp(p)))).join(',') + ')'; };
  M.alpha = (h, a) => { const c = M.hex(h); return `rgba(${c[0]},${c[1]},${c[2]},${a})`; };

  /* ---------- Rytmus ---------- */
  // b(n) = čas n-tého beatu; bar(n) = čas n-tého taktu (4/4)
  M.beats = function (bpm, offset = 0) { const s = 60 / bpm;
    return { spb: s, b: n => offset + n * s, bar: n => offset + n * 4 * s }; };

  /* ---------- Kreslenie ---------- */
  M.rrect = function (g, x, y, w, h, r) { r = Math.max(0, Math.min(r, Math.abs(w) / 2, Math.abs(h) / 2));
    g.beginPath(); g.roundRect(x, y, w, h, r); };
  // Text s voliteľným letterSpacing, zarovnaním a baseline
  M.text = function (g, str, x, y, o = {}) {
    g.save();
    g.font = o.font || '700 80px Inter';
    g.fillStyle = o.color || '#fff';
    g.textAlign = o.align || 'center';
    g.textBaseline = o.baseline || 'middle';
    if (o.spacing != null) g.letterSpacing = o.spacing + 'px';
    if (o.alpha != null) g.globalAlpha *= o.alpha;
    g.fillText(str, x, y);
    g.restore();
  };
  // Text po písmenách – každé písmeno dostane vlastný progres (stagger)
  // fn(i, char) -> {dx, dy, s, a, rot}
  M.letters = function (g, str, x, y, o, fn) {
    g.save(); g.font = o.font; g.textBaseline = 'middle'; g.textAlign = 'left';
    if (o.spacing != null) g.letterSpacing = o.spacing + 'px';
    const chars = [...str], widths = chars.map(c => g.measureText(c).width + (o.spacing || 0));
    const total = widths.reduce((a, b) => a + b, 0);
    let cx = o.align === 'left' ? x : o.align === 'right' ? x - total : x - total / 2;
    chars.forEach((c, i) => {
      const f = fn(i, c) || {}; const w = widths[i];
      g.save(); g.translate(cx + w / 2 + (f.dx || 0), y + (f.dy || 0));
      g.rotate(f.rot || 0); g.scale(f.s ?? 1, f.sy ?? f.s ?? 1);
      g.globalAlpha *= f.a ?? 1; g.fillStyle = f.color || o.color || '#fff';
      g.fillText(c, -w / 2 + (o.spacing || 0) / 2, 0); g.restore();
      cx += w;
    });
    g.restore();
    return total;
  };
  // Zmeria šírku textu
  M.measure = (g, str, font, spacing = 0) => { g.save(); g.font = font; g.letterSpacing = spacing + 'px';
    const w = g.measureText(str).width; g.restore(); return w; };
  // Maska (clip) obdĺžnikom – na "reveal" textu zdola
  M.clipRect = (g, x, y, w, h) => { g.beginPath(); g.rect(x, y, w, h); g.clip(); };

  // Filmový grain (deterministický podľa frame-u)
  M.grain = function (g, W, H, t, amount = 0.06, seed = 9) {
    const r = M.rng(Math.floor(t * 30) * 7919 + seed);
    g.save(); g.globalAlpha = amount;
    for (let i = 0; i < 1400; i++) {
      g.fillStyle = r() > .5 ? '#fff' : '#000';
      g.fillRect(r() * W, r() * H, 2, 2);
    }
    g.restore();
  };
  // Kurzor (šípka). press 0..1 = stlačenie (zmenší sa + krúžok kliknutia)
  M.cursor = function (g, x, y, o = {}) {
    const sc = (o.scale || 1.6) * (1 - 0.15 * (o.press || 0));
    if (o.ring) { g.save(); g.strokeStyle = M.alpha(o.ringColor || '#ffffff', 1 - o.ring); g.lineWidth = 4;
      g.beginPath(); g.arc(x, y, 12 + 50 * o.ring, 0, M.TAU); g.stroke(); g.restore(); }
    g.save(); g.translate(x, y); g.scale(sc, sc);
    g.shadowColor = 'rgba(0,0,0,.35)'; g.shadowBlur = 8; g.shadowOffsetY = 3;
    g.beginPath(); g.moveTo(0, 0); g.lineTo(0, 26); g.lineTo(6.5, 20); g.lineTo(11, 30); g.lineTo(15, 28.3); g.lineTo(10.6, 18.6); g.lineTo(19, 18.6); g.closePath();
    g.fillStyle = o.fill || '#fff'; g.fill(); g.shadowColor = 'transparent';
    g.lineWidth = 1.6; g.strokeStyle = o.stroke || '#000'; g.lineJoin = 'round'; g.stroke(); g.restore();
  };
  // Obrázok s "cover" orezom do obdĺžnika a zaoblenými rohmi
  M.image = function (g, img, x, y, w, h, o = {}) {
    g.save(); if (o.r) { M.rrect(g, x, y, w, h, o.r); g.clip(); }
    const sx = o.sx || 0, sy = o.sy || 0, sw = o.sw || img.width, sh = o.sh || img.height;
    g.drawImage(img, sx, sy, sw, sh, x, y, w, h); g.restore();
  };

  // Vinetácia
  M.vignette = function (g, W, H, a = 0.45) {
    const gr = g.createRadialGradient(W / 2, H / 2, Math.min(W, H) * .3, W / 2, H / 2, Math.max(W, H) * .75);
    gr.addColorStop(0, 'rgba(0,0,0,0)'); gr.addColorStop(1, `rgba(0,0,0,${a})`);
    g.fillStyle = gr; g.fillRect(0, 0, W, H);
  };

  /* ---------- Film ----------
     M.film({ W, H, DUR, BG, scenes:[{from,to,draw(g,t,T)}], after(g,T), cues, music })
     - draw dostane lokálny čas t (od začiatku scény) a globálny T
     - cues: [{t, type}] – zvukové efekty (click, pop, thump, whoosh, riser, tick, ding, type, swoosh, impact)
     - music: { bpm, style: 'pulse'|'piano'|'lofi'|'epic'|'none', key: 'A'|'C'|'D'|'E'|'F'|'G' }            */
  M.film = function (cfg) {
    const params = new URLSearchParams(location.search);
    const scale = Number(params.get('scale') || 1);
    const W = cfg.W, H = cfg.H;
    const cv = document.createElement('canvas');
    cv.id = 'c'; cv.width = Math.round(W * scale); cv.height = Math.round(H * scale);
    document.body.appendChild(cv);
    const g = cv.getContext('2d');

    function draw(T) {
      g.setTransform(scale, 0, 0, scale, 0, 0);
      g.globalAlpha = 1; g.filter = 'none';
      g.fillStyle = cfg.BG || '#111'; g.fillRect(0, 0, W, H);
      if (cfg.before) cfg.before(g, T);
      for (const s of cfg.scenes) if (T >= s.from && T < s.to) { g.save(); s.draw(g, T - s.from, T, s.to - s.from); g.restore(); }
      if (cfg.after) { g.save(); cfg.after(g, T); g.restore(); }
    }
    window.FILM = { W, H, DUR: cfg.DUR, FPS: cfg.FPS || 30, cues: cfg.cues || [], music: cfg.music || { style: 'none' }, title: cfg.title || 'film' };
    // Video podklady: cfg.videos = { klip: { dir: 'frames/klip', fps: 30, count: 300, ext: 'jpg' } }
    // Snímky priprav:  ffmpeg -i klip.mp4 -vf "fps=30,scale=1920:-2" -q:v 3 frames/klip/%04d.jpg
    // V scéne: const img = M.videoFrame('klip', lokálnyČas)  → Image (alebo null, kým sa nenačíta)
    const VID = cfg.videos || {}, vcache = new Map(), vorder = [];
    M._missing = [];
    const vkey = (name, i) => `${VID[name].dir}/${String(i).padStart(4, '0')}.${VID[name].ext || 'jpg'}`;
    M.videoFrame = function (name, t) {
      const v = VID[name]; if (!v) return null;
      let i = Math.floor(t * v.fps) + 1; i = v.loop ? ((i - 1) % v.count + v.count) % v.count + 1 : Math.max(1, Math.min(v.count, i));
      const k = vkey(name, i), c = vcache.get(k);
      if (c && c.complete && c.naturalWidth) return c;
      M._missing.push(k); return c && c.__prev ? c.__prev : null;
    };
    const loadFrame = k => new Promise(res => { if (vcache.has(k) && vcache.get(k).complete) return res();
      const im = new Image(); im.onload = im.onerror = () => res(); im.src = k; vcache.set(k, im); vorder.push(k);
      while (vorder.length > 180) vcache.delete(vorder.shift()); });
    window.seek = async (T) => {
      for (let pass = 0; pass < 4; pass++) { M._missing = []; draw(T); if (!M._missing.length) break;
        await Promise.all([...new Set(M._missing)].map(loadFrame)); }
      return true;
    };

    // Načítanie fontov pred renderom
    const fams = cfg.fonts || [];
    // Obrázky: cfg.images = { hero: 'assets/hero.png' } → v scénach IMG.hero
    const IMG = window.IMG = {};
    const imgs = Object.entries(cfg.images || {}).map(([k, src]) => new Promise((res, rej) => {
      const im = new Image(); im.onload = () => { IMG[k] = im; res(); }; im.onerror = () => rej(new Error('Obrázok sa nenačítal: ' + src)); im.src = src; }));
    window.__ready = Promise.all([...fams.map(f => document.fonts.load(f)), ...imgs]).then(() => document.fonts.ready).then(() => { draw(0); return true; });

    // Živý náhľad v bežnom prehliadači (v renderi vypnutý)
    if (!navigator.webdriver && !params.has('norun')) {
      document.body.style.cssText = 'margin:0;background:#0b0b0b;display:flex;flex-direction:column;align-items:center;justify-content:center;height:100vh;font:13px system-ui;color:#aaa';
      cv.style.cssText = 'max-width:96vw;max-height:88vh;box-shadow:0 10px 40px #000';
      const bar = document.createElement('input'); bar.type = 'range'; bar.min = 0; bar.max = cfg.DUR; bar.step = 0.001;
      bar.style.cssText = 'width:min(900px,90vw);margin-top:12px';
      const info = document.createElement('div'); info.style.marginTop = '6px';
      document.body.append(bar, info);
      let paused = false, t0 = performance.now(), off = 0, lastT = 0;
      bar.oninput = () => { off = Number(bar.value); t0 = performance.now(); paused = true; window.seek(off); };
      addEventListener('keydown', e => { if (e.code === 'Space') { if (!paused) off = lastT; paused = !paused; t0 = performance.now(); e.preventDefault(); } });
      window.__ready.then(() => (function loop() {
        const T = paused ? off : (off + (performance.now() - t0) / 1000) % cfg.DUR; lastT = T;
        if (!paused) { M._missing = []; draw(T); bar.value = T; M._missing.forEach(loadFrame); }
        info.textContent = `${T.toFixed(2)} s / ${cfg.DUR} s  ·  medzerník = pauza, posuvník = scrub`;
        requestAnimationFrame(loop);
      })());
    } else {
      document.body.style.margin = '0';
    }
    return { g, W, H, draw };
  };

  window.M = M;
})();
