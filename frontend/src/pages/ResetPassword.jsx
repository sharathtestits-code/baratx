import { useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { api } from "../api";

export default function ResetPassword() {
  const [params] = useSearchParams();
  const token = params.get("token") || "";
  const navigate = useNavigate();
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [done, setDone] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    if (!token) {
      setError("Missing reset token. Open the link from your email.");
      return;
    }
    if (password !== confirm) {
      setError("Passwords do not match");
      return;
    }
    setBusy(true);
    try {
      await api.resetPassword({ token, password });
      setDone(true);
      setTimeout(() => navigate("/login", { replace: true }), 1800);
    } catch (err) {
      setError(err.message || "Could not reset password");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="auth-card auth-card-x">
      <h1>Reset password</h1>

      {!token && (
        <p className="error">Missing reset token. Open the link from your email.</p>
      )}

      {error && <div className="error">{error}</div>}
      {done && <p className="success-banner">Password updated. Taking you to sign in…</p>}

      {token && !done && (
        <form onSubmit={handleSubmit}>
          <label>
            New password
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              minLength={8}
              autoComplete="new-password"
              required
            />
          </label>
          <label>
            Confirm password
            <input
              type="password"
              value={confirm}
              onChange={(e) => setConfirm(e.target.value)}
              minLength={8}
              autoComplete="new-password"
              required
            />
          </label>
          <button type="submit" disabled={busy}>
            {busy ? "Updating…" : "Update password"}
          </button>
        </form>
      )}

      <p className="switch-link">
        <Link to="/login">Back to sign in</Link>
        {" · "}
        <Link to="/forgot-password">Request a new link</Link>
      </p>
    </div>
  );
}
