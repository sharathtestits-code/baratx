/**
 * Scroll a compose target into view and focus it.
 * Prefer this over window.scrollTo({ top: 0 }) so right-rail / strip picks land on Drop a take.
 */
export function focusCompose(composeRef, options = {}) {
  const { block = "center", delay = 120 } = options;
  const node = composeRef?.current;
  const shell =
    (node && typeof node.closest === "function" && node.closest(".plaza-studio, .compose, form, #go-live")) ||
    document.querySelector("[data-coach='compose'], .plaza-studio.compose, #go-live, .arena-debate-form");

  shell?.scrollIntoView?.({ behavior: "smooth", block });

  window.setTimeout(() => {
    if (node && typeof node.focus === "function") {
      node.focus();
      return;
    }
    const fallback = shell?.querySelector?.("textarea, input:not([type='checkbox']):not([type='file'])");
    fallback?.focus?.();
  }, delay);
}
