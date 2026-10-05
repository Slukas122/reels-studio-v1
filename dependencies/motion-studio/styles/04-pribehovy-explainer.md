# 04 · Príbehový explainer

**Vzor:** `examples/04-pribehovy-explainer.html` (9:16, 18 s, 96 BPM) – "História Bitcoinu"
**Kedy:** história, príbeh firmy/produktu, "X za 60 sekúnd", vysvetlenie pojmu, edukačný short. Prompt vzor: *"história [TÉMA] od [ZAČIATOK] po dnes, prekvap ma storyboardom"*.

## Fakty najprv
Pred shotlistom si zapíš **overené fakty** s dátumami a číslami (4–8 kusov) a do komentára na začiatok súboru daj zdroj. Žiadne odhady ako fakty. Pri cenách a aktuálnych číslach uveď dátum.

## Vzhľad (editorial)
- Tmavá námornícka `#0F1428`, krémová `#F3EADB` a jeden akcent z témy (bitcoin oranžová `#F7931A`).
- Serif pre rozprávanie (**Instrument Serif**, kurzíva na emóciu), **Inter** 800 na čísla a **JetBrains Mono** na dátumy a osi.
- Grain 0,04. Ploché ilustrácie z jednoduchých tvarov (papier, pizza, grafy) – žiadne clipart ikony.

## Štruktúra
- **Hook (0–2,6 s):** konkrétny dátum písaný na stroji + veta s napätím ("niekto poslal e-mail, ktorý zmenil peniaze").
- **Kapitoly po ~3 s:** každá má **jeden vizuálny payoff** (dokument priletí, cenzúrny pruh, dve pizze, graf sa nakreslí, stĺpce sa polovičia).
- **Rokový čip hore** (v `after`) drží orientáciu a pri zmene kapitoly sa čísla vymenia posunom.
- **Záver:** jedno veľké číslo + jedna veta + podpis.

## Techniky vo vzore
Písací stroj s kurzorom · maskované riadky z pružiny · objekt priletí s rotáciou a dosadne · cenzúrny pruh (`expoOut`) · "napísané" riadky textu (šírka podľa `M.prog`) · log-mierka grafu s míľnikmi, ktoré vyskočia (`playful`) · halving stĺpce · počítadlo do veľkého čísla · rokový čip s preslide.

## Rytmus
96–100 BPM (pokojnejšie, rozprávačské). Vo vertikále drž obsah v strednej 70 % zóne (hore a dole prekáža UI sietí).

## Zakázané
Nepodložené čísla · viac ako 1 myšlienka na záber · titulky v rohoch · stock-foto vzhľad.

## Zvuk
`cinematic` (pomalé bubny, plochy). `type` na písanie, `paper` na dokument, `whoosh` na kapitoly, `tick` na míľniky, `riser` → `impact` na finále. Ak má video voiceover, pridaj ho cez `--track` (SFX ostanú).

## Palety (prepíš konštanty na začiatku `film.html`: NAVY, CREAM, ACC, MUTED)
- **A · Námornícka + oranžová (default):** NAVY #0F1428 · CREAM #F3EADB · ACC #F7931A · MUTED #8B93AE
- **B · Tmavozelená + zlatá:** NAVY #111A14 · CREAM #EFE9DA · ACC #D4A017 · MUTED #8FA394
- **C · Bordová + terakota:** NAVY #1A1010 · CREAM #F5E6DC · ACC #E4572E · MUTED #A68F87
- **Farby značky:** `python3 colors.py <logo alebo screenshot>` → BG → pozadie, INK → text, ACC → akcent (zvyšok dopočítaj ako tóny medzi BG a INK).
