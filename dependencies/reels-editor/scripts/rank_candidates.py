#!/usr/bin/env python3
"""Validate an editorial shortlist and rank it without pretending scores replace review."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path


WEIGHTS = {"hook": 0.25, "clarity": 0.25, "substance": 0.20, "delivery": 0.15, "payoff": 0.15}


def rank(data: dict, duration_ms: int | None = None) -> list[dict]:
    candidates = data.get("candidates")
    if not isinstance(candidates, list) or not candidates:
        raise ValueError("candidates must be a nonempty list")
    seen: set[str] = set()
    ranked = []
    for candidate in candidates:
        ident = candidate.get("id")
        if not isinstance(ident, str) or not ident.strip() or ident in seen:
            raise ValueError("candidate IDs must be unique nonempty strings")
        seen.add(ident)
        start, end = candidate.get("sourceStartMs"), candidate.get("sourceEndMs")
        if not isinstance(start, int) or not isinstance(end, int) or start < 0 or end <= start:
            raise ValueError(f"{ident}: invalid source time range")
        if duration_ms is not None and end > duration_ms:
            raise ValueError(f"{ident}: candidate exceeds source duration")
        if not isinstance(candidate.get("openingWords"), str) or not candidate["openingWords"].strip():
            raise ValueError(f"{ident}: openingWords is required")
        if not isinstance(candidate.get("payoffWords"), str) or not candidate["payoffWords"].strip():
            raise ValueError(f"{ident}: payoffWords is required")
        if not isinstance(candidate.get("evidence"), str) or not candidate["evidence"].strip():
            raise ValueError(f"{ident}: transcript/audio/visual evidence is required")
        scores = candidate.get("scores")
        if not isinstance(scores, dict) or set(scores) != set(WEIGHTS):
            raise ValueError(f"{ident}: scores must contain exactly {', '.join(WEIGHTS)}")
        for dimension, value in scores.items():
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or not 0 <= value <= 5:
                raise ValueError(f"{ident}: {dimension} must be 0–5")
        result = dict(candidate)
        result["weightedScore"] = round(sum(scores[key] * weight for key, weight in WEIGHTS.items()), 2)
        ranked.append(result)
    return sorted(ranked, key=lambda row: row["weightedScore"], reverse=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", type=Path, required=True)
    args = parser.parse_args()
    project = args.project.resolve()
    data = json.loads((project / "data" / "candidates.json").read_text(encoding="utf-8"))
    analysis_path = project / "data" / "analysis.json"
    duration_ms = None
    if analysis_path.exists():
        analysis = json.loads(analysis_path.read_text(encoding="utf-8"))
        duration = analysis.get("durationSeconds") or analysis.get("media", {}).get("durationSeconds")
        if duration is not None:
            duration_ms = round(float(duration) * 1000)
    results = rank(data, duration_ms)
    output = project / "data" / "candidate-ranking.json"
    output.write_text(json.dumps({"weights": WEIGHTS, "ranked": results}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for row in results:
        print(f"{row['id']}: {row['weightedScore']:.2f}/5 | {row['sourceStartMs']}–{row['sourceEndMs']} ms")
    print(output)


if __name__ == "__main__":
    main()
