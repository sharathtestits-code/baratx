import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { notificationsApi } from "../api";
import { useAuth } from "../context/AuthContext";
import Avatar from "../components/Avatar";

function formatWhen(iso) {
  try {
    const d = new Date(iso);
    return d.toLocaleString(undefined, {
      month: "short",
      day: "numeric",
      hour: "numeric",
      minute: "2-digit",
    });
  } catch {
    return "";
  }
}

function notificationCopy(n) {
  switch (n.type) {
    case "follow":
      return "followed you";
    case "like":
      return "liked your post";
    case "repost":
      return "reposted your post";
    case "reply":
      return "replied to your post";
    case "mention":
      return "mentioned you";
    case "message":
      return "sent you a message";
    case "badge":
      return n.message || "updated your account badge";
    default:
      return "interacted with you";
  }
}

export default function Notifications() {
  const { token } = useAuth();
  const navigate = useNavigate();
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!token) {
      setLoading(false);
      setError("Sign in to see notifications.");
      return;
    }
    let cancelled = false;
    async function load() {
      setLoading(true);
      setError("");
      try {
        const data = await notificationsApi.list(token);
        if (cancelled) return;
        setItems(Array.isArray(data?.items) ? data.items : []);
        // Never block the list UI on mark-read.
        notificationsApi.markRead(token).then(() => {
          window.dispatchEvent(new CustomEvent("bx:notifications-read"));
        }).catch(() => {});
      } catch (err) {
        if (!cancelled) setError(err.message || "Could not load notifications");
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    load();
    return () => {
      cancelled = true;
    };
  }, [token]);

  function openNotification(n) {
    if (n.type === "message" && n.actor?.username) {
      navigate(`/messages/${n.actor.username}`);
      return;
    }
    if (n.post_id) {
      navigate(`/posts/${n.post_id}`);
      return;
    }
    if (n.actor?.username) navigate(`/u/${n.actor.username}`);
  }

  return (
    <div className="feed-wrap">
      <div className="feed-header">
        <h1>Notifications</h1>
      </div>

      {loading ? (
        <p className="hint search-status">Loading notifications…</p>
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
        <div className="empty-state">
          <p className="empty-state-title">No notifications yet</p>
          <p className="hint">When people follow, like, reply, repost, or tag you, it shows up here.</p>
        </div>
      ) : (
        <div className="notif-list">
          {items.map((n) => (
            <button
              key={n.id}
              type="button"
              className={`notif-item${n.is_read ? "" : " unread"}`}
              onClick={() => openNotification(n)}
            >
              <Avatar
                name={n.actor?.display_name || "User"}
                username={n.actor?.username || "user"}
                url={n.actor?.avatar_url}
                size={44}
              />
              <div className="notif-body">
                <div className="notif-text">
                  {n.actor?.username ? (
                    <Link
                      to={`/u/${n.actor.username}`}
                      className="notif-actor"
                      onClick={(e) => e.stopPropagation()}
                    >
                      {n.actor.display_name}
                    </Link>
                  ) : (
                    <span className="notif-actor">Someone</span>
                  )}{" "}
                  {notificationCopy(n)}
                </div>
                {(n.reply_preview || n.post_preview) && (
                  <div className="notif-preview">{n.reply_preview || n.post_preview}</div>
                )}
                <div className="notif-time">{formatWhen(n.created_at)}</div>
              </div>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
