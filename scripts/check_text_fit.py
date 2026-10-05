#!/usr/bin/env python3
"""Measure a proposed text block against its real graphic box before rendering.

Example: python3 check_text_fit.py --font /path/to/font.ttf --text 'Dlouhý český titulek' \
  --font-size 76 --box-width 760 --box-height 220 --padding 24 --max-lines 2
"""

from __future__ import annotations

import argparse
import json
import re
import sys

from PIL import ImageFont

TIES = {"a", "i", "k", "o", "s", "u", "v", "z"}


def wrapped_lines(text: str, font: ImageFont.FreeTypeFont, width: float) -> list[str]:
    if width <= 0:
        raise ValueError("Usable text width must be positive")
    result: list[str] = []
    for paragraph in text.split("\n"):
        words = re.findall(r"\S+", paragraph)
        if not words:
            result.append("")
            continue
        units: list[str] = []
        index = 0
        while index < len(words):
            word = words[index]
            if word.casefold() in TIES and index + 1 < len(words):
                word += "\u00a0" + words[index + 1]
                index += 1
            elif re.fullmatch(r"\d[\d .,]*", word) and index + 1 < len(words) and words[index + 1] in {"%", "Kč", "€", "$"}:
                word += "\u00a0" + words[index + 1]
                index += 1
            units.append(word)
            index += 1
        line = ""
        for unit in units:
            candidate = f"{line} {unit}" if line else unit
            if line and font.getlength(candidate) > width:
                result.append(line)
                line = unit
            else:
                line = candidate
        result.append(line)
    return result


def check(text: str, font_path: str, font_size: int, box_width: float, box_height: float,
          padding: float, max_lines: int, line_height: float = 1.12) -> dict:
    if font_size <= 0 or box_width <= 0 or box_height <= 0 or padding < 0 or max_lines < 1:
        raise ValueError("Invalid box, type or line settings")
    font = ImageFont.truetype(font_path, font_size)
    lines = wrapped_lines(text, font, box_width - 2 * padding)
    widths = [font.getlength(line) for line in lines]
    measured_width = max(widths, default=0)
    measured_height = len(lines) * font_size * line_height
    usable_width = box_width - 2 * padding
    usable_height = box_height - 2 * padding
    issues = []
    if measured_width > usable_width + 0.1:
        issues.append("line_exceeds_width")
    if measured_height > usable_height + 0.1:
        issues.append("text_exceeds_height")
    if len(lines) > max_lines:
        issues.append("too_many_lines")
    return {
        "fits": not issues,
        "issues": issues,
        "lines": lines,
        "measured_width": round(measured_width, 1),
        "measured_height": round(measured_height, 1),
        "usable_width": round(usable_width, 1),
        "usable_height": round(usable_height, 1),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--font", required=True, help="The exact final TTF/OTF font file")
    parser.add_argument("--text", required=True)
    parser.add_argument("--font-size", type=int, required=True)
    parser.add_argument("--box-width", type=float, required=True)
    parser.add_argument("--box-height", type=float, required=True)
    parser.add_argument("--padding", type=float, default=0)
    parser.add_argument("--max-lines", type=int, default=2)
    parser.add_argument("--line-height", type=float, default=1.12)
    args = parser.parse_args()
    result = check(args.text, args.font, args.font_size, args.box_width, args.box_height,
                   args.padding, args.max_lines, args.line_height)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["fits"] else 2


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError) as exc:
        print(f"Text fit check failed: {exc}", file=sys.stderr)
        sys.exit(1)
