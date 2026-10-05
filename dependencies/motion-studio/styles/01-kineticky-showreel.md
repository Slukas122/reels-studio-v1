# 01 · Kinetický showreel

**Vzor:** `examples/01-kineticky-showreel.html` (9:16, 12 s, 120 BPM)
**Kedy:** hook na začiatok videa, intro kanála, predstavenie značky alebo služby, "ukáž, čo vieš". Silné pri krátkom texte (3–12 slov).

## Vzhľad
- Kontrast bez kompromisov: takmer čierna `#0E0E0C`, papierová biela `#F2EFE6` a jedna ostrá akcentová farba (`#FF4D1F`).
- Display font je úzky a masívny (**Anton**). Druhý hlas je kurzíva serifu (**Instrument Serif italic**) na jednu "ľudskú" vetu a UI font **Space Grotesk** na drobnosti.
- Text je obrovský: slovo zaberá 70–90 % šírky. Radšej jedno slovo na obraz ako vetu.
- Jemný grain (`M.grain`, 0,04–0,06) zjednotí scény.

## Pohybový jazyk
- **Každý beat = zmena.** Slovo, farba pozadia alebo nová technika. Pri 120 BPM je to každých 0,5 s.
- Nábeh slova je "punch": mierka 1,35 → 1 cez `snappy` + mikro-rotácia, ktorá dosadne.
- Masky: riadky vychádzajú zo škár (`clipRect` + posun o výšku riadku) so staggerom 0,1–0,15 s.
- Každá scéna má **inú techniku** (hook slová · maskované riadky · mriežka tvarov · počítadlo · marquee · lockup). Showreel = katalóg techník, nič sa neopakuje.
- Prechody sú match-cuty: kamera vletí do akcentového prvku, ktorý sa stane pozadím ďalšej scény (scéna 3 → 4 vo vzore).

## Štruktúra (12 s)
| čas | záber | technika |
|---|---|---|
| 0–2 | 4 slová na 4 beaty, pozadie preblikne | punch + farebný flip |
| 2–4 | 3 riadky z masiek, posun, odchod hore | mask reveal + track |
| 4–6 | mriežka tvarov: štvorce → kruhy, zoom do akcentu | stagger + morph + match-cut |
| 6–8 | valčekové počítadlo | rolling digits |
| 8–10 | marquee pozadie + karta s kurzívou a podčiarknutím | layering + ťah |
| 10–12 | logo lockup | mask reveal + playful bodka |

## Techniky vo vzore
Hook slová (scéna 1) · mask reveal riadkov (2) · mriežka so staggerom po diagonále a `rrect` radius morph (3) · valčekové číslice cez clip (4) · nekonečné marquee riadky s opačným smerom (5) · lockup s dvoma maskami (6).

## Zakázané
Fade-in celej vety · viac ako 2 farby + akcent · dlhé vety · pomalé tempo (nič dlhšie ako 2 s bez zmeny).

## Zvuk
`pulse` alebo `house`, 120–128 BPM. `thump`/`impact` na hook slová, `whoosh` na prechody, `tick` na počítadlo, `pop` na stagger (gain 0,3–0,4), `ding` na logo.

## Palety (prepíš konštanty na začiatku `film.html`: INK, PAPER, ACC)
- **A · Oranžová (default):** INK #0E0E0C · PAPER #F2EFE6 · ACC #FF4D1F
- **B · Elektrická modrá:** INK #0B0F2A · PAPER #EAF0FF · ACC #3D5AFE
- **C · Kyselinová:** INK #111111 · PAPER #F4F4EF · ACC #C6FF3D (akcent len na plochy/veľké tvary, na svetlom pozadí slabý kontrast)
- **Farby značky:** `python3 colors.py <logo alebo screenshot>` → BG → pozadie, INK → text, ACC → akcent (zvyšok dopočítaj ako tóny medzi BG a INK).
