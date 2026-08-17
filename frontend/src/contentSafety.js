/** Client-side mirror of backend adult/sexual content block (not a substitute). */

const ADULT_RE =
  /\b(porn(o|ography|hub)?|onlyfans|fansly|nudes?|nsfw|xxx+|sext(ing|s)?|escort|hookers?)\b|send\s+nudes?|\bsex\s*(tape|video|chat|cam|worker|work|pics?|photos?)\b|\b(dick|cock)\s*pics?\b|\b(blow\s*jobs?|hand\s*jobs?)\b|\berotic\s+(pics?|photos?|videos?|content)\b|\badult\s+(videos?|content|sites?|links?)\b|\bnaked\s+(pics?|photos?|selfies?|videos?)\b/i;

export const ADULT_BLOCK_MESSAGE =
  "Adult or sexual content is not allowed on BarathX. Keep posts, replies, and messages suitable for India's public square.";

export function isAdultOrSexualContent(text) {
  return ADULT_RE.test(text || "");
}

export function assertSafePublicText(text) {
  if (isAdultOrSexualContent(text)) {
    throw new Error(ADULT_BLOCK_MESSAGE);
  }
}
