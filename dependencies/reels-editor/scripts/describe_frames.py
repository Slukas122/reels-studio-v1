#!/usr/bin/env python3
"""Describe selected source frames with a local Ollama vision model."""

from __future__ import annotations

import argparse
import base64
import json
import urllib.error
import urllib.request
from pathlib import Path

ENDPOINT = "http://127.0.0.1:11434/api/chat"
PROMPT = (
    "Describe ONLY what is directly visible in this single video frame. "
    "Return JSON with keys: people (array), objects (array), visibleAction (string), "
    "onScreenText (array), framingNotes (string), uncertainty (string). "
    "Do not infer speech, identity, exact time, intent, or events between frames. "
    "Use empty arrays or 'unknown' when uncertain."
)


def choose_samples(samples: list[dict], limit: int) -> list[dict]:
    if len(samples) <= limit:
        return samples
    priority = [sample for sample in samples if sample["reason"] != "overview"]
    chosen = priority[: min(len(priority), limit // 2)]
    remaining = limit - len(chosen)
    pool = [sample for sample in samples if sample not in chosen]
    if remaining and pool:
        chosen.extend(pool[min(len(pool) - 1, round(i * (len(pool) - 1) / max(1, remaining - 1)))] for i in range(remaining))
    return sorted(chosen, key=lambda item: item["atSeconds"])


def describe(image_path: Path, model: str, timeout: int) -> dict:
    body = {
        "model": model,
        "stream": False,
        "format": "json",
        "options": {"temperature": 0},
        "messages": [{"role": "user", "content": PROMPT, "images": [base64.b64encode(image_path.read_bytes()).decode("ascii")]}],
    }
    request = urllib.request.Request(ENDPOINT, data=json.dumps(body).encode("utf-8"), headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        raw = json.load(response)["message"]["content"]
    value = json.loads(raw)
    if not isinstance(value, dict):
        raise ValueError("Vision model returned a non-object JSON response")
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", required=True, type=Path)
    parser.add_argument("--model", default="qwen2.5vl:3b")
    parser.add_argument("--max-frames", type=int, default=24)
    parser.add_argument("--timeout", type=int, default=180)
    args = parser.parse_args()
    if not 1 <= args.max_frames <= 120:
        parser.error("--max-frames must be between 1 and 120")
    project = args.project.expanduser().resolve()
    analysis = json.loads((project / "data/analysis.json").read_text(encoding="utf-8"))
    samples = choose_samples(analysis["visual"]["samples"], args.max_frames)
    results: list[dict] = []
    for index, sample in enumerate(samples, start=1):
        image = (project / sample["path"]).resolve()
        if project not in image.parents or not image.is_file():
            raise ValueError(f"Missing or unsafe sample path: {sample['path']}")
        try:
            description = describe(image, args.model, args.timeout)
        except urllib.error.URLError as exc:
            raise SystemExit("Local Ollama is unavailable. Start it and pull the selected vision model first.") from exc
        results.append({**sample, "description": description})
        print(f"Described frame {index}/{len(samples)} at {sample['atSeconds']:.2f}s")
    output = project / "data/visual-descriptions.json"
    output.write_text(json.dumps({"model": args.model, "samples": results}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {output}")


if __name__ == "__main__":
    main()
