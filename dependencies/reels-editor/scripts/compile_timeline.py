#!/usr/bin/env python3
"""Validate an edit plan and map source captions onto the output timeline."""

from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path
from typing import Any
from review_transcript import fingerprint, validate


def number(value: Any, label: str) -> float:
    if not isinstance(value, (int, float)) or isinstance(value, bool) or not math.isfinite(value):
        raise ValueError(f"{label} must be a finite number")
    return float(value)


def in_range(value: Any, low: float, high: float, label: str) -> float:
    result = number(value, label)
    if result < low or result > high:
        raise ValueError(f"{label} must be between {low} and {high}")
    return result


def asset(project: Path, relative: str, label: str) -> str:
    candidate = (project / "public" / relative).resolve()
    if project / "public" not in candidate.parents or not candidate.is_file():
        raise ValueError(f"{label} is missing or outside public/: {relative}")
    return relative


def srt_time(milliseconds: float) -> str:
    value = int(round(milliseconds))
    hours, remainder = divmod(value, 3600000)
    minutes, remainder = divmod(remainder, 60000)
    seconds, millis = divmod(remainder, 1000)
    return f"{hours:02}:{minutes:02}:{seconds:02},{millis:03}"


def mark_caption_pages(words: list[dict[str, Any]], max_words: int) -> None:
    """Start a fresh word count after punctuation or a full caption page."""
    count = 0
    for index, word in enumerate(words):
        count += 1
        punctuation = bool(re.search(r"[.!?…][\"')\]]?$", word["text"].strip()))
        word["pageBreakAfter"] = punctuation or count >= max_words or index == len(words) - 1
        if word["pageBreakAfter"]:
            count = 0


def check_speech_boundaries(segments: list[dict[str, Any]], words: list[dict[str, Any]]) -> None:
    """Reject cuts that leave a substantial fragment of a timed spoken word."""
    for segment in segments:
        for edge, at in (("start", segment["sourceStartMs"]), ("end", segment["sourceEndMs"])):
            for word in words:
                word_start = number(word.get("startMs"), "caption.startMs")
                word_end = number(word.get("endMs"), "caption.endMs")
                if word_end <= word_start:
                    continue
                # Short ASR timing errors are common. Require audible material on
                # both sides of the edit before treating the boundary as unsafe.
                if word_start + 80 < at < word_end - 80:
                    raise ValueError(
                        f'{segment["id"]} {edge} at {at:.0f}ms cuts through '
                        f'{str(word.get("text", "")).strip()!r} '
                        f'({word_start:.0f}–{word_end:.0f}ms). '
                        'Move the cut outside the word, then listen to the seam.'
                    )


