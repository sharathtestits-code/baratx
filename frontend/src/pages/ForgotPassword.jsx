import { useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api";

export default function ForgotPassword() {
  const [email, setEmail] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [devUrl, setDevUrl] = useState("");

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setMessage("");
    setDevUrl("");
    setBusy(true);
    try {
      const res = await api.forgotPassword(email.trim());
      setMessage(res.message || "If that email is registered, we sent a password reset link.");
      if (res.dev_reset_url) setDevUrl(res.dev_reset_url);
    } catch (err) {
      setError(err.message || "Could not send reset email");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="auth-card auth-card-x">
      <h1>Forgot password?</h1>
      <p className="hint">Enter your account email and we’ll send a reset link.</p>

      {error && <div className="error">{error}</div>}
      {message && <p className="success-banner">{message}</p>}
      {devUrl && (
        <p className="hint">
          Dev reset link: <a href={devUrl}>{devUrl}</a>
        </p>
      )}

      {!message && (
        <form onSubmit={handleSubmit}>
          <label>
            Email
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              autoComplete="email"
              required
            />
          </label>
          <button type="submit" disabled={busy}>
            {busy ? "Sending…" : "Send reset link"}
          </button>
        </form>
      )}

      <p className="switch-link">
        <Link to="/login">Back to sign in</Link>
      </p>
    </div>
  );
}
