/** Shared live/debate display helpers for empty-state trust and headline clarity. */

/** Prefer a short debate question as the headline; keep long scoop titles as context. */
export function debateHeadline(title = "") {
  const raw = String(title || "").trim();
  if (!raw) return "";
  const cleaned = raw.replace(/^\s*(SCOOP|BREAKING|UPDATE)\s*:\s*/i, "").trim();
  if (cleaned.length <= 72) return cleaned;
  const cut = cleaned.slice(0, 69).replace(/\s+\S*$/, "");
  return `${cut}…`;
}

export function debateHeadlineContext(title = "") {
  const raw = String(title || "").trim();
  const head = debateHeadline(raw);
  if (!raw || head === raw || head === raw.replace(/^\s*(SCOOP|BREAKING|UPDATE)\s*:\s*/i, "").trim()) {
    return "";
  }
  return raw;
}

/** Avoid advertising empty rooms as “0 takes”. */
export function liveTakesLabel(count, { firstVoice = "Be the first voice in this room." } = {}) {
  const n = typeof count === "number" ? count : null;
  if (n == null) return "";
  if (n <= 0) return firstVoice;
  if (n === 1) return "1 take in the room";
  return `${n} takes in the room`;
}
