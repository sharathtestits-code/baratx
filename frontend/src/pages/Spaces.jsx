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

  const featured = items[0];

  return (
    <div className="feed-wrap surface-page live-airwaves">
      <div className="feed-header live-airwaves-header">
        <div>
          <p className="live-eyebrow">Airwaves</p>
          <h1>Live</h1>
        </div>
        <span className="live-pill" aria-hidden="true">
          On air
        </span>
      </div>

      <section className="live-hero-stage" aria-label="Live stage">
        <div className="live-stage-wave" aria-hidden="true">
          <span />
          <span />
          <span />
          <span />
          <span />
          <span />
          <span />
        </div>
        <p className="live-hero-kicker">Now on BaratX</p>
        <h2 className="live-hero-title">
          {featured ? featured.title : "Start a room India can join"}
        </h2>
        <p className="hint">
          {featured
            ? `Hosted by @${featured.host?.username} · ${featured.post_count} posts`
            : "Timed discussion rooms for real-time text conversation."}
        </p>
        {featured ? (
          <Link to={`/spaces/${featured.id}`} className="btn btn-primary live-hero-cta">
            Join conversation
          </Link>
        ) : null}
      </section>

      <form className="surface-create live-create" onSubmit={createSpace}>
        <input
          type="text"
          placeholder="What should India hear right now?"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          maxLength={100}
          required
        />
        <button type="submit" className="btn btn-primary" disabled={creating || !title.trim()}>
          {creating ? "Opening…" : "Go live"}
        </button>
      </form>

      {error && <div className="error">{error}</div>}

      {loading ? (
        <p className="hint">Loading…</p>
      ) : items.length === 0 ? (
        <div className="empty-state">
          <p className="empty-state-title">No rooms on air</p>
          <p className="hint">Start a live room for a real-time text conversation.</p>
        </div>
      ) : (
        <ul className="surface-card-list live-room-list">
          {items.map((s) => (
            <li key={s.id}>
              <Link to={`/spaces/${s.id}`} className="surface-card-link live-room-card">
                <span className="live-room-dot" aria-hidden="true" />
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
