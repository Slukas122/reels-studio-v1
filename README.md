# Reels Studio V1 — instalační balíček

Původní Reels Studio **V1**, připravené pro instalaci na jiném počítači. Obsahuje také potřebné companion skilly `reels-editor` a `motion-studio`. Neobsahuje Reels Studio V2/V3, osobní brand manuál ani autorovy fotografie a videa.

## Nejjednodušší použití

Pošlete agentovi v Codexu nebo Claude Code tento odkaz a pokyn:

> Nainstaluj Reels Studio V1 z https://github.com/Slukas122/reels-studio-v1 podle README, včetně obou závislých skillů. Nepřepisuj existující skilly. Připrav nástroje pro střih mého videa a ověř instalaci.

Potřebujete agenta s přístupem k souborům a terminálu. Samotný webový chat bez možnosti spouštět programy video nevyrenderuje. Dostupnost generování obálky a vizuálního/poslechového ověření závisí na schopnostech agenta.

## Instalace

Python 3.10+ a Git musí být dostupné. Příkazy pro macOS/Linux (Windows: WSL2):

```sh
git clone https://github.com/Slukas122/reels-studio-v1.git
cd reels-studio-v1
python3 install.py
python3 doctor.py --target "$HOME/.codex/skills"
```

Pro Claude Code použijte `python3 install.py --claude` a kontrolu s `--target "$HOME/.claude/skills"`. Pro vlastní umístění použijte `--target /cesta/skills`.

Instalátor kopíruje všechny tři skilly vedle sebe. **Existující instalace nepřepisuje**; při konfliktu nic nezmění. Zálohujte/přesuňte starší instalace nebo zvolte jiný adresář. Restartujte/obnovte agenta po instalaci.

## Nástroje pro první render

Instalace instrukcí a instalace renderovacích nástrojů jsou oddělené. Příprava může stahovat Python/Node balíčky, Chromium a velký přepisovací model. Potřebuje internet a několik GB volného místa. Modely ani prostředí jiného počítače nejsou v repozitáři.

### Mluvené české video: FFmpeg cesta

Na macOS s Homebrew:

```sh
brew install python ffmpeg-full whisper-cpp
export PATH="$(brew --prefix ffmpeg-full)/bin:$PATH"
sh "$HOME/.codex/skills/reels-editor/scripts/setup_fast.sh"
python3 doctor.py --target "$HOME/.codex/skills" --runtime fast
```

Na Linuxu nainstalujte Python s venv, FFmpeg s filtrem `ass`, curl a `whisper-cli` z projektu whisper.cpp, např. sestavením pomocí CMake; všechny binárky dejte na PATH. Pak spusťte stejný `setup_fast.sh`. Existující GGML model lze předat proměnnou `REEL_WHISPER_MODEL`; jinak se stáhne large-v3-q5_0. Stable-ts si při prvním použití stáhne další zarovnávací model. Tato rychlá cesta je pro češtinu; ostatní jazyky řeší přibalená Remotion cesta.

### Motion grafika

Node.js 18+, npm a FFmpeg musí být na PATH. Zkopírujte `motion-studio/engine/` do nového pracovního adresáře a tam spusťte `bash setup.sh`; připraví Playwright a Chromium. Příklad postupu je v `motion-studio/SKILL.md`. Použijte vlastní obrázky: přibalené rastrové ukázky jsou záměrně neutrální DEMO plochy.

### Vrstvená videa / další jazyky

Použijte `reels-editor/references/remotion-path.md`. Obsahuje založení projektu, `npm install`, přepis, zarovnání titulků a render. Závislosti a šablona jsou přibalené, runtime balíčky se instalují v projektu. Remotion a ostatní třetí strany mají vlastní licenční podmínky.

U Claude změňte v příkazech `.codex/skills` na `.claude/skills`.

## Zadání videa

V Codexu vyvolejte `$reels-studio`, v Claude Code `/reels-studio` (podle podpory skillů daným klientem). Přiložte média a popište téma, jazyk, výsledek a styl. Například:

> Sestříhej dodané video do svislého reelska. Odstraň přeřeky a opakované pokusy, zachovej význam, přidej české titulky a tematickou obálku. Bez hudby. Výsledek ulož jako MP4.

## Původ a kompatibilita

14 původních souborů V1 odpovídá záloze `pre-v2-2026-10-05`, commit `eac4164`. Instrukce V1 zůstávají nezměněné. Distribuční vrstva navíc obsahuje instalátor, kontrolu a companion skilly; u nich jsou opravené přenositelné fonty a příprava Whisperu. Netvrdíme, že přibalené companion skilly jsou historickými snapshoty ze stejného okamžiku. Funkce pozdějšího Reels Studio ani osobní pravidla se nepřenášejí.

Nejde o samostatnou aplikaci ani o záruku bezchybného automatického střihu. Agent musí zkontrolovat skutečný export. Podporovaný instalační postup je macOS/Linux/WSL2; nativní Windows instalace není ověřená.

Fonty mají přiložené OFL licence a zvukové vzorky CC0. Ukázkové osobní fotografie a screenshoty byly nahrazeny neutrálními plochami.

## Ověření distribučního balíčku

Ověřena čistá instalace do prázdného adresáře, odmítnutí přepsání existujících skillů, 9 testů střihového workflow, render karty s přibaleným fontem a krátký motion MP4 po instalaci Playwrightu. Kompletní přepis a střih na novém Linux/Windows počítači nebyl end-to-end ověřen. Příslušné systémové nástroje a modely je stále potřeba připravit podle výše uvedeného postupu.

Veřejné motion ukázky používají neutrální jména, doménu example.com a DEMO obrázky. Neobsahují osobní branding jiné osoby. Licence třetích stran jsou zachované.
