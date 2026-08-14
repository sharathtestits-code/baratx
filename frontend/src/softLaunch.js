/** Soft launch window — Independence Day 15 August 2026. */

export const SOFT_LAUNCH_LINE =
  "Official soft launch · Independence Day · 15 August — join in your browser";

export const SOFT_LAUNCH_SHORT = "Soft launch · 15 August · join in browser";

export const APP_COMING_SOON_LINE = "iOS & Android apps coming soon";

/** In-product banner (Square): browser soft launch + apps soon. */
export const SOFT_LAUNCH_BANNER =
  "Soft launch · 15 August · browser now · iOS & Android apps coming soon";

/** Show soft-launch chrome through end of August 2026 IST. */
export function isSoftLaunchWindow() {
  try {
    return Date.now() < Date.parse("2026-09-01T00:00:00+05:30");
  } catch {
    return true;
  }
}
