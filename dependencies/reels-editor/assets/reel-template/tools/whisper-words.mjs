/** Merge Whisper's subword tokens into timed, displayable words. */
export const toTimedWords = (tokens) => {
  const words = [];
  let current = null;
  let pendingSpace = false;

  const flush = () => {
    if (current?.text.trim()) words.push(current);
    current = null;
  };

  for (const token of tokens) {
    const raw = token.text ?? "";
    if (!raw.trim()) {
      pendingSpace = true;
      continue;
    }
    const startsWord = /^\s/.test(raw) || pendingSpace;
    if (startsWord) flush();
    const start = Number(token.startMs);
    const end = Number(token.endMs);
    if (!current) {
      const prefix = words.length ? " " : "";
      current = {
        text: prefix + raw.trimStart(),
        startMs: Number.isFinite(start) && Number.isFinite(end) ? (start > end && words.length === 0 ? 0 : Math.max(0, Math.min(start, end))) : 0,
        endMs: Number.isFinite(end) ? Math.max(0, end) : 0,
        confidence: Number.isFinite(token.confidence) ? token.confidence : null,
      };
    } else {
      current.text += raw;
      if (Number.isFinite(end)) current.endMs = Math.max(current.endMs, end);
      if (Number.isFinite(token.confidence)) {
        current.confidence = current.confidence === null ? token.confidence : Math.min(current.confidence, token.confidence);
      }
    }
    pendingSpace = false;
  }
  flush();
  return words;
};
