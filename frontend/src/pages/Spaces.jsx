import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { spacesApi } from "../api";
import { useAuth } from "../context/AuthContext";
import PlazaPageHeader from "../components/PlazaPageHeader";

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
    <div className="plaza-page plaza-live">
      <PlazaPageHeader
        title="Live"
        sub="Open a room, Join conversation — mute, video, reactions (max 15)."
      />
      <section className="live-amphitheatre">
        <div className="live-amphitheatre-glow" aria-hidden="true" />
        <span className="live-pill">On air</span>
        <p className="live-eyebrow">Airwaves</p>
        <h2 className="live-amphitheatre-title">
          {featured ? featured.title : "Start a room India can join"}
        </h2>
        <p className="live-amphitheatre-sub">
          {featured
            ? `Hosted by @${featured.host?.username} · ${featured.post_count} takes in the room`
            : "Pick a room below or go live — Join conversation for audio & video."}
        </p>
        <div className="live-stage-wave" aria-hidden="true">
          <span />
          <span />
          <span />
          <span />
          <span />
          <span />
          <span />
        </div>
        <div className="live-amphitheatre-actions">
          {featured ? (
            <Link to={`/spaces/${featured.id}`} className="btn btn-primary">
              Join conversation
            </Link>
          ) : null}
          <a href="#go-live" className="btn btn-secondary">
            Go live
          </a>
        </div>
      </section>

      <form id="go-live" className="plaza-studio live-create" onSubmit={createSpace}>
        <p className="plaza-studio-label">Open a live room</p>
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

      <section className="plaza-takes">
        <div className="plaza-takes-head">
          <h2>Rooms on air</h2>
        </div>
        {loading ? (
          <p className="hint">Loading…</p>
        ) : items.length === 0 ? (
          <div className="empty-state">
            <p className="empty-state-title">No rooms on air</p>
            <p className="hint">Be the first host tonight.</p>
          </div>
        ) : (
          <ul className="plaza-onair-list live-room-grid">
            {items.map((s) => (
              <li key={s.id}>
                <Link to={`/spaces/${s.id}`} className="plaza-onair-card">
                  <span className="live-room-dot" aria-hidden="true" />
                  <strong>{s.title}</strong>
                  <span className="hint">
                    @{s.host?.username}
                    {s.is_host ? " · you" : ""} · {s.post_count} posts
                  </span>
                </Link>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}
