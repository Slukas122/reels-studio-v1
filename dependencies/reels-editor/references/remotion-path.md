# Remotion path: layered edits and any source language

Use when the cut needs timed B-roll, music, custom motion, multiple visual layers, localization, or a language beyond the Czech fast path. The bundled project and scripts are self-contained. Read [remotion-plan.md](remotion-plan.md) while editing the plan. Node, Python and FFmpeg are required; `stable-ts` is required for final-audio word alignment.

Set `REELS_SKILL` to the absolute directory of this skill. For each new, empty project:

```bash
python3 "$REELS_SKILL/scripts/scaffold_project.py" --input /absolute/source.mp4 --output /absolute/job
cd /absolute/job
npm install
python3 "$REELS_SKILL/scripts/analyze_media.py" --project .
npm run transcribe -- --model medium --language cs
python3 "$REELS_SKILL/scripts/review_transcript.py" --project . --init
```

Use the actual source language instead of `cs`; `auto` is available when uncertain. Review `data/analysis.json`, the full `data/transcript.txt`, contact frames and the source with audio. Correct only words verified by audio in `data/transcript-review.json`; then run `review_transcript.py --check`. Do not edit raw `source-captions.json` to bypass review. The optional local vision script can describe selected frames, but its output is a lead, not proof of motion or speech.

For a long or ambiguous source, write distinct candidates to `data/candidates.json` and use `rank_candidates.py` as a shortlist aid. Its format is [candidate-schema.md](candidate-schema.md). Audition the winner. Edit `data/edit-plan.json` with the actual segments, crop focus and only warranted layers. Keep `data/edit-notes.md` with reasons and boundary checks. Run:

```bash
python3 "$REELS_SKILL/scripts/compile_timeline.py" --project .
"$REELS_SKILL/.venv/bin/python" "$REELS_SKILL/scripts/align_final_audio.py" --project . --language cs
npm run lint
npm run still -- --frame=15 --output=outputs/preview-hook.png
```

Use the actual language and a Python environment with `stable-ts`. Run `sh "$REELS_SKILL/scripts/setup_alignment.sh"` once if this skill's `.venv` is absent, or use an existing environment with `stable-ts` for this one command. This setup does not download the Czech high-quality transcription model. `align_final_audio.py` assembles the selected source audio with the planned playback rates, aligns reviewed words to it, replaces `src/generated/captions.json`, writes `outputs/captions-source.srt` and `outputs/alignment-report.json`. **Run it again after every `compile_timeline.py` invocation**; the compiler regenerates source-time captions. Inspect words near every cut and at the final boundary. If alignment fails, fix the text or edit; never deliver guessed timing.

Preview the first and longest-caption frames, each crop/B-roll transition and the ending. Adjust the plan or composition. Then:

```bash
npm run render
npm run finish
python3 "$REELS_SKILL/scripts/qa_render.py" --project .
```

Watch `outputs/reel-final.mp4` with sound from start to end. Inspect `outputs/qa-report.json` and review frames, fix the edit, then repeat relevant steps. `npm run finish` runs after the raw render, so always review the finished file. The editable project is the job directory.

The shipped JSON renderer supports `punch`, B-roll, SFX, music, hook and CTA. For tracked framing, masks, kinetic text or custom transitions, implement and preview the actual Remotion composition; merely naming a new effect in JSON will fail validation. Prefer using the existing simple cut when it communicates better. Do not add Remotion Agent Skills as a hidden runtime requirement; consult the current official API reference only when changing JSX or upgrading packages.
