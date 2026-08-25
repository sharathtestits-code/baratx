import { useEffect } from "react";
import { applyTheme, DEFAULT_THEME, hasChosenTheme, markThemeChosen } from "../theme";

/**
 * Theme picker lives in Settings → Appearance (signed-in only).
 * Outside always uses Midnight. First signed-in run keeps Midnight silently.
 */
export default function ThemeOnboarding() {
  useEffect(() => {
    if (hasChosenTheme()) return;
    applyTheme(DEFAULT_THEME);
    markThemeChosen();
  }, []);

  return null;
}
