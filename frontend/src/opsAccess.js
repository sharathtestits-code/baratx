/** Ops console access — owner-only. Path never leaked to the public. */

const DEFAULT_PATH = "/bx-ops";
const PATH_CACHE_KEY = "bx_ops_path_owner";

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

function rememberOwnerPath(path) {
  cachedPath = normalizePath(path);
  try {
    sessionStorage.setItem(PATH_CACHE_KEY, cachedPath);
  } catch {
    /* ignore */
  }
  return cachedPath;
}

function sessionOwnerPath() {
  try {
    const p = sessionStorage.getItem(PATH_CACHE_KEY);
    return p ? normalizePath(p) : null;
  } catch {
    return null;
  }
}

/**
 * Ops console is owner-only. Requires API `user.is_ops_owner === true`.
 * No Vite username fallback (that would let a hardcoded name open the UI).
 */
export function canAccessOpsConsole(user) {
  if (!user?.username) return false;
  return user.is_ops_owner === true;
}

/** Sync path — owner cache / session / Vite env / default. */
export function opsConsolePath() {
  return cachedPath || sessionOwnerPath() || viteFallbackPath();
}

/** Apply path from /users/me when the signed-in user is an ops owner. */
export function applyOpsPathFromUser(user) {
  if (user?.is_ops_owner === true && user.ops_console_path) {
    return rememberOwnerPath(user.ops_console_path);
  }
  return opsConsolePath();
}

/**
 * Load console path. Requires bearer token of an ops owner.
 * Anonymous / non-owners get no path leak (keeps Vite/session fallback only).
 */
export function loadOpsConsolePath(apiBase, token) {
  if (cachedPath) return Promise.resolve(cachedPath);
  if (!token) {
    const session = sessionOwnerPath();
    if (session) {
      cachedPath = session;
      return Promise.resolve(cachedPath);
    }
    return Promise.resolve(viteFallbackPath());
  }
  if (pathPromise) return pathPromise;
  const base = (apiBase || import.meta.env.VITE_API_BASE || "").replace(/\/$/, "");
  const url = `${base}/ops/config`;
  pathPromise = fetch(url, {
    credentials: "omit",
    headers: { Authorization: `Bearer ${token}` },
  })
    .then(async (res) => {
      if (!res.ok) throw new Error(`ops config ${res.status}`);
      const data = await res.json();
      return rememberOwnerPath(data?.console_path);
    })
    .catch(() => {
      const session = sessionOwnerPath();
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
