# Design basis and maintenance

This skill consolidates the local `auto-reel-editor` legacy Remotion template, `auto-reel-editor-v2` editorial checks and `reel-editor` Czech FFmpeg/edited-audio alignment. Its bundled code is independent of those old directories. The fast path uses Whisper.cpp for accurate Czech text and `stable-ts` for word timing on selected audio. The Remotion path retains a reproducible layered project and now aligns selected speech after cuts.

External repositories reviewed at consolidation:

- [Remotion Agent Skills](https://github.com/remotion-dev/skills), commit `a9b199e`: official guidance for captions, media timing, audio and rendering. Its current documentation may change; consult it when editing the JSX composition or upgrading packages. The bundled Remotion template is version-pinned and should be upgraded as one set.
- [claude-shorts](https://github.com/AgriciDaniel/claude-shorts), commit `a369fad`: candidate scoring, audio-aware boundaries, content-type reframing and caption styles informed the editorial workflow. Its interactive approval loop, fixed candidate quotas, brittle platform presets and text-only filler removal are not adopted. A caption cannot omit a word still audible in the video.

The Remotion template currently pins every Remotion package to the same version. Do not mix versions. `npm install` happens in a job directory, not in the skill. Before a renderer upgrade, run its lint and a small end-to-end render with QA. The fast path needs a system FFmpeg with `ass` plus Whisper.cpp; its setup script installs a local Python environment. Model downloads can be large, so reuse the installed model when possible. Neither engine requires paid APIs or a server.

Both engines remain local editing tools; media rights, client approval, brand claims and actual platform requirements must be verified for the specific job. Do not treat any fixed export bitrate or safe-zone number from an external repository as a universal platform rule.
