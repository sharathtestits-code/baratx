/**
 * App Store listing policy helpers (pure — no Capacitor).
 * Guideline 4.8: Google Sign-In on iOS requires Sign in with Apple.
 */

export function googleSignInAllowed(platform, appleReady) {
  if (platform !== "ios") return true;
  return Boolean(appleReady);
}
