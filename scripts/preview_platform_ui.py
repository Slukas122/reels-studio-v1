#!/usr/bin/env python3
"""Preview an encoded 9:16 video under separate social-app planning masks."""

import argparse
import io
import json
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


# Editorial fallbacks on 1080x1920, not official specifications. Replace with
# current templates or captured account UI whenever possible.
FALLBACK_PROFILES = {
    "tiktok": {
        "label": "TikTok · editorial fallback",
        "rects": [[0, 0, 1080, 250], [0, 1490, 1080, 1920],
                  [880, 600, 1080, 1490], [0, 250, 60, 1490]],
    },
    "instagram": {
        "label": "Instagram Reels · editorial fallback",
        "rects": [[0, 0, 1080, 245], [0, 1450, 1080, 1920],
                  [890, 770, 1080, 1450], [0, 245, 55, 1450]],
    },
    "facebook": {
        "label": "Facebook Reels · editorial fallback",
        "rects": [[0, 0, 1080, 250], [0, 1400, 1080, 1920],
                  [890, 720, 1080, 1400], [0, 250, 55, 1400]],
    },
    "shorts": {
        "label": "YouTube Shorts · editorial fallback",
        "rects": [[0, 0, 1080, 240], [0, 1490, 1080, 1920],
                  [880, 720, 1080, 1490], [0, 240, 55, 1490]],
    },
}


def run(args):
    return subprocess.run(args, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout


def frame(video, second):
    data = run(["ffmpeg", "-v", "error", "-ss", str(second), "-i", str(video),
                "-frames:v", "1", "-f", "image2pipe", "-vcodec", "png", "pipe:1"])
    return Image.open(io.BytesIO(data)).convert("RGBA")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("video", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--platform", nargs="+", default=["tiktok", "instagram", "facebook"],
                        help="One or more profile names; default: tiktok instagram facebook")
    parser.add_argument("--times", help="Comma-separated seconds to inspect; defaults to five samples")
    parser.add_argument("--profiles", type=Path,
                        help="JSON mapping profile names to {label, rects}; rectangles use 1080x1920 coordinates")
    args = parser.parse_args()

    profiles = json.loads(args.profiles.read_text()) if args.profiles else FALLBACK_PROFILES
    for name in args.platform:
        if name not in profiles or "rects" not in profiles[name]:
            parser.error(f"Unknown or invalid profile: {name}")
        for rect in profiles[name]["rects"]:
            if len(rect) != 4 or not (0 <= rect[0] < rect[2] <= 1080 and
                                       0 <= rect[1] < rect[3] <= 1920):
                parser.error(f"Invalid rectangle in profile: {name}")

    info = json.loads(run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                           "-of", "json", str(args.video)]))
    duration = float(info["format"]["duration"])
    times = ([float(x) for x in args.times.split(",")] if args.times else
             [min(duration - .05, t) for t in (.4, duration * .25, duration * .5,
                                                duration * .75, duration - .4)])
    if not times or any(t < 0 or t >= duration for t in times):
        parser.error("Every sample time must be within the video duration")

    frames = [frame(args.video, t) for t in times]
    if any(im.width * 16 != im.height * 9 for im in frames):
        parser.error("Expected a 9:16 vertical video")
    tile_w, tile_h, label_h = 270, 480, 32
    sheet = Image.new("RGB", (tile_w * len(times), (tile_h + label_h) * len(args.platform)), "#111111")
    label_font = ImageFont.load_default()
    for row, name in enumerate(args.platform):
        profile = profiles[name]
        for col, (t, source) in enumerate(zip(times, frames)):
            im = source.copy()
            mask = Image.new("RGBA", im.size)
            draw = ImageDraw.Draw(mask)
            sx, sy = im.width / 1080, im.height / 1920
            for x1, y1, x2, y2 in profile["rects"]:
                draw.rectangle((round(x1 * sx), round(y1 * sy),
                                round(x2 * sx), round(y2 * sy)), fill=(230, 54, 54, 125))
            im = Image.alpha_composite(im, mask).convert("RGB")
            im = im.resize((tile_w, tile_h), Image.Resampling.LANCZOS)
            px, py = col * tile_w, row * (tile_h + label_h)
            sheet.paste(im, (px, py))
            ImageDraw.Draw(sheet).text((px + 5, py + tile_h + 5),
                                       f"{profile.get('label', name)} · {t:.2f}s",
                                       fill="white", font=label_font)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(args.out, quality=92)
    print(args.out)


if __name__ == "__main__":
    main()
