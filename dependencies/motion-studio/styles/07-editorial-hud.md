# 07 · Editorial HUD (módny lookbook)

**Vzor:** `examples/07-editorial-hud.html` (16:9, 12 s, 100 BPM) · podklad: `examples/assets/portrait/demo.jpg`
**Kedy:** predstavenie osobnosti, tvorcu, speakera, tímu alebo produktu "ako na móle". Profil, intro kanála, pozvánka s tvárou. Podklad je fotka (portrét, produkt, tím).

## Z čoho sa skladá
1. **Podklad** – reálna fotka. Grade (desaturácia, kontrast, jemná sépia) sa aplikuje **raz** do cache. **Halftone raster** (predkreslený vzor bodiek, `multiply`), zdvihnuté čierne (`screen`), vinetácia, grain.
2. **Looky** – 3–5 záberov z toho istého podkladu (celok, detail očí, posunutý výrez). Kamera: `cam` (bod v obrázku), `zoom`, pomalý `drift` a push-in. Strih = rack focus (blur 10 → 0) + krátky biely záblesk.
3. **Hľadáčik** – rohové zátvorky okolo tváre (súradnice `box` v pixeloch obrázka). Pri strihu sa na nový cieľ presunú pružinou `snappy`. Štítok „MODEL 01 · LOOK 00“ a skóre 0.95–0.99 ako pri detekcii tváre.
4. **Pravítko vľavo** so stupnicou a oranžovou značkou, ktorá ide s časom. Krížik v rohu.
5. **Počítadlo** „LOOK 00 / 03“, značka a sezóna vpravo hore, **timecode** vpravo dole.
6. **Split-flap tabuľa** – veľké číslice v akcente + dva riadky malých dlaždíc. Pri zmene looku písmená preklápajú náhodnými znakmi (seed) so staggerom 35 ms.
7. **Štítok ako na oblečení (care label)** – oranžový pás, prerušovaná čiara, „LOOK · TITLE CARD“ + farebný tag, titulok (Anton) sa napíše, 5 riadkov kľúč–hodnota v mono, symboly prania, čiarový kód zo seedu textu.

## Pravidlá
- **Výnimka z anti-slop pravidiel:** rohové popisky a rámiky sú tu dizajnový jazyk. Každý musí niesť informáciu (look, čas, skóre, kapitola), mono font, presné zarovnanie na mriežku a max. 2 veľkosti písma v HUD.
- Paleta: HUD `#EDEDE6`, akcent `#F26B3A`, štítok `#F1EFEA` / atrament `#161616`. Farby podkladu nechaj tlmené, aby HUD vynikol.
- Štítok strieda strany (vpravo / vľavo) podľa toho, kde je v zábere voľné miesto. Nikdy nezakrýva oči.
- Súradnice tváre (`box`) zmeraj na fotke cez mriežku (`PIL` + čiary každých 64 px) a over v stilloch.

## Zvuk
`pulse` 95–105 BPM. `impact` na strih, `swoosh` na štítok, séria `tick` na preklápanie tabule, `type` na riadky, `blip` na čiarový kód, `riser` pred záverom.

## Výkon
Veľký obrázok + halftone + grain → 1080p render cca 6–7 s na sekundu videa. Na náhľady používaj `--draft`.

## Palety (prepíš konštanty na začiatku `film.html`: HUD, ACC, CARD, INK, DARK)
- **A · Oranžová (default):** HUD #EDEDE6 · ACC #F26B3A · CARD #F1EFEA · INK #161616 · DARK #0F1110
- **B · Tyrkysová:** HUD #E8F0F0 · ACC #19C2B8 · CARD #EEF3F2 · INK #111818 · DARK #0B1212
- **C · Karmínová:** HUD #F0EDE6 · ACC #E23D5A · CARD #F3EEE9 · INK #1A1414 · DARK #120E0F
- **Farby značky:** `python3 colors.py <logo alebo screenshot>` → BG → pozadie, INK → text, ACC → akcent (zvyšok dopočítaj ako tóny medzi BG a INK).