def localized_titles(value: Any, label: str) -> dict[str, str]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise ValueError(f"{label}.locales must be an object")
    result: dict[str, str] = {}
    for locale, title in value.items():
        if not isinstance(locale, str) or not re.fullmatch(r"[a-z]{2,3}", locale):
            raise ValueError(f"{label}.locales has an invalid language code")
        if not isinstance(title, str) or not title.strip():
            raise ValueError(f"{label}.locales.{locale} must contain text")
        result[locale] = title.strip()
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", type=Path, required=True)
    args = parser.parse_args()
    project = args.project.expanduser().resolve()
    data_dir = project / "data"
    plan = json.loads((data_dir / "edit-plan.json").read_text(encoding="utf-8"))
    if plan.get("version") != 1:
        raise SystemExit("edit-plan.json must use version 1")

    source = asset(project, str(plan.get("source", "")), "source")
    analysis_path = data_dir / "analysis.json"
    source_duration_ms: float | None = None
    if analysis_path.exists():
        analysis = json.loads(analysis_path.read_text(encoding="utf-8"))
        source_duration_ms = number(analysis.get("durationSeconds", 0), "analysis duration") * 1000

    format_data = plan.get("format") or {}
    width = int(in_range(format_data.get("width", 1080), 320, 4320, "format.width"))
    height = int(in_range(format_data.get("height", 1920), 320, 4320, "format.height"))
    fps = in_range(format_data.get("fps", 30), 12, 120, "format.fps")

    segments_in = plan.get("segments")
    if not isinstance(segments_in, list) or not segments_in:
        raise SystemExit("edit-plan.json needs at least one segment")
    compiled_segments: list[dict[str, Any]] = []
    output_cursor = 0.0
    seen_ids: set[str] = set()
    for index, segment in enumerate(segments_in):
        if not isinstance(segment, dict):
            raise ValueError(f"segments[{index}] must be an object")
        segment_id = str(segment.get("id") or f"segment-{index + 1}")
        if segment_id in seen_ids:
            raise ValueError(f"Duplicate segment id: {segment_id}")
        seen_ids.add(segment_id)
        start = number(segment.get("sourceStartMs"), f"{segment_id}.sourceStartMs")
        end = number(segment.get("sourceEndMs"), f"{segment_id}.sourceEndMs")
        if start < 0 or end - start < 150:
            raise ValueError(f"{segment_id} must be at least 150ms and start at or after 0")
        if source_duration_ms is not None and end > source_duration_ms + 50:
            raise ValueError(f"{segment_id} ends after the source ({end:.0f} > {source_duration_ms:.0f}ms)")
        rate = in_range(segment.get("rate", 1), 0.5, 2.0, f"{segment_id}.rate")
        duration = (end - start) / rate
        compiled_segments.append(
            {
                "id": segment_id,
                "sourceStartMs": round(start, 3),
                "sourceEndMs": round(end, 3),
                "outputStartMs": round(output_cursor, 3),
                "outputEndMs": round(output_cursor + duration, 3),
                "rate": rate,
                "focusX": in_range(segment.get("focusX", 50), 0, 100, f"{segment_id}.focusX"),
                "focusY": in_range(segment.get("focusY", 50), 0, 100, f"{segment_id}.focusY"),
                "scale": in_range(segment.get("scale", 1), 1, 1.4, f"{segment_id}.scale"),
            }
        )
        output_cursor += duration

    spoken_duration = output_cursor
    hook = plan.get("hook")
    if hook is not None:
        if not isinstance(hook, dict) or not str(hook.get("text", "")).strip():
            raise ValueError("hook must contain non-empty text")
        hook = {"text": str(hook["text"]).strip(), "durationMs": in_range(hook.get("durationMs", 1400), 300, 4000, "hook.durationMs"), "locales": localized_titles(hook.get("locales"), "hook")}

    cta = plan.get("cta")
    if cta is not None:
        if not isinstance(cta, dict) or not str(cta.get("text", "")).strip():
            raise ValueError("cta must contain non-empty text")
        mode = cta.get("mode", "overlay")
        if mode not in {"overlay", "endcard"}:
            raise ValueError("cta.mode must be overlay or endcard")
        cta = {"text": str(cta["text"]).strip(), "durationMs": in_range(cta.get("durationMs", 1500), 400, 5000, "cta.durationMs"), "mode": mode, "locales": localized_titles(cta.get("locales"), "cta")}
    total_duration = spoken_duration + (cta["durationMs"] if cta and cta["mode"] == "endcard" else 0)

    effects: list[dict[str, Any]] = []
    for index, effect in enumerate(plan.get("effects") or []):
        if effect.get("type") != "punch":
            raise ValueError(f"effects[{index}].type must be punch")
        at = in_range(effect.get("atMs"), 0, spoken_duration, f"effects[{index}].atMs")
        effects.append({"type": "punch", "atMs": at, "durationMs": in_range(effect.get("durationMs", 380), 120, 1200, f"effects[{index}].durationMs"), "scale": in_range(effect.get("scale", 1.1), 1.01, 1.3, f"effects[{index}].scale")})

    broll: list[dict[str, Any]] = []
    for index, item in enumerate(plan.get("broll") or []):
        src = asset(project, str(item.get("src", "")), f"broll[{index}].src")
        start = in_range(item.get("fromMs"), 0, spoken_duration, f"broll[{index}].fromMs")
        end = in_range(item.get("toMs"), 0, spoken_duration, f"broll[{index}].toMs")
        if end - start < 250:
            raise ValueError(f"broll[{index}] must be at least 250ms")
        fit = item.get("fit", "cover")
        if fit not in {"cover", "contain"}:
            raise ValueError(f"broll[{index}].fit must be cover or contain")
        broll.append({"src": src, "fromMs": start, "toMs": end, "fit": fit})

    sfx: list[dict[str, Any]] = []
    for index, item in enumerate(plan.get("sfx") or []):
        sfx.append({"src": asset(project, str(item.get("src", "")), f"sfx[{index}].src"), "atMs": in_range(item.get("atMs"), 0, total_duration, f"sfx[{index}].atMs"), "volume": in_range(item.get("volume", 0.15), 0, 1, f"sfx[{index}].volume")})

    music = plan.get("music")
    if music is not None:
        music = {"src": asset(project, str(music.get("src", "")), "music.src"), "volume": in_range(music.get("volume", 0.07), 0, 0.5, "music.volume")}

    captions_cfg = {"enabled": True, "maxWordsPerPage": 4, "position": "lower", "highlightWords": [], "fontSize": 70, "speakerColors": {}}
    captions_cfg.update(plan.get("captions") or {})
    if captions_cfg["position"] not in {"middle", "lower"}:
        raise ValueError("captions.position must be middle or lower")
    captions_cfg["maxWordsPerPage"] = int(in_range(captions_cfg["maxWordsPerPage"], 1, 7, "captions.maxWordsPerPage"))
    if not isinstance(captions_cfg.get("highlightWords"), list):
        raise ValueError("captions.highlightWords must be an array")
    captions_cfg["fontSize"] = int(in_range(captions_cfg["fontSize"], 32, 120, "captions.fontSize"))
    if not isinstance(captions_cfg.get("speakerColors"), dict):
        raise ValueError("captions.speakerColors must be an object")

    brand = {
        "fontFamily": "Inter, Arial, sans-serif",
        "textColor": "#FFFFFF",
        "accentColor": "#FFE600",
        "backgroundColor": "#0B0B0D",
        "captionBoxColor": "rgba(0,0,0,0.58)",
        "logo": None,
        "fontFile": None,
    }
    brand.update(plan.get("brand") or {})
    if brand.get("logo"):
        asset(project, str(brand["logo"]), "brand.logo")
    if brand.get("fontFile"):
        asset(project, str(brand["fontFile"]), "brand.fontFile")

    source_captions_path = data_dir / "source-captions.json"
    source_captions = json.loads(source_captions_path.read_text(encoding="utf-8")) if source_captions_path.exists() else []
    if not isinstance(source_captions, list):
        raise ValueError("source-captions.json must be an array")
    review_path = data_dir / "transcript-review.json"
    if source_captions and not review_path.exists():
        raise ValueError("Transcription must be reviewed before rendering; run review_transcript.py --init")
    if review_path.exists():
        source_captions = validate(source_captions, json.loads(review_path.read_text(encoding="utf-8")), fingerprint(source_captions_path))
    if source_captions:
        check_speech_boundaries(compiled_segments, source_captions)
    remapped: list[dict[str, Any]] = []
    for segment in compiled_segments:
        segment_words: list[dict[str, Any]] = []
        for caption in source_captions:
            start = number(caption.get("startMs"), "caption.startMs")
            end = number(caption.get("endMs"), "caption.endMs")
            overlap_start = max(start, segment["sourceStartMs"])
            overlap_end = min(end, segment["sourceEndMs"])
            if overlap_end <= overlap_start:
                continue
            mapped_start = segment["outputStartMs"] + (overlap_start - segment["sourceStartMs"]) / segment["rate"]
            mapped_end = segment["outputStartMs"] + (overlap_end - segment["sourceStartMs"]) / segment["rate"]
            segment_words.append({"text": str(caption.get("text", "")), "startMs": round(mapped_start, 3), "endMs": round(mapped_end, 3), "timestampMs": round(mapped_start, 3), "confidence": caption.get("confidence"), "speaker": caption.get("speaker"), "pageBreakAfter": False})
        mark_caption_pages(segment_words, captions_cfg["maxWordsPerPage"])
        remapped.extend(segment_words)

    timeline = {
        "version": 1,
        "source": source,
        "format": {"width": width, "height": height, "fps": fps},
        "segments": compiled_segments,
        "spokenDurationMs": round(spoken_duration, 3),
        "totalDurationMs": round(total_duration, 3),
        "hook": hook,
        "cta": cta,
        "effects": effects,
        "broll": broll,
        "sfx": sfx,
        "music": music,
        "captions": captions_cfg,
        "brand": brand,
    }
    generated = project / "src" / "generated"
    generated.mkdir(parents=True, exist_ok=True)
    (generated / "timeline.json").write_text(json.dumps(timeline, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (generated / "captions.json").write_text(json.dumps(remapped, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    cues: list[list[dict[str, Any]]] = []
    current: list[dict[str, Any]] = []
    for word in remapped:
        current.append(word)
        if word["pageBreakAfter"]:
            cues.append(current)
            current = []
    if current:
        cues.append(current)
    outputs = project / "outputs"
    outputs.mkdir(exist_ok=True)
    srt = "\n".join(f"{index}\n{srt_time(cue[0]['startMs'])} --> {srt_time(cue[-1]['endMs'])}\n{''.join(word['text'] for word in cue).strip()}\n" for index, cue in enumerate(cues, start=1))
    (outputs / "captions-source.srt").write_text(srt, encoding="utf-8")
    print(f"Compiled {len(compiled_segments)} segments, {len(remapped)} caption tokens, {total_duration / 1000:.2f}s total")


if __name__ == "__main__":
    main()
