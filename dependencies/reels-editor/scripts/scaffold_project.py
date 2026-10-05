#!/usr/bin/env python3
"""Create an isolated reel project from the bundled Remotion template."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

from make_sfx import generate_all
from client_profile import ROOT as PROFILE_ROOT, apply_profile, load_profile, profile_path

SUPPORTED = {".mp4", ".mov", ".m4v", ".webm", ".mkv"}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True, help="Source video")
    parser.add_argument("--output", type=Path, required=True, help="New project directory")
    parser.add_argument("--client", help="Domain or slug of a saved local client profile")
    parser.add_argument("--profiles-root", type=Path, default=PROFILE_ROOT)
    args = parser.parse_args()

    source = args.input.expanduser().resolve()
    output = args.output.expanduser().resolve()
    if not source.is_file():
        raise SystemExit(f"Input video does not exist: {source}")
    if source.suffix.lower() not in SUPPORTED:
        raise SystemExit(f"Unsupported input extension: {source.suffix}")
    if output.exists() and any(output.iterdir()):
        raise SystemExit(f"Refusing to merge into non-empty directory: {output}")

    template = Path(__file__).resolve().parent.parent / "assets" / "reel-template"
    if not template.is_dir():
        raise SystemExit(f"Bundled template is missing: {template}")

    output.mkdir(parents=True, exist_ok=True)
    shutil.copytree(template, output, dirs_exist_ok=True)
    public = output / "public"
    public.mkdir(exist_ok=True)
    dest_name = f"source{source.suffix.lower()}"
    shutil.copy2(source, public / dest_name)
    generate_all(public / "sfx")

    plan_path = output / "data" / "edit-plan.json"
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    plan["source"] = dest_name
    plan_path.write_text(json.dumps(plan, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    manifest_path = output / "data" / "asset-manifest.json"
    manifest = {
        "assets": [
            {
                "path": dest_name,
                "origin": str(source),
                "rights": "user-provided",
            },
            {
                "path": "sfx/pop.wav",
                "origin": "generated-by-reels-editor",
                "rights": "generated",
            },
            {
                "path": "sfx/click.wav",
                "origin": "generated-by-reels-editor",
                "rights": "generated",
            },
            {
                "path": "sfx/whoosh.wav",
                "origin": "generated-by-reels-editor",
                "rights": "generated",
            },
        ]
    }
    manifest_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    if args.client:
        saved_profile = profile_path(args.profiles_root.expanduser().resolve(), args.client)
        if saved_profile.is_file():
            if load_profile(saved_profile)["status"] == "approved":
                apply_profile(output, saved_profile)
            else:
                print(f"Client profile is draft; using neutral defaults: {saved_profile}")
        else:
            print(f"No saved profile for {args.client}; using neutral defaults. Profile path: {saved_profile}")
    print(f"Created reel project: {output}")
    print(f"Copied source to: public/{dest_name}")
    print("Next: cd into the project and run npm install")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(130)
