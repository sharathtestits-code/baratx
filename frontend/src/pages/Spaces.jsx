import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { spacesApi } from "../api";
import { useAuth } from "../context/AuthContext";

export default function Spaces() {
  const { token } = useAuth();
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [title, setTitle] = useState("");
  const [creating, setCreating] = useState(false);

  async function load() {
    setLoading(true);
    setError("");
    try {
      const data = await spacesApi.list(token, "open");
      setItems(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token]);

  async function createSpace(e) {
    e.preventDefault();
    if (!title.trim()) return;
    setCreating(true);
    setError("");
    try {
      const created = await spacesApi.create(token, { title: title.trim(), duration_hours: 24 });
      setItems((prev) => [created, ...prev]);
      setTitle("");
    } catch (err) {
      setError(err.message);
    } finally {
      setCreating(false);
    }
  }

  return (
    <div className="feed-wrap surface-page">
      <div className="feed-header">
        <h1>Spaces</h1>
      </div>
      <p className="hint surface-lead">
        Timed text discussion rooms. Host a topic, invite people in, close when you’re done.
      </p>

      <form className="surface-create" onSubmit={createSpace}>
        <input
          type="text"
          placeholder="What is this Space about?"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          maxLength={100}
          required
        />
        <button type="submit" className="btn btn-primary" disabled={creating || !title.trim()}>
          {creating ? "Opening…" : "Create your Space"}
        </button>
      </form>

      {error && <div className="error">{error}</div>}

      {loading ? (
        <p className="hint">Loading…</p>
      ) : items.length === 0 ? (
        <div className="empty-state">
          <p className="empty-state-title">No open Spaces</p>
          <p className="hint">Start a room for a live text conversation.</p>
        </div>
      ) : (
        <ul className="surface-card-list">
          {items.map((s) => (
            <li key={s.id}>
              <Link to={`/spaces/${s.id}`} className="surface-card-link">
                <strong>{s.title}</strong>
                <span className="hint">
                  Hosted by @{s.host?.username}
                  {s.is_host ? " (you)" : ""}
                </span>
                <span className="surface-meta">
                  {s.post_count} posts · {s.status}
                </span>
              </Link>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
