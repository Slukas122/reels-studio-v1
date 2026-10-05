#!/usr/bin/env python3
"""Validate the finished MP4 and extract representative review frames."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


def run(command: list[str], cwd: Path, check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(command, cwd=cwd, text=True, capture_output=True)
    if check and result.returncode != 0:
        raise RuntimeError(f"Command failed: {' '.join(command)}\n{result.stderr[-4000:]}")
    return result


def parse_json(text: str) -> dict[str, Any]:
    return json.loads(text[text.find("{") : text.rfind("}") + 1])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--video", default="outputs/reel-final.mp4")
    args = parser.parse_args()
    project = args.project.expanduser().resolve()
    video = (project / args.video).resolve()
    cli = project / "node_modules" / ".bin" / "remotion"
    if not cli.exists():
        raise SystemExit("Run npm install first")
    if not video.is_file():
        raise SystemExit(f"Finished video is missing: {video}")

    timeline = json.loads((project / "src" / "generated" / "timeline.json").read_text(encoding="utf-8"))
    result = run([str(cli), "ffprobe", "-v", "error", "-show_format", "-show_streams", "-of", "json", str(video)], project)
    probe = parse_json(result.stdout + result.stderr)
    streams = probe.get("streams", [])
    video_stream = next((stream for stream in streams if stream.get("codec_type") == "video"), None)
    audio_stream = next((stream for stream in streams if stream.get("codec_type") == "audio"), None)
    duration = float(probe.get("format", {}).get("duration") or 0)
    expected = float(timeline["totalDurationMs"]) / 1000
    errors: list[str] = []
    warnings: list[str] = []

    if video_stream is None:
        errors.append("No video stream")
    else:
        if int(video_stream.get("width", 0)) != int(timeline["format"]["width"]) or int(video_stream.get("height", 0)) != int(timeline["format"]["height"]):
            errors.append("Output dimensions do not match the timeline")
        if video_stream.get("codec_name") != "h264":
            errors.append(f"Expected H.264, got {video_stream.get('codec_name')}")
        if video_stream.get("pix_fmt") != "yuv420p":
            warnings.append(f"Expected yuv420p, got {video_stream.get('pix_fmt')}")
    if audio_stream is None:
        errors.append("No audio stream")
    elif audio_stream.get("codec_name") != "aac":
        warnings.append(f"Expected AAC, got {audio_stream.get('codec_name')}")
    if abs(duration - expected) > 0.25:
        errors.append(f"Duration mismatch: expected {expected:.3f}s, got {duration:.3f}s")

    black = run([str(cli), "ffmpeg", "-hide_banner", "-i", str(video), "-vf", "blackdetect=d=0.5:pix_th=0.10", "-an", "-f", "null", "-"], project, check=False)
    black_ranges = [
        {"start": float(start), "end": float(end), "duration": float(length)}
        for start, end, length in re.findall(r"black_start:([0-9.]+)\s+black_end:([0-9.]+)\s+black_duration:([0-9.]+)", black.stderr)
    ]
    if any(item["duration"] > 1.0 for item in black_ranges):
        warnings.append("Detected a black interval longer than 1 second")

    silence = run([str(cli), "ffmpeg", "-hide_banner", "-i", str(video), "-af", "silencedetect=noise=-45dB:d=1.5", "-vn", "-f", "null", "-"], project, check=False)
    silence_ranges: list[dict[str, float]] = []
    open_start: float | None = None
    for line in silence.stderr.splitlines():
        start_match = re.search(r"silence_start:\s*([0-9.]+)", line)
        end_match = re.search(r"silence_end:\s*([0-9.]+)", line)
        if start_match:
            open_start = float(start_match.group(1))
        if end_match and open_start is not None:
            end = float(end_match.group(1))
            silence_ranges.append({"start": open_start, "end": end, "duration": end - open_start})
            open_start = None
    if any(item["duration"] > 2.5 for item in silence_ranges):
        warnings.append("Detected an audio-silence interval longer than 2.5 seconds")

    variant = "" if video.name == "reel-final.mp4" else f"-{video.stem}"
    review_dir = project / "outputs" / f"qa-frames{variant}"
    review_dir.mkdir(parents=True, exist_ok=True)
    review_frames: list[str] = []
    for index, fraction in enumerate((0.03, 0.2, 0.5, 0.8, 0.97), start=1):
        at = max(0, duration * fraction)
        path = review_dir / f"qa-{index:02d}.jpg"
        extracted = run([str(cli), "ffmpeg", "-hide_banner", "-loglevel", "error", "-ss", f"{at:.3f}", "-i", str(video), "-frames:v", "1", "-q:v", "2", "-y", str(path)], project, check=False)
        if extracted.returncode == 0 and path.exists():
            review_frames.append(str(path.relative_to(project)))

    report = {
        "passed": not errors,
        "video": str(video.relative_to(project)),
        "expectedDurationSeconds": round(expected, 3),
        "actualDurationSeconds": round(duration, 3),
        "errors": errors,
        "warnings": warnings,
        "blackIntervals": black_ranges,
        "silenceIntervals": silence_ranges,
        "reviewFrames": review_frames,
        "probe": probe,
    }
    report_path = project / "outputs" / f"qa-report{variant}.json"
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"QA {'passed' if not errors else 'failed'}: {report_path}")
    for message in errors:
        print(f"ERROR: {message}")
    for message in warnings:
        print(f"WARNING: {message}")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
