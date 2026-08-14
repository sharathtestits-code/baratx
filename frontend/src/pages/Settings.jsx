import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api, socialApi } from "../api";
import { useAuth } from "../context/AuthContext";
import Avatar from "../components/Avatar";
import Logo from "../components/Logo";
import ThemePicker from "../components/ThemePicker";
import { applyTheme, getStoredTheme, markThemeChosen } from "../theme";
import { LOCALES, applyDocumentLanguage, getStoredLanguage, localeMeta } from "../i18n";
import { mvpLabel } from "../mvpVersion";

export default function Settings() {
  const { user, token, logout, updateUser } = useAuth();
  const navigate = useNavigate();
  const [error, setError] = useState("");
  const [msg, setMsg] = useState("");
  const [theme, setTheme] = useState(() => user?.theme || getStoredTheme());
  const [themeSaving, setThemeSaving] = useState(false);
  const [language, setLanguage] = useState(() => user?.language || getStoredLanguage());
  const [languageSaving, setLanguageSaving] = useState(false);
  const [mutes, setMutes] = useState([]);
  const [blocks, setBlocks] = useState([]);
  const [listsLoading, setListsLoading] = useState(true);

  const selectedLocale = localeMeta(language);

  useEffect(() => {
    if (user?.theme) setTheme(user.theme);
  }, [user?.theme]);

  useEffect(() => {
    if (user?.language) {
      setLanguage(user.language);
      applyDocumentLanguage(user.language);
    }
  }, [user?.language]);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      setListsLoading(true);
      try {
        const [m, b] = await Promise.all([
          socialApi.listMutes(token),
          socialApi.listBlocks(token),
        ]);
        if (!cancelled) {
          setMutes(m);
          setBlocks(b);
        }
      } catch (err) {
        if (!cancelled) setError(err.message);
      } finally {
        if (!cancelled) setListsLoading(false);
      }
    }
    load();
    return () => {
      cancelled = true;
    };
  }, [token]);

  async function saveTheme(nextId) {
    setTheme(nextId);
    applyTheme(nextId);
    setThemeSaving(true);
    setMsg("");
    setError("");
    try {
      const updated = await api.updateMe(token, { theme: nextId });
      updateUser(updated);
      markThemeChosen();
      setMsg("Appearance saved.");
    } catch (err) {
      setError(err.message);
    } finally {
      setThemeSaving(false);
    }
  }

  async function saveLanguage(nextId) {
    if (!nextId || nextId === language) return;
    setLanguage(nextId);
    applyDocumentLanguage(nextId);
    setLanguageSaving(true);
    setMsg("");
    setError("");
    try {
      const updated = await api.updateMe(token, { language: nextId });
      updateUser(updated);
      setMsg(
        nextId === "en"
          ? "Language saved. English UI is active."
          : "Language preference saved. Full Hindi/Telugu UI chrome is coming next — English remains until then."
      );
    } catch (err) {
      setError(err.message);
    } finally {
      setLanguageSaving(false);
    }
  }

  async function unmute(username) {
    try {
      await socialApi.unmute(token, username);
      setMutes((prev) => prev.filter((u) => u.username !== username));
    } catch (err) {
      setError(err.message);
    }
  }

  async function unblock(username) {
    try {
      await socialApi.unblock(token, username);
      setBlocks((prev) => prev.filter((u) => u.username !== username));
    } catch (err) {
      setError(err.message);
    }
  }

  function handleLogout() {
    logout();
    navigate("/");
  }

  return (
    <div className="feed-wrap surface-page plaza-page">
      <div className="feed-header">
        <h1>Settings and privacy</h1>
      </div>

      {error && <div className="error">{error}</div>}
      {msg && <p className="hint ok-hint">{msg}</p>}

      <section className="settings-section">
        <h2>Appearance</h2>
        <p className="hint">
          Default is Tri-Color Midnight (dark). Switch to Saffron, Monsoon, or Ink anytime.
        </p>
        <ThemePicker value={theme} onChange={saveTheme} compact />
        {themeSaving && <p className="hint">Saving…</p>}
      </section>

      <section className="settings-section settings-language">
        <div className="settings-lang-brand" aria-label="BarathX">
          <Logo variant="full" className="settings-lang-logo" />
          <p className="settings-lang-brand-native" lang={selectedLocale.id}>
            {selectedLocale.brandNative}
            {selectedLocale.id !== "en" ? ` · ${selectedLocale.tagline}` : ` · ${selectedLocale.tagline}`}
          </p>
        </div>
        <h2>Language</h2>
        <p className="hint">
          English is the default. Hindi and Telugu preferences are saved to your account now; full
          translated UI ships in a later update. The BarathX logo stays the same in every language.
        </p>
        <div className="settings-lang-grid" role="radiogroup" aria-label="Language">
          {LOCALES.map((loc) => (
            <button
              key={loc.id}
              type="button"
              role="radio"
              aria-checked={language === loc.id}
              className={`settings-lang-option${language === loc.id ? " is-active" : ""}`}
              disabled={languageSaving}
              onClick={() => saveLanguage(loc.id)}
            >
              <span className="settings-lang-option-logo" aria-hidden="true">
                <Logo variant="mark" />
              </span>
              <span className="settings-lang-native">{loc.native}</span>
              <span className="hint">{loc.label}</span>
              {language === loc.id ? (
                <span className="settings-lang-selected-brand" lang={loc.id}>
                  BarathX
                  {loc.id !== "en" ? ` · ${loc.brandNative}` : ""}
                </span>
              ) : null}
            </button>
          ))}
        </div>
        {languageSaving && <p className="hint">Saving…</p>}
      </section>

      <section className="settings-section">
        <h2>Profile</h2>
        <p className="hint">Update your display name, username, bio, and photos.</p>
        <Link className="btn btn-secondary" to={`/u/${user?.username}`}>
          Edit profile
        </Link>
      </section>

      <section className="settings-section">
        <h2>Muted accounts</h2>
        {listsLoading ? (
          <p className="hint">Loading…</p>
        ) : mutes.length === 0 ? (
          <p className="hint">You haven’t muted anyone.</p>
        ) : (
          <ul className="settings-user-list">
            {mutes.map((u) => (
              <li key={u.id} className="settings-user-row">
                <Link to={`/u/${u.username}`} className="settings-user-link">
                  <Avatar name={u.display_name} username={u.username} url={u.avatar_url} size={36} />
                  <span>
                    <strong>{u.display_name}</strong>
                    <span className="hint">@{u.username}</span>
                  </span>
                </Link>
                <button type="button" className="btn btn-ghost" onClick={() => unmute(u.username)}>
                  Unmute
                </button>
              </li>
            ))}
          </ul>
        )}
      </section>

      <section className="settings-section">
        <h2>Blocked accounts</h2>
        {listsLoading ? (
          <p className="hint">Loading…</p>
        ) : blocks.length === 0 ? (
          <p className="hint">You haven’t blocked anyone.</p>
        ) : (
          <ul className="settings-user-list">
            {blocks.map((u) => (
              <li key={u.id} className="settings-user-row">
                <Link to={`/u/${u.username}`} className="settings-user-link">
                  <Avatar name={u.display_name} username={u.username} url={u.avatar_url} size={36} />
                  <span>
                    <strong>{u.display_name}</strong>
                    <span className="hint">@{u.username}</span>
                  </span>
                </Link>
                <button type="button" className="btn btn-ghost" onClick={() => unblock(u.username)}>
                  Unblock
                </button>
              </li>
            ))}
          </ul>
        )}
      </section>

      <section className="settings-section">
        <h2>Badges</h2>
        <ul className="settings-badge-legend">
          <li>
            <strong className="badge-name badge-blue">Blue official</strong> — BarathX staff / platform
            accounts.
          </li>
          <li>
            <strong className="badge-name badge-gold">Gold BarathX</strong> — BarathX brand voices (topic
            accounts), not personal verification.
          </li>
        </ul>
        <Link className="btn btn-secondary" to="/guidelines">
          Community guidelines
        </Link>
      </section>

      <section className="settings-section">
        <h2>Founding 100</h2>
        <p className="hint">
          100 Founding spots, earned by opening a debate that gets real engagement, not by signing
          up.
        </p>
        <Link className="btn btn-secondary" to="/rewards">
          View rewards
        </Link>
      </section>

      <section className="settings-section">
        <h2>Account</h2>
        <button type="button" className="btn btn-secondary" onClick={handleLogout}>
          Log out
        </button>
      </section>

      <p className="hint settings-mvp-label" aria-label="App version">
        BarathX {mvpLabel()}
      </p>
    </div>
  );
}
