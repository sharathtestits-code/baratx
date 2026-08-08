import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { messagesApi } from "../api";
import { useAuth } from "../context/AuthContext";
import Avatar from "../components/Avatar";
import EmptyState from "../components/EmptyState";

export default function Messages() {
  const { token } = useAuth();
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!token) {
      setLoading(false);
      setError("Sign in to see messages.");
      return;
    }
    let cancelled = false;
    async function load() {
      setLoading(true);
      setError("");
      try {
        const data = await messagesApi.conversations(token);
        if (!cancelled) setItems(Array.isArray(data) ? data : []);
      } catch (err) {
        if (!cancelled) setError(err.message || "Could not load messages");
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    load();
    return () => {
      cancelled = true;
    };
  }, [token]);

  return (
    <div className="feed-wrap">
      <div className="feed-header">
        <h1>Messages</h1>
      </div>
      {loading ? (
        <p className="hint search-status">Loading messages…</p>
      ) : error ? (
        <div className="error">
          {error}
          <div style={{ marginTop: 8 }}>
            <button type="button" className="btn-secondary" onClick={() => window.location.reload()}>
              Retry
            </button>
          </div>
        </div>
      ) : items.length === 0 ? (
        <EmptyState
          title="No conversations yet"
          hint="Find someone in Explore and tap Message on their profile."
          primaryTo="/search"
          primaryLabel="Find people"
          secondaryTo="/feed"
          secondaryLabel="Back to Square"
        />
      ) : (
        <div className="people-list">
          {items.map((c) => (
            <Link key={c.user.id} to={`/messages/${c.user.username}`} className="people-row dm-row">
              <Avatar name={c.user.display_name} username={c.user.username} url={c.user.avatar_url} size={48} />
              <div className="dm-main">
                <div className="people-name">
                  {c.user.display_name}
                  {c.unread_count > 0 && <span className="dm-unread">{c.unread_count}</span>}
                </div>
                <div className="people-bio">{c.last_message?.text}</div>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
