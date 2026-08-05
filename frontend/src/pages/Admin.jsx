import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { adminApi } from "../api";

const SECRET_KEY = "baratx_admin_secret";

function formatWhen(iso) {
  if (!iso) return "—";
  try {
    return new Date(iso).toLocaleString(undefined, {
      dateStyle: "medium",
      timeStyle: "short",
    });
  } catch {
    return String(iso);
  }
}

function verifiedLabel(u) {
  const parts = [];
  if (u.is_email_verified) parts.push("email");
  if (u.is_phone_verified) parts.push("phone");
  return parts.length ? parts.join(" · ") : "—";
}

export default function Admin() {
  const [secret, setSecret] = useState(() => sessionStorage.getItem(SECRET_KEY) || "");
  const [draft, setDraft] = useState("");
  const [stats, setStats] = useState(null);
  const [users, setUsers] = useState([]);
  const [total, setTotal] = useState(0);
  const [error, setError] = useState("");
  const [msg, setMsg] = useState("");
  const [busy, setBusy] = useState(false);
  const [postText, setPostText] = useState("");
  const [postAs, setPostAs] = useState("baratx");
  const [posting, setPosting] = useState(false);

  const load = useCallback(async (adminSecret) => {
    if (!adminSecret) return;
    setBusy(true);
    setError("");
    try {
      const [s, u] = await Promise.all([
        adminApi.stats(adminSecret),
        adminApi.users(adminSecret, { limit: 100, offset: 0 }),
      ]);
      setStats(s);
      setUsers(u.users || []);
      setTotal(u.total || 0);
    } catch (err) {
      setStats(null);
      setUsers([]);
      setTotal(0);
      setError(err.message || "Could not load admin data");
    } finally {
      setBusy(false);
    }
  }, []);

  useEffect(() => {
    if (secret) load(secret);
  }, [secret, load]);

  function handleUnlock(e) {
    e.preventDefault();
    const next = draft.trim();
    if (!next) {
      setError("Enter the admin secret");
      return;
    }
    sessionStorage.setItem(SECRET_KEY, next);
    setSecret(next);
  }

  function handleLock() {
    sessionStorage.removeItem(SECRET_KEY);
    setSecret("");
    setDraft("");
    setStats(null);
    setUsers([]);
    setTotal(0);
    setError("");
    setMsg("");
  }

  async function handleAdminPost(e) {
    e.preventDefault();
    if (!postText.trim() || !secret) return;
    setPosting(true);
    setError("");
    setMsg("");
    try {
      const post = await adminApi.createPost(secret, {
        text: postText.trim(),
        username: postAs,
      });
      setPostText("");
      setMsg(`Posted as @${post.author?.username || postAs}`);
      load(secret);
    } catch (err) {
      setError(err.message || "Could not post");
    } finally {
      setPosting(false);
    }
  }

  if (!secret) {
    return (
      <div className="admin-unlock">
        <h1>Registrations</h1>
        <p className="admin-lead">Enter the ADMIN_SECRET from Railway to view signups.</p>
        {error && <div className="admin-error">{error}</div>}
        <form className="admin-unlock-form" onSubmit={handleUnlock}>
          <label className="admin-field" htmlFor="admin-secret">
            Admin secret
          </label>
          <input
            id="admin-secret"
            type="password"
            value={draft}
            onChange={(e) => setDraft(e.target.value)}
            autoComplete="current-password"
            required
          />
          <button type="submit" className="admin-btn admin-btn-primary" disabled={busy}>
            {busy ? "Opening…" : "Open"}
          </button>
        </form>
      </div>
    );
  }

  const statItems = stats
    ? [
        { value: stats.total_users, label: "Total users" },
        { value: stats.users_with_posts ?? "—", label: "Users who posted" },
        { value: stats.posters_last_24h ?? "—", label: "Posters (24h)" },
        { value: stats.posts_last_24h ?? "—", label: "Posts (24h)" },
        { value: stats.total_posts ?? "—", label: "Total posts" },
        { value: stats.users_last_24h, label: "Signups (24h)" },
        { value: stats.email_verified, label: "Email verified" },
        { value: stats.with_phone, label: "With phone" },
      ]
    : [];

  return (
    <div className="admin-panel">
      <header className="admin-header">
        <div>
          <h1>Registrations</h1>
          <p className="admin-lead">Live BaratX signup overview</p>
        </div>
        <div className="admin-actions">
          <button
            type="button"
            className="admin-btn admin-btn-ghost"
            onClick={() => load(secret)}
            disabled={busy}
          >
            {busy ? "Refreshing…" : "Refresh"}
          </button>
          <button type="button" className="admin-btn admin-btn-ghost" onClick={handleLock}>
            Lock
          </button>
        </div>
      </header>

      {error && <div className="admin-error">{error}</div>}
      {msg && <p className="admin-ok">{msg}</p>}

      <section className="admin-compose" aria-labelledby="admin-compose-title">
        <h2 id="admin-compose-title">Post as BaratX</h2>
        <p className="admin-lead">Publish from an official account without logging into the app.</p>
        <form className="admin-compose-form" onSubmit={handleAdminPost}>
          <div className="admin-field-block">
            <label className="admin-field" htmlFor="admin-post-as">
              Account
            </label>
            <select
              id="admin-post-as"
              className="admin-select"
              value={postAs}
              onChange={(e) => setPostAs(e.target.value)}
            >
              <option value="baratx">@baratx — BaratX</option>
              <option value="bharatvoices">@bharatvoices — Bharat Voices</option>
              <option value="indiatech">@indiatech — India Tech Daily</option>
            </select>
          </div>

          <div className="admin-field-block">
            <label className="admin-field" htmlFor="admin-post-text">
              Post
            </label>
            <textarea
              id="admin-post-text"
              className="admin-textarea"
              value={postText}
              onChange={(e) => setPostText(e.target.value)}
              maxLength={500}
              rows={4}
              placeholder="Say something India can reply to…"
              required
            />
          </div>

          <div className="admin-compose-footer">
            <span className="admin-char-count">{postText.length}/500</span>
            <button
              type="submit"
              className="admin-btn admin-btn-primary"
              disabled={posting || !postText.trim()}
            >
              {posting ? "Posting…" : "Post"}
            </button>
          </div>
        </form>
      </section>

      {statItems.length > 0 && (
        <div className="admin-stats">
          {statItems.map((item) => (
            <div className="admin-stat" key={item.label}>
              <span className="admin-stat-value">{item.value}</span>
              <span className="admin-stat-label">{item.label}</span>
            </div>
          ))}
        </div>
      )}

      <p className="admin-count">
        Showing {users.length} of {total} users (newest first)
      </p>

      <div className="admin-table-wrap">
        <table className="admin-table">
          <thead>
            <tr>
              <th>Joined</th>
              <th>Username</th>
              <th>Name</th>
              <th>Email</th>
              <th>Phone</th>
              <th>Method</th>
              <th>Verified</th>
            </tr>
          </thead>
          <tbody>
            {users.length === 0 && !busy && (
              <tr>
                <td colSpan={7} className="admin-empty">
                  No registrations yet.
                </td>
              </tr>
            )}
            {users.map((u) => (
              <tr key={u.id}>
                <td>{formatWhen(u.created_at)}</td>
                <td>
                  <Link className="admin-user-link" to={`/u/${encodeURIComponent(u.username)}`}>
                    @{u.username}
                  </Link>
                </td>
                <td>{u.display_name}</td>
                <td>{u.email || "—"}</td>
                <td>{u.phone || "—"}</td>
                <td>{u.signup_method}</td>
                <td>{verifiedLabel(u)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
