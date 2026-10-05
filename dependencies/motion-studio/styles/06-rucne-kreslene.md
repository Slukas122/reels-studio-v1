# 06 · Ručne kreslený / papier

**Vzor:** `examples/06-rucne-kreslene.html` (9:16, 12 s, 90 BPM)
**Kedy:** útulný, ľudský tón. Edukácia, "ako to funguje", whiteboard explainer, osobný príbeh, detské alebo wellness témy.

## Vzhľad
- **Papier:** krémová `#F2E8D5` + vlákna a bodky + vinetácia. Textúru predkresli **raz** do offscreen canvasu so seedom – je to deterministická cache.
- **Atrament** `#2A2826` a akvarelové farby: modrá `#5A8BB5`, terakota `#D0654A`, okrová `#E2B04A`. Najviac 3 akvarelové farby.
- **Rukopis:** Caveat (700 na nadpisy, 400 na poznámky).

## Techniky (všetky vo vzore)
- **Boiling line:** čiary sa "prekreslia" 8× za sekundu. Jitter so seedom `boil(T) = floor(T * 8)` napodobňuje ručnú animáciu "on twos". Toto robí 80 % dojmu.
- **Kreslenie ťahom:** `setLineDash([dĺžka * p, dĺžka * 2])`, pričom `p` ide z `M.prog`.
- **Dvojitý ťah:** druhá tenšia čiara s iným seedom a alfou 0,45 pôsobí ako ceruzka.
- **Rovné vs. oblé:** obdĺžniky kresli `lineTo` s jitterom a šípky a podčiarknutia `smooth: true`.
- **Akvarel `wash()`:** 5 vrstiev s alfou 0,16, `multiply`, okraj tmavší (stroke), tvar z `M.noise`. Rastie cez `soft` alebo `playful` pružinu.
- **Rukopis sa píše:** clip zľava doprava podľa `p` a text sa mierne trasie spolu s boil.
- Každá scéna začína na "čistom papieri" a kreslí sa pred očami.

## Štruktúra (12 s)
| čas | záber |
|---|---|
| 0–3 | otázka rukopisom + akvarelová škvrna + dvojité podčiarknutie |
| 3–6 | doodle diagram (laptop → šípka → filmový pás), kreslí sa postupne |
| 6–9 | 3 kroky v akvarelových kruhoch, spojené čiarkami, na konci fajka |
| 9–12 | pointa na veľkej akvarelovej škvrne + doodle hviezdičky + podpis |

## Pravidlá
- Kresby jednoduché, ako by ich nakreslil človek za 10 sekúnd. Menej je viac.
- Rukopis min. 60 px pri šírke 1080. Pre dlhšie texty radšej 2 riadky.
- Žiadne dokonalé tvary, žiadne gradienty, žiadne tiene.

## Zvuk
`lofi` 85–95 BPM (vinyl praskanie). `pen` na každý ťah, `paper` na novú scénu, `pop` (gain 0,4–0,5) na akvarel, `ding` na pointu.

## Palety (prepíš konštanty na začiatku `film.html`: PAPER, INK, BLUE, TERRA, OCHRE)
- **A · Klasický akvarel (default):** PAPER #F2E8D5 · INK #2A2826 · BLUE #5A8BB5 · TERRA #D0654A · OCHRE #E2B04A
- **B · Pastel:** PAPER #F4EFE6 · INK #2B2A33 · BLUE #7FA7C9 · TERRA #E48FA6 · OCHRE #F2C66D
- **C · Príroda:** PAPER #EFEADB · INK #1F2A22 · BLUE #5E8C6A · TERRA #C96F4A · OCHRE #D9B44A
- **Farby značky:** `python3 colors.py <logo alebo screenshot>` → BG → pozadie, INK → text, ACC → akcent (zvyšok dopočítaj ako tóny medzi BG a INK).
