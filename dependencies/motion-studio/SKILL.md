---
name: motion-studio
description: Vytvorí hotové motion-graphics video (MP4 so zvukom, 6–30 s) čisto z kódu – bez After Effects a bez AI video modelu – v 9 štýloch (kinetický showreel, launch reel produktu tmavý aj svetlý, UI morph loop, príbehový explainer, dáta a grafy, ručne kreslený/papier, editorial HUD s fotkou, Apple keynote, retro neon). Pred prácou sa opýta na režim, štýl, formát, farby a hudbu. Použi VŽDY, keď používateľ chce motion grafiku, animované video, animovaný reel/short, promo produktu alebo webu, showreel, animovaný explainer, animovaný graf, intro/outro, animáciu z fotky, alebo povie "motion design", "animuj mi", "sprav z toho video", "motion studio" – aj keď nespomenie štýl.
---

# Motion Studio

Každé video je **program**, nie video. Napíšeš jeden HTML súbor s funkciou `window.seek(t)`, ktorá nakreslí presný frame pre čas `t`. Headless prehliadač ho odfotí frame po frame, ffmpeg z toho spraví MP4. Výsledok je deterministický: rovnaký kód = rovnaké video, oprava = jeden riadok + nový render.

**Prompt je 10 % videa. Zvyšných 90 % je postup:** otázky → assety → shotlist na rytmus → build zo vzoru → pozri sa na vlastné frame-y → oprav → render.

## Štruktúra skillu
```
engine/     motion.js (knižnica), render.mjs (render + zvuk + stopy + kritika), audio.mjs (hudba + efekty),
            sfx/ (reálne zvukové efekty CC0), capture.mjs (screenshoty webu), colors.py (farby z obrázka),
            beats.py (tempo vlastnej skladby), setup.sh, fonts.css + fonts/ (OFL, s diakritikou)
styles/     01–09: vzhľad, pohyb, štruktúra a 3 palety pre každý štýl
examples/   01–09 (+ 02b): funkčný vzorový film pre každý štýl – ZAČNI VŽDY Z NEHO
prompty/    kritika.md (hodnotenie frame-ov), zadania.md (vzory zadaní)
```

## Rozsah tejto verzie
Režimy **čistá animácia**, **fotka/obrázok + animácia** a **web (screenshoty podľa URL) + animácia**. Dĺžka 6–30 s. Ak používateľ chce animácie nad vlastným videom, titulky k videu alebo film dlhší ako 30 s, povedz mu, že to táto verzia nerobí, a ponúkni najbližšiu možnosť (napr. 30 s verziu alebo animáciu z fotky).

## Výber štýlu

| Štýl | Na čo | Formát | Súbory |
|---|---|---|---|
| 01 Kinetický showreel | hook, intro, predstavenie značky, typografia | 9:16 | `styles/01-kineticky-showreel.md` |
| 02 Launch reel (tmavý) | promo produktu / webu / appky z URL, reálne screenshoty, CTA | 9:16 | `styles/02-launch-reel.md` |
| 02b Launch reel (svetlý SaaS) | to isté ako 16:9 film s obrími číslami a "3D" kartami | 16:9 | `styles/02-launch-reel.md` |
| 03 UI morph loop | appka / služba "v jednom ťahu", nekonečný loop | 1:1 | `styles/03-ui-morph-loop.md` |
| 04 Príbehový explainer | príbeh, história, "X za 30 sekúnd", fakty | 9:16 | `styles/04-pribehovy-explainer.md` |
| 05 Dáta a grafy | čísla, výsledky, porovnania, financie | 16:9 | `styles/05-data-grafy.md` |
| 06 Ručne kreslený | útulné vysvetľovanie, whiteboard, akvarel | 9:16 | `styles/06-rucne-kreslene.md` |
| 07 Editorial HUD | osobnosť / tvorca / tím z fotky, módny lookbook | 16:9 | `styles/07-editorial-hud.md` |
| 08 Keynote (Apple) | ohlásenie produktu, kurzu, eventu – pokojne a "draho" | 16:9 | `styles/08-keynote.md` |
| 09 Retro neon | showreel kanála, prehľad videí, synthwave | 16:9 | `styles/09-retro-neon.md` |

Formát každého štýlu sa dá zmeniť (9:16 / 1:1 / 16:9 / 4:5) – prepočítaj layout na nové `W/H`, neorezávaj.

## Postup (drž poradie, nepreskakuj brány)

### 1 · Úvodné otázky – VŽDY na začiatku
Z toho, čo používateľ napísal, si najprv vytiahni všetko, čo už vieš. Na zvyšok sa opýtaj **naraz** – ak máš nástroj `AskUserQuestion`, použi ho (max 4 otázky na jedno volanie, prípadne druhé kolo). Čo už zadanie obsahuje, sa nepýtaj.

