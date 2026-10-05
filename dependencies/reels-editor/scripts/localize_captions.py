#!/usr/bin/env python3
"""Offline phrase-level subtitle translation using locally installed Argos models."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def srt_time(ms: float) -> str:
    total = int(round(ms))
    hours, rest = divmod(total, 3600000)
    minutes, rest = divmod(rest, 60000)
    seconds, millis = divmod(rest, 1000)
    return f"{hours:02}:{minutes:02}:{seconds:02},{millis:03}"


def group_words(words: list[dict]) -> list[dict]:
    cues: list[dict] = []
    group: list[dict] = []
    for word in words:
        group.append(word)
        if word.get("pageBreakAfter"):
            cues.append({"startMs": group[0]["startMs"], "endMs": group[-1]["endMs"],
                         "text": "".join(str(item["text"]) for item in group).strip(),
                         "speaker": group[0].get("speaker")})
            group = []
    if group:
        cues.append({"startMs": group[0]["startMs"], "endMs": group[-1]["endMs"],
                     "text": "".join(str(item["text"]) for item in group).strip(),
                     "speaker": group[0].get("speaker")})
    return cues


def validate(cues: list[dict], source: list[dict]) -> list[str]:
    if len(cues) != len(source):
        raise ValueError("Translated cue count differs from the source")
    warnings: list[str] = []
    for index, (cue, original) in enumerate(zip(cues, source)):
        if cue.get("startMs") != original["startMs"] or cue.get("endMs") != original["endMs"]:
            raise ValueError(f"Cue {index + 1} changes source timing")
        if not str(cue.get("text", "")).strip():
            raise ValueError(f"Cue {index + 1} is empty")
        duration = max(0.1, (cue["endMs"] - cue["startMs"]) / 1000)
        if len(cue["text"]) / duration > 24:
            warnings.append(f"Cue {index + 1} may be too fast to read")
    return warnings


def translate_in_context(source_cues: list[dict], engine: object) -> list[dict]:
    """Translate full utterances, then fit their words into existing timed cues."""
    translated: list[dict] = []
    group: list[dict] = []

    def flush() -> None:
        if not group:
            return
        sentence = " ".join(cue["text"] for cue in group)
        words = str(engine.translate(sentence)).split()
        if len(words) < len(group):
            raise ValueError("Translation has fewer words than timed cues; review this utterance manually")
        cursor = 0
        for index, cue in enumerate(group):
            remaining_cues = len(group) - index
            remaining_words = len(words) - cursor
            if remaining_cues == 1:
                count = remaining_words
            else:
                seconds = max(0.1, cue["endMs"] - cue["startMs"])
                rest_seconds = sum(max(0.1, item["endMs"] - item["startMs"]) for item in group[index:])
                count = max(1, min(remaining_words - remaining_cues + 1, round(remaining_words * seconds / rest_seconds)))
            translated.append(dict(cue, text=" ".join(words[cursor:cursor + count])))
            cursor += count
        group.clear()

    for cue in source_cues:
        group.append(cue)
        if re.search(r"[.!?…][\"')\]]?$", cue["text"]) or cue["endMs"] - group[0]["startMs"] >= 7000:
            flush()
    flush()
    return translated


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", required=True, type=Path)
    parser.add_argument("--source", required=True, help="Source language code, e.g. cs")
    parser.add_argument("--target", required=True, help="Target language code, e.g. en")
    parser.add_argument("--install-model", action="store_true", help="Download and install the free Argos language package once")
    parser.add_argument("--check", action="store_true", help="Validate an existing reviewed translation")
    args = parser.parse_args()
    if not all(re.fullmatch(r"[a-z]{2,3}", value) for value in (args.source, args.target)):
        parser.error("Languages must be two- or three-letter lowercase codes")
    project = args.project.expanduser().resolve()
    words = json.loads((project / "src/generated/captions.json").read_text(encoding="utf-8"))
    source_cues = group_words(words)
    output_dir = project / "public/locales"
    output_dir.mkdir(parents=True, exist_ok=True)
    output = output_dir / f"{args.target}.json"
    if args.check:
        cues = json.loads(output.read_text(encoding="utf-8"))
    else:
        try:
            import argostranslate.package
            import argostranslate.translate
        except ImportError as exc:
            raise SystemExit("Install optional local translator with `python3 -m pip install argostranslate`") from exc
        if args.install_model:
            argostranslate.package.update_package_index()
            packages = argostranslate.package.get_available_packages()
            selected = next((p for p in packages if p.from_code == args.source and p.to_code == args.target), None)
            if selected is not None:
                route = [selected]
            else:
                first = next((p for p in packages if p.from_code == args.source and p.to_code == "en"), None)
                second = next((p for p in packages if p.from_code == "en" and p.to_code == args.target), None)
                if first is None or second is None:
                    raise SystemExit(f"No supported Argos route for {args.source} -> {args.target}")
                route = [first, second]
            installed_pairs = {(p.from_code, p.to_code) for p in argostranslate.package.get_installed_packages()}
            for package in route:
                if (package.from_code, package.to_code) not in installed_pairs:
                    argostranslate.package.install_from_path(package.download())
        installed = argostranslate.translate.get_installed_languages()
        source_lang = next((item for item in installed if item.code == args.source), None)
        target_lang = next((item for item in installed if item.code == args.target), None)
        translation = source_lang.get_translation(target_lang) if source_lang and target_lang else None
        if translation is None:
            raise SystemExit("Required local language model is unavailable; retry with --install-model")
        cues = translate_in_context(source_cues, translation)
    warnings = validate(cues, source_cues)
    output.write_text(json.dumps(cues, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (project / "outputs").mkdir(exist_ok=True)
    srt = "\n".join(f"{index}\n{srt_time(cue['startMs'])} --> {srt_time(cue['endMs'])}\n{cue['text']}\n" for index, cue in enumerate(cues, start=1))
    (project / "outputs" / f"captions-{args.target}.srt").write_text(srt, encoding="utf-8")
    print(f"Wrote {output} and outputs/captions-{args.target}.srt; inspect the translation before rendering")
    for warning in warnings:
        print(f"WARNING: {warning}")


if __name__ == "__main__":
    main()
