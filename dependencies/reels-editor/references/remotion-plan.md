# Remotion edit-plan contract

Edit `data/edit-plan.json`. Source times and output layer times are **milliseconds**. `source` and every media asset are paths beneath project `public/`. Run `compile_timeline.py` after changes, then `align_final_audio.py` before render.

```json
{
  "version": 1,
  "source": "source.mp4",
  "format": {"width": 1080, "height": 1920, "fps": 30},
  "segments": [
    {"id": "opening", "sourceStartMs": 2400, "sourceEndMs": 7600, "rate": 1, "focusX": 52, "focusY": 45, "scale": 1}
  ],
  "hook": null,
  "cta": null,
  "effects": [],
  "broll": [],
  "sfx": [],
  "music": null,
  "captions": {"enabled": true, "maxWordsPerPage": 4, "position": "lower", "highlightWords": [], "fontSize": 66, "speakerColors": {}},
  "brand": {"fontFamily": "Inter, Arial, sans-serif", "textColor": "#FFFFFF", "accentColor": "#FFE600", "backgroundColor": "#0B0B0D", "captionBoxColor": "rgba(0,0,0,0.58)", "logo": null, "fontFile": null}
}
```

Segments are joined in listed order. `rate` is 0.5–2, but 1 is preferred for natural speech. `focusX` and `focusY` are percentages, and `scale` is 1–1.4. Inspect the actual crop and motion before finalizing. The compiler rejects cuts through a substantial part of a timed word, but ASR times are imperfect; listen to every boundary.

Optional visible overlays:

```json
"hook": {"text": "A truthful, useful context line", "durationMs": 1400},
"cta": {"text": "Relevant next step", "durationMs": 1500, "mode": "overlay"}
```

`cta.mode` is `overlay` or `endcard`; an end card extends duration. Hook and CTA may have a `locales` map for requested subtitle translations. These are optional, and text should not overpromise.

Optional timed layers, on the **output** timeline:

```json
"effects": [{"type": "punch", "atMs": 4200, "durationMs": 380, "scale": 1.08}],
"broll": [{"src": "broll/demo.mp4", "fromMs": 8800, "toMs": 12100, "fit": "cover"}],
"sfx": [{"src": "sfx/click.wav", "atMs": 4200, "volume": 0.12}],
"music": {"src": "music/licensed-bed.mp3", "volume": 0.06}
```

Supported effect type is **only `punch`** without JSX edits. B-roll fit is `cover` or `contain`. Record B-roll, music, font and logo provenance in `data/asset-manifest.json`. Use `data/client-profile.json` only if its profile was approved. `src/generated/*` is compiled output, except the final-audio aligner deliberately updates `captions.json`; do not hand-edit generated files.
