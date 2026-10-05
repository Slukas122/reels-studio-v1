---
name: reels-editor
description: Edit supplied video and audio into a finished Reel, Short or TikTok with story-led cuts, visual reframing, captions checked against the final audio, purposeful sound and effects, and a reviewed MP4. Use for short-form editing of existing footage, including talking heads, podcasts, product demos, events and screen recordings.
---

# Reels editor

Make a **finished, watched video**, not just an edit plan. Work autonomously from the user's brief. Keep source files intact and each job in its own directory. Default to one 9:16 video in the source language; adjust format, length and versions when requested. Never pad a weak story to hit a target duration.

## Workflow: spend effort only after the story earns it

1. **Preflight cheaply.** Probe every source for duration, streams, frame rate, dimensions and orientation. Check usable audio and disk space. Read the brief and any approved brand profile. For long footage, create a low-resolution contact sheet and a draft transcript before installing or running heavier models. Review the full transcript and major visual intervals; inspect and listen around candidate moments. Silence and shot changes are leads, not automatic edits. See [editorial.md](references/editorial.md).
2. **Select before polishing.** Shortlist distinct self-contained ideas with a truthful opening, context, development and payoff. Weigh the spoken claim, delivery and visible evidence together. Audition the best candidates with picture and sound. Record why the winner beats alternatives in the job notes. If there is only one viable passage, say so. Do not manufacture a viral hook or select solely from transcript text.
3. **Lock a rough cut.** Mark exact source in/out points around words, breaths, gestures and action. Make a low-cost rough assembly and listen to each seam before captions, effects or full-resolution rendering. Keep useful pauses; remove filler only by removing the corresponding audio and video. Preserve causal order and meaning. Listen to 2–3 seconds *after* the last source out point so a new thought is not accidentally started in the final tail. End on the payoff; add a CTA only when the brief calls for one.
4. **Choose the smallest capable engine.** The bundled [fast FFmpeg path](references/fast-path.md) is preferred for a Czech spoken Reel when crop, cards, restrained cut accents and word-highlighted captions suffice. It aligns approved words to **edited audio**. The bundled [Remotion path](references/remotion-path.md) handles other languages, timed B-roll, music, custom graphics and more complex motion. Both live in this skill; do not call the three superseded skill directories. Install only the selected path's dependencies. For a Czech job needing Remotion layers, use Remotion and the final-audio alignment step in its path.
5. **Finish picture, captions and sound together.** Default to a minimal but brisk native Reel: strong source shots, clean captions, direct cuts and music that supports the speech. Inspect each selected shot at start, middle and end and around movement. Keep faces, hands, products or on-screen proof visible in the vertical crop; use a designed card or readable inset for landscape screens when cropping hides the point. Match caption text to audible words, break by meaning and reading pace, maintain contrast and phone-safe placement. An animated active word may aid scanning; avoid constant bouncing and oversized text. Add motion or SFX only at meaningful visual or semantic beats and keep speech clearly intelligible. Music is optional. See [design-and-sound.md](references/design-and-sound.md).
6. **Render, watch, revise.** Generate a preview before expensive final render. Check opening, every cut, longest caption, shot/crop changes and the ending. Run technical QA, then review the *finished MP4 with sound from start to end* at normal speed and phone size. Fix errors, rerender and repeat affected checks. Document any limitation honestly. Deliver the MP4, source-language SRT, editable job/project, notes and QA report. See [quality-gates.md](references/quality-gates.md).

## Non-negotiable evidence rules

- Verify names, numbers, claims, speaker attribution and uncertain ASR words from audio or a trusted brief. Never silently paraphrase speech in captions or alter a claim by joining incompatible fragments.
- Actual source motion and audio take priority over stills, vision-model descriptions and ASR timestamps. If a moment matters, open the moving clip with sound.
- Use user-provided or licensed B-roll, music, fonts and logos; record their origin. A website's visual style is a draft until approved for client use.
- A successful command or technical QA report does not prove editorial quality. If the final media cannot be viewed or heard, do not label it fully reviewed.
- Do not force one style, cut frequency, sound effect count or duration across every source. A natural, compelling performance can remain visually quiet.

For adapting the renderer or investigating the design basis, read [research-and-toolchain.md](references/research-and-toolchain.md). External repositories are inspiration and API references, not runtime dependencies.
