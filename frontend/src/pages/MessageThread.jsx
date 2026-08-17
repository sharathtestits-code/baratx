import { useEffect, useRef, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { messagesApi } from "../api";
import { useAuth } from "../context/AuthContext";
import Avatar from "../components/Avatar";
import ContentSafetyNote from "../components/ContentSafetyNote";
import { assertSafePublicText } from "../contentSafety";

export default function MessageThread() {
  const { username } = useParams();
  const { token, user } = useAuth();
  const navigate = useNavigate();
  const [messages, setMessages] = useState([]);
  const [peer, setPeer] = useState(null);
  const [text, setText] = useState("");
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const bottomRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      setLoading(true);
      setError("");
      try {
        const data = await messagesApi.thread(token, username);
        if (cancelled) return;
        setMessages(data);
        const other = (data || []).find((m) => m.sender?.username === username)?.sender
          || (data || []).find((m) => m.recipient?.username === username)?.recipient
          || null;
        setPeer(other);
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
    setError("");
    try {
      assertSafePublicText(text);
      const msg = await messagesApi.send(token, username, text.trim());
      setMessages((prev) => [...prev, msg]);
      setText("");
      inputRef.current?.focus();
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  const displayName = peer?.display_name || username;

  return (
    <div className="plaza-page dm-thread">
      <header className="dm-thread-header">
        <button type="button" className="dm-back" onClick={() => navigate("/messages")} aria-label="Back to messages">
          ←
        </button>
        <Link to={`/u/${username}`} className="dm-peer">
          <Avatar name={displayName} username={username} url={peer?.avatar_url} size={40} />
          <div className="dm-peer-copy">
            <div className="dm-peer-name">{displayName}</div>
            <div className="dm-peer-handle">@{username}</div>
          </div>
        </Link>
      </header>

      {loading ? (
        <p className="hint search-status">Loading conversation…</p>
      ) : (
        <div className="dm-messages">
          {messages.length === 0 ? (
            <div className="dm-empty">
              <Avatar name={displayName} username={username} url={peer?.avatar_url} size={64} />
              <p className="dm-empty-title">Say hello to {displayName}</p>
              <p className="hint">
                Keep it respectful — this is a private message on India&apos;s public square.
              </p>
            </div>
          ) : (
            messages.map((m) => {
              const mine = m.sender.username === user?.username;
              return (
                <div key={m.id} className={`dm-bubble ${mine ? "mine" : "theirs"}`}>
                  {!mine && (
                    <Avatar
                      name={m.sender.display_name}
                      username={m.sender.username}
                      url={m.sender.avatar_url}
                      size={28}
                    />
                  )}
                  <div className="dm-bubble-text">{m.text}</div>
                </div>
              );
            })
          )}
          <div ref={bottomRef} />
        </div>
      )}

      {error && <div className="error dm-error">{error}</div>}

      <form className="dm-compose" onSubmit={send}>
        <ContentSafetyNote compact />
        <div className="dm-compose-row">
          <input
            ref={inputRef}
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder={`Message @${username}…`}
            maxLength={1000}
            aria-label="Message text"
            enterKeyHint="send"
            autoComplete="off"
          />
          <button type="submit" className="dm-send" disabled={busy || !text.trim()}>
            {busy ? "…" : "Send"}
          </button>
        </div>
      </form>
    </div>
  );
}
