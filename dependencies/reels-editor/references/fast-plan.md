# Fast path plan fields

Times are seconds in the original source. `segments` order is output order.

```json
{
  "source": "/absolute/source.mp4",
  "language": "cs",
  "spokenText": "Přesná slova slyšitelná v sestřihu.",
  "segments": [
    {"start": 12.4, "end": 16.8, "focusX": 0.5, "zoom": 1.0},
    {"start": 48.1, "end": 70.2, "focusX": 0.5, "zoom": 1.08}
  ],
  "style": {
    "fontFamily": "Arial",
    "textColor": "FFFFFF",
    "accentColor": "FFE07A",
    "outlineColor": "101010",
    "fontSize": 72,
    "maskSourceCaptions": false
  },
  "effects": {
    "colorGrade": false,
    "cutFlashes": false,
    "cutSounds": false,
    "labels": [],
    "cards": []
  }
}
```

`focusX` runs 0–1 from left to right; `zoom` is 1–1.25. The script requires each segment to last at least 0.4 seconds and the total to remain under 90 seconds. `effects.labels`, if used, needs one label per segment. `effects.cards`, if used, needs one concise `{ "title": "...", "detail": "..." }` card per segment and replaces the source picture with a designed full-screen card. Do not set both arrays merely to fill them. `maskSourceCaptions` covers a fixed lower region; inspect the frame before using it.

Only an approved profile from `profiles/<client>.json` is applied when `inspect` receives `--client`. A website observation is not approval. The plan is editable and the source stays untouched.
