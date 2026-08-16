import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

const SEEN_KEY = "bx_security_trust_seen_v1";

/**
 * One-time trust modal, what BarathX does to keep accounts & data safer.
 */
export default function SecurityTrustModal() {
  const { user } = useAuth();
  const [open, setOpen] = useState(false);

  useEffect(() => {
    if (!user) return undefined;
    try {
      if (localStorage.getItem(SEEN_KEY) === "1") return undefined;
    } catch {
      /* ignore */
    }
    const id = window.setTimeout(() => setOpen(true), 900);
    return () => window.clearTimeout(id);
  }, [user?.id]);

  function dismiss() {
    try {
      localStorage.setItem(SEEN_KEY, "1");
    } catch {
      /* ignore */
    }
    setOpen(false);
  }

  if (!open) return null;

  return (
    <div className="security-trust-backdrop" role="presentation" onClick={dismiss}>
      <div
        className="security-trust-modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="security-trust-title"
        onClick={(e) => e.stopPropagation()}
      >
        <p className="security-trust-kicker">Your data · Our promise</p>
        <h2 id="security-trust-title">BarathX keeps your account locked down</h2>
        <p className="hint">
          Soft launch or not, we treat sign-in and personal data as product, not an afterthought.
        </p>
        <ul className="security-trust-list">
          <li>
            <strong>Passwords hashed</strong>, we never store your password in plain text.
          </li>
          <li>
            <strong>Email &amp; phone stay private</strong>, other people can’t see them on your
            profile.
          </li>
          <li>
            <strong>Secure sign-in</strong>. Google checks, OTP limits, and rate limits on login
            attempts.
          </li>
          <li>
            <strong>Session kill switch</strong>. Log out or “Sign out everywhere” in Settings
            invalidates stolen tokens on other devices.
          </li>
          <li>
            <strong>You control mail</strong>, unsubscribe anytime; delete your account in Settings.
          </li>
        </ul>
        <div className="security-trust-actions">
          <button type="button" className="btn btn-primary" onClick={dismiss}>
            Got it
          </button>
          <Link to="/settings" className="btn btn-secondary" onClick={dismiss}>
            Privacy &amp; security
          </Link>
        </div>
      </div>
    </div>
  );
}
