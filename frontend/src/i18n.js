/**
 * Lightweight locale preference for BarathX.
 * Full UI strings for Hindi / Telugu are phased — see brand/product/I18N_HINDI_TELUGU.md.
 * Backend already accepts language: en | hi | te on the user profile.
 */

export const LOCALES = [
  { id: "en", label: "English", native: "English" },
  { id: "hi", label: "Hindi", native: "हिन्दी" },
  { id: "te", label: "Telugu", native: "తెలుగు" },
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
