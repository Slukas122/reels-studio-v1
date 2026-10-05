# 02 · Launch reel produktu

**Vzor:** `examples/02-launch-reel.html` (9:16, 15 s, 120 BPM) · assety: `examples/assets/`
**Kedy:** promo webu, appky, SaaS, e-shopu, kurzu, lead magnetu. Všade, kde existuje URL.

## Zlaté pravidlo
**Reálne screenshoty, nikdy vymyslené UI.** Najprv `node capture.mjs <url>` (mobil) alebo `--desktop`, potom si assety pozri a vyber 3–5 najsilnejších: hero, karty funkcií, cenník, formulár/CTA. Farby a font preber z `assets/brand.json`, aby reel vyzeral ako značka.

## Vzhľad
- Pozadie a akcent zo značky (vo vzore tmavá `#0A0C10` + oranžová `#FF6B35`, font Space Grotesk).
- Screenshoty v zaoblenom rámiku s tieňom (karta) alebo v telefóne (hero).
- Kurzor (`M.cursor`) robí reálne akcie: klik, písanie, hover. Každý klik = krúžok (`ring`) + zvuk `click`.

## Štruktúra – 5 beatov (15 s)
| čas | beat | čo sa deje |
|---|---|---|
| 0–2,5 | **Hook** | problém do 5 slov, obrovská kinetická typografia; kľúčové slovo dostane efekt (vo vzore sa "polovičnú" rozpolí) |
| 2,5–5 | **Produkt sa objaví** | telefón vyjde zdola, screenshot sa poskladá z pásov, kamera sa priblíži k nadpisu |
| 5–10,5 | **3 funkcie** | reálne karty prilietajú ako balíček, veľké číslo v pozadí, kurzor klikne na detail |
| 10,5–12,5 | **Jedno číslo** | dôkaz: cena, počet používateľov, ušetrený čas (`[METRIC]`) |
| 12,5–15 | **CTA** | reálny formulár: kurzor napíše e-mail, klikne na tlačidlo, lockup URL + "odkaz v popise" |

## Techniky vo vzore
Rozpolenie slova (translate → clip, dve polovice) · telefón s dynamic island a skladaním z pásov · balíček kariet (hĺbka = zmenšenie + stmavenie) · kurzor po `M.track` s kliknutím · písanie do reálneho inputu (prekrytie placeholdera) · stlačenie tlačidla.

## Pozície v screenshote
Súradnice prvkov (tlačidlo, input) zmeraj v pixeloch screenshotu a prepočítaj koeficientom `k = šírka_na_plátne / img.width`. Over ich v stilloch: kurzor musí trafiť tlačidlo.

## Formáty
Najprv 9:16. Potom 1:1 a 16:9 z tej istej osi: prepočítaj pozície cez `W/H` a daj karty vedľa seba namiesto pod seba.

## Svetlý variant 02b (SaaS, 16:9)
**Vzor:** `examples/02b-launch-reel-svetly.html` (14 s, 116 BPM). Svetlé plátno `#F3F3F1`, obrie číslo vľavo (Inter 800, 230–380 px), reálne screenshoty vpravo.
- **„3D“ karty bez 3D:** `g.transform(cos(rotY), sin(rotY) * 0.18, 0, 1, 0, 0)` = rotácia okolo osi Y. Balíček: každá nová karta posunie staršie dozadu (menšie, vyššie, mierne vybielené).
- **Ghost motion blur:** počas rýchleho príletu nakresli kartu aj v 5 predošlých časoch s alfou 0,1 (funkcia `ghost`).
- Kapitoly „01 / SKILLY · 02 / YOUTUBE · 03 / WEB“ + mono popisky v rohoch (značka, kapitola, timecode, URL).
- Vejár thumbnailov okolo spoločného pivotu pod obrazom, odznak „✓ Nové video“ s rozbiehajúcim sa krúžkom.
- Okno prehliadača s reálnou stránkou, ktorá sa scrolluje (`full.png` z `capture.mjs`), záverečný lockup cez stlmené okno.

## Zvuk
`pulse`. `click` na každú akciu kurzora, `type` na každé písmeno, `whoosh` na príchod karty, `impact` na číslo, `ding` na úspech.

## Palety (prepíš konštanty na začiatku `film.html`: BG, CARD, TXT, MUTED, ACC  (02b: BG, INK, GRAY, ACC))
- **A · Tmavá + oranžová (default):** 02: BG #0A0C10 · CARD #141821 · TXT #F3F1EC · MUTED #8C93A3 · ACC #FF6B35 — 02b: BG #F3F3F1 · INK #121316 · GRAY #7B7F8A · ACC #FF6B35
- **B · Fialová / modrá:** 02: BG #0E0B1A · CARD #1A1530 · TXT #F4F0FF · MUTED #9A93B8 · ACC #8B5CF6 — 02b: BG #F6F7FB · INK #0F172A · GRAY #64748B · ACC #2563EB
- **C · Zelená fintech / magenta:** 02: BG #07130F · CARD #0F2019 · TXT #EAF7F0 · MUTED #86A396 · ACC #22C55E — 02b: BG #FAF7F2 · INK #1C1917 · GRAY #78716C · ACC #D946EF
- **Farby značky:** `python3 colors.py <logo alebo screenshot>` → BG → pozadie, INK → text, ACC → akcent (zvyšok dopočítaj ako tóny medzi BG a INK).