1. **Režim:** Čistá animácia · Fotka/obrázok + animácia (nech priloží súbor) · Web + animácia (nech dá URL)
2. **Štýl:** odporuč 1–2 z tabuľky podľa obsahu, s jednou vetou prečo; ostatné ako možnosti
3. **Formát a dĺžka:** 9:16 (reels/shorts) · 16:9 (YouTube) · 1:1 · 4:5 – a 6–30 s (default 12–15 s)
4. **Farby:** Paleta A/B/C zo štýlu (popíš ich slovami, napr. "čierna + oranžová") · Farby z mojej značky (web alebo logo) · Vlastné (hex kódy)
5. **Hudba:** Vlastná skladba (nahraj MP3 – odporúčané, strihy sa zosynchronizujú na beaty) · Syntetizovaná (ponúkni 2–3 štýly, ktoré sa hodia, z `node audio.mjs --list`) · Bez hudby, len zvukové efekty

Ak používateľ povie "rovno to sprav", zvoľ odporúčané možnosti a na konci napíš, čo si zvolil.

### 2 · Príprava prostredia (raz za vlákno)
```bash
mkdir -p motion && cp -r <skill>/engine/* motion/ && cd motion && bash setup.sh
cp <skill>/examples/NN-*.html film.html          # vzor zvoleného štýlu
cp -r <skill>/examples/assets .                   # ak vzor používa obrázky
node render.mjs film.html --stills                # test, že všetko beží
```
`setup.sh` nainštaluje Playwright (+ Chromium) a ak chýba ffmpeg, doinštaluje `imageio-ffmpeg`. Ak niečo zlyhá, oprav to skôr, než začneš tvoriť.

### 3 · Assety, farby, hudba
- **Web:** `node capture.mjs <url>` (alebo `--desktop`) → `assets/hero.png`, `full.png`, `section-NN.png`, `brand.json`. Pozri sa na ne (Read) a vyber, čo animovať. **Nikdy nevymýšľaj UI produktu – animuj reálne screenshoty.**
- **Fotka:** ulož do `assets/`, pozri sa na ňu, zmeraj súradnice tváre (mriežka cez PIL, čiary každých 64 px) a over ich v stilloch. Drahý grade (sepia, contrast) aplikuj raz do cache canvasu.
- **Farby zo značky:** `python3 colors.py assets/hero.png [--dark|--light]` (alebo logo) → role `BG, INK, ACC, ACC2, MUTED` + kontrast. Namapuj ich na konštanty vzoru (tabuľka v `styles/NN-*.md`). Text musí mať kontrast 7:1, akcent na veľký text aspoň 3:1.
- **Paleta A/B/C:** hodnoty sú v `styles/NN-*.md` → prepíš konštanty na začiatku `film.html`.
- **Vlastná skladba:** `python3 beats.py hudba.mp3 [--from 12.5]` → BPM a posun prvej doby. Vo filme `const B = M.beats(bpm, offset)`, `music: { style: 'none' }`, všetky strihy a veľké momenty daj na `B.b(n)` / `B.bar(n)`. Render s `--track hudba.mp3 --track-from 12.5`. Vyber úsek skladby s energiou (refrén, drop), nie tiché intro.
- **Syntetizovaná hudba:** `music: { style, bpm, key }`. Štýly: `pulse house synthwave corporate hiphop lofi piano ambient cinematic minimal none`. Ak si používateľ nevie vybrať, vygeneruj ukážky: `node audio.mjs --demo out/` (10 s z každého štýlu) a pošli mu ich.
- **Fakty (04, 05):** over ich. Dáta, ktoré nie sú reálne, označ vo videu ako "ukážkové".

### 4 · Shotlist na rytmus → ukáž a počkaj na OK
Pri 120 BPM je beat 0,5 s a takt 2 s. Každý záber: `čas · obraz · text · pohyb · zvuk`. Hook do 2 s, nový vizuálny moment každé 2–4 s, veľké momenty na začiatok taktu, žiadna "mŕtva" sekunda. Ukáž 5–8 riadkov. Ak používateľ odpovie "ok" alebo "rovno", pokračuj.

### 5 · Build
Uprav `film.html` zo vzoru – texty, farby, dáta a scény podľa shotlistu a `styles/NN-*.md`. Scéna je `{from, to, draw(g, t, T, dur)}` (`t` lokálny čas scény, `T` globálny). Zvuky do `cues` na beaty/akcie.

### 6 · Kritika – pozri sa na vlastné frame-y (povinné, min. 2 kolá)
```bash
node render.mjs film.html --stills --every 0.25     # out/film_contact.png + out/film_phone.png
```
Otvor oba obrázky (Read) a postupuj podľa `prompty/kritika.md`: 7 kritérií 1–10, 3 najhoršie problémy s časom, oprava, nové stilly. Končíš, keď je všetko 8+ (max 4 kolá). Detail rýchlej akcie: `--from 3.8 --to 4.4 --every 0.05`.

### 7 · Render a kontrola
```bash
node render.mjs film.html --draft     # rýchly náhľad (½ rozlíšenie) – voliteľné
node render.mjs film.html             # finál
```
Výstup: `out/film.mp4` (H.264 + AAC, −14 LUFS) a `out/film_stopy/` (`video-bez-zvuku.mp4`, `hudba.wav`, `efekty.wav` – na dokončenie v strihovom programe). Voľby: `--fps 60`, `--sub 4` (silnejší motion blur), `--track`, `--track-from`, `--no-audio`, `--png`. Render 12 s trvá cca 30–90 s.
Skontroluj výstup: `ffmpeg -i out/film.mp4 -vf fps=1,scale=240:-1,tile=6x3 -frames:v 1 out/final_sheet.png` → Read.

