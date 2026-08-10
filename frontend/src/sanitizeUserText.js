/**
 * Strip bidi/format controls that enable filename spoofing (e.g. exe.png ↔ gnp.exe).
 * Keep ZWJ/ZWNJ for emoji and Indic scripts.
 */
const BIDI_OR_FORMAT = /[\u061C\u200E\u200F\u202A-\u202E\u2060\u2066-\u2069\uFEFF]/g;

export function sanitizeUserText(text) {
  const raw = String(text ?? "");
  let out = "";
  for (const ch of raw.replace(BIDI_OR_FORMAT, "")) {
    const code = ch.codePointAt(0);
    // Unicode Cf (format) except ZWNJ (0x200C) and ZWJ (0x200D).
    if (
      (code >= 0x00ad && code <= 0x00ad) || // soft hyphen
      (code >= 0x0600 && code <= 0x0605) ||
      (code >= 0x061c && code <= 0x061c) ||
      (code >= 0x06dd && code <= 0x06dd) ||
      (code >= 0x070f && code <= 0x070f) ||
      (code >= 0x08e2 && code <= 0x08e2) ||
      (code >= 0x180e && code <= 0x180e) ||
      (code >= 0x200b && code <= 0x200f && code !== 0x200c && code !== 0x200d) ||
      (code >= 0x202a && code <= 0x202e) ||
      (code >= 0x2060 && code <= 0x2064) ||
      (code >= 0x2066 && code <= 0x206f) ||
      (code >= 0xfeff && code <= 0xfeff) ||
      (code >= 0xfff9 && code <= 0xfffb)
    ) {
      continue;
    }
    out += ch;
  }
  return out;
}
