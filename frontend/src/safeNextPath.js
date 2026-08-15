/**
 * Safe in-app redirect targets after signup/login.
 * Blocks open redirects (//evil, https://…, javascript:, etc.).
 */

const ALLOWED_PREFIXES = [
  "/home",
  "/feed",
  "/spaces",
  "/arenas",
  "/rewards",
  "/communities",
  "/search",
  "/notifications",
  "/messages",
  "/bookmarks",
  "/lists",
  "/settings",
  "/u/",
  "/posts/",
  "/hashtag/",
  "/onboarding",
  "/guidelines",
  "/privacy",
  "/terms",
];

function isAllowedPath(pathOnly) {
  return ALLOWED_PREFIXES.some((p) => {
    if (p.endsWith("/")) {
      return pathOnly.startsWith(p);
    }
    return pathOnly === p || pathOnly.startsWith(`${p}/`);
  });
}

export function safeNextPath(raw, fallback = "/home") {
  const value = (raw || "").trim();
  if (!value) return fallback;
  if (/^[a-zA-Z][a-zA-Z0-9+.-]*:/.test(value)) return fallback;
  if (!value.startsWith("/") || value.startsWith("//") || value.includes("\\")) return fallback;

  let decoded = value;
  try {
    decoded = decodeURIComponent(value);
  } catch {
    return fallback;
  }
  if (
    !decoded.startsWith("/") ||
    decoded.startsWith("//") ||
    decoded.includes("\\") ||
    /^[a-zA-Z][a-zA-Z0-9+.-]*:/.test(decoded)
  ) {
    return fallback;
  }

  const pathOnly = decoded.split("?")[0].split("#")[0];
  if (!isAllowedPath(pathOnly)) return fallback;
  return decoded;
}