### 8 · Odovzdanie
MP4 ulož tam, kde ho používateľ uvidí (priečinok s výstupmi alebo jeho pripojený priečinok), a pošli ho. Jednou vetou povedz, čo video robí a akú hudbu/paletu si použil. Ponúkni 1–2 vylepšenia (iný formát, iná hudba, iná paleta). Úpravy rob vetou ("zrýchli", "väčší text", "paleta B") – oprav kód a prerenderuj.

## Render kontrakt (tvrdé pravidlá)
- Video je čistá funkcia času. **Zakázané:** `Math.random` (použi `M.rng(seed)`, `M.hash`, `M.noise`), `setTimeout`, CSS transitions/animations, `requestAnimationFrame` v renderi, stav medzi frame-ami. Cache je povolená, len ak je deterministická.
- Všetky fonty z `fonts.css` uveď v `fonts: [...]` a obrázky v `images: {...}`.
- Pohyb robí pružina (`M.sp`, `M.track`), nie lineárny fade. Easing (`M.prog` + `M.ease`) len na ťahy, počítadlá a wipe.
- Text čitateľný na mobile: pri šírke 1080 px min. ~40 px popisky, 90+ px hlavný text. Over vo `film_phone.png`.

## Zakázané defaulty ("AI slop")
Nadpis v strede na gradiente · všetko len fade-in · popisky a rámiky v rohoch (výnimka: štýly 07, 09 a 02b – tam je HUD zámerný a každý popisok nesie informáciu) · glow na UI · generické výbuchy častíc · 5 fontov a 5 farieb · statický záber dlhší ako 3 s · vymyslené UI produktu · vymyslené fakty. **Jeden display font + jeden UI font, jedna akcentová farba** (ak brief nepovie inak).

## motion.js – ťahák
```js
M.sp(t, 'snappy'|'base'|'heavy'|'playful'|'soft')   // pružina 0→1 (t<0 → 0)
M.track(t, [[čas, hodnota], ...], preset)            // hodnota s viacerými cieľmi (bez reštartu)
M.trackN(t, [[čas, [x,y]], ...])                      // to isté pre polia
M.loopTrack / M.loopTrackN(t, keys, DUR, preset)      // bezšvový loop (posledná hodnota = prvá)
M.prog(t, start, dur, M.ease.out|inOut|expoOut|...)  // progres 0..1 s easingom
M.window(t, tIn, tOut, fadeIn, fadeOut)               // alfa okno (nábeh/odchod)
M.beats(bpm, offset) → { b(n), bar(n), spb }          // časy beatov (offset z beats.py)
M.rng(seed) · M.hash(n) · M.noise(x, seed)            // deterministická náhoda
M.text(g, str, x, y, {font, color, align, spacing, alpha}) · M.letters(...) · M.measure(...)
M.rrect · M.clipRect · M.image(g, img, x, y, w, h, {r}) · M.cursor(g, x, y, {press, ring})
M.mix(a, b, p) · M.alpha(hex, a) · M.hex · M.grain(g, W, H, T) · M.vignette(g, W, H)
M.film({ W, H, DUR, BG, FPS, fonts, images, music:{bpm, style, key}, musicGain, cues:[{t, type, gain, pan}], before, scenes, after })
```
Zvuky (`cues.type`) – reálne nahrávky: `click tick pop type ding blip glitch impact thump paper scroll toggle error`; syntetizované: `whoosh swoosh riser pen`. Hlasitosť efektu `gain` (0,3–1), hudby `musicGain` (default 0,8).

## Časté chyby (už raz odladené – nerob ich znova)
- **Maska a posun:** pri delení textu najprv `translate`, potom `clipRect`.
- **Diakritika a masky:** Š, Ť, Ľ, Ó presahujú nad verzálky – masku daj o 10–15 % vyššiu ako font.
- **Bodky pri p = 0:** `lineCap: 'round'` s nulovou dĺžkou nakreslí bodku – pri `p <= 0` nekresli.
- **Oblúk nulovej dĺžky** (donut, loader): pri `s ≈ 0` nekresli.
- **Mŕtve frame-y na hranách scén:** prázdny frame dlhší ako 0,2 s je chyba.
- **Loop:** `M.loopTrack`, posledný kľúč aspoň 0,4 s pred koncom; over, že frame `DUR − 1/fps` ≈ frame 0.
- **Obrázky:** render beží cez lokálny server; obrázky dávaj do `assets/` vedľa `film.html`.
- **Počítadlá:** ak má byť číslo čitateľné, nech sa ku koncu spomalí (`M.ease.expoOut`).
- **Tretie strany:** na screenshotoch a thumbnailoch nepoužívaj tváre iných ľudí bez súhlasu – vyber zábery bez nich alebo ich orež.
