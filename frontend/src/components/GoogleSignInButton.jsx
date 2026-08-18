import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api, topicsApi } from "../api";
import { useAuth } from "../context/AuthContext";
import { isNativeApp } from "../native";
import {
  friendlyNativeGoogleError,
  nativeGoogleConfigured,
  nativeGoogleIdToken,
} from "../nativeGoogleAuth";
import { openBrowserGoogleSignIn } from "../nativeGoogleBrowserAuth";
import { hasSeenTopicOnboarding, markTopicOnboardingSeen } from "../topicsOnboarding";

const CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID || "";

/**
 * Google sign-in:
 * - Web: GIS renderButton (popup account chooser)
 * - Native Capacitor: @capgo/capacitor-social-login → ID token → /auth/google
 * - Native fallback: system browser → barathx.com/native-google-auth → deep link JWT
 */
export default function GoogleSignInButton({
  label = "Continue with Google",
  onError,
  confirmAge18 = false,
  requireAgeConfirm = false,
  acceptPrivacy = false,
  requirePrivacyConfirm = false,
}) {
  const { login } = useAuth();
  const navigate = useNavigate();
  const wrapRef = useRef(null);
  const hostRef = useRef(null);
  const callbackRef = useRef(null);
  const ageRef = useRef({ confirmAge18, requireAgeConfirm, acceptPrivacy, requirePrivacyConfirm });
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [gisReady, setGisReady] = useState(false);
  const [browserHint, setBrowserHint] = useState("");
  const native = isNativeApp();

  ageRef.current = { confirmAge18, requireAgeConfirm, acceptPrivacy, requirePrivacyConfirm };

  async function finishWithIdToken(idToken) {
    const {
      confirmAge18: ageOk,
      requireAgeConfirm: needAge,
      acceptPrivacy: privacyOk,
      requirePrivacyConfirm: needPrivacy,
    } = ageRef.current;
    if (needAge && !ageOk) {
      const msg = "You must be 18 or older to join BarathX. Confirm your age to continue.";
      setError(msg);
      onError?.(msg);
      return;
    }
    if (needPrivacy && !privacyOk) {
      const msg = "Accept the Privacy Policy (DPDP) to create an account.";
      setError(msg);
      onError?.(msg);
      return;
    }
    setBusy(true);
    setError("");
    try {
      const data = await api.loginGoogle({
        id_token: idToken,
        ...(ageOk ? { confirm_age_18: true } : {}),
        ...(privacyOk ? { accept_privacy: true } : {}),
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
      confirmAge18: ageOk,
      requireAgeConfirm: needAge,
      acceptPrivacy: privacyOk,
      requirePrivacyConfirm: needPrivacy,
    } = ageRef.current;
    if (needAge && !ageOk) {
      const msg = "You must be 18 or older to join BarathX. Confirm your age to continue.";
      setError(msg);
      onError?.(msg);
      return;
    }
    if (needPrivacy && !privacyOk) {
      const msg = "Accept the Privacy Policy (DPDP) to create an account.";
      setError(msg);
      onError?.(msg);
      return;
    }
    setBusy(true);
    setError("");
    setBrowserHint("Opening Google in your browser… Sign in there, then you’ll return to the app.");
    try {
      await openBrowserGoogleSignIn({ confirmAge18: ageOk, acceptPrivacy: privacyOk });
    } catch (err) {
      const msg = err?.message || "Could not open browser for Google Sign-In.";
      setError(msg);
      onError?.(msg);
      setBrowserHint("");
    } finally {
      setBusy(false);
    }
  }

  async function handleNativeGoogle() {
    const {
      confirmAge18: ageOk,
      requireAgeConfirm: needAge,
      acceptPrivacy: privacyOk,
      requirePrivacyConfirm: needPrivacy,
    } = ageRef.current;
    if (needAge && !ageOk) {
      const msg = "You must be 18 or older to join BarathX. Confirm your age to continue.";
      setError(msg);
      onError?.(msg);
      return;
    }
    if (needPrivacy && !privacyOk) {
      const msg = "Accept the Privacy Policy (DPDP) to create an account.";
      setError(msg);
      onError?.(msg);
      return;
    }
    if (!nativeGoogleConfigured()) {
      const msg =
        "Native Google isn’t fully set up on this build. Tap “Continue with Google in browser” below, or use phone OTP.";
      setError(msg);
      setBrowserHint(msg);
      onError?.(msg);
      return;
    }
    setBusy(true);
    setError("");
    setBrowserHint("");
    try {
      const idToken = await nativeGoogleIdToken();
      setBusy(false);
      await finishWithIdToken(idToken);
    } catch (err) {
      const msg = friendlyNativeGoogleError(err);
      // Error 16 / re-auth: do NOT auto-open the browser (feels broken).
      // User taps “Continue with Google in browser” when ready.
      if (err?.code === "16" || /couldn't re-auth|Play App Signing SHA-1/i.test(msg)) {
        setBusy(false);
        const hint =
          "Native Google failed on this Play build. Tap “Continue with Google in browser” below — sign in there, then you’ll return to the app.";
        setError(hint);
        setBrowserHint(hint);
        onError?.(hint);
        return;
      }
      setError(msg);
      onError?.(msg);
      setBusy(false);
    }
  }

  useEffect(() => {
    function onBrowserAuthError(ev) {
      const msg = ev?.detail || "Google sign-in failed in browser.";
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
        // popup is more reliable than redirect on iOS Safari / in-app browsers
        ux_mode: "popup",
        auto_select: false,
        cancel_on_tap_outside: true,
        context: "signin",
        // Prefer FedCM where available; falls back when unsupported.
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
    const ageBlocked = requireAgeConfirm && !confirmAge18;
    const privacyBlocked = requirePrivacyConfirm && !acceptPrivacy;
    const blocked = ageBlocked || privacyBlocked;
    return (
      <div className="x-google-wrap">
        <button
          type="button"
          className="x-btn x-btn-google"
          disabled={busy || blocked}
          onClick={handleNativeGoogle}
        >
          <GoogleG className="x-btn-icon" />
          {busy ? "Signing in…" : label}
        </button>
        <button
          type="button"
          className="x-btn x-btn-outline"
          style={{ marginTop: "0.65rem" }}
          disabled={busy || blocked}
          onClick={startBrowserGoogle}
        >
          {busy ? "Opening browser…" : "Continue with Google in browser"}
        </button>
        {ageBlocked && (
          <p className="hint x-google-loading">Confirm you are 18+ above to continue with Google.</p>
        )}
        {privacyBlocked && !ageBlocked && (
          <p className="hint x-google-loading">Accept the Privacy Policy above to continue with Google.</p>
        )}
        {!blocked && (
          <p className="hint x-google-loading">
            {browserHint ||
              "If Google fails on this Play build, use “in browser” above — or phone OTP."}
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

  const ageBlocked = requireAgeConfirm && !confirmAge18;
  const privacyBlocked = requirePrivacyConfirm && !acceptPrivacy;
  const blocked = ageBlocked || privacyBlocked;

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
            ageBlocked
              ? "Confirm you are 18+ first"
              : privacyBlocked
                ? "Accept Privacy Policy first"
                : label
          }
          aria-label={label}
          aria-disabled={blocked}
        />
      </div>
      {ageBlocked && (
        <p className="hint x-google-loading">Confirm you are 18+ above to continue with Google.</p>
      )}
      {privacyBlocked && !ageBlocked && (
        <p className="hint x-google-loading">Accept the Privacy Policy above to continue with Google.</p>
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
