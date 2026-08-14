/**
 * Native Google Sign-In via @capgo/capacitor-social-login (Capacitor 8).
 * Web continues to use Google Identity Services in GoogleSignInButton.
 *
 * Required Google Cloud clients (same project):
 * - Web application → VITE_GOOGLE_CLIENT_ID (also GOOGLE_CLIENT_ID on API)
 * - Android (package com.baratx.app + SHA-1) — console only, not passed to JS
 * - iOS (bundle com.baratx.app) → VITE_GOOGLE_IOS_CLIENT_ID + Info.plist URL scheme
 */
import { SocialLogin } from "@capgo/capacitor-social-login";
import { getNativePlatform, isNativeApp } from "./native";

const WEB_CLIENT_ID = (import.meta.env.VITE_GOOGLE_CLIENT_ID || "").trim();
const IOS_CLIENT_ID = (import.meta.env.VITE_GOOGLE_IOS_CLIENT_ID || "").trim();

let initPromise = null;

export function nativeGoogleConfigured() {
  if (!isNativeApp()) return false;
  if (!WEB_CLIENT_ID) return false;
  if (getNativePlatform() === "ios" && !IOS_CLIENT_ID) return false;
  return true;
}

export async function ensureNativeGoogleReady() {
  if (!isNativeApp()) {
    throw new Error("Native Google Sign-In is only available in the app.");
  }
  if (!WEB_CLIENT_ID) {
    throw new Error("Google Sign-In is not configured. Missing VITE_GOOGLE_CLIENT_ID.");
  }
  const platform = getNativePlatform();
  if (platform === "ios" && !IOS_CLIENT_ID) {
    throw new Error(
      "Google Sign-In on iOS needs VITE_GOOGLE_IOS_CLIENT_ID (and the reversed URL scheme in Info.plist). Use phone OTP for now, or finish MOBILE.md setup."
    );
  }

  if (!initPromise) {
    initPromise = SocialLogin.initialize({
      google: {
        webClientId: WEB_CLIENT_ID,
        mode: "online",
        ...(IOS_CLIENT_ID
          ? {
              iOSClientId: IOS_CLIENT_ID,
              // So ID token `aud` matches API GOOGLE_CLIENT_ID (web client).
              iOSServerClientId: WEB_CLIENT_ID,
            }
          : {}),
      },
    }).catch((err) => {
      initPromise = null;
      throw err;
    });
  }
  await initPromise;
}

/**
 * @returns {Promise<string>} Google ID token for POST /auth/google
 */
export async function nativeGoogleIdToken() {
  await ensureNativeGoogleReady();
  const res = await SocialLogin.login({
    provider: "google",
    options: {
      scopes: ["email", "profile", "openid"],
      style: "bottom",
      filterByAuthorizedAccounts: false,
    },
  });

  const idToken = res?.result?.idToken || null;
  if (!idToken) {
    throw new Error("Google did not return an ID token. Try again or use phone OTP.");
  }
  return idToken;
}

export function friendlyNativeGoogleError(err) {
  const raw = String(err?.message || err || "");
  const code = err?.code || "";
  if (code === "USER_CANCELLED" || /cancel/i.test(raw)) {
    return "Google sign-in was cancelled.";
  }
  if (/28444|Developer console is not set up|console is not set up/i.test(raw)) {
    return "Google Sign-In needs Android OAuth setup: add package com.baratx.app + this build’s SHA-1 in Google Cloud (see MOBILE.md). Phone OTP still works.";
  }
  if (/16|Account reauth failed/i.test(raw)) {
    return "Google couldn’t re-auth that account. Try another Google account, or use phone OTP.";
  }
  if (/VITE_GOOGLE_IOS_CLIENT_ID|iOS needs/i.test(raw)) {
    return raw;
  }
  return raw || "Google sign-in failed";
}
