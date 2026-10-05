// =====================================================================
// Motion Studio – render (render.mjs)
//
//   node render.mjs film.html                 → out/<názov>.mp4 (video + zvuk)
//   node render.mjs film.html --stills        → contact sheet + phone test na kritiku
//   node render.mjs film.html --draft         → rýchly náhľad (polovičné rozlíšenie, 30 fps)
//
// Voľby: --fps 30|60  --sub 1|2|4 (motion blur)  --scale 0.5  --from 2 --to 5
//        --out out  --track hudba.mp3 [--track-from 12.5] (vlastná skladba)  --no-audio  --png
//        --every 0.5 (interval pre --stills)
// =====================================================================
import { spawn, spawnSync, execSync } from 'node:child_process';
import { mkdirSync, writeFileSync, existsSync, rmSync, readFileSync } from 'node:fs';
import { createServer } from 'node:http';
import { extname } from 'node:path';
import { resolve, basename, dirname, join } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { synth, writeWav } from './audio.mjs';

const HERE = dirname(fileURLToPath(import.meta.url));
const argv = process.argv.slice(2);
const flag = k => argv.includes('--' + k);
const opt = (k, d) => { const i = argv.indexOf('--' + k); return i >= 0 ? argv[i + 1] : d; };
const html = resolve(argv.find(a => a.endsWith('.html')) || 'index.html');
const NAME = basename(html, '.html');
const OUT = resolve(opt('out', 'out'));
const DRAFT = flag('draft');
const SCALE = Number(opt('scale', DRAFT ? 0.5 : 1));
const SUB = Number(opt('sub', DRAFT ? 1 : 2));
mkdirSync(OUT, { recursive: true });

// ---------- ffmpeg ----------
function findFfmpeg() {
  if (process.env.FFMPEG) return process.env.FFMPEG;
  if (spawnSync('ffmpeg', ['-version']).status === 0) return 'ffmpeg';
  try { return execSync('python3 -c "import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())"').toString().trim(); } catch {}
  console.error('\n✗ ffmpeg sa nenašiel. Spusti: bash setup.sh  (alebo pip install imageio-ffmpeg)\n'); process.exit(1);
}
const FF = findFfmpeg();
const run = (args) => { const r = spawnSync(FF, ['-hide_banner', '-loglevel', 'error', '-y', ...args], { stdio: 'inherit' }); if (r.status) throw new Error('ffmpeg zlyhal'); };

// ---------- prehliadač ----------
let chromium;
try { ({ chromium } = await import('playwright')); }
catch { try { ({ chromium } = await import(pathToFileURL(join(HERE, 'node_modules/playwright/index.mjs')).href)); }
  catch { console.error('\n✗ Chýba Playwright. Spusti: bash setup.sh\n'); process.exit(1); } }
async function launch() {
  try { return await chromium.launch(); }
  catch (e) {
    for (const p of ['/opt/pw-browsers/chromium', '/usr/bin/chromium', '/usr/bin/chromium-browser', '/usr/bin/google-chrome'])
      if (existsSync(p)) try { return await chromium.launch({ executablePath: p }); } catch {}
    throw e;
  }
}

// Lokálny server (file:// by "zašpinil" canvas obrázkami a export by zlyhal)
const ROOT = dirname(html);
const MIME = { '.html': 'text/html; charset=utf-8', '.js': 'text/javascript', '.mjs': 'text/javascript', '.css': 'text/css', '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.webp': 'image/webp', '.svg': 'image/svg+xml', '.ttf': 'font/ttf', '.otf': 'font/otf', '.woff2': 'font/woff2', '.json': 'application/json', '.gif': 'image/gif' };
const server = createServer((req, res) => {
  const p = join(ROOT, decodeURIComponent(req.url.split('?')[0]));
  if (!p.startsWith(ROOT) || !existsSync(p)) { res.writeHead(404); return res.end(); }
  res.writeHead(200, { 'Content-Type': MIME[extname(p).toLowerCase()] || 'application/octet-stream' }); res.end(readFileSync(p));
});
await new Promise(r => server.listen(0, '127.0.0.1', r));
const BASE = `http://127.0.0.1:${server.address().port}/`;

const browser = await launch();
const page = await browser.newPage({ viewport: { width: 400, height: 400 } });
page.on('pageerror', e => console.error('Chyba v stránke:', e.message));
await page.goto(BASE + encodeURIComponent(basename(html)) + `?scale=${SCALE}&norun`);
await page.waitForFunction(() => window.__ready !== undefined, null, { timeout: 15000 });
await page.evaluate(() => window.__ready);
const FILM = await page.evaluate(() => ({ W: FILM.W, H: FILM.H, DUR: FILM.DUR, FPS: FILM.FPS, cues: FILM.cues, music: FILM.music }));
const FPS = Number(opt('fps', DRAFT ? 30 : FILM.FPS || 30));
const FROM = Number(opt('from', 0)), TO = Number(opt('to', FILM.DUR));
const W = Math.round(FILM.W * SCALE), H = Math.round(FILM.H * SCALE);

// Formát snímok: PNG pre stilly (bezstratové), JPEG 95 % pre video (2–3× rýchlejšie, rozdiel po H.264 neviditeľný). --png vynúti PNG.
let FMT = 'image/png';
const grab = (t) => page.evaluate(async ([t, fmt]) => { await window.seek(t);
  return document.getElementById('c').toDataURL(fmt, 0.95).split(',')[1]; }, [t, FMT]);

