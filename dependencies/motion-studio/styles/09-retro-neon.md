# 09 · Retro neon reel (synthwave)

**Vzor:** `examples/09-retro-neon.html` (16:9, 12 s, 118 BPM) · obsah: reálne YouTube thumbnaily (`examples/assets/yt/`)
**Kedy:** showreel kanála, prehľad videí, hudobné / herné / kreatívne témy, "throwback" nálada.

## Vzhľad
- Pozadie: radiálny gradient `#2A0E6B` → `#150734`, blikajúce hviezdičky (štvorčeky so seedom, alfa max 0,25).
- Neóny: cyan `#22E5FF`, ružová `#FF2EA6`, oranžová `#FF9A3C`, žltá `#FFE45C`. **Neónový ťah = farebný stroke so `shadowBlur` 28 + tenký biely stroke navrch.**
- **Pixelové písmo:** text sa vykreslí do malého plátna (1/5–1/8 veľkosti) a zväčší bez vyhladenia (`imageSmoothingEnabled = false`). Cache podľa reťazca.
- **Synthwave slnko:** vertikálny gradient žltá → oranžová → ružová, vodorovné pruhy vyrezané `destination-out` a posúvajúce sa nadol. **Perspektívna mriežka** podlahy: zbiehavé čiary + vodorovné čiary s `z^2.2`, ktoré idú k divákovi.
- **Kamerový HUD:** rohové zátvorky, „UKÁZKA / REEL 26“, blikajúce „● REC“, timecode a názov kapitoly vpravo dole (mono 30 px). Na HUD platí rovnaká výnimka ako pri štýle 07.

## Pohybový jazyk
- **Trim paths:** obrysy kariet sa nakreslia (`setLineDash([obvod * p, obvod])`), staggered 0,18 s.
- Predná karta prepína obsah **na beat** (každé 2 beaty).
- Mriežka thumbnailov: nábeh `playful` so staggerom, **skenovacie zvýraznenie** (`M.track` cez indexy) dvihne a rozjasní aktívnu dlaždicu.
- Neónový nápis na konci **zabliká** (náhodné on/off zo seedu 0,8 s) a potom svieti.
- Glitch: 0,3 s RGB posun (cyan kópia pod textom s posunom).

## Štruktúra (12 s)
| čas | kapitola |
|---|---|
| 0–2,4 | 01 HOOK: ružové pozadie, scanlines, pixelový text po 8-inách, meter so zvukom |
| 2,4–6 | 02 STACK: 4 neónové obrysy + predná karta s thumbnailmi na beat, iskra |
| 6–9 | 03 GRID: slnko + mriežka, 3×2 thumbnaily so skenom |
| 9–12 | 04 OUTRO: neónový nápis, pixelové počítadlo, slnko zapadá |

## Zakázané
Viac ako 4 neónové farby naraz · glow na všetkom (textové bloky nechaj bez glow) · rozmazané pixelové písmo (vždy bez vyhladenia) · thumbnaily orezané tak, že nie je čitateľný nadpis (drž 16:9).

## Zvuk
`synthwave` 105–115 BPM. `blip` na písmená, `impact` na glitch, `swoosh` na obrysy, `click` na prepínanie kariet, `pop` na dlaždice, `riser` → `impact` na nápis, `tick` na počítadlo.

## Palety (prepíš konštanty na začiatku `film.html`: BG, PURP, CYAN, PINK, ORNG, YEL)
- **A · Synthwave (default):** BG #150734 · PURP #2A0E6B · CYAN #22E5FF · PINK #FF2EA6 · ORNG #FF9A3C · YEL #FFE45C
- **B · Vaporwave:** BG #1B0F2E · PURP #3A1C5C · CYAN #01CDFE · PINK #FF71CE · ORNG #B967FF · YEL #FFFB96
- **C · Terminál:** BG #030A06 · PURP #0B2A16 · CYAN #39FF14 · PINK #00E5A0 · ORNG #B6FF3B · YEL #E8FFB0
- **Farby značky:** `python3 colors.py <logo alebo screenshot>` → BG → pozadie, INK → text, ACC → akcent (zvyšok dopočítaj ako tóny medzi BG a INK).
