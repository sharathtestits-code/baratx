import { useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { spacesApi } from "../api";
import { useAuth } from "../context/AuthContext";
import PlazaPageHeader from "../components/PlazaPageHeader";

const SUGGESTED_DEBATES = [
  "Should WFH stay the default in India tech?",
  "Kohli or Rohit — who carries big games?",
  "One civic problem your city still ignores",
  "Is hustle culture burning junior talent?",
];

export default function Spaces() {
  const { token } = useAuth();
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [title, setTitle] = useState("");
  const [creating, setCreating] = useState(false);
  const titleRef = useRef(null);

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

  function startSuggested(topic) {
    setTitle(topic);
    const el = document.getElementById("go-live");
    el?.scrollIntoView({ behavior: "smooth", block: "center" });
    window.setTimeout(() => titleRef.current?.focus?.(), 200);
  }

  const featured = items[0];
  const empty = !loading && items.length === 0;

  return (
    <div className="plaza-page plaza-live">
      <PlazaPageHeader
        title="Live"
        sub="Start a live. Jump in. Mute, video, reactions — max 15."
      />
      <section className={`live-amphitheatre${empty ? " is-empty-hero" : ""}`}>
        <div className="live-amphitheatre-glow" aria-hidden="true" />
        <span className="live-pill">{empty ? "Start one" : "Live now"}</span>
        <h2 className="live-amphitheatre-title">
          {featured
            ? featured.title
            : empty
              ? "No rooms live — start one"
              : "Start a room India can join"}
        </h2>
        <p className="live-amphitheatre-sub">
          {featured
            ? `Hosted by @${featured.host?.username} · ${featured.post_count} takes in the room`
            : "Open a 15-person talk. Argue live — mute, video, reactions."}
        </p>
        {empty && (
          <button
            type="button"
            className="live-suggested-pill"
            onClick={() => startSuggested(SUGGESTED_DEBATES[0])}
          >
            {SUGGESTED_DEBATES[0]}
          </button>
        )}
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
              Jump in
            </Link>
          ) : (
            <button
              type="button"
              className="btn btn-primary"
              onClick={() => startSuggested(title.trim() || SUGGESTED_DEBATES[0])}
            >
              Start a live
            </button>
          )}
          {featured ? (
            <a href="#go-live" className="btn btn-secondary">
              Host your own
            </a>
          ) : (
            <Link to="/arenas" className="btn btn-secondary">
              Browse arenas
            </Link>
          )}
        </div>
      </section>

      <form id="go-live" className="plaza-studio live-create" onSubmit={createSpace}>
        <p className="plaza-studio-label">Start a live</p>
        <input
          ref={titleRef}
          type="text"
          placeholder="What are we arguing?"
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
          <h2>Rooms live</h2>
        </div>
        {loading ? (
          <p className="hint">Loading…</p>
        ) : items.length === 0 ? (
          <div className="live-empty-suggest">
            <p className="live-empty-suggest-title">Suggested debates</p>
            <p className="hint">Tap a topic to prefill — then go live.</p>
            <div className="live-empty-chips">
              {SUGGESTED_DEBATES.map((topic) => (
                <button
                  key={topic}
                  type="button"
                  className="live-empty-chip"
                  onClick={() => startSuggested(topic)}
                >
                  {topic}
                </button>
              ))}
            </div>
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
