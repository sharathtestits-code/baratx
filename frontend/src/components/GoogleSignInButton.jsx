import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api, topicsApi } from "../api";
import { useAuth } from "../context/AuthContext";
import { isNativeApp } from "../native";
import { openBrowserGoogleSignIn } from "../nativeGoogleBrowserAuth";
import { hasSeenTopicOnboarding, markTopicOnboardingSeen } from "../topicsOnboarding";

const CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID || "";

/**
 * Google sign-in:
 * - Web: GIS renderButton (one account chooser)
 * - Native: one Custom Tabs session → barathx.com/native-google-auth (auto-starts Google)
 *   Skips Capgo Credential Manager so users are not asked to pick an account twice.
 */
export default function GoogleSignInButton({
  label = "Continue with Google",
  onError,
  acceptPrivacy = false,
  requirePrivacyConfirm = false,
  turnstileToken = "",
  requireTurnstile = false,
}) {
  const { login } = useAuth();
  const navigate = useNavigate();
  const wrapRef = useRef(null);
  const hostRef = useRef(null);
  const callbackRef = useRef(null);
  const consentRef = useRef({
    acceptPrivacy,
    requirePrivacyConfirm,
    turnstileToken,
    requireTurnstile,
  });
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [gisReady, setGisReady] = useState(false);
  const [browserHint, setBrowserHint] = useState("");
  const native = isNativeApp();

  consentRef.current = {
    acceptPrivacy,
    requirePrivacyConfirm,
    turnstileToken,
    requireTurnstile,
  };

  async function finishWithIdToken(idToken) {
    const {
      acceptPrivacy: privacyOk,
      requirePrivacyConfirm: needPrivacy,
      turnstileToken: tsToken,
      requireTurnstile: needTs,
    } = consentRef.current;
    if (needPrivacy && !privacyOk) {
      const msg = "Accept the Privacy Policy (DPDP) to create an account.";
      setError(msg);
      onError?.(msg);
      return;
    }
    if (needTs && !tsToken) {
      const msg = "Complete the security check, or sign up with phone OTP.";
      setError(msg);
      onError?.(msg);
      return;
    }
    setBusy(true);
    setError("");
    try {
      const data = await api.loginGoogle({
        id_token: idToken,
        ...(privacyOk ? { accept_privacy: true } : {}),
        ...(tsToken ? { turnstile_token: tsToken } : {}),
      });
      login(data.access_token);
      const next =
        typeof sessionStorage !== "undefined" ? sessionStorage.getItem("bx_next") : "";
      if (next && next.startsWith("/") && !next.startsWith("//")) {
        sessionStorage.removeItem("bx_next");
        navigate(next);
        return;
      }
      if (hasSeenTopicOnboarding()) {
        navigate("/home");
        return;
      }
      try {
        const mine = await topicsApi.mine(data.access_token);
        if (mine && mine.length > 0) {
          markTopicOnboardingSeen();
        }
      } catch {
        // Square guide still works without prior topics.
      }
      sessionStorage.setItem("bx_welcome", "1");
      navigate("/feed?welcome=1");
    } catch (err) {
      const msg = err.message || "Google sign-in failed";
      setError(msg);
      onError?.(msg);
    } finally {
      setBusy(false);
    }
  }

  callbackRef.current = async (response) => {
    if (!response?.credential) return;
    await finishWithIdToken(response.credential);
  };

  async function startBrowserGoogle() {
    const {
      acceptPrivacy: privacyOk,
      requirePrivacyConfirm: needPrivacy,
      turnstileToken: tsToken,
      requireTurnstile: needTs,
    } = consentRef.current;
    if (needPrivacy && !privacyOk) {
      const msg = "Accept the Privacy Policy (DPDP) to create an account.";
      setError(msg);
      onError?.(msg);
      return;
    }
    if (needTs && !tsToken) {
      const msg = "Complete the security check, or sign up with phone OTP.";
      setError(msg);
      onError?.(msg);
      return;
    }
    setBusy(true);
    setError("");
    setBrowserHint("Opening Google — pick your account once, then you’ll return to the app.");
    try {
      await openBrowserGoogleSignIn({
        acceptPrivacy: privacyOk,
        turnstileToken: tsToken,
      });
    } catch (err) {
      const msg = err?.message || "Could not open Google Sign-In.";
      setError(msg);
      onError?.(msg);
      setBrowserHint("");
    } finally {
      setBusy(false);
    }
  }

  useEffect(() => {
    function onBrowserAuthError(ev) {
      const msg = ev?.detail || "Google sign-in failed.";
      setError(String(msg));
      setBrowserHint("");
      onError?.(String(msg));
    }
    window.addEventListener("bx-google-auth-error", onBrowserAuthError);
    return () => window.removeEventListener("bx-google-auth-error", onBrowserAuthError);
  }, [onError]);

  useEffect(() => {
    if (!CLIENT_ID || native) return undefined;
    let cancelled = false;
    let resizeTimer = null;

    function render() {
      if (cancelled || !window.google?.accounts?.id || !hostRef.current || !wrapRef.current) {
        return false;
      }

      window.google.accounts.id.initialize({
        client_id: CLIENT_ID,
        callback: (res) => callbackRef.current?.(res),
        ux_mode: "popup",
        auto_select: false,
        cancel_on_tap_outside: true,
        context: "signin",
        use_fedcm_for_prompt: true,
      });

      try {
        window.google.accounts.id.cancel();
      } catch {
        // ignore
      }

      const width = Math.max(240, Math.floor(wrapRef.current.offsetWidth || 320));
      hostRef.current.innerHTML = "";
      window.google.accounts.id.renderButton(hostRef.current, {
        theme: "outline",
        size: "large",
        shape: "pill",
        text: "continue_with",
        width,
        logo_alignment: "left",
      });
      setGisReady(true);
      return true;
    }

    function waitAndRender() {
      if (render()) return;
      const id = window.setInterval(() => {
        if (render()) window.clearInterval(id);
      }, 200);
      window.setTimeout(() => window.clearInterval(id), 12000);
    }

    waitAndRender();

    function onResize() {
      window.clearTimeout(resizeTimer);
      resizeTimer = window.setTimeout(() => render(), 150);
    }
    window.addEventListener("resize", onResize);

    return () => {
      cancelled = true;
      window.clearTimeout(resizeTimer);
      window.removeEventListener("resize", onResize);
      try {
        window.google?.accounts?.id?.cancel();
      } catch {
        // ignore
      }
    };
  }, [native]);

  if (native) {
    const privacyBlocked = requirePrivacyConfirm && !acceptPrivacy;
    const turnstileBlocked = requireTurnstile && !turnstileToken;
    const blocked = privacyBlocked || turnstileBlocked;
    return (
      <div className="x-google-wrap">
        <button
          type="button"
          className="x-btn x-btn-google"
          disabled={busy || blocked}
          onClick={startBrowserGoogle}
        >
          <GoogleG className="x-btn-icon" />
          {busy ? "Opening Google…" : label}
        </button>
        {privacyBlocked && (
          <p className="hint x-google-loading">Accept the Privacy Policy above to continue with Google.</p>
        )}
        {turnstileBlocked && !privacyBlocked && (
          <p className="hint x-google-loading">Complete the security check above, or use phone OTP.</p>
        )}
        {!blocked && (
          <p className="hint x-google-loading">
            {browserHint || "One Google account pick — then you’re back in the app."}
          </p>
        )}
        {error && !onError && <p className="x-inline-error">{error}</p>}
      </div>
    );
  }

  if (!CLIENT_ID) {
    return (
      <div className="x-google-wrap">
        <button
          type="button"
          className="x-btn x-btn-google"
          onClick={() => {
            const msg = "Google sign-in is not configured yet. Add VITE_GOOGLE_CLIENT_ID.";
            setError(msg);
            onError?.(msg);
          }}
        >
          <GoogleG className="x-btn-icon" />
          {label}
        </button>
        {error && <p className="x-inline-error">{error}</p>}
      </div>
    );
  }

  const privacyBlocked = requirePrivacyConfirm && !acceptPrivacy;
  const turnstileBlocked = requireTurnstile && !turnstileToken;
  const blocked = privacyBlocked || turnstileBlocked;

  return (
    <div className={`x-google-wrap${blocked ? " is-age-blocked" : ""}`} ref={wrapRef}>
      <div
        className={`x-google-shell ${busy ? "is-busy" : ""} ${gisReady ? "is-ready" : ""}${
          blocked ? " is-age-blocked" : ""
        }`}
      >
        <div className="x-btn x-btn-google x-google-face" aria-hidden="true">
          <GoogleG className="x-btn-icon" />
          {busy ? "Signing in…" : label}
        </div>
        <div
          ref={hostRef}
          className="google-btn-host"
          title={
            privacyBlocked
              ? "Accept Privacy Policy first"
              : turnstileBlocked
                ? "Complete security check first"
                : label
          }
          aria-label={label}
          aria-disabled={blocked}
        />
      </div>
      {privacyBlocked && (
        <p className="hint x-google-loading">Accept the Privacy Policy above to continue with Google.</p>
      )}
      {turnstileBlocked && !privacyBlocked && (
        <p className="hint x-google-loading">Complete the security check above, or use phone OTP.</p>
      )}
      {!gisReady && !error && !blocked && <p className="hint x-google-loading">Loading Google…</p>}
      {error && !onError && <p className="x-inline-error">{error}</p>}
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
