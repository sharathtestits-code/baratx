import { useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { api } from "../api";
import { useAuth } from "../context/AuthContext";

export default function VerifyEmail() {
  const [params] = useSearchParams();
  const token = params.get("token") || "";
  const { token: authToken, updateUser, user } = useAuth();
  const [status, setStatus] = useState(token ? "loading" : "missing");
  const [message, setMessage] = useState("");

  useEffect(() => {
    if (!token) return;
    let cancelled = false;
    api
      .verifyEmail(token)
      .then(async (res) => {
        if (cancelled) return;
        setStatus("ok");
        setMessage(res.message || "Email confirmed.");
        if (authToken) {
          try {
            const me = await api.me(authToken);
            updateUser(me);
          } catch {
            /* ignore refresh errors */
          }
        }
      })
      .catch((err) => {
        if (cancelled) return;
        setStatus("error");
        setMessage(err.message || "Could not verify email");
      });
    return () => {
      cancelled = true;
    };
  }, [token, authToken, updateUser]);

  return (
    <div className="auth-card">
      <h1>Confirm email</h1>
      {status === "loading" && <p className="hint">Confirming your email…</p>}
      {status === "missing" && (
        <p className="error">Missing verification token. Open the link from your email.</p>
      )}
      {status === "ok" && <p className="success-banner">{message}</p>}
      {status === "error" && <p className="error">{message}</p>}
      <p className="switch-link">
        {user || authToken ? (
          <Link to="/feed">Go to feed</Link>
        ) : (
          <>
            <Link to="/login">Log in</Link>
            {" · "}
            <Link to="/signup">Sign up</Link>
          </>
        )}
      </p>
    </div>
  );
}
