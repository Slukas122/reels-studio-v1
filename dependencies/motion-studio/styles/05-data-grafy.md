# 05 · Dáta a grafy

**Vzor:** `examples/05-data-grafy.html` (16:9, 12 s, 110 BPM)
**Kedy:** výsledky, porovnania, financie, investovanie, reporty, "čísla za rok", infografiky do YouTube videa.

## Dáta
- Všetky čísla drž v objekte `DATA` na začiatku súboru, aby sa dali vymeniť bez zásahu do animácie.
- Reálne dáta = uveď zdroj a dátum (malý mono text). Fiktívne dáta = napíš "ukážkové dáta".
- Formátuj po slovensky: `toLocaleString('sk-SK')`, medzera ako oddeľovač tisícov, " %" s medzerou, "€" za číslom.

## Vzhľad (švajčiarsky / terminál)
- Svetlé plátno `#F5F4EF`, atrament `#111318`, 3 odtiene šedej a **jedna** akcentová farba (`#0FA968`) len pre to, na čom záleží (tvoja hodnota, víťaz).
- **Inter** na nadpisy a čísla, **JetBrains Mono** na hodnoty a osi.
- Veľa vzduchu, zarovnanie doľava, okraj 200 px pri 1920 šírke.

## Grafy vo vzore
| scéna | typ | technika |
|---|---|---|
| KPI | obrie číslo + sparkline | počítadlo `expoOut` + kreslená čiara + bodka na konci |
| stĺpce | ranking | rast so staggerom (`heavy`) → **preusporiadanie podľa poradia** (`base`) |
| donut | alokácia | segmenty rastú postupne, medzery 0,012 rad, legenda s nábehom |
| čiary | porovnanie | plocha pod čiarou, sekundárna línia šedá, **scrub kurzor s tooltipom** |
| záver | výzva | ink wipe + veta |

## Pohybový jazyk
- Grafy sa **kreslia** (čiara rastie po bodoch s interpoláciou posledného úseku). Nikdy sa neobjavia naraz.
- Hodnoty idú od 0 s `expoOut`, aby sa na konci spomalili a dali sa prečítať.
- Na zmenu poradia použi `M.lerp(pôvodný_index, nový_index, M.sp(...))`.
- Akcent sa objaví až pri pointe (Bitcoin zelený, ostatné šedé).

## Zakázané
3D grafy · koláčové grafy s 8+ dielmi · dúhové palety · os bez popisu · čísla bez jednotky · graf bez pointy.

## Zvuk
`minimal` alebo `pulse` 100–115 BPM. `tick` na počítadlá (každých 0,1 s), `pop` na stĺpce, `click` na segmenty, `blip` na scrub, `ding` keď číslo dobehne.

## Palety (prepíš konštanty na začiatku `film.html`: BG, INK, G1, G2, G3, ACC)
- **A · Svetlá + zelená (default):** BG #F5F4EF · INK #111318 · G1 #6B7080 · G2 #C9CBD2 · G3 #E6E6E1 · ACC #0FA968
- **B · Tmavý terminál + tyrkys:** BG #0E1117 · INK #F2F4F8 · G1 #8B93A5 · G2 #3A4150 · G3 #232833 · ACC #22D3EE
- **C · Papier + červená:** BG #F7F5F0 · INK #16130F · G1 #7A7266 · G2 #D6CFC3 · G3 #E9E4DA · ACC #E4572E
- **Farby značky:** `python3 colors.py <logo alebo screenshot>` → BG → pozadie, INK → text, ACC → akcent (zvyšok dopočítaj ako tóny medzi BG a INK).
