#!/usr/bin/env python3
"""Farby značky z obrázka (logo, screenshot webu, fotka) → návrh palety pre film.
   python3 colors.py logo.png                 → hlavné farby + návrh rolí (BG, INK, ACC, ACC2, MUTED) + kontrast
   python3 colors.py assets/hero.png --dark   → preferuj tmavé pozadie
   Pre web: najprv  node capture.mjs https://web.sk  (→ assets/hero.png, brand.json), potom colors.py assets/hero.png
"""
import sys, json, warnings
warnings.filterwarnings("ignore")
from PIL import Image

def lum(c):
    def ch(v):
        v /= 255; return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = c; return 0.2126 * ch(r) + 0.7152 * ch(g) + 0.0722 * ch(b)
def contrast(a, b):
    la, lb = sorted([lum(a), lum(b)], reverse=True); return (la + 0.05) / (lb + 0.05)
def sat(c):
    mx, mn = max(c), min(c); return 0 if mx < 60 else (mx - mn) / mx   # veľmi tmavé = neutrálne
hexc = lambda c: '#%02X%02X%02X' % tuple(c)

path = sys.argv[1]; dark = '--dark' in sys.argv; light = '--light' in sys.argv
im = Image.open(path).convert('RGB'); im.thumbnail((400, 400))
q = im.quantize(colors=12, method=Image.Quantize.MEDIANCUT)
pal = q.getpalette()[:36]; counts = sorted(q.getcolors(), reverse=True)
cols = [(n, tuple(pal[i * 3:i * 3 + 3])) for n, i in counts]
total = sum(n for n, _ in cols)
neutrals = [c for n, c in cols if sat(c) < 0.18]
# akcenty: sýte a svetlé pixely zoskupené podľa odtieňa (nájde aj malé tlačidlo / logo)
import colorsys
bins = {}
for r, g, b in im.getdata():
    h, sv, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
    if sv > 0.45 and v > 0.45:
        k = int(h * 24) % 24; e = bins.setdefault(k, [0, 0, 0, 0]); e[0] += 1; e[1] += r; e[2] += g; e[3] += b
vivid = sorted([(e[0], (e[1] // e[0], e[2] // e[0], e[3] // e[0])) for e in bins.values() if e[0] > 20], reverse=True)

bgc = max(neutrals, key=lambda c: -lum(c)) if dark else (max(neutrals, key=lum) if light else (neutrals[0] if neutrals else cols[0][1]))
ink = max([c for _, c in cols] + [(245, 245, 240), (18, 18, 20)], key=lambda c: contrast(c, bgc))
acc = vivid[0][1] if vivid else (255, 107, 53)
acc2 = vivid[1][1] if len(vivid) > 1 else None
muted = tuple(int(bgc[i] * 0.5 + ink[i] * 0.5) for i in range(3))

print('Hlavné farby (podiel):')
for n, c in cols[:8]: print(f'  {hexc(c)}  {100 * n / total:4.1f} %  sýtosť {sat(c):.2f}')
roles = {'BG': hexc(bgc), 'INK': hexc(ink), 'ACC': hexc(acc), 'MUTED': hexc(muted)}
if acc2: roles['ACC2'] = hexc(acc2)
print('\nNávrh rolí:', json.dumps(roles))
print(f'Kontrast INK/BG {contrast(ink, bgc):.1f}:1 (min 7 na text)  ·  ACC/BG {contrast(acc, bgc):.1f}:1 (min 3 na veľký text)')
if contrast(acc, bgc) < 3: print('⚠ Akcent má na pozadí slabý kontrast – použi ho na plochy, nie na text, alebo zmeň pozadie.')
