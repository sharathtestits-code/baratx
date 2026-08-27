import { useEffect, useRef, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import Logo from "../components/Logo";

const CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID || "";
const API_BASE = (import.meta.env.VITE_API_BASE || "").replace(/\/$/, "");
const DEEP_LINK = "barathx://google-auth";

/**
 * Opened from the Android/iOS app in a system browser.
 * Completes Google Sign-In with the Web client, then deep-links the JWT back into the app.
 */
export default function NativeGoogleAuth() {
  const [params] = useSearchParams();
  const acceptPrivacy = params.get("privacy") === "1";
  const turnstileToken = params.get("ts") || "";
  const dateOfBirth = (params.get("dob") || "").trim();
  const confirmAge18 = params.get("age") === "1";
  const hostRef = useRef(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    if (!CLIENT_ID) {
      setError("Google Sign-In is not configured on the website.");
      return undefined;
    }
    let cancelled = false;

    function finish(accessToken) {
      const deep = `${DEEP_LINK}?token=${encodeURIComponent(accessToken)}`;
      const intent =
        `intent://google-auth?token=${encodeURIComponent(accessToken)}` +
        `#Intent;scheme=barathx;package=com.baratx.app;end`;
      const isAndroid = /Android/i.test(navigator.userAgent || "");
      window.location.href = isAndroid ? intent : deep;
      // Fallback UI if the app doesn’t catch the deep link
      setTimeout(() => {
        if (!cancelled) {
          setBusy(false);
          setError("");
          setReady(true);
          const host = hostRef.current;
          if (host) {
            host.innerHTML = `<a href="${deep}" style="display:inline-block;background:#ff671f;color:#111;font-weight:700;text-decoration:none;padding:0.85rem 1.1rem;border-radius:999px;">Open BarathX app</a>`;
          }
        }
      }, 1200);
    }

    async function exchange(idToken) {
      setBusy(true);
      setError("");
      try {
        const res = await fetch(`${API_BASE}/auth/google`, {
          method: "POST",
          headers: { "Content-Type": "application/json", "X-BarathX-Client": "web" },
          body: JSON.stringify({
            id_token: idToken,
            accept_privacy: acceptPrivacy,
            ...(confirmAge18 ? { confirm_age_18: true } : {}),
            ...(dateOfBirth ? { date_of_birth: dateOfBirth } : {}),
            ...(turnstileToken ? { turnstile_token: turnstileToken } : {}),
          }),
        });
        const data = await res.json().catch(() => ({}));
        if (!res.ok) {
          throw new Error(data.detail || data.message || "Google sign-in failed");
        }
        if (!data.access_token) throw new Error("No access token returned");
        finish(data.access_token);
      } catch (err) {
        const msg = String(err?.message || err);
        setError(msg);
        setBusy(false);
        // Still notify the app so the browser sheet can close with context
        window.location.href = `${DEEP_LINK}?error=${encodeURIComponent(msg.slice(0, 180))}`;
      }
    }

    function renderButton() {
      if (cancelled || !window.google?.accounts?.id || !hostRef.current) return false;
      window.google.accounts.id.initialize({
        client_id: CLIENT_ID,
        callback: (res) => {
          if (res?.credential) exchange(res.credential);
        },
        ux_mode: "popup",
        auto_select: false,
        context: "signin",
      });
      hostRef.current.innerHTML = "";
      window.google.accounts.id.renderButton(hostRef.current, {
        theme: "outline",
        size: "large",
        shape: "pill",
        text: "continue_with",
        width: Math.min(320, hostRef.current.offsetWidth || 280),
      });
      setReady(true);
      return true;
    }

    function boot() {
      if (renderButton()) return;
      const t = window.setInterval(() => {
        if (renderButton()) window.clearInterval(t);
      }, 200);
      window.setTimeout(() => window.clearInterval(t), 8000);
    }

    if (window.google?.accounts?.id) boot();
    else {
      const existing = document.querySelector('script[src*="accounts.google.com/gsi/client"]');
      if (existing) {
        existing.addEventListener("load", boot);
      } else {
        const s = document.createElement("script");
        s.src = "https://accounts.google.com/gsi/client";
        s.async = true;
        s.onload = boot;
        document.head.appendChild(s);
      }
    }

    return () => {
      cancelled = true;
    };
  }, [acceptPrivacy, turnstileToken, dateOfBirth, confirmAge18]);

  return (
    <div className="page page-auth bx-native-google-auth">
      <main className="auth-card" style={{ margin: "3rem auto", maxWidth: 420 }}>
        <Logo variant="full" title="BarathX" />
        <h1 style={{ marginTop: "1rem" }}>Continue with Google</h1>
        <p className="hint">
          This browser window signs you into the BarathX app (bypasses Android Google re-auth issues).
        </p>
        {!acceptPrivacy ? (
          <p className="error">
            Go back to the app, accept <strong>Privacy &amp; Terms</strong>, then try Google again.
          </p>
        ) : null}
        {acceptPrivacy && (!confirmAge18 || !dateOfBirth) ? (
          <p className="error">
            Go back to the app, enter your <strong>date of birth</strong> and confirm you are 18+,
            then try Google again.
          </p>
        ) : null}
        <div ref={hostRef} className="google-btn-host" style={{ marginTop: "1.25rem", minHeight: 48 }} />
        {!ready && !error && <p className="hint">Loading Google…</p>}
        {busy && <p className="hint">Signing you in…</p>}
        {error && <p className="error">{error}</p>}
        <p className="hint" style={{ marginTop: "1.5rem" }}>
          <Link to="/privacy">Privacy</Link> · <Link to="/terms">Terms</Link> ·{" "}
          <Link to="/age-consent">Age consent</Link>
        </p>
      </main>
    </div>
  );
}
