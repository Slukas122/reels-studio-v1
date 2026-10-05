#!/usr/bin/env python3
"""Align reviewed Remotion captions to the assembled spoken audio, then replace generated timings."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
from pathlib import Path


def run(command: list[str]) -> None:
    subprocess.run(command, check=True)


def srt_time(milliseconds: float) -> str:
    value = max(0, round(milliseconds))
    h, rest = divmod(value, 3600000)
    m, rest = divmod(rest, 60000)
    s, ms = divmod(rest, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--language", required=True, help="Source speech language, e.g. cs or en")
    parser.add_argument("--model", default="small", help="Installed stable-ts Whisper model")
    args = parser.parse_args()
    project = args.project.expanduser().resolve()
    generated = project / "src" / "generated"
    timeline = json.loads((generated / "timeline.json").read_text(encoding="utf-8"))
    captions_path = generated / "captions.json"
    captions = json.loads(captions_path.read_text(encoding="utf-8"))
    if not captions:
        raise SystemExit("No reviewed words selected; compile the edit plan and review captions first")
    source = (project / "public" / timeline["source"]).resolve()
    if not source.is_file() or project / "public" not in source.parents:
        raise SystemExit("Compiled source must exist beneath project/public")
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise SystemExit("FFmpeg is required for final-audio alignment")
    filters = []
    labels = []
    for index, segment in enumerate(timeline["segments"]):
        start = segment["sourceStartMs"] / 1000
        end = segment["sourceEndMs"] / 1000
        rate = segment["rate"]
        filters.append(f"[0:a]atrim=start={start:.6f}:end={end:.6f},asetpts=PTS-STARTPTS,atempo={rate:.6f}[a{index}]")
        labels.append(f"[a{index}]")
    filters.append("".join(labels) + f"concat=n={len(labels)}:v=0:a=1[out]")
    output = project / "outputs"
    output.mkdir(exist_ok=True)
    audio = output / "edited-speech.wav"
    run([ffmpeg, "-hide_banner", "-loglevel", "error", "-y", "-i", str(source), "-filter_complex", ";".join(filters), "-map", "[out]", "-ar", "16000", "-ac", "1", "-c:a", "pcm_s16le", str(audio)])
    try:
        import stable_whisper
    except ImportError as exc:
        raise SystemExit("Install stable-ts in the selected Python environment before final-audio alignment") from exc
    expected = " ".join(str(item["text"]).strip() for item in captions).strip()
    model = stable_whisper.load_model(args.model, device="cpu")
    aligned = model.align(str(audio), expected, language=args.language, verbose=False)
    words = [word for segment in aligned.segments for word in segment.words if str(word.word).strip()]
    if len(words) < len(captions) * 0.85:
        raise SystemExit(f"Alignment returned {len(words)} words for {len(captions)} caption tokens; review exact speech")
    lexical = lambda value: re.findall(r"[^\W_]+", value.casefold(), flags=re.UNICODE)
    if lexical(" ".join(str(word.word) for word in words)) != lexical(expected):
        raise SystemExit("Aligned words differ from the reviewed caption text; inspect the cut and transcript")
    near_zero = [str(word.word).strip() for word in words if word.end - word.start < 0.04]
    substantive = [word for word in near_zero if any(len(part) > 4 for part in lexical(word))]
    boundary_zero = words[0].end - words[0].start < 0.04 or words[-1].end - words[-1].start < 0.04
    if boundary_zero or len(near_zero) > max(4, len(words) * 0.12) or substantive:
        raise SystemExit(f"Alignment has suspicious near-zero words {near_zero}; review transcript or use a better model")
    result = []
    for index, word in enumerate(words):
        text = str(word.word)
        result.append({
            "text": text if index == 0 or text.startswith(" ") else " " + text,
            "startMs": round(float(word.start) * 1000, 3),
            "endMs": round(float(word.end) * 1000, 3),
            "timestampMs": round(float(word.start) * 1000, 3),
            "confidence": None,
            "speaker": None,
            "pageBreakAfter": False,
        })
    max_words = int(timeline["captions"]["maxWordsPerPage"])
    pages = []
    current = []
    for index, word in enumerate(result):
        current.append(word)
        ending = bool(re.search(r"[.!?…][\"')\]]?$", word["text"].strip()))
        if ending or len(current) >= max_words or index == len(result) - 1:
            word["pageBreakAfter"] = True
            pages.append(current)
            current = []
    # Preserve the compiler output until the replacement is fully validated.
    duration = timeline["spokenDurationMs"]
    if result[0]["startMs"] < -1 or result[-1]["endMs"] > duration + 150:
        raise SystemExit("Aligned captions exceed assembled speech duration")
    srt = "\n".join(
        f"{i}\n{srt_time(page[0]['startMs'])} --> {srt_time(page[-1]['endMs'])}\n{''.join(item['text'] for item in page).strip()}\n"
        for i, page in enumerate(pages, 1)
    )
    captions_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output / "captions-source.srt").write_text(srt, encoding="utf-8")
    report = {"captionTokensBefore": len(captions), "alignedWords": len(result), "nearZeroWords": near_zero, "spokenDurationMs": duration, "lastCaptionEndMs": result[-1]["endMs"], "model": args.model, "language": args.language, "requiresAudioReview": True}
    (output / "alignment-report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Aligned {len(result)} words to {audio}; inspect the captions and {output / 'alignment-report.json'}")


if __name__ == "__main__":
    main()
