#!/usr/bin/env bash
# Motion Studio – jednorazová príprava prostredia (Cowork / Claude Code / Linux / macOS)
# Spusti v priečinku projektu:  bash setup.sh
set -e
cd "$(dirname "$0")"

echo "→ Node.js"
if ! command -v node >/dev/null; then echo "✗ Chýba Node.js 18+. (macOS: brew install node)"; exit 1; fi
node -v

echo "→ ffmpeg"
if command -v ffmpeg >/dev/null; then ffmpeg -version | head -1
else
  echo "  ffmpeg nie je v systéme, skúšam pip balík imageio-ffmpeg…"
  pip install -q imageio-ffmpeg 2>/dev/null || pip install -q --break-system-packages imageio-ffmpeg
  python3 -c "import imageio_ffmpeg;print('  ok:', imageio_ffmpeg.get_ffmpeg_exe())"
fi

echo "→ Playwright (headless prehliadač)"
[ -f package.json ] || npm init -y >/dev/null
if [ -n "$PLAYWRIGHT_BROWSERS_PATH" ] && [ -d "$PLAYWRIGHT_BROWSERS_PATH" ]; then
  # prostredie už má prehliadač – zober verziu Playwrightu, ktorá k nemu sedí
  V=$(npm ls -g playwright 2>/dev/null | grep -o 'playwright@[0-9.]*' | head -1)
  npm i -D --silent ${V:-playwright} >/dev/null
else
  npm i -D --silent playwright >/dev/null
  npx playwright install chromium >/dev/null 2>&1 || npx playwright install --with-deps chromium
fi
echo "✓ Hotovo. Test: node render.mjs film.html --stills"
