import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { messagesApi } from "../api";
import { useAuth } from "../context/AuthContext";
import Avatar from "../components/Avatar";

export default function Messages() {
  const { token } = useAuth();
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let cancelled = false;
    async function load() {
      setLoading(true);
      try {
        const data = await messagesApi.conversations(token);
        if (!cancelled) setItems(data);
      } catch (err) {
        if (!cancelled) setError(err.message);
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
        <p className="hint">Loading…</p>
      ) : error ? (
        <div className="error">{error}</div>
      ) : items.length === 0 ? (
        <div className="empty-state">
          <p className="empty-state-title">No conversations yet</p>
          <p className="hint">Open a profile and tap Message to start a DM.</p>
        </div>
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
                <div className="people-bio">{c.last_message.text}</div>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
