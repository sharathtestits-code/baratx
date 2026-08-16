import { useEffect, useRef, useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { api } from "../api";
import { useAuth } from "../context/AuthContext";

export default function VerifyEmail() {
  const [params] = useSearchParams();
  const token = (params.get("token") || "").trim();
  const navigate = useNavigate();
  const { token: authToken, updateUser, user } = useAuth();
  const [status, setStatus] = useState(token ? "loading" : "missing");
  const [message, setMessage] = useState("");
  const [resending, setResending] = useState(false);
  const startedRef = useRef(false);
  const authTokenRef = useRef(authToken);
  const updateUserRef = useRef(updateUser);

  useEffect(() => {
    authTokenRef.current = authToken;
    updateUserRef.current = updateUser;
  }, [authToken, updateUser]);

  // Verify once per token, do not re-run when AuthContext re-renders
  // (unstable updateUser / session hydrate), or the first success consumes
  // the one-time token and the retry shows "already used".
  useEffect(() => {
    if (!token || startedRef.current) return undefined;
    startedRef.current = true;
    let cancelled = false;

    api
      .verifyEmail(token)
      .then(async (res) => {
        if (cancelled) return;
        setStatus("ok");
        setMessage(res.message || "Email confirmed.");
        const session = authTokenRef.current;
        if (session) {
          try {
            const me = await api.me(session);
            updateUserRef.current?.(me);
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
  }, [token]);

  useEffect(() => {
    if (status !== "ok") return undefined;
    if (!(user || authToken)) return undefined;
    const t = setTimeout(() => navigate("/feed", { replace: true }), 1600);
    return () => clearTimeout(t);
  }, [status, user, authToken, navigate]);

  async function resend() {
    if (!authToken || resending) return;
    setResending(true);
    try {
      const res = await api.resendVerification(authToken);
      setMessage(res.message || "Verification email sent. Check your inbox.");
      setStatus("resent");
    } catch (err) {
      setMessage(err.message || "Could not resend verification email");
    } finally {
      setResending(false);
    }
  }

  return (
    <div className="auth-card">
      <h1>Confirm email</h1>
      {status === "loading" && <p className="hint">Confirming your email…</p>}
      {status === "missing" && (
        <p className="error">Missing verification token. Open the link from your email.</p>
      )}
      {status === "ok" && (
        <>
          <p className="success-banner">{message}</p>
          {(user || authToken) && <p className="hint">Taking you to your feed…</p>}
        </>
      )}
      {status === "resent" && <p className="success-banner">{message}</p>}
      {status === "error" && (
        <>
          <p className="error">{message}</p>
          <p className="hint">
            If you already confirmed, you can sign in. Otherwise request a fresh link below.
          </p>
          {authToken && (
            <button type="button" className="btn btn-primary" disabled={resending} onClick={resend}>
              {resending ? "Sending…" : "Resend confirmation email"}
            </button>
          )}
        </>
      )}
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
