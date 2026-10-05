# Hybrid footage and motion path

Use when source footage and designed animation both carry part of the message. Read the reels-editor SKILL and its relevant path first. Use Motion Studio for sections whose visuals genuinely benefit from its code-rendered typography, diagrams or UI animation. Keep one shared timeline with exact output times for speech, motion, captions, music and SFX.

## Select the assembly method

- **Motion over ongoing source speech:** The reels-editor Remotion plan supports a timed `broll` video layer. Export the motion clip at the composition ratio and frame rate, place it under `public/`, and set `fromMs`/`toMs` on the output timeline. Its audio is not automatically the desired mix; keep speech and music planning in the main edit.
- **Standalone motion section that adds time:** The simple Remotion JSON `broll` layer only covers existing timeline time. Do not pretend it inserts duration. Extend the Remotion composition deliberately, or create matched footage and motion sections and concatenate them with FFmpeg. Recalculate every downstream caption, music and cue time after insertion. If spoken captions remain, align to the **final assembled audio**.
- **Simple full-screen interlude:** FFmpeg concat is reasonable if each section is normalized to the same canvas, frame rate, video codec, pixel format, audio sample rate and channel layout. Add silence to a section without speech only when needed to keep A/V timing explicit. Probe the concatenated output, inspect each join and listen to the mix.

Do not layer the Motion Studio output as if it had alpha; its normal render is a full-frame image with a background. For a transparent or tracked overlay, implement the graphics in the Remotion composition or create a deliberately keyed/alpha-capable asset and verify edges in the final render.

Keep the footage's original claim and timing intact. A motion graphic may clarify the claim, but may not add unsupported figures, UI states or outcomes. Validate the assembled MP4, not just the component clips.
