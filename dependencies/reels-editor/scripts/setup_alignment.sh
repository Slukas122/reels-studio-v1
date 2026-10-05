#!/bin/sh
set -eu
SKILL_DIR=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
if [ ! -x "$SKILL_DIR/.venv/bin/python" ]; then
  python3 -m venv "$SKILL_DIR/.venv"
fi
if ! "$SKILL_DIR/.venv/bin/python" -c 'import stable_whisper, PIL, numpy' >/dev/null 2>&1; then
  "$SKILL_DIR/.venv/bin/python" -m pip install 'stable-ts==2.19.1' Pillow numpy
fi
echo "Ready: $SKILL_DIR/.venv/bin/python $SKILL_DIR/scripts/align_final_audio.py"
