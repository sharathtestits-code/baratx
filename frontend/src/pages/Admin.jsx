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

export default function Admin() {
  const [secret, setSecret] = useState(() => sessionStorage.getItem(SECRET_KEY) || "");
  const [draft, setDraft] = useState("");
  const [stats, setStats] = useState(null);
  const [users, setUsers] = useState([]);
  const [total, setTotal] = useState(0);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

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
  }

  if (!secret) {
    return (
      <div className="auth-card auth-card-x admin-card">
        <h1>Registrations</h1>
        <p className="hint">Enter the ADMIN_SECRET from Railway to view signups.</p>
        {error && <div className="error">{error}</div>}
        <form onSubmit={handleUnlock}>
          <label>
            Admin secret
            <input
              type="password"
              value={draft}
              onChange={(e) => setDraft(e.target.value)}
              autoComplete="current-password"
              required
            />
          </label>
          <button type="submit" disabled={busy}>
            {busy ? "Opening…" : "Open"}
          </button>
        </form>
        <p className="switch-link">
          <Link to="/">Back to BaratX</Link>
        </p>
      </div>
    );
  }

  return (
    <div className="admin-panel">
      <header className="admin-header">
        <div>
          <h1>Registrations</h1>
          <p className="hint">Live BaratX signup overview</p>
        </div>
        <div className="admin-actions">
          <button type="button" className="btn-secondary" onClick={() => load(secret)} disabled={busy}>
            {busy ? "Refreshing…" : "Refresh"}
          </button>
          <button type="button" className="btn-secondary" onClick={handleLock}>
            Lock
          </button>
        </div>
      </header>

      {error && <div className="error">{error}</div>}

      {stats && (
        <div className="admin-stats">
          <div className="admin-stat">
            <span className="admin-stat-value">{stats.total_users}</span>
            <span className="admin-stat-label">Total users</span>
          </div>
          <div className="admin-stat">
            <span className="admin-stat-value">{stats.users_last_24h}</span>
            <span className="admin-stat-label">Last 24 hours</span>
          </div>
          <div className="admin-stat">
            <span className="admin-stat-value">{stats.users_last_7d}</span>
            <span className="admin-stat-label">Last 7 days</span>
          </div>
          <div className="admin-stat">
            <span className="admin-stat-value">{stats.email_verified}</span>
            <span className="admin-stat-label">Email verified</span>
          </div>
          <div className="admin-stat">
            <span className="admin-stat-value">{stats.with_phone}</span>
            <span className="admin-stat-label">With phone</span>
          </div>
        </div>
      )}

      <p className="hint admin-count">
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
                  <Link to={`/u/${encodeURIComponent(u.username)}`}>@{u.username}</Link>
                </td>
                <td>{u.display_name}</td>
                <td>{u.email || "—"}</td>
                <td>{u.phone || "—"}</td>
                <td>{u.signup_method}</td>
                <td>
                  {u.is_email_verified ? "email" : ""}
                  {u.is_email_verified && u.is_phone_verified ? " · " : ""}
                  {u.is_phone_verified ? "phone" : ""}
                  {!u.is_email_verified && !u.is_phone_verified ? "—" : ""}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
