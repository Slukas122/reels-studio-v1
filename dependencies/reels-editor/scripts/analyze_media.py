#!/usr/bin/env python3
"""Probe media, detect silence and shot boundaries, and sample visual evidence."""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import subprocess
import tempfile
from pathlib import Path
from typing import Any


def run(command: list[str], cwd: Path, check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(command, cwd=cwd, text=True, capture_output=True)
    if check and result.returncode != 0:
        raise RuntimeError(
            f"Command failed ({result.returncode}): {' '.join(command)}\n{result.stderr[-4000:]}"
        )
    return result


def remotion(project: Path) -> str:
    candidate = project / "node_modules" / ".bin" / "remotion"
    if not candidate.exists():
        raise SystemExit("Remotion is not installed. Run `npm install` in the project first.")
    return str(candidate)


def parse_json_output(text: str) -> dict[str, Any]:
    start = text.find("{")
    end = text.rfind("}")
    if start < 0 or end < start:
        raise ValueError("No JSON object found in command output")
    return json.loads(text[start : end + 1])


def complement_silence(silences: list[dict[str, float]], duration: float) -> list[dict[str, float]]:
    speech: list[dict[str, float]] = []
    cursor = 0.0
    for item in silences:
        start = max(0.0, item["start"])
        end = min(duration, item["end"])
        if start - cursor >= 0.12:
            speech.append({"start": round(cursor, 3), "end": round(start, 3)})
        cursor = max(cursor, end)
    if duration - cursor >= 0.12:
        speech.append({"start": round(cursor, 3), "end": round(duration, 3)})
    return speech


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--min-silence", type=float, default=0.5)
    args = parser.parse_args()

    project = args.project.expanduser().resolve()
    plan = json.loads((project / "data" / "edit-plan.json").read_text(encoding="utf-8"))
    source = (project / "public" / plan["source"]).resolve()
    if not source.is_file() or project / "public" not in source.parents:
        raise SystemExit(f"Source is missing or outside public/: {source}")
    cli = remotion(project)

    probe = run(
        [cli, "ffprobe", "-v", "error", "-show_format", "-show_streams", "-of", "json", str(source)],
        project,
    )
    metadata = parse_json_output(probe.stdout + probe.stderr)
    duration = float(metadata.get("format", {}).get("duration") or 0)
    streams = metadata.get("streams", [])
    has_audio = any(stream.get("codec_type") == "audio" for stream in streams)
    video = next((stream for stream in streams if stream.get("codec_type") == "video"), {})

    loudness: dict[str, Any] | None = None
    silences: list[dict[str, float]] = []
    threshold = -35.0
    if has_audio:
        measured = run(
            [
                cli,
                "ffmpeg",
                "-hide_banner",
                "-i",
                str(source),
                "-map",
                "0:a:0",
                "-af",
                "loudnorm=print_format=json",
                "-f",
                "null",
                os.devnull,
            ],
            project,
            check=False,
        )
        matches = re.findall(r"\{\s*\"input_i\"[\s\S]*?\}", measured.stderr)
        if matches:
            loudness = json.loads(matches[-1])
            try:
                candidate = float(loudness.get("input_thresh", threshold))
                if math.isfinite(candidate):
                    threshold = candidate
            except (TypeError, ValueError):
                pass

        detected = run(
            [
                cli,
                "ffmpeg",
                "-hide_banner",
                "-i",
                str(source),
                "-map",
                "0:a:0",
                "-af",
                f"silencedetect=noise={threshold}dB:d={args.min_silence}",
                "-f",
                "null",
                os.devnull,
            ],
            project,
            check=False,
        )
        open_start: float | None = None
        for line in detected.stderr.splitlines():
            start_match = re.search(r"silence_start:\s*([0-9.]+)", line)
            end_match = re.search(r"silence_end:\s*([0-9.]+)", line)
            if start_match:
                open_start = float(start_match.group(1))
            if end_match and open_start is not None:
                end = float(end_match.group(1))
                silences.append(
                    {"start": round(open_start, 3), "end": round(end, 3), "duration": round(end - open_start, 3)}
                )
                open_start = None
        if open_start is not None and duration > open_start:
            silences.append(
                {"start": round(open_start, 3), "end": round(duration, 3), "duration": round(duration - open_start, 3)}
            )

    frames_dir = project / "analysis" / "frames"
    frames_dir.mkdir(parents=True, exist_ok=True)
    frame_paths: list[str] = []
    visual_samples: list[dict[str, Any]] = []
    shot_boundaries: list[float] = []
    if duration > 0:
        try:
            from PIL import Image, ImageChops, ImageStat
        except ImportError as exc:
            raise RuntimeError("Adaptive visual analysis requires Pillow: python3 -m pip install Pillow") from exc
        def extract(at: float, path: Path) -> bool:
            command = [cli, "ffmpeg", "-hide_banner", "-loglevel", "error", "-ss", f"{at:.3f}", "-i", str(source), "-frames:v", "1"]
            command.extend(["-q:v", "3", "-y", str(path)])
            result = run(command, project, check=False)
            return result.returncode == 0 and path.exists()

        # The bundled Remotion FFmpeg omits fps/scene filters. Its output -r
        # option still extracts a timed image sequence in one fast pass.
        scan_step = max(0.25, duration / 240)
        previous = None
        with tempfile.TemporaryDirectory(prefix="reel-scan-", dir=project / "analysis") as temporary:
            count = min(240, math.ceil(duration / scan_step))
            scan = run([cli, "ffmpeg", "-hide_banner", "-loglevel", "error", "-i", str(source), "-vf", "scale=96:54", "-r", f"{1 / scan_step:.8f}", "-frames:v", str(count), "-q:v", "3", "-y", str(Path(temporary) / "scan-%04d.jpg")], project, check=False)
            if scan.returncode != 0:
                raise RuntimeError(f"Could not extract scan frames: {scan.stderr[-1000:]}")
            for index, scan_path in enumerate(sorted(Path(temporary).glob("scan-*.jpg"))):
                at = min(duration - 0.01, index * scan_step)
                with Image.open(scan_path) as frame:
                    current = frame.convert("L").copy()
                if previous is not None:
                    difference = ImageStat.Stat(ImageChops.difference(previous, current)).mean[0]
                    if difference >= 35 and at > 0.2 and (not shot_boundaries or at - shot_boundaries[-1] >= 0.5):
                        shot_boundaries.append(round(at, 3))
                previous = current
        # About one overview image per second for short sources, capped at 120.
        step = max(1, math.ceil(duration / 120))
        for stale in frames_dir.glob("overview-*.jpg"):
            stale.unlink()
        overview_count = min(120, math.ceil(duration / step))
        overview = run([cli, "ffmpeg", "-hide_banner", "-loglevel", "error", "-i", str(source), "-r", f"{1 / step:.8f}", "-frames:v", str(overview_count), "-q:v", "3", "-y", str(frames_dir / "overview-%04d.jpg")], project, check=False)
        if overview.returncode != 0:
            raise RuntimeError(f"Could not extract overview frames: {overview.stderr[-1000:]}")
        for index, path in enumerate(sorted(frames_dir.glob("overview-*.jpg"))):
            visual_samples.append({"atSeconds": min(duration, round(index * step, 3)), "path": str(path.relative_to(project)), "reason": "overview"})
        # Boundaries get an exact frame and a nearby follow-up frame. Limit the
        # additional extracts so long, fast-cut sources remain affordable.
        boundaries = shot_boundaries[:30]
        for index, at in enumerate(boundaries, start=1):
            for suffix, offset in (("cut", 0.0), ("after", 0.3)):
                sample_at = min(duration - 0.01, at + offset)
                path = frames_dir / f"scene-{index:03d}-{suffix}.jpg"
                if extract(sample_at, path):
                    visual_samples.append({"atSeconds": round(sample_at, 3), "path": str(path.relative_to(project)), "reason": suffix})
        # Keep the small contact set for quick inspection and old consumers.
        for fraction in (0.05, 0.25, 0.5, 0.75, 0.95):
            at = max(0, duration * fraction)
            path = frames_dir / f"source-{round(fraction * 100):02d}.jpg"
            if extract(at, path):
                frame_paths.append(str(path.relative_to(project)))

    analysis = {
        "source": plan["source"],
        "durationSeconds": round(duration, 3),
        "video": {
            "codec": video.get("codec_name"),
            "width": video.get("width"),
            "height": video.get("height"),
            "pixelFormat": video.get("pix_fmt"),
            "averageFrameRate": video.get("avg_frame_rate"),
        },
        "hasAudio": has_audio,
        "loudness": loudness,
        "silenceThresholdDb": round(threshold, 2) if has_audio else None,
        "silences": silences,
        "speechWindows": complement_silence(silences, duration) if has_audio else [],
        "visual": {"overviewStepSeconds": step if duration > 0 else None, "shotBoundariesSeconds": shot_boundaries, "samples": sorted(visual_samples, key=lambda item: item["atSeconds"])},
        "contactFrames": frame_paths,
        "rawProbe": metadata,
    }
    path = project / "data" / "analysis.json"
    path.write_text(json.dumps(analysis, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {path}")
    print(f"Duration: {duration:.2f}s; audio: {'yes' if has_audio else 'no'}; silence intervals: {len(silences)}")


if __name__ == "__main__":
    main()
