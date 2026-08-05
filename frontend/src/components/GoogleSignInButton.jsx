import { useState } from "react";
import { api } from "../api";
import { useAuth } from "../context/AuthContext";
import { useNavigate } from "react-router-dom";

const CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID || "";

/**
 * Google Identity Services button. Requires VITE_GOOGLE_CLIENT_ID and a matching
 * GOOGLE_CLIENT_ID on the API. Shows a disabled stub when not configured.
 */
export default function GoogleSignInButton({ label = "Continue with Google", onError }) {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [showFallback, setShowFallback] = useState(false);

  async function handleCredential(response) {
    if (!response?.credential) return;
    setBusy(true);
    setError("");
    try {
      const data = await api.loginGoogle({ id_token: response.credential });
      login(data.access_token);
      navigate("/feed");
    } catch (err) {
      const msg = err.message || "Google sign-in failed";
      setError(msg);
      onError?.(msg);
    } finally {
      setBusy(false);
    }
  }

  function startGoogle() {
    setError("");
    setShowFallback(false);
    if (!CLIENT_ID) {
      setError("Google sign-in is not configured yet. Add VITE_GOOGLE_CLIENT_ID.");
      return;
    }
    if (!window.google?.accounts?.id) {
      setError("Google script still loading — try again in a moment.");
      return;
    }
    window.google.accounts.id.initialize({
      client_id: CLIENT_ID,
      callback: handleCredential,
      ux_mode: "popup",
    });
    window.google.accounts.id.prompt((notification) => {
      if (notification.isNotDisplayed() || notification.isSkippedMoment()) {
        setShowFallback(true);
        requestAnimationFrame(() => {
          const host = document.getElementById("google-btn-host");
          if (!host || !window.google?.accounts?.id) return;
          host.innerHTML = "";
          window.google.accounts.id.renderButton(host, {
            theme: "outline",
            size: "large",
            shape: "pill",
            text: "continue_with",
            width: host.offsetWidth || 320,
          });
        });
      }
    });
  }

  if (!CLIENT_ID) {
    return (
      <div className="x-google-wrap">
        <button type="button" className="x-btn x-btn-google" onClick={startGoogle}>
          <GoogleG className="x-btn-icon" />
          {label}
        </button>
        {error && <p className="x-inline-error">{error}</p>}
      </div>
    );
  }

  return (
    <div className="x-google-wrap">
      {!showFallback && (
        <button type="button" className="x-btn x-btn-google" onClick={startGoogle} disabled={busy}>
          <GoogleG className="x-btn-icon" />
          {busy ? "Signing in…" : label}
        </button>
      )}
      <div id="google-btn-host" className="google-btn-host" hidden={!showFallback} />
      {error && <p className="x-inline-error">{error}</p>}
    </div>
  );
}

function GoogleG({ className = "" }) {
  return (
    <svg className={className} viewBox="0 0 24 24" width="18" height="18" aria-hidden="true">
      <path
        fill="#EA4335"
        d="M12 10.2v3.6h5.1c-.2 1.2-.9 2.2-1.9 2.9l3.1 2.4c1.8-1.7 2.9-4.1 2.9-7 0-.7-.1-1.3-.2-1.9H12z"
      />
      <path
        fill="#34A853"
        d="M5.3 14.3 4.4 15l-2.1 1.6C3.8 19.5 7.6 22 12 22c2.7 0 5-.9 6.7-2.4l-3.1-2.4c-.9.6-2 .9-3.6.9-2.8 0-5.1-1.9-5.9-4.4z"
      />
      <path
        fill="#4A90E2"
        d="M3.2 7.4C2.4 9 2 10.4 2 12s.4 3 1.2 4.6l2.9-2.3C5.7 13.5 5.5 12.8 5.5 12s.2-1.5.6-2.3L3.2 7.4z"
      />
      <path
        fill="#FBBC05"
        d="M12 5.5c1.5 0 2.8.5 3.8 1.5l2.8-2.8C16.9 2.5 14.7 1.5 12 1.5 7.6 1.5 3.8 4 2.3 7.4l3 2.3C6.9 7.4 9.2 5.5 12 5.5z"
      />
    </svg>
  );
}
