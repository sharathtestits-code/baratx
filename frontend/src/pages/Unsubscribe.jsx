import { useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { api } from "../api";
import Logo from "../components/Logo";

/**
 * One-click unsubscribe landing, linked from activity emails.
 */
export default function Unsubscribe() {
  const [params] = useSearchParams();
  const token = (params.get("token") || "").trim();
  const [status, setStatus] = useState(token ? "working" : "missing");
  const [message, setMessage] = useState("");

  useEffect(() => {
    if (!token) return undefined;
    let cancelled = false;
    api
      .unsubscribeEmail(token)
      .then((res) => {
        if (cancelled) return;
        setStatus("ok");
        setMessage(res?.message || "Unsubscribed from activity emails.");
      })
      .catch((err) => {
        if (cancelled) return;
        setStatus("error");
        setMessage(err.message || "Could not unsubscribe.");
      });
    return () => {
      cancelled = true;
    };
  }, [token]);

  return (
    <div className="auth-card auth-card-x">
      <Logo variant="full" className="auth-logo" title="BarathX" />
      <h1>Email notifications</h1>
      {status === "missing" && (
        <p className="hint">
          Missing unsubscribe link. Open Settings → Email notifications, or use the link in a BarathX
          activity email.
        </p>
      )}
      {status === "working" && <p className="hint">Unsubscribing…</p>}
      {status === "ok" && (
        <>
          <p className="ok-hint">{message}</p>
          <p className="hint">In-app Alerts still work. You can re-enable emails anytime in Settings.</p>
        </>
      )}
      {status === "error" && <div className="error">{message}</div>}
      <p className="switch-link">
        <Link to="/settings">Open Settings</Link>
        {" · "}
        <Link to="/login">Sign in</Link>
      </p>
    </div>
  );
}
