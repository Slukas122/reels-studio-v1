// =====================================================================
// Motion Studio – zber reálnych assetov z webu (capture.mjs)
//   node capture.mjs https://produkt.sk            → assets/ (mobil 430 px @2x)
//   node capture.mjs https://produkt.sk --desktop  → desktop 1440 px
// Uloží: hero.png (prvá obrazovka), full.png (celá stránka),
//        section-01.png… (bloky pod nadpismi h2/h3), brand.json (farby, fonty, nadpisy, logo)
// Pravidlo: v launch reeli animuj IBA tieto reálne obrázky, nikdy nevymýšľaj UI.
// =====================================================================
import { mkdirSync, writeFileSync } from 'node:fs';
import { existsSync } from 'node:fs';
let chromium; try { ({ chromium } = await import('playwright')); } catch { console.error('Chýba Playwright → bash setup.sh'); process.exit(1); }

const url = process.argv[2]; if (!url) { console.error('Použitie: node capture.mjs <url> [--desktop] [--out assets]'); process.exit(1); }
const desktop = process.argv.includes('--desktop');
const oi = process.argv.indexOf('--out'); const OUT = oi > 0 ? process.argv[oi + 1] : 'assets';
mkdirSync(OUT, { recursive: true });

async function launch() { try { return await chromium.launch(); } catch (e) {
  for (const p of ['/opt/pw-browsers/chromium', '/usr/bin/chromium', '/usr/bin/google-chrome']) if (existsSync(p)) try { return await chromium.launch({ executablePath: p }); } catch {}
  throw e; } }
const b = await launch();
const p = await b.newPage(desktop ? { viewport: { width: 1440, height: 900 }, deviceScaleFactor: 1 } : { viewport: { width: 430, height: 932 }, deviceScaleFactor: 2 });
await p.goto(url, { waitUntil: 'networkidle', timeout: 45000 }).catch(() => p.goto(url, { waitUntil: 'load' }));
// zavri cookie lištu (bežné texty SK/CZ/EN)
for (const txt of ['Odmietnuť', 'Odmítnout', 'Reject all', 'Decline', 'Prijať všetko', 'Přijmout vše', 'Accept all', 'Accept', 'Súhlasím', 'OK']) {
  const el = p.getByRole('button', { name: txt, exact: true }).first();
  if (await el.isVisible().catch(() => false)) { await el.click().catch(() => {}); break; }
}
await p.waitForTimeout(800);
await p.screenshot({ path: `${OUT}/hero.png` });
await p.screenshot({ path: `${OUT}/full.png`, fullPage: true });

const info = await p.evaluate(() => {
  const cs = e => e ? getComputedStyle(e) : null;
  const colors = {}; const bump = c => { if (c && !/rgba\(0, 0, 0, 0\)|transparent/.test(c)) colors[c] = (colors[c] || 0) + 1; };
  document.querySelectorAll('body *').forEach((e, i) => { if (i > 3000) return; const s = getComputedStyle(e); bump(s.backgroundColor); bump(s.color); });
  const heads = [...document.querySelectorAll('h1,h2,h3')].map(h => h.textContent.trim().replace(/\s+/g, ' ')).filter(Boolean).slice(0, 25);
  const blocks = [...document.querySelectorAll('h2,h3')].map(h => { let e = h;
    while (e.parentElement && e.getBoundingClientRect().height < 180 && e.parentElement !== document.body) e = e.parentElement;
    const r = e.getBoundingClientRect(); return { title: h.textContent.trim().replace(/\s+/g, ' ').slice(0, 60), x: r.x, y: r.y + scrollY, w: r.width, h: r.height }; })
    .filter(r => r.w > 150 && r.h > 80 && r.h < 1400);
  const logo = document.querySelector('header img, [class*=logo] img, img[alt*=logo i], [class*=logo] svg');
  return { title: document.title, bg: cs(document.body).backgroundColor, text: cs(document.body).color,
    fonts: [...new Set([cs(document.body).fontFamily, cs(document.querySelector('h1'))?.fontFamily].filter(Boolean))],
    colors: Object.entries(colors).sort((a, b) => b[1] - a[1]).slice(0, 12).map(x => x[0]), headings: heads, blocks,
    logo: logo ? (logo.currentSrc || logo.src || 'svg') : null };
});
let n = 0; const seen = new Set();
for (const bl of info.blocks) { const key = Math.round(bl.y / 20); if (seen.has(key) || n >= 12) continue; seen.add(key);
  await p.screenshot({ path: `${OUT}/section-${String(++n).padStart(2, '0')}.png`, clip: { x: bl.x, y: bl.y, width: bl.w, height: bl.h }, fullPage: true }).catch(() => n--);
  bl.file = `section-${String(n).padStart(2, '0')}.png`; }
writeFileSync(`${OUT}/brand.json`, JSON.stringify(info, null, 2));
await b.close();
console.log(`✓ ${OUT}/hero.png, full.png, ${n} sekcií, brand.json\n  Farby: ${info.colors.slice(0, 5).join(' | ')}\n  Fonty: ${info.fonts.join(' | ')}`);
