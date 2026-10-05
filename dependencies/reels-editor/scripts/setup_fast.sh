#!/bin/sh
set -eu
SKILL_DIR=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
FFMPEG_FULL=/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg
if [ -x "$FFMPEG_FULL" ]; then
  FFMPEG_CHECK="$FFMPEG_FULL"
else
  FFMPEG_CHECK=$(command -v ffmpeg || true)
fi
if [ -z "$FFMPEG_CHECK" ] || ! "$FFMPEG_CHECK" -hide_banner -filters 2>/dev/null | grep -q ' ass '; then
  if ! command -v brew >/dev/null 2>&1; then
    echo "FFmpeg with libass is required; install it manually on this platform." >&2
    exit 1
  fi
  brew install ffmpeg-full
  FFMPEG_CHECK="$(brew --prefix ffmpeg-full)/bin/ffmpeg"
fi
sh "$SKILL_DIR/scripts/setup_alignment.sh"
if ! command -v whisper-cli >/dev/null 2>&1; then
  if command -v brew >/dev/null 2>&1; then
    brew install whisper-cpp
  else
    echo 'Install whisper.cpp (whisper-cli) and add it to PATH; see README prerequisites.' >&2
    exit 1
  fi
fi
mkdir -p "$SKILL_DIR/models"
if [ ! -s "$SKILL_DIR/models/active.bin" ]; then
  if [ -n "${REEL_WHISPER_MODEL:-}" ]; then
    [ -s "$REEL_WHISPER_MODEL" ] || { echo 'REEL_WHISPER_MODEL does not exist' >&2; exit 1; }
    ln "$REEL_WHISPER_MODEL" "$SKILL_DIR/models/active.bin" 2>/dev/null || cp "$REEL_WHISPER_MODEL" "$SKILL_DIR/models/active.bin"
  else
    curl -fL --retry 3 --output "$SKILL_DIR/models/active.partial" 'https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-large-v3-q5_0.bin'
    mv "$SKILL_DIR/models/active.partial" "$SKILL_DIR/models/active.bin"
  fi
fi
"$FFMPEG_CHECK" -hide_banner -filters 2>/dev/null | grep -q ' ass ' || {
  echo "FFmpeg ass filter is missing" >&2; exit 1;
}
echo "Ready: $SKILL_DIR/.venv/bin/python $SKILL_DIR/scripts/fast_reel.py"
