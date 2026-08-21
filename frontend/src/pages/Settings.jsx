import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api, socialApi } from "../api";
import { useAuth } from "../context/AuthContext";
import { useLocale } from "../context/LocaleContext";
import Avatar from "../components/Avatar";
import Logo from "../components/Logo";
import ThemePicker from "../components/ThemePicker";
import { applyTheme, getStoredTheme, markThemeChosen } from "../theme";
import { LOCALES, getStoredLanguage, localeMeta } from "../i18n";
import { mvpLabel } from "../mvpVersion";

export default function Settings() {
  const { user, token, logout, revokeAllSessions, updateUser } = useAuth();
  const { language: localeLang, setLanguage: setLocaleLanguage, t } = useLocale();
  const navigate = useNavigate();
  const [error, setError] = useState("");
  const [msg, setMsg] = useState("");
  const [theme, setTheme] = useState(() => user?.theme || getStoredTheme());
  const [themeSaving, setThemeSaving] = useState(false);
  const [language, setLanguage] = useState(() => user?.language || localeLang || getStoredLanguage());
  const [languageSaving, setLanguageSaving] = useState(false);
  const [emailActivity, setEmailActivity] = useState(() => user?.email_activity_enabled !== false);
  const [emailSaving, setEmailSaving] = useState(false);
  const [exportBusy, setExportBusy] = useState(false);
  const [deleteConfirm, setDeleteConfirm] = useState("");
  const [deleting, setDeleting] = useState(false);
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
      setLocaleLanguage(user.language);
    }
  }, [user?.language, setLocaleLanguage]);

  useEffect(() => {
    if (user && typeof user.email_activity_enabled === "boolean") {
      setEmailActivity(user.email_activity_enabled);
    }
  }, [user?.email_activity_enabled]);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      if (!token) {
        setListsLoading(false);
        setMutes([]);
        setBlocks([]);
        return;
      }
      setListsLoading(true);
      try {
        const [m, b] = await Promise.all([
          socialApi.listMutes(token),
          socialApi.listBlocks(token),
        ]);
        if (!cancelled) {
          setMutes(Array.isArray(m) ? m : []);
          setBlocks(Array.isArray(b) ? b : []);
        }
      } catch (err) {
        if (!cancelled) setError(err.message || "Could not load mutes/blocks.");
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
      setMsg(t("settings.appearanceSaved"));
    } catch (err) {
      setError(err.message);
    } finally {
      setThemeSaving(false);
    }
  }

  async function saveLanguage(nextId) {
    if (!nextId || nextId === language) return;
    setLanguage(nextId);
    setLocaleLanguage(nextId);
    setLanguageSaving(true);
    setMsg("");
    setError("");
    try {
      const updated = await api.updateMe(token, { language: nextId });
      updateUser(updated);
      setMsg(translateSaved(nextId));
    } catch (err) {
      setError(err.message);
    } finally {
      setLanguageSaving(false);
    }
  }

  function translateSaved(nextId) {
    // Use the newly selected language for the confirmation itself.
    if (nextId === "hi") return "भाषा सेव हो गई। इंटरफ़ेस अपडेट हो गया।";
    if (nextId === "te") return "భాష సేవ్ అయింది. UI అప్‌డేట్ అయింది.";
    return "Language saved. UI updated.";
  }

  async function saveEmailActivity(next) {
    setEmailActivity(next);
    setEmailSaving(true);
    setMsg("");
    setError("");
    try {
      const updated = await api.updateMe(token, { email_activity_enabled: next });
      updateUser(updated);
      setMsg(
        next
          ? "Activity emails on, you’ll get one email per notification."
          : "Unsubscribed from activity emails. In-app Alerts still work."
      );
    } catch (err) {
      setEmailActivity(!next);
      setError(err.message);
    } finally {
      setEmailSaving(false);
    }
  }

  async function deleteAccount() {
    if (deleteConfirm.trim().toUpperCase() !== "DELETE") {
      setError("Type DELETE to confirm account deletion");
      return;
    }
    setDeleting(true);
    setError("");
    setMsg("");
    try {
      await api.deleteMe(token);
      logout();
      navigate("/");
    } catch (err) {
      setError(err.message);
    } finally {
      setDeleting(false);
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

  async function handleExportData() {
    setExportBusy(true);
    setError("");
    try {
      const data = await api.exportMyData(token);
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `barathx-data-export-${new Date().toISOString().slice(0, 10)}.json`;
      a.click();
      URL.revokeObjectURL(url);
      setMsg("Download started. That’s a copy of personal data we hold (DPDP right to access).");
    } catch (err) {
      setError(err.message || "Could not export your data.");
    } finally {
      setExportBusy(false);
    }
  }

  async function handleLogout() {
    await logout();
    navigate("/");
  }

  async function handleRevokeAll() {
    if (
      !window.confirm(
        "Sign out every device and browser that has your BarathX account? You’ll need to log in again here too."
      )
    ) {
      return;
    }
    try {
      await revokeAllSessions();
      navigate("/");
    } catch (err) {
      setError(err.message || "Could not sign out all sessions.");
    }
  }

  return (
    <div className="feed-wrap surface-page plaza-page settings-page">
      <div className="feed-header settings-header">
        <button
          type="button"
          className="settings-back"
          onClick={() => {
            if (window.history.length > 1) navigate(-1);
            else navigate("/home");
          }}
          aria-label="Back"
        >
          ← Back
        </button>
        <h1>{t("settings.title")}</h1>
        <span className="settings-header-spacer" aria-hidden="true" />
      </div>

      {error && <div className="error">{error}</div>}
      {msg && <p className="hint ok-hint">{msg}</p>}

      <section className="settings-section">
        <h2>{t("settings.appearance")}</h2>
        <p className="hint">{t("settings.appearanceHint")}</p>
        <ThemePicker value={theme} onChange={saveTheme} compact />
        {themeSaving && <p className="hint">{t("settings.saving")}</p>}
      </section>

      <section className="settings-section settings-language">
        <div className="settings-lang-brand" aria-label="BarathX">
          <Logo variant="full" className="settings-lang-logo" />
          <p className="settings-lang-brand-native" lang={selectedLocale.id}>
            {selectedLocale.brandNative} · {selectedLocale.tagline}
          </p>
        </div>
        <h2>{t("settings.language")}</h2>
        <p className="hint">{t("settings.languageHint")}</p>
        <div className="settings-lang-grid" role="radiogroup" aria-label={t("settings.language")}>
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
        {languageSaving && <p className="hint">{t("settings.saving")}</p>}
      </section>

      <section className="settings-section">
        <h2>Email notifications</h2>
        <p className="hint">
          One email per activity (reply, like, follow, mention). Turn off anytime. Alerts in the app
          still work.
        </p>
        <label className="age-gate settings-email-toggle">
          <input
            type="checkbox"
            checked={emailActivity}
            disabled={emailSaving || !user?.email}
            onChange={(e) => saveEmailActivity(e.target.checked)}
          />
          <span>
            {user?.email
              ? "Send me activity emails"
              : "Add an email on your profile to receive activity emails"}
          </span>
        </label>
        {emailSaving && <p className="hint">{t("settings.saving")}</p>}
      </section>

      <section className="settings-section settings-security">
        <h2>Privacy &amp; security</h2>
        <p className="hint">
          Your password is hashed. Email and phone stay private on your profile. Sessions expire;
          password reset and “sign out everywhere” kill stolen tokens on other devices.
        </p>
        <ul className="settings-security-points">
          <li>Passwords stored with bcrypt, never plain text</li>
          <li>Email / phone visible only to you</li>
          <li>Confirm email before posting (if you signed up with email)</li>
          <li>Login &amp; OTP attempts are rate-limited</li>
          <li>Log out revokes your session token so a copied key stops working</li>
          <li>
            India DPDP: access, correct, erase, and withdraw consent (see Privacy Policy)
          </li>
        </ul>
        <div className="settings-security-actions">
          <button type="button" className="btn btn-secondary" onClick={handleExportData} disabled={exportBusy}>
            {exportBusy ? "Preparing…" : "Download my data"}
          </button>
          <Link className="btn btn-secondary" to="/privacy">
            Read Privacy Policy
          </Link>
          <button type="button" className="btn btn-secondary" onClick={handleRevokeAll}>
            Sign out everywhere
          </button>
        </div>

        <div className="settings-danger">
          <h3>Delete account</h3>
          <p className="hint">
            Permanently removes your account and posts. Type <strong>DELETE</strong> to confirm.
          </p>
          <input
            type="text"
            className="settings-delete-input"
            placeholder="Type DELETE"
            value={deleteConfirm}
            onChange={(e) => setDeleteConfirm(e.target.value)}
            autoComplete="off"
          />
          <button
            type="button"
            className="btn btn-danger"
            disabled={deleting || deleteConfirm.trim().toUpperCase() !== "DELETE"}
            onClick={deleteAccount}
          >
            {deleting ? "Deleting…" : "Delete my account"}
          </button>
        </div>
      </section>

      <section className="settings-section">
        <h2>{t("settings.profile")}</h2>
        <p className="hint">{t("settings.profileHint")}</p>
        <Link className="btn btn-secondary" to={`/u/${user?.username}`}>
          {t("settings.editProfile")}
        </Link>
      </section>

      <section className="settings-section">
        <h2>{t("settings.muted")}</h2>
        {listsLoading ? (
          <p className="hint">{t("settings.loading")}</p>
        ) : mutes.length === 0 ? (
          <p className="hint">{t("settings.noMutes")}</p>
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
                  {t("settings.unmute")}
                </button>
              </li>
            ))}
          </ul>
        )}
      </section>

      <section className="settings-section">
        <h2>{t("settings.blocked")}</h2>
        {listsLoading ? (
          <p className="hint">{t("settings.loading")}</p>
        ) : blocks.length === 0 ? (
          <p className="hint">{t("settings.noBlocks")}</p>
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
                  {t("settings.unblock")}
                </button>
              </li>
            ))}
          </ul>
        )}
      </section>

      <section className="settings-section">
        <h2>Help &amp; WhatsApp</h2>
        <p className="hint">
          First 1000 members can log bugs on Early issues (ops gets an email). Join WhatsApp to
          talk concerns live.
        </p>
        <div className="settings-security-actions">
          <Link className="btn btn-secondary" to="/early-issues">
            Early issues
          </Link>
          <a
            className="btn btn-secondary"
            href="https://chat.whatsapp.com/EV3Uj35EXrHImZ6MZxGAtU?mode=gi_t"
            target="_blank"
            rel="noreferrer"
          >
            WhatsApp Community
          </a>
          <a
            className="btn btn-secondary"
            href="https://whatsapp.com/channel/0029VbDMIgqHQbS9tfQo6u2o"
            target="_blank"
            rel="noreferrer"
          >
            WhatsApp Channel
          </a>
        </div>
      </section>

      <section className="settings-section">
        <h2>Badges</h2>
        <ul className="settings-badge-legend">
          <li>
            <strong className="badge-name badge-blue">Blue official</strong>. BarathX staff / platform
            accounts.
          </li>
          <li>
            <strong className="badge-name badge-gold">Gold BarathX</strong>. BarathX brand voices (topic
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
          {t("settings.logout")}
        </button>
      </section>

      <p className="hint settings-mvp-label" aria-label="App version">
        BarathX {mvpLabel()}
      </p>
    </div>
  );
}
