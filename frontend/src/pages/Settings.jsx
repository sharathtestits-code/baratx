import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api, socialApi } from "../api";
import { useAuth } from "../context/AuthContext";
import Avatar from "../components/Avatar";

const LANGUAGES = [
  { value: "en", label: "English" },
  { value: "hi", label: "Hindi" },
  { value: "te", label: "Telugu" },
];

export default function Settings() {
  const { user, token, logout, updateUser } = useAuth();
  const navigate = useNavigate();
  const [language, setLanguage] = useState(user?.language || "en");
  const [saving, setSaving] = useState(false);
  const [msg, setMsg] = useState("");
  const [error, setError] = useState("");
  const [mutes, setMutes] = useState([]);
  const [blocks, setBlocks] = useState([]);
  const [listsLoading, setListsLoading] = useState(true);

  useEffect(() => {
    setLanguage(user?.language || "en");
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

  async function saveLanguage(e) {
    e.preventDefault();
    setSaving(true);
    setMsg("");
    setError("");
    try {
      const updated = await api.updateMe(token, { language });
      updateUser(updated);
      setMsg("Language saved.");
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
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
    <div className="feed-wrap surface-page">
      <div className="feed-header">
        <h1>Settings and privacy</h1>
      </div>

      {error && <div className="error">{error}</div>}
      {msg && <p className="hint ok-hint">{msg}</p>}

      <section className="settings-section">
        <h2>Language</h2>
        <p className="hint">Choose your preferred language for BaratX.</p>
        <form className="settings-form" onSubmit={saveLanguage}>
          <select
            className="settings-select"
            value={language}
            onChange={(e) => setLanguage(e.target.value)}
            aria-label="Language"
          >
            {LANGUAGES.map((l) => (
              <option key={l.value} value={l.value}>
                {l.label}
              </option>
            ))}
          </select>
          <button type="submit" className="btn btn-primary" disabled={saving}>
            {saving ? "Saving…" : "Save"}
          </button>
        </form>
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
        <h2>Account</h2>
        <button type="button" className="btn btn-secondary" onClick={handleLogout}>
          Log out
        </button>
      </section>
    </div>
  );
}
