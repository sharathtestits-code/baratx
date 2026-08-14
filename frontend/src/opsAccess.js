/** Ops console — path is public for SPA routing; UI is owner-only. */

const DEFAULT_PATH = "/bx-ops";
const PATH_CACHE_KEY = "bx_ops_path";

let cachedPath = null;
let pathPromise = null;

function normalizePath(raw) {
  let p = String(raw || DEFAULT_PATH).trim() || DEFAULT_PATH;
  if (!p.startsWith("/")) p = `/${p}`;
  p = p.replace(/\/$/, "") || DEFAULT_PATH;
  return p;
}

function viteFallbackPath() {
  const fromEnv = (import.meta.env.VITE_OPS_CONSOLE_PATH || "").trim();
  return fromEnv ? normalizePath(fromEnv) : DEFAULT_PATH;
}

function rememberPath(path) {
  cachedPath = normalizePath(path);
  try {
    sessionStorage.setItem(PATH_CACHE_KEY, cachedPath);
  } catch {
    /* ignore */
  }
  return cachedPath;
}

function sessionPath() {
  try {
    const p = sessionStorage.getItem(PATH_CACHE_KEY);
    return p ? normalizePath(p) : null;
  } catch {
    return null;
  }
}

/**
 * Ops console UI is owner-only. Requires API `user.is_ops_owner === true`.
 * No Vite username fallback.
 */
export function canAccessOpsConsole(user) {
  if (!user?.username) return false;
  return user.is_ops_owner === true;
}

/** Sync path — API cache / session / Vite env / default. */
export function opsConsolePath() {
  return cachedPath || sessionPath() || viteFallbackPath();
}

/** Apply path from /users/me when the signed-in user is an ops owner. */
export function applyOpsPathFromUser(user) {
  if (user?.is_ops_owner === true && user.ops_console_path) {
    return rememberPath(user.ops_console_path);
  }
  return opsConsolePath();
}

/**
 * Load console path from API (public path hint for routing).
 * Console UI still requires is_ops_owner + ADMIN_SECRET.
 */
export function loadOpsConsolePath(apiBase, _token) {
  if (cachedPath) return Promise.resolve(cachedPath);
  if (pathPromise) return pathPromise;
  const base = (apiBase || import.meta.env.VITE_API_BASE || "").replace(/\/$/, "");
  const url = `${base}/ops/config`;
  pathPromise = fetch(url, { credentials: "omit" })
    .then(async (res) => {
      if (!res.ok) throw new Error(`ops config ${res.status}`);
      const data = await res.json();
      return rememberPath(data?.console_path);
    })
    .catch(() => {
      const session = sessionPath();
      if (session) {
        cachedPath = session;
        return cachedPath;
      }
      return viteFallbackPath();
    })
    .finally(() => {
      pathPromise = null;
    });
  return pathPromise;
}
