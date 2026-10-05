# 03 · UI morph loop

**Vzor:** `examples/03-ui-morph-loop.html` (1:1, 8 s, 120 BPM, bezšvový loop)
**Kedy:** príbeh appky/SaaS v jednom ťahu, produktový teaser, animácia na web alebo do hlavičky. Najviac bookmarkovaný formát trendu.

## Koncept
**Jeden kontajner sa nikdy nestrihne.** Ten istý element mení šírku, výšku, radius a farbu zo stavu do stavu (logo → tlačidlo → e-mail pole → loader → úspech → karta → graf → ⌘K paleta → logo). Kurzor spúšťa každú zmenu. Posledný frame = prvý frame, takže sa video dá prehrávať donekonečna.

## Spec – zapíš si ho pred kódom
```
stavy (8–12): [názov, šírka, výška, radius, farba, obsah]
rytmus: 120 BPM, nový stav každé 2 beaty (1 s) → 8 stavov = 8 s
kurzor: pozícia pred každým stavom, klik 0,03 s pred morphom
```

## Vzhľad
- Teplé neutrálne plátno (`#ECE8E1`), tmavý kontajner (`#15171C`), biele karty, **jedna** akcentová farba (`#2F54EB`) + zelená len pre "úspech".
- Font Inter, veľkosti 30–90 px. Jemný tieň pod kontajnerom (blur 50, offset 24).

## Pohybový jazyk
- Rozmery a farba: `M.loopTrack` / `M.loopTrackN` (`base` pre rozmery, `snappy` pre radius a farbu). Najviac malý overshoot, žiadne skákanie.
- Obsah sa objaví **po** začatí morphu (+0,12 s) a zmizne **pred** ďalším (−0,06 s). Takto sa texty nikdy neprekrývajú.
- V každom stave sa niečo deje: písanie, točiaci sa loader, kreslená fajka, rastúce číslo, stĺpce, kreslená čiara, posun výberu.

## Loop bez švu
- Kľúče rozmerov končia návratom do stavu 0 v čase `BACK` ≈ `DUR − 0,45 s`.
- `M.loopTrack` dopočíta pružiny, ktoré sa nestihli usadiť, na začiatok ďalšieho kola.
- Kontrola: stills pri `t = DUR − 1/fps` a `t = 0` musia byť takmer totožné.

## Zakázané
Strih medzi stavmi · bouncy easing · gradienty a glow na UI · častice · mŕtvy čas · text vo vnútri kontajnera počas morphu.

## Zvuk
`piano`, `minimal` alebo `corporate`. `click` pred morphom, `pop` (gain 0,35) pri morphe, `type` pri písaní, `ding` na úspech, `blip` na výber v palete.

## Palety (prepíš konštanty na začiatku `film.html`: CANVAS, INK, WHITE, ACC)
- **A · Teplá neutrálna + modrá (default):** CANVAS #ECE8E1 · INK #15171C · WHITE #FFFFFF · ACC #2F54EB
- **B · Šalvia + zelená:** CANVAS #EEF2EE · INK #13201A · WHITE #FFFFFF · ACC #0E9F6E
- **C · Levanduľa + fialová:** CANVAS #F1ECF7 · INK #1B1526 · WHITE #FFFFFF · ACC #7C3AED
- **Farby značky:** `python3 colors.py <logo alebo screenshot>` → BG → pozadie, INK → text, ACC → akcent (zvyšok dopočítaj ako tóny medzi BG a INK).
