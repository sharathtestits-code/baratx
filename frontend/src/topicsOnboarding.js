/** Topic onboarding is one-time. Arenas tab is for ongoing picks. */

export const TOPICS_SEEN_KEY = "bx_topics_seen";
const LEGACY_SESSION_KEY = "bx_topics_done";

export function hasSeenTopicOnboarding() {
  try {
    if (localStorage.getItem(TOPICS_SEEN_KEY) === "1") return true;
    // Older builds used sessionStorage — promote so login no longer loops.
    if (sessionStorage.getItem(LEGACY_SESSION_KEY) === "1") {
      localStorage.setItem(TOPICS_SEEN_KEY, "1");
      return true;
    }
    return false;
  } catch {
    return false;
  }
}

export function markTopicOnboardingSeen() {
  try {
    localStorage.setItem(TOPICS_SEEN_KEY, "1");
    sessionStorage.setItem(LEGACY_SESSION_KEY, "1");
  } catch {
    // ignore
  }
}
