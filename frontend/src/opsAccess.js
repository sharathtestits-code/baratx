/** Who may open the private ops console UI (path is still secret + unlock code). */

const DEFAULT_OWNERS = ["sharath"];

function ownerSet() {
  const raw = (import.meta.env.VITE_OPS_OWNER_USERNAMES || "").trim();
  const list = raw
    ? raw.split(/[\s,]+/).map((s) => s.trim().toLowerCase()).filter(Boolean)
    : DEFAULT_OWNERS;
  return new Set(list);
}

/**
 * Ops console is owner-only. Logged-out users and everyone else get a normal 404.
 * API money actions still require the ops unlock code separately.
 */
export function canAccessOpsConsole(user) {
  if (!user?.username) return false;
  return ownerSet().has(String(user.username).toLowerCase());
}

export function opsConsolePath() {
  return (import.meta.env.VITE_OPS_CONSOLE_PATH || "/bx-ops").replace(/\/$/, "") || "/bx-ops";
}
