/**
 * Browser-based Google Sign-In for the native app.
 * Bypasses Android Credential Manager SHA-1 issues by using the working Web OAuth client.
 *
 * Flow: app opens https://barathx.com/native-google-auth → GIS → API → barathx://google-auth?token=
 */
import { Browser } from "@capacitor/browser";
import { App } from "@capacitor/app";
import { isNativeApp } from "./native";

const PUBLIC_URL = (import.meta.env.VITE_PUBLIC_URL || "https://barathx.com").replace(/\/$/, "");
const DEEP_LINK_SCHEME = "barathx";

export function nativeGoogleDeepLinkPrefix() {
  return `${DEEP_LINK_SCHEME}://google-auth`;
}

export function buildNativeGoogleAuthUrl({
  confirmAge18 = false,
  acceptPrivacy = false,
} = {}) {
  const u = new URL(`${PUBLIC_URL}/native-google-auth`);
  if (confirmAge18) u.searchParams.set("age", "1");
  if (acceptPrivacy) u.searchParams.set("privacy", "1");
  u.searchParams.set("src", "app");
  return u.toString();
}

export async function openBrowserGoogleSignIn({
  confirmAge18 = false,
  acceptPrivacy = false,
} = {}) {
  if (!isNativeApp()) {
    throw new Error("Browser Google Sign-In is only for the app.");
  }
  const url = buildNativeGoogleAuthUrl({ confirmAge18, acceptPrivacy });
  await Browser.open({ url, presentationStyle: "popover" });
}

export function parseGoogleAuthDeepLink(url) {
  if (!url || typeof url !== "string") return null;
  if (!url.startsWith(`${DEEP_LINK_SCHEME}://google-auth`)) return null;
  try {
    const parsed = new URL(url.replace(`${DEEP_LINK_SCHEME}://`, "https://dummy/"));
    const token =
      parsed.searchParams.get("token") ||
      parsed.searchParams.get("access_token") ||
      "";
    const err = parsed.searchParams.get("error") || "";
    return { token: token.trim(), error: err.trim() };
  } catch {
    return null;
  }
}

/** Listen once for barathx://google-auth deep links; returns unsubscribe. */
export function listenForNativeGoogleAuth({ onToken, onError }) {
  if (!isNativeApp()) return () => {};

  const handle = async (event) => {
    const parsed = parseGoogleAuthDeepLink(event?.url || "");
    if (!parsed) return;
    try {
      await Browser.close();
    } catch {
      // ignore
    }
    if (parsed.error) {
      onError?.(parsed.error);
      return;
    }
    if (parsed.token) {
      onToken?.(parsed.token);
    }
  };

  let sub = null;
  App.addListener("appUrlOpen", handle).then((handleRef) => {
    sub = handleRef;
  });

  return () => {
    try {
      sub?.remove?.();
    } catch {
      // ignore
    }
  };
}
