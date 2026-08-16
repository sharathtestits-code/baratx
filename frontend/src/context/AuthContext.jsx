import { createContext, useContext, useEffect, useState } from "react";
import { ApiError, api } from "../api";
import { applyTheme, isValidTheme } from "../theme";

const AuthContext = createContext(null);

function isAuthFailure(err) {
  if (err instanceof ApiError && (err.status === 401 || err.status === 403)) return true;
  const msg = String(err?.message || "").toLowerCase();
  return /not authenticated|invalid or expired token|unauthorized|401/.test(msg);
}

function isTransientFailure(err) {
  if (err instanceof ApiError && (err.code === "network" || err.code === "timeout" || err.status === 0)) {
    return true;
  }
  if (err instanceof ApiError && err.status >= 500) return true;
  const msg = String(err?.message || "").toLowerCase();
  return /could not reach|timed out|failed to fetch|502|503|504/.test(msg);
}

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem("iv_token"));
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(() => Boolean(localStorage.getItem("iv_token")));
  const [bootError, setBootError] = useState("");

  useEffect(() => {
    if (!token) {
      setUser(null);
      setBootError("");
      setLoading(false);
      return;
    }
    let cancelled = false;
    setLoading(true);
    setBootError("");
    api
      .me(token)
      .then((me) => {
        if (cancelled) return;
        setUser(me);
        setBootError("");
        if (isValidTheme(me?.theme)) applyTheme(me.theme);
      })
      .catch((err) => {
        if (cancelled) return;
        // Only clear session on real auth failures. Network/5xx blips must not
        // log people out into a 404 after hard refresh during API deploys.
        if (isAuthFailure(err)) {
          setToken(null);
          setUser(null);
          setBootError("");
          localStorage.removeItem("iv_token");
          return;
        }
        if (isTransientFailure(err)) {
          setBootError(err.message || "Could not reach BarathX. Check your connection and try again.");
          return;
        }
        setBootError(err.message || "Could not load your session.");
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [token]);

  function login(newToken) {
    // Keep loading true until /users/me resolves so Feed doesn't bounce to /login.
    setLoading(true);
    setUser(null);
    setBootError("");
    localStorage.setItem("iv_token", newToken);
    setToken(newToken);
  }

  async function logout() {
    const current = localStorage.getItem("iv_token");
    localStorage.removeItem("iv_token");
    setToken(null);
    setUser(null);
    setBootError("");
    setLoading(false);
    // Best-effort: don't block UI if the network is down.
    if (current) {
      try {
        await api.revokeSessions(current);
      } catch {
        /* ignore */
      }
    }
  }

  async function revokeAllSessions() {
    if (!token) {
      logout();
      return;
    }
    try {
      await api.revokeSessions(token);
    } catch {
      /* still clear local session */
    }
    localStorage.removeItem("iv_token");
    setToken(null);
    setUser(null);
    setBootError("");
    setLoading(false);
  }

  function updateUser(partialOrFull) {
    setUser((prev) => ({ ...prev, ...partialOrFull }));
    if (isValidTheme(partialOrFull?.theme)) applyTheme(partialOrFull.theme);
  }

  function retryBoot() {
    if (!token) return;
    setLoading(true);
    setBootError("");
    api
      .me(token)
      .then((me) => {
        setUser(me);
        setBootError("");
        if (isValidTheme(me?.theme)) applyTheme(me.theme);
      })
      .catch((err) => {
        if (isAuthFailure(err)) {
          setToken(null);
          setUser(null);
          localStorage.removeItem("iv_token");
          return;
        }
        setBootError(err.message || "Could not reach BarathX. Check your connection and try again.");
      })
      .finally(() => setLoading(false));
  }

  return (
    <AuthContext.Provider
      value={{
        token,
        user,
        loading,
        bootError,
        login,
        logout,
        revokeAllSessions,
        updateUser,
        retryBoot,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
