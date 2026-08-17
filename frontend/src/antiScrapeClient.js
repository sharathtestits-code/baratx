/**
 * Client-side guards against automated browser scroll scrapers
 * (Puppeteer / Playwright / Selenium infinite-scrolling the feed).
 */

const LOAD_WINDOW_MS = 12_000;
const MAX_LOADS_IN_WINDOW = 8;

/** True when the page is driven by WebDriver / headless automation. */
export function isAutomatedBrowser() {
  if (typeof navigator === "undefined") return true;
  try {
    if (navigator.webdriver) return true;
    const ua = navigator.userAgent || "";
    if (/HeadlessChrome|PhantomJS|Selenium|Puppeteer|Playwright/i.test(ua)) return true;
    if (window.callPhantom || window._phantom || window.__nightmare) return true;
    if (window.domAutomation || window.domAutomationController) return true;
  } catch {
    return true;
  }
  return false;
}

/**
 * Sliding-window throttle for infinite-scroll loadMore.
 * Returns false when a bot is hammering the sentinel.
 */
export function allowScrollPageLoad(timestampsRef) {
  const now = Date.now();
  const recent = (timestampsRef.current || []).filter((t) => now - t < LOAD_WINDOW_MS);
  if (recent.length >= MAX_LOADS_IN_WINDOW) {
    timestampsRef.current = recent;
    return false;
  }
  recent.push(now);
  timestampsRef.current = recent;
  return true;
}
