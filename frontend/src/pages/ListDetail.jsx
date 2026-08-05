import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { listsApi, searchApi } from "../api";
import { useAuth } from "../context/AuthContext";
import PostCard from "../components/PostCard";
import Avatar from "../components/Avatar";

export default function ListDetail() {
  const { listId } = useParams();
  const { token } = useAuth();
  const navigate = useNavigate();
  const [list, setList] = useState(null);
  const [members, setMembers] = useState([]);
  const [posts, setPosts] = useState([]);
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState("");

  async function load() {
    setLoading(true);
    setError("");
    try {
      const [l, m, feed] = await Promise.all([
        listsApi.get(token, listId),
        listsApi.members(token, listId),
        listsApi.feed(token, listId),
      ]);
      setList(l);
      setMembers(m);
      setPosts(feed);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token, listId]);

  useEffect(() => {
    if (!query.trim() || query.trim().length < 2) {
      setResults([]);
      return;
    }
    let cancelled = false;
    const t = setTimeout(async () => {
      try {
        const data = await searchApi.search(query.trim(), token);
        if (!cancelled) setResults((data.users || []).slice(0, 6));
      } catch {
        if (!cancelled) setResults([]);
      }
    }, 250);
    return () => {
      cancelled = true;
      clearTimeout(t);
    };
  }, [query, token]);

  async function addMember(username) {
    setBusy(username);
    setError("");
    try {
      await listsApi.addMember(token, listId, username);
      setQuery("");
      setResults([]);
      await load();
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy("");
    }
  }

  async function removeMember(username) {
    setBusy(username);
    setError("");
    try {
      await listsApi.removeMember(token, listId, username);
      await load();
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy("");
    }
  }

  async function deleteList() {
    if (!window.confirm("Delete this list?")) return;
    try {
      await listsApi.remove(token, listId);
      navigate("/lists");
    } catch (err) {
      setError(err.message);
    }
  }

  if (loading) {
    return (
      <div className="feed-wrap">
        <p className="hint">Loading…</p>
      </div>
    );
  }

  if (!list) {
    return (
      <div className="feed-wrap">
        <div className="error">{error || "List not found"}</div>
        <Link to="/lists">Back to Lists</Link>
      </div>
    );
  }

  return (
    <div className="feed-wrap surface-page">
      <div className="feed-header surface-header-row">
        <div>
          <Link to="/lists" className="back-link">
            ← Lists
          </Link>
          <h1>{list.name}</h1>
          {list.description ? <p className="hint">{list.description}</p> : null}
        </div>
        <button type="button" className="btn btn-ghost" onClick={deleteList}>
          Delete
        </button>
      </div>

      {error && <div className="error">{error}</div>}

      <section className="settings-section">
        <h2>Members</h2>
        <div className="surface-add-row">
          <input
            type="search"
            placeholder="Search people to add…"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
        </div>
        {results.length > 0 && (
          <ul className="settings-user-list surface-search-results">
            {results.map((u) => (
              <li key={u.id} className="settings-user-row">
                <Link to={`/u/${u.username}`} className="settings-user-link">
                  <Avatar name={u.display_name} username={u.username} url={u.avatar_url} size={32} />
                  <span>
                    <strong>{u.display_name}</strong>
                    <span className="hint">@{u.username}</span>
                  </span>
                </Link>
                <button
                  type="button"
                  className="btn btn-primary"
                  disabled={busy === u.username}
                  onClick={() => addMember(u.username)}
                >
                  Add
                </button>
              </li>
            ))}
          </ul>
        )}
        {members.length === 0 ? (
          <p className="hint">No members yet. Add people to build this timeline.</p>
        ) : (
          <ul className="settings-user-list">
            {members.map((u) => (
              <li key={u.id} className="settings-user-row">
                <Link to={`/u/${u.username}`} className="settings-user-link">
                  <Avatar name={u.display_name} username={u.username} url={u.avatar_url} size={36} />
                  <span>
                    <strong>{u.display_name}</strong>
                    <span className="hint">@{u.username}</span>
                  </span>
                </Link>
                <button
                  type="button"
                  className="btn btn-ghost"
                  disabled={busy === u.username}
                  onClick={() => removeMember(u.username)}
                >
                  Remove
                </button>
              </li>
            ))}
          </ul>
        )}
      </section>

      <section className="settings-section">
        <h2>Timeline</h2>
        {posts.length === 0 ? (
          <div className="empty-state">
            <p className="empty-state-title">No posts yet</p>
            <p className="hint">When members post, their updates show up here.</p>
          </div>
        ) : (
          <div className="post-list">
            {posts.map((post) => (
              <PostCard
                key={post.id}
                post={post}
                onDeleted={(id) => setPosts((p) => p.filter((x) => x.id !== id))}
              />
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
