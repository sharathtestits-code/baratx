import { useEffect } from "react";
import { applyTheme, getStoredTheme, hasChosenTheme, markThemeChosen } from "../theme";

/**
 * Theme picker lives in Settings → Appearance.
 * On first run we keep Tri-Color Midnight silently (no modal stack).
 */
export default function ThemeOnboarding() {
  useEffect(() => {
    if (hasChosenTheme()) return;
    applyTheme(getStoredTheme());
    markThemeChosen();
  }, []);

  return null;
}
