/** Ops console access — prefer API (Railway) over Vite build-time defaults. */

const DEFAULT_PATH = "/bx-ops";

let cachedPath = null;
let pathPromise = null;

function normalizePath(raw) {
  let p = String(raw || DEFAULT_PATH).trim() || DEFAULT_PATH;
  if (!p.startsWith("/")) p = `/${p}`;
  p = p.replace(/\/$/, "") || DEFAULT_PATH;
  return p;
}

function viteFallbackPath() {
  return normalizePath(import.meta.env.VITE_OPS_CONSOLE_PATH || DEFAULT_PATH);
}

function viteOwnerFallback(user) {
  if (!user?.username) return false;
  const raw = (import.meta.env.VITE_OPS_OWNER_USERNAMES || "").trim();
  const list = raw
    ? raw.split(/[\s,]+/).map((s) => s.trim().toLowerCase()).filter(Boolean)
    : ["sharath"];
  return list.includes(String(user.username).toLowerCase());
}

/**
 * Ops console is owner-only. Prefer `user.is_ops_owner` from GET /users/me
 * (Railway OPS_OWNER_USERNAMES). Vite list is fallback only.
 */
export function canAccessOpsConsole(user) {
  if (!user?.username) return false;
  if (typeof user.is_ops_owner === "boolean") return user.is_ops_owner;
  return viteOwnerFallback(user);
}

/** Sync path — uses API cache when loaded, else Vite / default. */
export function opsConsolePath() {
  return cachedPath || viteFallbackPath();
}

/** Load console path from API (OPS_CONSOLE_PATH on Railway). Safe to call often. */
export function loadOpsConsolePath(apiBase) {
  if (cachedPath) return Promise.resolve(cachedPath);
  if (pathPromise) return pathPromise;
  const base = (apiBase || import.meta.env.VITE_API_BASE || "").replace(/\/$/, "");
  const url = `${base}/ops/config`;
  pathPromise = fetch(url, { credentials: "omit" })
    .then(async (res) => {
      if (!res.ok) throw new Error(`ops config ${res.status}`);
      const data = await res.json();
      cachedPath = normalizePath(data?.console_path);
      return cachedPath;
    })
    .catch(() => {
      cachedPath = viteFallbackPath();
      return cachedPath;
    })
    .finally(() => {
      pathPromise = null;
    });
  return pathPromise;
}
