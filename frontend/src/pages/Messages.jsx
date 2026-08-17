import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { messagesApi } from "../api";
import { useAuth } from "../context/AuthContext";
import Avatar from "../components/Avatar";
import ContentSafetyNote from "../components/ContentSafetyNote";
import PlazaPageHeader from "../components/PlazaPageHeader";

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
    <div className="plaza-page dm-inbox">
      <PlazaPageHeader title="Messages" sub="Private chats with people you follow and debate." />
      <ContentSafetyNote />

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
        <div className="dm-inbox-empty">
          <p className="dm-empty-title">Your inbox is quiet</p>
          <p className="hint">
            Open someone&apos;s profile and tap <strong>Message</strong> to start a respectful chat.
          </p>
          <Link to="/search" className="btn btn-primary dm-empty-cta">
            Find people to message
          </Link>
        </div>
      ) : (
        <div className="people-list dm-inbox-list">
          {items.map((c) => (
            <Link key={c.user.id} to={`/messages/${c.user.username}`} className="people-row dm-row">
              <Avatar name={c.user.display_name} username={c.user.username} url={c.user.avatar_url} size={48} />
              <div className="dm-main">
                <div className="people-name">
                  {c.user.display_name}
                  {c.unread_count > 0 && <span className="dm-unread">{c.unread_count}</span>}
                </div>
                <div className="people-bio dm-preview">{c.last_message?.text || "Say hello"}</div>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
