# Fast FFmpeg path: Czech spoken Reels

Use this when the source speech is Czech and the job needs a polished cut, vertical crop, word-highlighted captions, restrained accents, or full-screen explanatory cards. It is the fastest route when the Remotion layer system is unnecessary. It requires FFmpeg with `ass`, Whisper.cpp and Python `stable-ts`.

Set `REELS_SKILL` to this skill directory. First use only:

```bash
sh "$REELS_SKILL/scripts/setup_fast.sh"
```

The setup installs a local virtual environment and reuses `models/active.bin` if present; `REEL_WHISPER_MODEL` can point to an existing GGML model. Do not rerun setup for every job. The high-quality Czech model and short final-audio aligner are separate because speed and accuracy have different roles.

For a new, empty job directory:

```bash
"$REELS_SKILL/.venv/bin/python" "$REELS_SKILL/scripts/fast_reel.py" inspect /absolute/source.mp4 --project /absolute/job
```

Read `transcript.json`, watch/listen to selected candidates, then edit `plan.json`. The exact schema is [fast-plan.md](fast-plan.md). `spokenText` must be the **exact speech retained after all cuts**. Put selected source intervals in output order, with `focusX` and optional zoom. Before rendering, use `frames` to inspect start, middle and end of each selected segment:

```bash
"$REELS_SKILL/.venv/bin/python" "$REELS_SKILL/scripts/fast_reel.py" frames --project /absolute/job
"$REELS_SKILL/.venv/bin/python" "$REELS_SKILL/scripts/fast_reel.py" render --project /absolute/job
```

`render` assembles the selected audio, checks the transcript against it, aligns the approved words to **that audio**, burns word-timed captions and renders `output/reel.mp4`. It also writes `output/captions.srt`, `output/qa.json`, frames and timing data. Read the report and watch the complete MP4 with sound. If alignment fails, correct `spokenText` or the cut from audio evidence; do not loosen a check simply to make the render pass. For screen recordings, use `effects.cards` when the native screen is unreadable in portrait. Effects are off by default and must be judged in the render.

This path supports Czech speech only. For another language, multiple timed media layers or advanced graphics, use [remotion-path.md](remotion-path.md).
