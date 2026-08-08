import { useEffect, useState } from "react";
import { api } from "../api";
import { useAuth } from "../context/AuthContext";
import ThemePicker from "./ThemePicker";
import { applyTheme, getStoredTheme, hasChosenTheme, markThemeChosen } from "../theme";

/**
 * First-run appearance chooser. Shows once per browser until the user picks or skips.
 * Choice is saved locally and to the account when logged in; editable later in Settings.
 */
export default function ThemeOnboarding() {
  const { token, user, updateUser } = useAuth();
  const [open, setOpen] = useState(false);
  const [theme, setTheme] = useState(getStoredTheme);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (!token || !user) {
      setOpen(false);
      return;
    }
    if (user.theme) {
      applyTheme(user.theme);
      setTheme(user.theme);
    }
    setOpen(!hasChosenTheme());
  }, [token, user]);

  if (!open) return null;

  async function persist(id) {
    setSaving(true);
    try {
      applyTheme(id);
      markThemeChosen();
      if (token) {
        const updated = await api.updateMe(token, { theme: id });
        updateUser(updated);
      }
      setOpen(false);
    } catch {
      markThemeChosen();
      setOpen(false);
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="theme-onboard-backdrop" role="presentation">
      <div
        className="theme-onboard-card"
        role="dialog"
        aria-modal="true"
        aria-labelledby="theme-onboard-title"
      >
        <h2 id="theme-onboard-title">Choose your look</h2>
        <p className="hint">Pick a theme for BharatX. Change it anytime in Settings → Appearance.</p>
        <ThemePicker
          value={theme}
          onChange={(id) => {
            setTheme(id);
            applyTheme(id);
          }}
        />
        <div className="theme-onboard-actions">
          <button type="button" className="btn btn-ghost" onClick={() => persist(theme)} disabled={saving}>
            Skip for now
          </button>
          <button
            type="button"
            className="btn btn-primary"
            onClick={() => persist(theme)}
            disabled={saving}
          >
            {saving ? "Saving…" : "Continue"}
          </button>
        </div>
      </div>
    </div>
  );
}
