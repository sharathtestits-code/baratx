/**
 * Lightweight locale preference for BarathX.
 * Full UI strings for Hindi / Telugu are phased — see brand/product/I18N_HINDI_TELUGU.md.
 * Backend already accepts language: en | hi | te on the user profile.
 *
 * Brand rule: BX logo mark + Latin "BarathX" wordmark stay in every locale.
 * Native lines are optional subtitles only — never replace the logo.
 */

export const LOCALES = [
  {
    id: "en",
    label: "English",
    native: "English",
    brandNative: "BarathX",
    tagline: "India's public square",
  },
  {
    id: "hi",
    label: "Hindi",
    native: "हिन्दी",
    brandNative: "बारथX",
    tagline: "भारत का सार्वजनिक चौक",
  },
  {
    id: "te",
    label: "Telugu",
    native: "తెలుగు",
    brandNative: "బరత్X",
    tagline: "భారత్ పబ్లిక్ స్క్వేర్",
  },
];

const STORAGE_KEY = "bx_lang";

export function getStoredLanguage(fallback = "en") {
  try {
    const v = localStorage.getItem(STORAGE_KEY);
    if (v === "en" || v === "hi" || v === "te") return v;
  } catch {
    /* ignore */
  }
  return fallback;
}

export function applyDocumentLanguage(lang) {
  const id = lang === "hi" || lang === "te" ? lang : "en";
  if (typeof document !== "undefined") {
    document.documentElement.lang = id;
  }
  try {
    localStorage.setItem(STORAGE_KEY, id);
  } catch {
    /* ignore */
  }
  return id;
}

export function localeMeta(id) {
  return LOCALES.find((l) => l.id === id) || LOCALES[0];
}
