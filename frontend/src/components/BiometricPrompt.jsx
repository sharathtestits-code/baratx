import { useEffect, useState } from "react";
import { useAuth } from "../context/AuthContext";
import { isNativeApp } from "../native";
import {
  isBiometricAvailable,
  isBiometricEnabled,
  enableBiometric,
  hasSavedCredentials,
  biometricLogin,
} from "../biometricAuth";

const DISMISS_KEY = "bx_bio_prompt_dismissed";

/**
 * After login on native, offer to enable Face ID / Touch ID.
 * Shows once per device unless the user dismisses it.
 */
export function BiometricEnablePrompt() {
  const { user, token } = useAuth();
  const [show, setShow] = useState(false);
  const [bio, setBio] = useState(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    if (!isNativeApp() || !token || !user) return;
    if (isBiometricEnabled()) return;
    if (sessionStorage.getItem(DISMISS_KEY)) return;
    isBiometricAvailable().then((result) => {
      if (result.available) {
        setBio(result);
        setShow(true);
      }
    });
  }, [token, user]);

  if (!show || !bio) return null;

  async function handleEnable() {
    setBusy(true);
    try {
      await enableBiometric(token, user?.username);
      setShow(false);
    } catch {
      setShow(false);
    } finally {
      setBusy(false);
    }
  }

  function handleDismiss() {
    sessionStorage.setItem(DISMISS_KEY, "1");
    setShow(false);
  }

  return (
    <div className="bx-bio-prompt" role="dialog" aria-label="Enable biometric unlock">
      <div className="bx-bio-prompt-card">
        <p className="bx-bio-prompt-title">
          Enable {bio.label}?
        </p>
        <p className="bx-bio-prompt-body">
          Unlock BarathX with {bio.label} next time instead of typing your password.
        </p>
        <div className="bx-bio-prompt-actions">
          <button
            type="button"
            className="btn btn-primary"
            disabled={busy}
            onClick={handleEnable}
          >
            {busy ? "Verifying…" : `Enable ${bio.label}`}
          </button>
          <button
            type="button"
            className="btn btn-ghost"
            onClick={handleDismiss}
          >
            Not now
          </button>
        </div>
      </div>
    </div>
  );
}

/**
 * On app open (native), if biometric is enabled, auto-login with stored token.
 * Call this as a hook in the top-level App before showing the login screen.
 */
export function useBiometricAutoLogin() {
  const { token, login } = useAuth();
  const [tried, setTried] = useState(false);

  useEffect(() => {
    if (tried || token) return;
    if (!isNativeApp() || !isBiometricEnabled()) {
      setTried(true);
      return;
    }
    let cancelled = false;
    hasSavedCredentials().then((has) => {
      if (cancelled || !has) {
        setTried(true);
        return;
      }
      biometricLogin()
        .then((savedToken) => {
          if (!cancelled && savedToken) login(savedToken);
        })
        .catch(() => {})
        .finally(() => {
          if (!cancelled) setTried(true);
        });
    });
    return () => { cancelled = true; };
  }, [token, tried, login]);

  return tried;
}
