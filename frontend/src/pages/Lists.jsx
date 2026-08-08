import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { listsApi } from "../api";
import { useAuth } from "../context/AuthContext";
import EmptyState from "../components/EmptyState";

export default function Lists() {
  const { token } = useAuth();
  const [lists, setLists] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [creating, setCreating] = useState(false);

  async function load() {
    setLoading(true);
    setError("");
    try {
      const data = await listsApi.list(token);
      setLists(data);
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

  async function createList(e) {
    e.preventDefault();
    if (!name.trim()) return;
    setCreating(true);
    setError("");
    try {
      const created = await listsApi.create(token, {
        name: name.trim(),
        description: description.trim(),
      });
      setLists((prev) => [created, ...prev]);
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
        <h1>Lists</h1>
      </div>
      <p className="hint surface-lead">
        Curate accounts into named lists and follow their posts in one timeline.
      </p>

      <form className="surface-create" onSubmit={createList}>
        <input
          type="text"
          placeholder="List name"
          value={name}
          onChange={(e) => setName(e.target.value)}
          maxLength={50}
          required
        />
        <input
          type="text"
          placeholder="Description (optional)"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          maxLength={160}
        />
        <button type="submit" className="btn btn-primary" disabled={creating || !name.trim()}>
          {creating ? "Creating…" : "Create list"}
        </button>
      </form>

      {error && <div className="error">{error}</div>}

      {loading ? (
        <p className="hint">Loading…</p>
      ) : lists.length === 0 ? (
        <EmptyState
          title="No lists yet"
          hint="Create a list above, then add people from Explore."
          primaryTo="/search"
          primaryLabel="Add from Explore"
          secondaryTo="/feed"
          secondaryLabel="Back to Square"
        />
      ) : (
        <ul className="surface-card-list">
          {lists.map((list) => (
            <li key={list.id}>
              <Link to={`/lists/${list.id}`} className="surface-card-link">
                <strong>{list.name}</strong>
                {list.description ? <span className="hint">{list.description}</span> : null}
                <span className="surface-meta">{list.member_count} members</span>
              </Link>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
