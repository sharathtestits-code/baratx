/** BaratX appearance themes — applied via data-theme on <html>. */

export const THEME_STORAGE_KEY = "bx_theme";
export const THEME_CHOSEN_KEY = "bx_theme_chosen";

export const THEMES = [
  {
    id: "saffron",
    name: "Saffron",
    blurb: "Warm India-first look — the BaratX default.",
    swatch: ["#faf8f5", "#ff671f", "#0f1419"],
  },
  {
    id: "midnight",
    name: "Midnight",
    blurb: "Dark charcoal with saffron highlights.",
    swatch: ["#121216", "#ff7a3d", "#f4f4f5"],
  },
  {
    id: "monsoon",
    name: "Monsoon",
    blurb: "Cool mist and teal for a calmer feed.",
    swatch: ["#f3f6f8", "#0d9488", "#0f172a"],
  },
  {
    id: "ink",
    name: "Ink",
    blurb: "Clean paper with deep navy accents.",
    swatch: ["#ffffff", "#000080", "#0f1419"],
  },
];

export const THEME_IDS = THEMES.map((t) => t.id);
export const DEFAULT_THEME = "saffron";

export function isValidTheme(id) {
  return THEME_IDS.includes(id);
}

export function getStoredTheme() {
  try {
    const id = localStorage.getItem(THEME_STORAGE_KEY);
    return isValidTheme(id) ? id : DEFAULT_THEME;
  } catch {
    return DEFAULT_THEME;
  }
}

export function hasChosenTheme() {
  try {
    return localStorage.getItem(THEME_CHOSEN_KEY) === "1";
  } catch {
    return false;
  }
}

export function applyTheme(themeId) {
  const id = isValidTheme(themeId) ? themeId : DEFAULT_THEME;
  document.documentElement.setAttribute("data-theme", id);
  try {
    localStorage.setItem(THEME_STORAGE_KEY, id);
  } catch {
    // ignore quota / private mode
  }
  return id;
}

export function markThemeChosen() {
  try {
    localStorage.setItem(THEME_CHOSEN_KEY, "1");
  } catch {
    // ignore
  }
}

/** Call once at boot before React paints when possible. */
export function initThemeFromStorage() {
  return applyTheme(getStoredTheme());
}
