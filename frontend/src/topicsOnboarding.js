/** Topic onboarding is one-time. Arenas tab is for ongoing picks. */

export const TOPICS_SEEN_KEY = "bx_topics_seen";

export function hasSeenTopicOnboarding() {
  try {
    return localStorage.getItem(TOPICS_SEEN_KEY) === "1";
  } catch {
    return false;
  }
}

export function markTopicOnboardingSeen() {
  try {
    localStorage.setItem(TOPICS_SEEN_KEY, "1");
    // Migrate old session flag so this browser tab stops looping.
    sessionStorage.setItem("bx_topics_done", "1");
  } catch {
    // ignore
  }
}
