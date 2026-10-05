#!/usr/bin/env python3
"""Create and validate audio-grounded caption corrections without rewriting speech."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path


def fingerprint(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def lexical_words(value: str) -> list[str]:
    return re.findall(r"[^\W_]+(?:[’'-][^\W_]+)*", value, flags=re.UNICODE)


def validate(source: list[dict], review: dict, source_hash: str) -> list[dict]:
    if review.get("version") != 1 or review.get("sourceSha256") != source_hash:
        raise ValueError("Review is missing, outdated, or uses an unsupported version")
    tokens = review.get("tokens")
    if not isinstance(tokens, list) or len(tokens) != len(source):
        raise ValueError("Every source token must have exactly one reviewed token")
    for index, (original, item) in enumerate(zip(source, tokens)):
        if not isinstance(item, dict) or item.get("index") != index:
            raise ValueError(f"Token {index} has a missing or changed index")
        if item.get("original") != original.get("text"):
            raise ValueError(f"Token {index} does not match the source transcript")
        replacement = item.get("text")
        if not isinstance(replacement, str) or not replacement.strip():
            raise ValueError(f"Token {index} has empty text")
        if len(lexical_words(replacement)) != len(lexical_words(str(original.get("text", "")))):
            raise ValueError(f"Token {index} changes the number of spoken words")
        if item.get("speaker") is not None and not isinstance(item["speaker"], str):
            raise ValueError(f"Token {index} has an invalid speaker ID")
        if [word.casefold() for word in lexical_words(replacement)] != [word.casefold() for word in lexical_words(str(original.get("text", "")))]:
            if item.get("evidence") != "audio-verified" or not str(item.get("reason", "")).strip():
                raise ValueError(f"Token {index} changes spoken text without audio-verified evidence and a reason")
    return [dict(original, text=item["text"], speaker=item.get("speaker", original.get("speaker"))) for original, item in zip(source, tokens)]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", required=True, type=Path)
    parser.add_argument("--init", action="store_true", help="Initialize review from the raw transcript")
    parser.add_argument("--check", action="store_true", help="Validate the reviewed transcript")
    args = parser.parse_args()
    project = args.project.expanduser().resolve()
    source_path = project / "data/source-captions.json"
    review_path = project / "data/transcript-review.json"
    if not source_path.is_file():
        raise SystemExit("Missing data/source-captions.json; transcribe the source first")
    source = json.loads(source_path.read_text(encoding="utf-8"))
    if not isinstance(source, list):
        raise SystemExit("Source captions must be an array")
    source_hash = fingerprint(source_path)
    if args.init:
        if review_path.exists():
            raise SystemExit("Refusing to overwrite an existing transcript review")
        review = {"version": 1, "sourceSha256": source_hash, "tokens": [
            {"index": index, "original": item["text"], "text": item["text"], "speaker": item.get("speaker"), "evidence": None, "reason": None}
            for index, item in enumerate(source)
        ]}
        review_path.write_text(json.dumps(review, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        queue = [
            {"index": index, "atMs": item.get("startMs"), "text": item.get("text"), "confidence": item.get("confidence"),
             "context": "".join(str(word.get("text", "")) for word in source[max(0, index - 3):index + 4]).strip()}
            for index, item in enumerate(source)
            if isinstance(item.get("confidence"), (int, float)) and item["confidence"] < 0.65
        ]
        (project / "data/transcript-review-queue.json").write_text(json.dumps(queue, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"Initialized {review_path} with {len(source)} tokens")
    if args.check:
        if not review_path.exists():
            raise SystemExit("Missing transcript review; run --init first")
        review = json.loads(review_path.read_text(encoding="utf-8"))
        checked = validate(source, review, source_hash)
        print(f"Validated {len(checked)} reviewed tokens")
    if not args.init and not args.check:
        parser.error("Select --init or --check")


if __name__ == "__main__":
    main()
