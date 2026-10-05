# Motion Studio – návod (Motion Studio)

Balík na tvorbu motion grafiky v Claude. Celé video je kód, takže netreba After Effects ani video AI. Obsahuje **1 skill s 9 štýlmi**, výber farieb a hudby, reálne zvukové efekty, vzorové videá a kontrolu kvality.

## Čo potrebuješ
- **Claude s platenou verziou** (Pro alebo vyššie) a **Cowork** v desktopovej aplikácii Claude. Cowork má vlastný počítač v cloude, kde sa video vyrenderuje. Nič neinštaluješ k sebe.
- Najlepšie výsledky dáva model **Opus 5.5** s vyšším úsilím (effort).

## Inštalácia (2 minúty)
1. Stiahni `motion-studio.zip` (nerozbaľuj ho).
2. V Claude over, že máš zapnuté **Nastavenia → Capabilities → Code execution and file creation**. Potom otvor **Customize → Skills** a klikni **+ Create skill** → nahraj ZIP.
3. Skontroluj, že je skill zapnutý.
4. Otvor Cowork a napíš napríklad: *„Sprav mi kinetický showreel so slovami: Toto celé je len kód.“*

Pri prvom spustení si Claude pripraví prostredie (Playwright, ffmpeg). Trvá to približne minútu.

## 9 štýlov
| # | Štýl | Na čo |
|---|---|---|
| 01 | Kinetický showreel | hooky, intrá, predstavenie značky |
| 02 | Launch reel produktu | promo webu alebo appky z URL, reálne screenshoty |
| 03 | UI morph loop | appka v jednom ťahu, nekonečný loop |
| 04 | Príbehový explainer | história, príbeh, „X za 60 sekúnd“ |
| 05 | Dáta a grafy | čísla, výsledky, financie |
| 06 | Ručne kreslený / papier | útulné vysvetľovanie, akvarel, rukopis |
| 07 | Editorial HUD | tvoja fotka ako módny lookbook |
| 08 | Keynote (Apple) | ohlásenie produktu alebo kurzu, pokojne a „draho“ |
| 09 | Retro neon | showreel kanála, synthwave, neóny |

Launch reel má aj svetlý variant 02b (SaaS štýl, 16:9).

Hotové zadania na skopírovanie nájdeš v `prompty/zadania.md`.

## Čo sa ťa Claude opýta na začiatku
Režim (animácia / fotka + animácia / web + animácia), štýl, formát a dĺžku, farby a hudbu. Ak chceš, odpovedz rovno v zadaní – vzory sú v `prompty/zadania.md`.

## Ako dostať najlepší výsledok
1. **Daj referenciu.** Screenshot videa, ktoré sa ti páči, alebo URL produktu.
2. **Povedz presné texty a čísla.** Claude nemusí hádať.
3. **Nechaj ho pozrieť sa na vlastné frame-y.** Skill to robí automaticky, pýtaj si aspoň 2 kolá opráv.
4. **Iteruj vetou.** „Zrýchli to.“ „Väčší text.“ „Iná farba.“ Oprava trvá sekundy.
5. **Jeden chat = jedna značka.** Druhé video v tom istom chate je rýchlejšie.

## Časté otázky
**Funguje to v ChatGPT?** Nie. Balík je postavený na Claude a Cowork (Claude musí video vyrenderovať a pozrieť sa naň).
**Môžem použiť vlastnú hudbu?** Áno a odporúčam to. Nahraj MP3, Claude zmeria tempo a strihy zosynchronizuje na beaty. Bezplatnú hudbu nájdeš napr. v YouTube Audio Library alebo na Uppbeat.
**Aké farby?** Každý štýl má 3 palety, alebo ti Claude vytiahne farby z tvojho webu či loga.
**Dostanem aj samostatné stopy?** Áno – video bez zvuku, hudbu a efekty zvlášť, ak chceš video dokončiť v strihovom programe.
**Ako dlhé videá?** 6–30 s na jeden prompt.
**Komerčné použitie?** Videá sú tvoje. Fonty v balíku majú licenciu OFL (voľne použiteľné).

---
Motion Studio · example.com