// ---------- STILLS: contact sheet + phone test ----------
if (flag('stills')) {
  const every = Number(opt('every', 0.5));
  const dir = join(OUT, 'stills'); rmSync(dir, { recursive: true, force: true }); mkdirSync(dir, { recursive: true });
  let n = 0;
  for (let t = FROM; t < TO - 1e-6; t += every) writeFileSync(join(dir, `f${String(n++).padStart(4, '0')}.png`), Buffer.from(await grab(t), 'base64'));
  await browser.close(); server.close();
  const cols = FILM.W >= FILM.H ? 4 : 6, rows = Math.ceil(n / cols);
  const tw = FILM.W >= FILM.H ? 480 : 270;
  run(['-i', join(dir, 'f%04d.png'), '-vf', `scale=${tw}:-1,pad=iw+6:ih+6:3:3:color=0x333333,tile=${cols}x${rows}`, '-frames:v', '1', join(OUT, `${NAME}_contact.png`)]);
  run(['-i', join(dir, 'f%04d.png'), '-vf', `scale=360:-1,pad=iw+6:ih+6:3:3:color=0x333333,tile=${Math.min(n, 5)}x${Math.ceil(n / 5)}`, '-frames:v', '1', join(OUT, `${NAME}_phone.png`)]);
  console.log(`✓ ${n} stillov (každých ${every}s)\n  ${join(OUT, NAME + '_contact.png')}\n  ${join(OUT, NAME + '_phone.png')}`);
  process.exit(0);
}

// ---------- VIDEO ----------
if (!flag('png')) FMT = 'image/jpeg';
const silent = join(OUT, `${NAME}_silent.mp4`);
const vf = SUB > 1 ? ['-vf', `tmix=frames=${SUB},select='eq(mod(n\\,${SUB})\\,${SUB - 1})',setpts=N/${FPS}/TB`] : [];
const ff = spawn(FF, ['-hide_banner', '-loglevel', 'error', '-y', '-f', 'image2pipe', '-framerate', String(FPS * SUB), '-i', '-',
  ...vf, '-r', String(FPS), '-c:v', 'libx264', '-preset', DRAFT ? 'veryfast' : 'medium', '-crf', DRAFT ? '23' : '16',
  '-pix_fmt', 'yuv420p', '-movflags', '+faststart', silent], { stdio: ['pipe', 'inherit', 'inherit'] });

const total = Math.round((TO - FROM) * FPS * SUB), t0 = Date.now();
console.log(`Renderujem ${NAME}: ${W}x${H}, ${FPS} fps, ${SUB} subframe(y), ${(TO - FROM).toFixed(1)} s`);
for (let i = 0; i < total; i++) {
  const png = Buffer.from(await grab(FROM + i / (FPS * SUB)), 'base64');
  if (!ff.stdin.write(png)) await new Promise(r => ff.stdin.once('drain', r));
  if (i % (FPS * SUB) === 0) process.stdout.write(`  ${(i / (FPS * SUB)).toFixed(0)} s / ${(TO - FROM).toFixed(0)} s  (${((Date.now() - t0) / 1000).toFixed(0)} s)\r`);
}
ff.stdin.end();
await new Promise(r => ff.on('close', r));
await browser.close(); server.close();
console.log(`\n✓ obraz hotový za ${((Date.now() - t0) / 1000).toFixed(0)} s`);

// ---------- ZVUK + MIX + STOPY ----------
// Výstup: out/NAME.mp4 (hotové video so zvukom) + out/NAME_stopy/ (video bez zvuku, hudba.wav, efekty.wav)
const final = join(OUT, `${NAME}.mp4`);
const STEMS = join(OUT, `${NAME}_stopy`);
const track = opt('track'), trackFrom = Number(opt('track-from', 0));
if (flag('no-audio')) { run(['-i', silent, '-c', 'copy', final]); }
else {
  mkdirSync(STEMS, { recursive: true });
  const A = synth(track ? { ...FILM, music: { style: 'none' } } : FILM);
  const musicWav = join(STEMS, 'hudba.wav'), sfxWav = join(STEMS, 'efekty.wav'), mixWav = join(STEMS, 'mix.wav');
  writeWav(sfxWav, A.sfx);
  if (track) {
    // vlastná skladba: orez od --track-from, fade-out na konci, hlasitosť -16 LUFS
    run(['-ss', String(trackFrom), '-i', resolve(track), '-t', String(FILM.DUR + 0.8), '-af',
      `afade=t=in:st=0:d=0.05,afade=t=out:st=${Math.max(0, FILM.DUR - 0.8)}:d=0.8,loudnorm=I=-16:TP=-2,aresample=48000`, '-ac', '2', '-c:a', 'pcm_s16le', musicWav]);
  } else if ((FILM.music?.style || 'none') !== 'none') writeWav(musicWav, A.music);
  const hasMusic = existsSync(musicWav);
  if (hasMusic) run(['-i', musicWav, '-i', sfxWav, '-filter_complex', `[0:a]volume=${FILM.musicGain ?? 0.8}[m];[m][1:a]amix=inputs=2:normalize=0:duration=longest[a]`, '-map', '[a]', '-c:a', 'pcm_s16le', mixWav]);
  else writeWav(mixWav, A.sfx);
  run(['-i', silent, '-ss', String(FROM), '-t', String(TO - FROM), '-i', mixWav, '-map', '0:v', '-map', '1:a', '-c:v', 'copy',
    '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-shortest', final]);
  run(['-i', silent, '-c', 'copy', join(STEMS, 'video-bez-zvuku.mp4')]);
  rmSync(mixWav, { force: true });
}
rmSync(silent, { force: true });
console.log(`✓ HOTOVO → ${final}` + (flag('no-audio') ? '' : `\n  stopy pre strih → ${STEMS}/ (video-bez-zvuku.mp4, hudba.wav, efekty.wav)`));
