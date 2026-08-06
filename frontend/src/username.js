/** Shared username rules — keep in sync with backend schemas.normalize_username */
const USERNAME_RE = /^[a-zA-Z0-9][a-zA-Z0-9._-]{2,19}$/;

export function normalizeUsernameInput(raw) {
  return (raw || "").trim().replace(/^@/, "").toLowerCase();
}

export function validateUsername(raw) {
  const v = normalizeUsernameInput(raw);
  if (!USERNAME_RE.test(v) || v.includes("..") || v.includes("--") || v.endsWith(".") || v.endsWith("-")) {
    return "Username must be 3–20 chars: letters, numbers, underscore, period, or hyphen (e.g. rahul_99)";
  }
  return null;
}

export { USERNAME_RE };
