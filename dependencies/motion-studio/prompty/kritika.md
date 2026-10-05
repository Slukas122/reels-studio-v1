# Kritika – "prísny motion director"

Otvor `out/film_contact.png` a `out/film_phone.png` (Read) a pozri sa na ne poriadne. Buď prísny motion director, nie hrdý autor.

## Ohodnoť 1–10
1. **Hook** – je v prvých 2 s silný, čitateľný obraz?
2. **Čitateľnosť na mobile** – dá sa text vo `film_phone.png` (360 px) prečítať bez námahy?
3. **Kvalita pohybu** – pružiny, žiadne lineárne kĺzanie, žiadne mŕtve frame-y?
4. **Pestrosť** – deje sa niečo nové každé 2–4 s?
5. **Kompozícia** – vyváženosť, vzduch, nič sa nedotýka okrajov, nič sa neprekrýva?
6. **Zhoda so štýlom / značkou** – farby, fonty a pravidlá zo `styles/NN-*.md`?
7. **Sync so zvukom** – sú `cues` na akciách a beatoch?

## Hľadaj konkrétne
Texty, ktoré sa prekrývajú pri výmene · niečo, čo kĺže namiesto pružiny · popisky a rámiky v rohoch · nadpis v strede na gradiente · rozmazaný zväčšený text · odrezaná diakritika (Š, Ť, Ľ) · bodky alebo artefakty z nulových ťahov · prázdny frame na hrane scény · text za okrajom · kurzor mimo cieľa · zasekávanie na šve loopu.

## Výstup
```
Kolo N: hook 8 · mobil 6 · pohyb 7 · pestrosť 9 · kompozícia 7 · štýl 8 · zvuk 8
1. [4,0 s] text "RYTMUS" presahuje doprava → zmenšiť na 230 px
2. [7,8 s] prázdny oranžový frame 0,4 s → skrátiť odchod
3. [phone] popisok 28 px nečitateľný → 44 px
```
Oprav 3 najhoršie, znova `--stills` (alebo len dotknutý úsek `--from --to`) a urob nové kolo. Končíš, keď je všetko 8+.
