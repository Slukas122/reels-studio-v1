import assert from "node:assert/strict";
import test from "node:test";
import {toTimedWords} from "./whisper-words.mjs";

test("joins Czech subwords and punctuation without changing spoken text", () => {
  const tokens = [
    {text: " já", startMs: 100, endMs: 200, confidence: 0.9},
    {text: " ne", startMs: 210, endMs: 260, confidence: 0.8},
    {text: "ch", startMs: 260, endMs: 320, confidence: 0.7},
    {text: "ci", startMs: 320, endMs: 380, confidence: 0.95},
    {text: ",", startMs: 380, endMs: 390, confidence: 0.6},
    {text: " dě", startMs: 400, endMs: 450, confidence: 0.9},
    {text: "lat", startMs: 450, endMs: 520, confidence: 0.85},
    {text: ".", startMs: 520, endMs: 530, confidence: 0.9},
  ];
  const words = toTimedWords(tokens);
  assert.deepEqual(words.map((word) => word.text), ["já", " nechci,", " dělat."]);
  assert.deepEqual(words.map((word) => [word.startMs, word.endMs]), [[100, 200], [210, 390], [400, 530]]);
  assert.equal(words[1].confidence, 0.6);
  assert.equal(words.map((word) => word.text).join(""), tokens.map((token) => token.text).join("").trim());
});

test("ignores empty fragments and repairs inverted first timestamp", () => {
  const words = toTimedWords([
    {text: "No", startMs: 1000, endMs: 380, confidence: 0.5},
    {text: " ", startMs: 380, endMs: 380, confidence: 0},
    {text: " pokračujeme", startMs: 380, endMs: 800, confidence: 0.9},
  ]);
  assert.deepEqual(words.map((word) => word.text), ["No", " pokračujeme"]);
  assert.deepEqual(words.map((word) => [word.startMs, word.endMs]), [[0, 380], [380, 800]]);
});
