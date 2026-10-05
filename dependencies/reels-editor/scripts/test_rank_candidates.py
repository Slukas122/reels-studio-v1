import unittest

from rank_candidates import rank


class CandidateRankingTests(unittest.TestCase):
    def setUp(self):
        self.candidates = {
            "candidates": [
                {
                    "id": "clear",
                    "sourceStartMs": 1000,
                    "sourceEndMs": 12000,
                    "openingWords": "Here is the point",
                    "payoffWords": "That is why",
                    "evidence": "Audio and picture reviewed",
                    "scores": {"hook": 4, "clarity": 5, "substance": 5, "delivery": 4, "payoff": 5},
                },
                {
                    "id": "weak",
                    "sourceStartMs": 18000,
                    "sourceEndMs": 29000,
                    "openingWords": "Well",
                    "payoffWords": "Maybe",
                    "evidence": "Audio and picture reviewed",
                    "scores": {"hook": 1, "clarity": 3, "substance": 2, "delivery": 2, "payoff": 1},
                },
            ]
        }

    def test_ranks_stronger_candidate(self):
        self.assertEqual([item["id"] for item in rank(self.candidates, 30000)], ["clear", "weak"])

    def test_rejects_out_of_bounds_candidate(self):
        with self.assertRaisesRegex(ValueError, "exceeds source duration"):
            rank(self.candidates, 25000)


if __name__ == "__main__":
    unittest.main()
