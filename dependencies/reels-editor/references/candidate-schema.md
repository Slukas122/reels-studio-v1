# Optional candidate shortlist

For a source with multiple plausible stories, record the evidence and compare candidates. Do not fabricate extra candidates for a short source.

`data/candidates.json`:

```json
{
  "candidates": [
    {
      "id": "useful-example",
      "sourceStartMs": 10000,
      "sourceEndMs": 39000,
      "openingWords": "Actual first spoken words",
      "payoffWords": "Actual last spoken words",
      "evidence": "Listened at 10–39 s; picture shows the product at 24 s",
      "scores": {"hook": 4, "clarity": 5, "substance": 4, "delivery": 4, "payoff": 4}
    }
  ]
}
```

All five scores run 0–5. `rank_candidates.py --project .` validates the format and writes `data/candidate-ranking.json`. It cannot verify the quotation, delivery, image or claim. Inspect the source and note the winner and rejected alternatives in `data/edit-notes.md`.
