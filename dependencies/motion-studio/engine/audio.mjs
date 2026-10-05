// =====================================================================
// Motion Studio – zvuk (audio.mjs)
// Hudba: syntetizovaná v kóde (11 štýlov) ALEBO vlastná skladba (render.mjs --track).
// Efekty: reálne nahrávky CC0 (Kenney.nl, priečinok sfx/) + syntetizované whoosh/riser/pen.
// Samostatne:  node audio.mjs film.json out/audio.wav
// =====================================================================
import { readFileSync, writeFileSync, readdirSync, existsSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const SR = 48000;
const HERE = dirname(fileURLToPath(import.meta.url));
export const MUSIC_STYLES = {
  pulse: 'moderná elektronika, tech promo (110–128 BPM)',
  house: 'house, energické a tanečné (118–126 BPM)',
  synthwave: 'retro 80s, neón (100–118 BPM)',
  corporate: 'pozitívne, "startup" promo, durové (100–120 BPM)',
  hiphop: 'boom bap beat, sebavedomé (84–96 BPM)',
  lofi: 'pokojné, útulné, vinyl (70–90 BPM)',
  piano: 'elegantný klavír, prémiové (65–85 BPM)',
  ambient: 'vzdušné plochy bez bicích, keynote (60–80 BPM)',
  cinematic: 'filmové bubny a plochy, príbeh (80–100 BPM)',
  minimal: 'len pulz a sub-bas, dáta a UI (100–120 BPM)',
  none: 'bez hudby (len efekty)',
};

function rngF(seed) { let s = seed >>> 0; return () => (s = (s * 1664525 + 1013904223) >>> 0) / 4294967296; }
const mtof = m => 440 * Math.pow(2, (m - 69) / 12);
const KEYS = { C: 48, 'C#': 49, D: 50, 'D#': 51, E: 52, F: 53, 'F#': 54, G: 55, 'G#': 56, A: 57, 'A#': 58, B: 59 };

// ---------- WAV čítanie (PCM16 mono/stereo) ----------
function readWav(path) {
  const b = readFileSync(path); let o = 12, ch = 1, data = null, bits = 16;
  while (o < b.length - 8) { const id = b.toString('ascii', o, o + 4), sz = b.readUInt32LE(o + 4);
    if (id === 'fmt ') { ch = b.readUInt16LE(o + 10); bits = b.readUInt16LE(o + 22); }
    if (id === 'data') { data = b.subarray(o + 8, o + 8 + sz); break; } o += 8 + sz + (sz % 2); }
  if (!data || bits !== 16) return null;
  const n = data.length / 2 / ch, out = new Float32Array(n);
  for (let i = 0; i < n; i++) { let v = 0; for (let c = 0; c < ch; c++) v += data.readInt16LE((i * ch + c) * 2); out[i] = v / ch / 32768; }
  return out;
}
let SAMPLES = null;
function samples() {
  if (SAMPLES) return SAMPLES; SAMPLES = {};
  const dir = join(HERE, 'sfx'); if (!existsSync(dir)) return SAMPLES;
  for (const f of readdirSync(dir)) { const m = f.match(/^([a-z]+)-\d+\.wav$/); if (!m) continue;
    const s = readWav(join(dir, f)); if (s) (SAMPLES[m[1]] ||= []).push(s); }
  return SAMPLES;
}

// ---------- jednoduchý reverb (Schroeder) ----------
function reverb(x, wet = 0.25, size = 1) {
  const combs = [1557, 1617, 1491, 1422].map(d => Math.round(d * size)), aps = [225, 556];
  const out = new Float32Array(x.length);
  for (const d of combs) { const buf = new Float32Array(d); let p = 0, lp = 0;
    for (let i = 0; i < x.length; i++) { const y = buf[p]; lp = y * 0.8 + lp * 0.2; buf[p] = x[i] + lp * 0.8; out[i] += y * 0.25; p = (p + 1) % d; } }
  for (const d of aps) { const buf = new Float32Array(d); let p = 0;
    for (let i = 0; i < x.length; i++) { const bv = buf[p], y = -out[i] + bv; buf[p] = out[i] + bv * 0.5; out[i] = y; p = (p + 1) % d; } }
  for (let i = 0; i < x.length; i++) out[i] = x[i] * (1 - wet * 0.5) + out[i] * wet;
  return out;
}

export function synth(film) {
  const DUR = film.DUR, N = Math.ceil((DUR + 1.5) * SR);
  const mL = new Float32Array(N), mR = new Float32Array(N);   // hudba
  const sL = new Float32Array(N), sR = new Float32Array(N);   // efekty
  const rnd = rngF(1234), noise = () => rnd() * 2 - 1;
  const addTo = (L, R) => (i, v, pan = 0) => { if (i >= 0 && i < N) { L[i] += v * (1 - Math.max(0, pan)); R[i] += v * (1 + Math.min(0, pan)); } };
  const add = addTo(mL, mR), addS = addTo(sL, sR);
  const kicks = [];

  // ---------- nástroje ----------
  function kick(t0, g = 1, punch = 1) { kicks.push(t0); const s = Math.floor(t0 * SR); let ph = 0;
    for (let i = 0; i < 0.45 * SR; i++) { const t = i / SR, f = 45 + 120 * punch * Math.exp(-t * 30); ph += f / SR;
      add(s + i, (Math.sin(ph * 2 * Math.PI) * Math.exp(-t * 7) + (t < .004 ? noise() * .3 : 0)) * 0.9 * g); } }
  function snare(t0, g = 1, tone = 190) { const s = Math.floor(t0 * SR); let lp = 0;
    for (let i = 0; i < 0.25 * SR; i++) { const t = i / SR; lp += (noise() - lp) * 0.5;
      add(s + i, (lp * 0.3 * Math.exp(-t * 20) + Math.sin(2 * Math.PI * tone * t) * 0.3 * Math.exp(-t * 30)) * g); } }
  function clap(t0, g = 1) { const s = Math.floor(t0 * SR); let bp = 0, prev = 0;
    for (let i = 0; i < 0.18 * SR; i++) { const t = i / SR, n = noise(); bp += ((n - prev) - bp) * 0.35; prev = n;
      const env = (t < 0.025 ? 0.6 + 0.4 * Math.cos(t * 2 * Math.PI * 120) : 1) * Math.exp(-t * 28);
      add(s + i, bp * 0.22 * env * g, (i % 2) ? .15 : -.15); } }
  function hat(t0, g = 1, open = false) { const s = Math.floor(t0 * SR); let prev = 0;
    for (let i = 0; i < (open ? .2 : .05) * SR; i++) { const t = i / SR, n = noise(), hp = n - prev; prev = n;
      add(s + i, hp * 0.045 * Math.exp(-t * (open ? 22 : 80)) * g, 0.3); } }
  function tone(t0, dur, midi, g, type = 'saw', pan = 0, cutoff = 0.08, atk = 0.005, rel = 4, detune = 0) {
    const s = Math.floor(t0 * SR), f = mtof(midi) * (1 + detune); let lp = 0, ph = 0;
    for (let i = 0; i < (dur + 0.5) * SR; i++) { const t = i / SR; ph += f / SR; const p = ph % 1;
      let v = type === 'saw' ? 2 * p - 1 : type === 'sq' ? (p < .5 ? 1 : -1) : type === 'tri' ? 4 * Math.abs(p - .5) - 1 : Math.sin(2 * Math.PI * p);
      lp += (v - lp) * cutoff;
      const env = Math.min(1, t / atk) * (t < dur ? Math.exp(-t * rel * 0.25) : Math.exp(-dur * rel * .25) * Math.exp(-(t - dur) * 14));
      add(s + i, (type === 'sine' ? v : lp) * env * g, pan); } }
  function piano(t0, midi, g = 1, dur = 2.5) { const s = Math.floor(t0 * SR), f = mtof(midi);
    for (let i = 0; i < dur * SR; i++) { const t = i / SR;
      const v = Math.sin(2 * Math.PI * f * t) + .45 * Math.sin(4 * Math.PI * f * t) * Math.exp(-t * 3) + .2 * Math.sin(6 * Math.PI * f * t) * Math.exp(-t * 6);
      add(s + i, v * Math.min(1, t / .004) * Math.exp(-t * 1.6) * 0.15 * g, (midi - 60) / 40); } }
  function rhodes(t0, midi, g = 1, dur = 2) { const s = Math.floor(t0 * SR), f = mtof(midi);
    for (let i = 0; i < dur * SR; i++) { const t = i / SR, trem = 1 + 0.15 * Math.sin(2 * Math.PI * 4.5 * t);
      const v = Math.sin(2 * Math.PI * f * t + 1.2 * Math.sin(2 * Math.PI * f * t) * Math.exp(-t * 4));
      add(s + i, v * Math.min(1, t / .01) * Math.exp(-t * 1.2) * 0.1 * g * trem, (midi - 62) / 50); } }
  function pad(t0, dur, midis, g = 1, bright = 0.02) { midis.forEach((m, k) => { const s = Math.floor(t0 * SR); let lp = 0;
    const f1 = mtof(m) * 1.004, f2 = mtof(m) * 0.996;
    for (let i = 0; i < (dur + 1) * SR; i++) { const t = i / SR;
      const v = ((f1 * t) % 1 * 2 - 1) + ((f2 * t) % 1 * 2 - 1); lp += (v - lp) * bright;
      const env = Math.min(1, t / 0.7) * (t < dur ? 1 : Math.exp(-(t - dur) * 4));
      add(s + i, lp * env * 0.045 * g, k % 2 ? .45 : -.45); } }); }
  function pluck(t0, midi, g = 1, pan = 0) { tone(t0, 0.18, midi, 0.1 * g, 'saw', pan, 0.25, .002, 22); tone(t0, 0.18, midi + 12, 0.04 * g, 'sq', -pan, 0.2, .002, 26); }

  // ---------- hudba ----------
  const mu = film.music || {}; let style = mu.style || 'none'; if (style === 'epic') style = 'cinematic';
  if (style !== 'none' && MUSIC_STYLES[style]) {
    const bpm = mu.bpm || 110, spb = 60 / bpm, root = KEYS[mu.key || 'A'] ?? 57;
    const minor = [[0, [0, 3, 7]], [8, [0, 4, 7]], [3, [0, 4, 7]], [10, [0, 4, 7]]];   // i – VI – III – VII
    const major = [[0, [0, 4, 7]], [7, [0, 4, 7]], [9, [0, 3, 7]], [5, [0, 4, 7]]];    // I – V – vi – IV
    const prog = style === 'corporate' ? major : minor;
    const bars = Math.ceil(DUR / (4 * spb)) + 1;
    for (let b = 0; b < bars; b++) {
      const t = b * 4 * spb, [off, tri] = prog[b % 4], r = root + off - (off > 7 ? 12 : 0), ch = tri.map(x => r + 12 + x);
      const q = n => t + n * spb; // štvrťová nota n v takte
      if (style === 'pulse') {
        for (let n = 0; n < 4; n++) { kick(q(n), .9); hat(q(n + .5), 1, n === 3); } clap(q(1), .8); clap(q(3), .8);
        for (let e = 0; e < 8; e++) tone(q(e / 2), spb / 2 * .8, r - 12 + (e % 4 === 3 ? 12 : 0), .26, 'saw', 0, .05, .003, 8);
        for (let s = 0; s < 16; s++) tone(q(s / 4), spb / 4 * .6, ch[s % 3] + 12 * (s % 8 > 3 ? 1 : 0), .06, 'sq', s % 2 ? .5 : -.5, .12, .002, 18);
        pad(t, 4 * spb, ch, .7);
      } else if (style === 'house') {
        for (let n = 0; n < 4; n++) { kick(q(n), 1); hat(q(n + .5), 1.2, true); hat(q(n + .25), .5); hat(q(n + .75), .5); }
        clap(q(1), .7); clap(q(3), .7);
        for (let n = 0; n < 4; n++) tone(q(n + .5), spb * .4, r - 12, .3, 'saw', 0, .07, .003, 6);
        [0.5, 1.75, 2.5, 3.25].forEach(p => ch.forEach((m, k) => tone(q(p), spb * .3, m + 12, .05, 'saw', k - 1, .18, .002, 10)));
        pad(t, 4 * spb, ch, .5, .03);
      } else if (style === 'synthwave') {
        for (let n = 0; n < 4; n++) { kick(q(n), .9, .8); hat(q(n + .5), .7); } snare(q(1), .8, 170); snare(q(3), .8, 170);
        for (let e = 0; e < 8; e++) tone(q(e / 2), spb / 2 * .85, r - 12 + (e % 2 ? 12 : 0), .22, 'saw', 0, .04, .003, 5);
        for (let s = 0; s < 8; s++) tone(q(s / 2), spb / 2 * .7, ch[s % 3] + 12, .07, 'saw', s % 2 ? .4 : -.4, .09, .003, 10, .004);
        pad(t, 4 * spb, ch, 1, .015);
      } else if (style === 'corporate') {
        kick(q(0), .7); kick(q(2), .6); clap(q(1), .5); clap(q(3), .5); for (let n = 0; n < 8; n++) hat(q(n / 2), .5);
        for (let s = 0; s < 8; s++) pluck(q(s / 2), ch[[0, 1, 2, 1, 2, 0, 1, 2][s]] + 12, 1.1, s % 2 ? .3 : -.3);
        tone(t, 4 * spb * .95, r - 12, .18, 'tri', 0, .5, .02, 1); piano(t, r + 12, .7, 4 * spb);
        pad(t, 4 * spb, ch, .45, .03);
      } else if (style === 'hiphop') {
        const sw = spb * 0.08; kick(q(0), 1); kick(q(1.75) + sw, .7); kick(q(2.5), .85); snare(q(1), .8); snare(q(3), .8);
        for (let e = 0; e < 8; e++) hat(q(e / 2) + (e % 2 ? sw : 0), e % 2 ? .5 : .8);
        ch.concat([ch[0] + 12]).forEach((m, k) => rhodes(q(0) + k * .012, m, 1.1, 4 * spb));
        tone(q(0), spb * 1.4, r - 24, .35, 'sine', 0, 1, .01, 2); tone(q(2.5), spb * 1.2, r - 24, .3, 'sine', 0, 1, .01, 2);
      } else if (style === 'lofi') {
        kick(q(0), .8); kick(q(2.5), .6); snare(q(1), .45); snare(q(3), .45);
        for (let e = 0; e < 8; e++) hat(q(e / 2), e % 2 ? .5 : .8);
        ch.concat([ch[0] + 12]).forEach((m, k) => rhodes(q(0) + k * .015, m, .9, 4 * spb));
        tone(q(0), 2 * spb, r - 12, .2, 'sine', 0, 1, .01, 2); tone(q(2), 2 * spb, r - 5, .18, 'sine', 0, 1, .01, 2);
      } else if (style === 'piano') {
        ch.forEach((m, k) => piano(q(0) + k * .02, m, .9, 4 * spb + 1)); piano(q(0), r, 1.1, 4 * spb + 1);
        [0, 1, 2, 1, 2, 0, 1, 2].forEach((a, k) => piano(q(k / 2), ch[a] + 12, .5, 1.5));
      } else if (style === 'ambient') {
        pad(t, 4 * spb, ch.concat([r]), 1.4, .012);
        [0, 2].forEach(k => piano(q(k * 2), ch[(b + k) % 3] + 24, .35, 3));
      } else if (style === 'cinematic') {
        kick(q(0), 1, .7); kick(q(2), .7, .7); kick(q(2.5), .5, .7);
        for (let n = 0; n < 4; n++) tone(q(n), .25, r - 12, .16, 'sine', 0, 1, .002, 12);
        pad(t, 4 * spb, ch.concat([r]), 1.3); tone(t, 4 * spb, r - 12, .22, 'saw', 0, .02, .25, .5);
      } else if (style === 'minimal') {
        for (let n = 0; n < 4; n++) { kick(q(n), .55, .5); hat(q(n + .5), .6); }
        for (let e = 0; e < 8; e++) tone(q(e / 2), spb * .3, r - 12, .16, 'sine', 0, 1, .002, 10);
        if (b % 2 === 0) tone(q(0), 4 * spb, ch[2] + 12, .03, 'tri', .3, .4, .5, .3);
      }
    }
    if (style === 'lofi') for (let i = 0; i < N; i++) if (rnd() < 0.0004) add(i, noise() * 0.22);
    // sidechain: hudba "dýcha" s kickom (pulse, house, synthwave)
    if (['pulse', 'house', 'synthwave'].includes(style)) { const env = new Float32Array(N).fill(1);
      for (const k of kicks) { const s = Math.floor(k * SR); for (let i = 0; i < 0.22 * SR && s + i < N; i++) env[s + i] = Math.min(env[s + i], 0.55 + 0.45 * (i / (0.22 * SR))); }
      for (let i = 0; i < N; i++) { mL[i] *= env[i]; mR[i] *= env[i]; } }
    const wet = { piano: .35, ambient: .5, cinematic: .4, lofi: .22, corporate: .2, synthwave: .25, hiphop: .15 }[style] ?? .12;
    const rl = reverb(mL, wet, 1), rr = reverb(mR, wet, 1.03); mL.set(rl); mR.set(rr);
    // vyrovnanie hlasitosti medzi štýlmi (cieľové RMS)
    let e = 0; for (let i = 0; i < N; i++) e += mL[i] * mL[i] + mR[i] * mR[i];
    const rms = Math.sqrt(e / (2 * N)) || 1, k = Math.min(8, 0.11 / rms); for (let i = 0; i < N; i++) { mL[i] *= k; mR[i] *= k; }
    // fade out hudby
    const f0 = Math.floor((DUR - .5) * SR); for (let i = f0; i < N; i++) { const k = Math.max(0, 1 - (i - f0) / (.8 * SR)); mL[i] *= k; mR[i] *= k; }
  }

  // ---------- efekty ----------
  const S = samples();
  const play = (arr, s, g, pan, idx) => { if (!arr || !arr.length) return false; const smp = arr[idx % arr.length];
    for (let i = 0; i < smp.length; i++) addS(s + i, smp[i] * g, pan); return true; };
  const SYN = {
    whoosh: (s, g) => { let a = 0, b = 0; const n = .5 * SR; for (let i = 0; i < n; i++) { const p = i / n, c = 0.01 + 0.2 * Math.sin(Math.PI * p); a += (noise() - a) * c; b += (a - b) * c; addS(s + i, (a - b) * Math.pow(Math.sin(Math.PI * p), 1.5) * 1.4 * g, (p - .5) * 1.2); } },
    swoosh: (s, g) => { let a = 0; const n = .3 * SR; for (let i = 0; i < n; i++) { const p = i / n; a += (noise() - a) * (0.35 - 0.3 * p); addS(s + i, a * Math.pow(1 - p, 2) * Math.min(1, p * 30) * .6 * g); } },
    riser: (s, g) => { let a = 0; const n = 1.2 * SR; for (let i = 0; i < n; i++) { const p = i / n; a += (noise() - a) * (0.01 + 0.3 * p * p); addS(s + i, (a * .5 + Math.sin(2 * Math.PI * (200 + 900 * p * p) * i / SR) * .06) * p * p * .8 * g); } },
    pen: (s, g) => { let a = 0; for (let i = 0; i < .35 * SR; i++) { const t = i / SR; a += (noise() - a) * .6; addS(s + i, a * (.5 + .5 * Math.sin(t * 90)) * Math.min(1, t * 40) * Math.exp(-t * 5) * .12 * g); } },
    sub: (s, g) => { let ph = 0; for (let i = 0; i < .5 * SR; i++) { const t = i / SR; ph += (50 + 60 * Math.exp(-t * 20)) / SR; addS(s + i, Math.sin(2 * Math.PI * ph) * Math.exp(-t * 7) * .8 * g); } },
  };
  (film.cues || []).forEach((c, idx) => {
    const s = Math.floor(c.t * SR), g = c.gain ?? 1, pan = c.pan ?? 0, type = c.type;
    if (type === 'impact' || type === 'thump') { SYN.sub(s, g * (type === 'impact' ? 1 : .7)); play(S[type], s, g * .8, pan, idx); return; }
    if (SYN[type]) return SYN[type](s, g);
    if (!play(S[type], s, g * .8, pan, idx)) play(S.click, s, g * .6, pan, idx);
  });

  // ---------- mix ----------
  const L = new Float32Array(N), R = new Float32Array(N), mg = film.musicGain ?? 0.8, sg = film.sfxGain ?? 1;
  for (let i = 0; i < N; i++) { L[i] = Math.tanh(mL[i] * mg + sL[i] * sg); R[i] = Math.tanh(mR[i] * mg + sR[i] * sg); }
  const clip = (A) => A.map(v => Math.tanh(v));
  return { L, R, N, music: { L: clip(mL), R: clip(mR), N }, sfx: { L: clip(sL), R: clip(sR), N } };
}

export function writeWav(path, { L, R, N }) {
  const b = Buffer.alloc(44 + N * 4);
  b.write('RIFF', 0); b.writeUInt32LE(36 + N * 4, 4); b.write('WAVEfmt ', 8);
  b.writeUInt32LE(16, 16); b.writeUInt16LE(1, 20); b.writeUInt16LE(2, 22);
  b.writeUInt32LE(SR, 24); b.writeUInt32LE(SR * 4, 28); b.writeUInt16LE(4, 32); b.writeUInt16LE(16, 34);
  b.write('data', 36); b.writeUInt32LE(N * 4, 40);
  for (let i = 0; i < N; i++) {
    b.writeInt16LE(Math.round(Math.max(-1, Math.min(1, L[i])) * 32767), 44 + i * 4);
    b.writeInt16LE(Math.round(Math.max(-1, Math.min(1, R[i])) * 32767), 46 + i * 4);
  }
  writeFileSync(path, b);
}

if (process.argv[1] && process.argv[1].endsWith('audio.mjs')) {
  if (process.argv[2] === '--list') { for (const [k, v] of Object.entries(MUSIC_STYLES)) console.log(`${k.padEnd(10)} ${v}`); }
  else if (process.argv[2] === '--demo') {
    // node audio.mjs --demo out/  → 10 s ukážka každého hudobného štýlu (na výber podľa ucha)
    const dir = process.argv[3] || 'out'; const tempos = { pulse: 120, house: 124, synthwave: 110, corporate: 112, hiphop: 90, lofi: 80, piano: 72, ambient: 70, cinematic: 90, minimal: 110 };
    for (const [k, bpm] of Object.entries(tempos)) writeWav(join(dir, `hudba-${k}.wav`), synth({ DUR: 10, music: { style: k, bpm, key: 'A' }, cues: [] }));
    console.log(`✓ ukážky v ${dir}/hudba-*.wav`);
  } else if (process.argv[2]) {
    const film = JSON.parse(readFileSync(process.argv[2], 'utf8'));
    writeWav(process.argv[3] || 'out/audio.wav', synth(film)); console.log('audio hotové');
  }
}
