#!/usr/bin/env python3
"""Generate a tiny rights-clean SFX starter pack using only the standard library."""

from __future__ import annotations

import argparse
import math
import random
import struct
import wave
from pathlib import Path

RATE = 48_000


def _write(path: Path, samples: list[float]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    peak = max(1.0, max(abs(sample) for sample in samples))
    pcm = b"".join(
        struct.pack("<h", int(max(-1, min(1, sample / peak)) * 32767))
        for sample in samples
    )
    with wave.open(str(path), "wb") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(2)
        handle.setframerate(RATE)
        handle.writeframes(pcm)


def _pop() -> list[float]:
    duration = 0.16
    return [
        0.62
        * math.exp(-24 * t)
        * (math.sin(2 * math.pi * (160 + 520 * t) * t) + 0.25 * math.sin(2 * math.pi * 720 * t))
        for t in (index / RATE for index in range(int(RATE * duration)))
    ]


def _click() -> list[float]:
    rng = random.Random(7)
    duration = 0.07
    return [
        math.exp(-70 * t)
        * (0.45 * rng.uniform(-1, 1) + 0.3 * math.sin(2 * math.pi * 1100 * t))
        for t in (index / RATE for index in range(int(RATE * duration)))
    ]


def _whoosh() -> list[float]:
    rng = random.Random(11)
    duration = 0.42
    samples: list[float] = []
    smooth = 0.0
    for index in range(int(RATE * duration)):
        t = index / RATE
        phase = t / duration
        envelope = math.sin(math.pi * phase) ** 1.7
        smooth = 0.92 * smooth + 0.08 * rng.uniform(-1, 1)
        sweep = math.sin(2 * math.pi * (180 + 900 * phase * phase) * t)
        samples.append(envelope * (0.36 * smooth + 0.12 * sweep))
    return samples


def generate_all(output: Path) -> None:
    _write(output / "pop.wav", _pop())
    _write(output / "click.wav", _click())
    _write(output / "whoosh.wav", _whoosh())


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    generate_all(args.output.resolve())


if __name__ == "__main__":
    main()
