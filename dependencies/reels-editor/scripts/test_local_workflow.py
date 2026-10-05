"""Focused checks for transcript integrity, profiles, and subtitle timing."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from client_profile import apply_profile, client_key
from compile_timeline import localized_titles, mark_caption_pages
from localize_captions import group_words, translate_in_context, validate as validate_translation
from review_transcript import validate as validate_review


class EchoTranslator:
    def translate(self, value: str) -> str:
        return value.replace(" Dobrý", " Good").replace(" den", " day")


class LocalWorkflowTests(unittest.TestCase):
    def test_caption_page_count_restarts_after_sentence(self) -> None:
        words = [{"text": value, "pageBreakAfter": False} for value in
                 (" One", " two", " three.", " And", " this", " continues", " now.")]
        mark_caption_pages(words, 4)
        self.assertEqual([index for index, word in enumerate(words) if word["pageBreakAfter"]], [2, 6])

    def test_localized_title_requires_language_and_text(self) -> None:
        self.assertEqual(localized_titles({"en": " How to help? "}, "hook"), {"en": "How to help?"})
        with self.assertRaisesRegex(ValueError, "language code"):
            localized_titles({"EN-US": "How?"}, "hook")

    def test_review_allows_punctuation_and_case_but_blocks_unverified_rewrite(self) -> None:
        source = [{"text": " dobry", "startMs": 0, "endMs": 400}, {"text": " den", "startMs": 400, "endMs": 800}]
        review = {"version": 1, "sourceSha256": "hash", "tokens": [
            {"index": 0, "original": " dobry", "text": " Dobry,", "evidence": None, "reason": None},
            {"index": 1, "original": " den", "text": " den.", "evidence": None, "reason": None},
        ]}
        self.assertEqual(validate_review(source, review, "hash")[0]["text"], " Dobry,")
        review["tokens"][0]["text"] = " Dobrý,"
        with self.assertRaisesRegex(ValueError, "audio-verified"):
            validate_review(source, review, "hash")
        review["tokens"][0].update({"evidence": "audio-verified", "reason": "Accent confirmed from audio"})
        review["tokens"][0]["speaker"] = "SPEAKER_00"
        checked = validate_review(source, review, "hash")
        self.assertEqual(checked[0]["text"], " Dobrý,")
        self.assertEqual(checked[0]["speaker"], "SPEAKER_00")
        review["tokens"][1]["text"] = " den dnes."
        with self.assertRaisesRegex(ValueError, "number of spoken words"):
            validate_review(source, review, "hash")

    def test_profile_is_applied_without_overwriting_source(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            project = root / "project"
            (project / "data").mkdir(parents=True)
            (project / "public").mkdir()
            (project / "data/edit-plan.json").write_text(json.dumps({"brand": {"logo": None}, "captions": {"enabled": True}}))
            (project / "data/asset-manifest.json").write_text(json.dumps({"assets": []}))
            profile_dir = root / "xy.cz"
            profile_dir.mkdir()
            (profile_dir / "logo.png").write_bytes(b"logo")
            profile = {"version": 1, "status": "approved", "brand": {"logo": "logo.png", "accentColor": "#123456"}, "captions": {"fontSize": 64}, "editorial": {}, "audio": {}, "locales": {}}
            path = profile_dir / "video-profile.json"
            path.write_text(json.dumps(profile))
            apply_profile(project, path)
            plan = json.loads((project / "data/edit-plan.json").read_text())
            self.assertEqual(plan["brand"]["accentColor"], "#123456")
            self.assertTrue((project / "public" / plan["brand"]["logo"]).exists())
            self.assertEqual(client_key("https://XY.CZ/about"), "xy.cz")

    def test_translation_keeps_cue_times(self) -> None:
        words = [
            {"text": " Dobrý", "startMs": 0, "endMs": 400, "pageBreakAfter": False},
            {"text": " den.", "startMs": 400, "endMs": 800, "pageBreakAfter": True},
        ]
        source = group_words(words)
        translated = translate_in_context(source, EchoTranslator())
        self.assertEqual(translated[0]["startMs"], 0)
        self.assertEqual(translated[0]["endMs"], 800)
        self.assertEqual(validate_translation(translated, source), [])


if __name__ == "__main__":
    unittest.main()
