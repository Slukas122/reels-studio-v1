#!/usr/bin/env python3
"""Manage reusable local client video profiles without a hosted database."""

from __future__ import annotations

import argparse
import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "client-profiles"


def client_key(value: str) -> str:
    value = value.lower().strip().removeprefix("https://").removeprefix("http://").split("/")[0]
    if not re.fullmatch(r"[a-z0-9][a-z0-9.-]{1,251}[a-z0-9]", value) or ".." in value:
        raise ValueError("Client must be a domain or a simple slug")
    return value


def profile_path(root: Path, client: str) -> Path:
    return root / client_key(client) / "video-profile.json"


def load_profile(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if value.get("version") != 1 or value.get("status") not in {"draft", "approved"}:
        raise ValueError("Profile must have version 1 and draft/approved status")
    for key in ("brand", "captions", "editorial", "audio", "locales"):
        if not isinstance(value.get(key), dict):
            raise ValueError(f"Profile is missing {key}")
    return value


def apply_profile(project: Path, path: Path, allow_draft: bool = False) -> None:
    profile = load_profile(path)
    if profile["status"] != "approved" and not allow_draft:
        raise ValueError("Client profile is draft; approve it or explicitly use --allow-draft")
    plan_path = project / "data/edit-plan.json"
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    for key in ("brand", "captions"):
        plan[key].update(profile[key])
    manifest_path = project / "data/asset-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    client_dir = path.parent.resolve()
    for field in ("logo", "fontFile"):
        rel = plan["brand"].get(field)
        if not rel:
            continue
        src = (client_dir / rel).resolve()
        if client_dir not in src.parents or not src.is_file():
            raise ValueError(f"Profile {field} is missing or outside the client directory")
        dest = project / "public" / "client" / field.lower() / src.name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
        plan["brand"][field] = str(dest.relative_to(project / "public"))
        manifest["assets"].append({"path": plan["brand"][field], "origin": str(src), "rights": "client-provided; verify licence"})
    plan_path.write_text(json.dumps(plan, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (project / "data/client-profile.json").write_text(json.dumps(profile, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Applied {profile['status']} client profile from {path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("init", "apply", "show"))
    parser.add_argument("--client", required=True)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--project", type=Path)
    parser.add_argument("--allow-draft", action="store_true")
    args = parser.parse_args()
    root = args.root.expanduser().resolve()
    path = profile_path(root, args.client)
    if args.action == "init":
        if path.exists():
            raise SystemExit(f"Refusing to overwrite existing profile: {path}")
        path.parent.mkdir(parents=True, exist_ok=True)
        profile = {
            "version": 1, "client": client_key(args.client), "status": "draft",
            "brand": {"fontFamily": "Inter, Arial, sans-serif", "fontFile": None, "textColor": "#FFFFFF", "accentColor": "#FFE600", "backgroundColor": "#0B0B0D", "captionBoxColor": "rgba(0,0,0,0.58)", "logo": None},
            "captions": {"maxWordsPerPage": 4, "position": "lower", "highlightWords": [], "fontSize": 70, "speakerColors": {}},
            "editorial": {"audience": None, "hookStyle": None, "pacing": "natural", "cta": None, "avoid": []},
            "audio": {"musicPolicy": "optional", "sfxPolicy": "meaningful-events-only"},
            "locales": {"source": "auto", "targets": []},
            "sources": []
        }
        path.write_text(json.dumps(profile, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"Created draft profile: {path}")
    elif args.action == "show":
        if not path.exists():
            raise SystemExit(f"No profile for {args.client}")
        print(path.read_text(encoding="utf-8"))
    else:
        if not args.project:
            parser.error("--project is required for apply")
        if not path.exists():
            raise SystemExit(f"No profile for {args.client}")
        apply_profile(args.project.expanduser().resolve(), path, allow_draft=args.allow_draft)


if __name__ == "__main__":
    main()
