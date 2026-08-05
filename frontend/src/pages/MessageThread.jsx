import { useEffect, useRef, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { messagesApi } from "../api";
import { useAuth } from "../context/AuthContext";
import Avatar from "../components/Avatar";

export default function MessageThread() {
  const { username } = useParams();
  const { token, user } = useAuth();
  const navigate = useNavigate();
  const [messages, setMessages] = useState([]);
  const [text, setText] = useState("");
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const bottomRef = useRef(null);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      setLoading(true);
      setError("");
      try {
        const data = await messagesApi.thread(token, username);
        if (!cancelled) setMessages(data);
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
  }, [token, username]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function send(e) {
    e.preventDefault();
    if (!text.trim() || busy) return;
    setBusy(true);
    try {
      const msg = await messagesApi.send(token, username, text.trim());
      setMessages((prev) => [...prev, msg]);
      setText("");
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="feed-wrap dm-thread">
      <div className="feed-header follow-list-header">
        <button type="button" className="back-btn" onClick={() => navigate("/messages")}>
          ←
        </button>
        <div>
          <h1>
            <Link to={`/u/${username}`}>@{username}</Link>
          </h1>
        </div>
      </div>

      {loading ? (
        <p className="hint">Loading…</p>
      ) : (
        <div className="dm-messages">
          {messages.map((m) => {
            const mine = m.sender.username === user?.username;
            return (
              <div key={m.id} className={`dm-bubble ${mine ? "mine" : "theirs"}`}>
                {!mine && (
                  <Avatar name={m.sender.display_name} username={m.sender.username} url={m.sender.avatar_url} size={28} />
                )}
                <div className="dm-bubble-text">{m.text}</div>
              </div>
            );
          })}
          <div ref={bottomRef} />
        </div>
      )}

      {error && <div className="error">{error}</div>}

      <form className="dm-compose" onSubmit={send}>
        <input
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Write a message…"
          maxLength={1000}
        />
        <button type="submit" disabled={busy || !text.trim()}>
          Send
        </button>
      </form>
    </div>
  );
}
