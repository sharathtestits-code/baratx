import { createContext, useContext, useEffect, useState } from "react";
import { api } from "../api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem("iv_token"));
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(() => Boolean(localStorage.getItem("iv_token")));

  useEffect(() => {
    if (!token) {
      setUser(null);
      setLoading(false);
      return;
    }
    let cancelled = false;
    setLoading(true);
    api
      .me(token)
      .then((me) => {
        if (!cancelled) setUser(me);
      })
      .catch(() => {
        if (cancelled) return;
        // Stale/broken session — clear so visitors see the public landing again.
        setToken(null);
        setUser(null);
        localStorage.removeItem("iv_token");
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
    localStorage.setItem("iv_token", newToken);
    setToken(newToken);
  }

  function logout() {
    localStorage.removeItem("iv_token");
    setToken(null);
    setUser(null);
    setLoading(false);
  }

  function updateUser(partialOrFull) {
    setUser((prev) => ({ ...prev, ...partialOrFull }));
  }

  return (
    <AuthContext.Provider value={{ token, user, loading, login, logout, updateUser }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
