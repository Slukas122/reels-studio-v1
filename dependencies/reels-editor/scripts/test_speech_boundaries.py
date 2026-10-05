import unittest

from compile_timeline import check_speech_boundaries


class SpeechBoundaryTests(unittest.TestCase):
    def test_rejects_original_clipped_nejenom(self):
        words = [
            {"text": " pomohl.", "startMs": 131300, "endMs": 132000},
            {"text": " Nejenom", "startMs": 132000, "endMs": 132680},
        ]
        segment = {"id": "ending", "sourceStartMs": 100000, "sourceEndMs": 132250}
        with self.assertRaisesRegex(ValueError, "Nejenom"):
            check_speech_boundaries([segment], words)

    def test_accepts_complete_ending(self):
        words = [
            {"text": " Nejenom", "startMs": 132000, "endMs": 132680},
            {"text": " cokoliv.", "startMs": 136200, "endMs": 136700},
        ]
        segment = {"id": "ending", "sourceStartMs": 100000, "sourceEndMs": 137000}
        check_speech_boundaries([segment], words)


if __name__ == "__main__":
    unittest.main()
