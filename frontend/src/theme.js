/** BaratX appearance themes — applied via data-theme on <html>. */

export const THEME_STORAGE_KEY = "bx_theme";
export const THEME_CHOSEN_KEY = "bx_theme_chosen";

export const THEMES = [
  {
    id: "midnight",
    name: "Tri-Color Midnight",
    blurb: "Dark premium look — saffron, green & navy accents. Default.",
    swatch: ["#0D0D12", "#FF9933", "#138808", "#FFFFFF"],
  },
  {
    id: "saffron",
    name: "Saffron",
    blurb: "Warm light India-first look.",
    swatch: ["#faf8f5", "#ff671f", "#0f1419"],
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
/** Default: Tri-Color Midnight (dark). Users can change in the hamburger menu → Appearance. */
export const DEFAULT_THEME = "midnight";

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

const THEME_COLORS = {
  midnight: "#0D0D12",
  saffron: "#FF671F",
  monsoon: "#0d9488",
  ink: "#000080",
};

export function applyTheme(themeId) {
  const id = isValidTheme(themeId) ? themeId : DEFAULT_THEME;
  document.documentElement.setAttribute("data-theme", id);
  const meta = document.querySelector('meta[name="theme-color"]');
  if (meta) meta.setAttribute("content", THEME_COLORS[id] || THEME_COLORS.midnight);
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
