import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { communitiesApi } from "../api";
import { useAuth } from "../context/AuthContext";

export default function Communities() {
  const { token } = useAuth();
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [creating, setCreating] = useState(false);

  async function load() {
    setLoading(true);
    setError("");
    try {
      const data = await communitiesApi.list(token);
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

  async function createCommunity(e) {
    e.preventDefault();
    if (!name.trim()) return;
    setCreating(true);
    setError("");
    try {
      const created = await communitiesApi.create(token, {
        name: name.trim(),
        description: description.trim(),
      });
      setItems((prev) => [created, ...prev]);
      setName("");
      setDescription("");
    } catch (err) {
      setError(err.message);
    } finally {
      setCreating(false);
    }
  }

  return (
    <div className="feed-wrap surface-page">
      <div className="feed-header">
        <h1>Communities</h1>
      </div>
      <p className="hint surface-lead">
        Member-run groups, city, craft, or interest. For national sided debate use{" "}
        <Link to="/arenas">Arenas</Link> instead (Sports, Politics, Startups…).
      </p>

      <form className="surface-create" onSubmit={createCommunity}>
        <input
          type="text"
          placeholder="Community name"
          value={name}
          onChange={(e) => setName(e.target.value)}
          maxLength={60}
          required
        />
        <input
          type="text"
          placeholder="What is this community about?"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          maxLength={280}
        />
        <button type="submit" className="btn btn-primary" disabled={creating || !name.trim()}>
          {creating ? "Creating…" : "Create community"}
        </button>
      </form>

      {error && <div className="error">{error}</div>}

      {loading ? (
        <p className="hint">Loading…</p>
      ) : items.length === 0 ? (
        <div className="empty-state">
          <p className="empty-state-title">No communities yet</p>
          <p className="hint">Start one around a city, craft, or interest.</p>
        </div>
      ) : (
        <ul className="surface-card-list">
          {items.map((c) => (
            <li key={c.id}>
              <Link to={`/communities/${c.slug}`} className="surface-card-link">
                <strong>{c.name}</strong>
                {c.description ? <span className="hint">{c.description}</span> : null}
                <span className="surface-meta">
                  {c.member_count} members{c.is_member ? " · Joined" : ""}
                </span>
              </Link>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
