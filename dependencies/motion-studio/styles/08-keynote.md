# 08 · Keynote (Apple štýl)

**Vzor:** `examples/08-apple-keynote.html` (16:9, 14 s, 72 BPM) – ohlásenie workshopu „Ukázkový event“
**Kedy:** ohlásenie produktu, kurzu, eventu alebo novej verzie, kde má výsledok pôsobiť draho a pokojne.

## Princíp: zdržanlivosť
Modely animujú všetko, lebo môžu. Apple animuje len to, čo niečo znamená. **Jedna myšlienka na záber, dlhé držanie (2,5–3,5 s), prechody cez čiernu.** Žiadny bounce, žiadne rýchle strihy, žiadne efekty navyše.

## Vzhľad
- Čierna `#000`, biely text `#F5F5F7`, sivé `#86868B` a `#6E6E73` na podtitulky a drobné písmo (fine print dole, 20 px).
- Inter 600–800 s negatívnym prestrkaním (−2 až −6 px). Titulky 104–150 px, jedna veta na obraz.
- **Svetlo** namiesto grafiky: aditívny bloom (`lighter`) z 3–4 farebných radiálnych gradientov + biele jadro, pomaly "dýcha".
- **Chrómový titulok:** lineárny gradient šedých tónov s pohyblivým odleskom (pozícia stopu podľa času) + slabý odraz na podlahe.
- Produkt v zariadení (notebook, telefón) s **reálnym screenshotom**, odlesk skla, jemná žiara pod ním.

## Pohybový jazyk
- **Odhalenie „blur → ostré“:** alfa 0 → 1, blur 18 → 0 px, posun 24 px hore, mierka 1,04 → 1, `M.ease.out`, 0,9–1,1 s.
- Kamera: pomalý push-in (1 → 1,05 za 3 s). Pružina len `soft`.
- Stagger medzi prvkami 0,25–0,35 s. Nikdy nie všetko naraz.
- Obálka scény `env()`: nábeh z čiernej 0,4–0,8 s, odchod do čiernej 0,4 s.

## Štruktúra (14 s)
| čas | záber |
|---|---|
| 0–3,2 | svetlo sa rozsvieti, jedno slovo („Claude.“), drobné písmo |
| 3,2–6,2 | chrómový titulok s odleskom („naplno.“) |
| 6,2–9,6 | produkt v zariadení + veta a podveta |
| 9,6–12 | tri fakty v stĺpcoch (dátum, čas, cena) |
| 12–14 | lockup + URL + fine print |

## Zakázané
Viac ako 1 myšlienka na obraz · farebné pozadia · bouncy pružiny · častice · HUD popisky · text menší ako 20 px (okrem fine print) · rýchly strih.

## Zvuk
`ambient` alebo `piano` 65–80 BPM. Minimum efektov: jemný `riser` (gain 0,25), `swoosh` 0,3, `ding` 0,5 na lockup.

## Palety (prepíš konštanty na začiatku `film.html`: farby svetla v `bloom()` (pole cols), farba URL v lockupe)
- **A · Teplé svetlo (default):** bloom [255,122,61] [255,79,163] [90,169,255] [255,214,140] · URL #F7A24A
- **B · Chladné svetlo:** bloom [90,169,255] [124,92,255] [64,224,208] [200,220,255] · URL #7DB6FF
- **C · Zlaté svetlo:** bloom [255,196,87] [255,140,66] [255,236,190] [255,170,120] · URL #FFC857
- **Farby značky:** `python3 colors.py <logo alebo screenshot>` → BG → pozadie, INK → text, ACC → akcent (zvyšok dopočítaj ako tóny medzi BG a INK).
