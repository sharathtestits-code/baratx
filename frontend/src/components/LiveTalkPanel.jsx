import { forwardRef, useEffect, useImperativeHandle, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { spacesApi } from "../api";
import Avatar from "./Avatar";

const REACTIONS = ["👍", "❤️", "😂", "👏", "🔥", "😮", "🎉", "👎"];

/**
 * Live Talk — under Live rooms.
 * Join conversation → mute / video primary; pin, chat, DM, remove under ⋯.
 */
const LiveTalkPanel = forwardRef(function LiveTalkPanel(
  { spaceId, token, isHost, autoJoinToken = 0 },
  ref
) {
  const [state, setState] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [chat, setChat] = useState("");
  const [menuUser, setMenuUser] = useState(null);
  const [moreOpen, setMoreOpen] = useState(false);
  const [showChat, setShowChat] = useState(false);
  const [floatReacts, setFloatReacts] = useState([]);
  const localVideoRef = useRef(null);
  const mediaRef = useRef(null);
  const seenReactIds = useRef(new Set());
  const moreRef = useRef(null);

  async function refresh() {
    if (!token || !spaceId) return;
    try {
      const data = await spacesApi.talkGet(token, spaceId);
      setState(data);
      setError("");
      // Float new reactions
      const next = [];
      for (const r of data.reactions || []) {
        if (seenReactIds.current.has(r.id)) continue;
        seenReactIds.current.add(r.id);
        next.push({
          key: `${r.id}-${Date.now()}`,
          emoji: r.emoji,
          name: r.user?.display_name || r.user?.username || "",
        });
      }
      if (next.length) {
        setFloatReacts((prev) => [...prev, ...next].slice(-12));
        setTimeout(() => {
          setFloatReacts((prev) => prev.filter((x) => !next.some((n) => n.key === x.key)));
        }, 2600);
      }
    } catch (err) {
      setError(err.message || "Could not load conversation audio");
    }
  }

  useEffect(() => {
    refresh();
    const t = setInterval(refresh, 3000);
    return () => clearInterval(t);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token, spaceId]);

  useEffect(() => {
    return () => stopMedia();
  }, []);

  useEffect(() => {
    if (!autoJoinToken) return;
    join();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [autoJoinToken]);

  useEffect(() => {
    if (state?.my_video && localVideoRef.current && mediaRef.current) {
      localVideoRef.current.srcObject = mediaRef.current;
    }
  }, [state?.my_video, state?.participant_count]);

  useEffect(() => {
    function onDoc(e) {
      if (moreRef.current && !moreRef.current.contains(e.target)) setMoreOpen(false);
    }
    document.addEventListener("mousedown", onDoc);
    return () => document.removeEventListener("mousedown", onDoc);
  }, []);

  useImperativeHandle(ref, () => ({
    join,
    leave,
    scrollIntoView: () => {
      document.getElementById("live-talk-panel")?.scrollIntoView({
        behavior: "smooth",
        block: "start",
      });
    },
  }));

  function stopMedia() {
    const stream = mediaRef.current;
    if (stream) {
      stream.getTracks().forEach((tr) => tr.stop());
      mediaRef.current = null;
    }
    if (localVideoRef.current) localVideoRef.current.srcObject = null;
  }

  async function ensureMedia({ wantVideo }) {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: true,
        video: wantVideo ? { facingMode: "user", width: { ideal: 640 } } : false,
      });
      if (mediaRef.current) {
        mediaRef.current.getTracks().forEach((tr) => tr.stop());
      }
      mediaRef.current = stream;
      if (localVideoRef.current) {
        localVideoRef.current.srcObject = wantVideo ? stream : null;
      }
      return stream;
    } catch {
      setError("Allow microphone / camera to use Live conversation");
      return null;
    }
  }

  async function join() {
    if (!token || busy) return;
    setBusy(true);
    setError("");
    try {
      const data = await spacesApi.talkJoin(token, spaceId);
      setState(data);
      await ensureMedia({ wantVideo: false });
      const stream = mediaRef.current;
      if (stream) {
        stream.getAudioTracks().forEach((tr) => {
          tr.enabled = false;
        });
      }
      requestAnimationFrame(() => {
        document.getElementById("live-talk-panel")?.scrollIntoView({
          behavior: "smooth",
          block: "start",
        });
      });
    } catch (err) {
      setError(err.message || "Could not join conversation");
    } finally {
      setBusy(false);
    }
  }

  async function leave() {
    setBusy(true);
    setError("");
    setMoreOpen(false);
    try {
      const data = await spacesApi.talkLeave(token, spaceId);
      setState(data);
      stopMedia();
    } catch (err) {
      setError(err.message || "Could not leave");
    } finally {
      setBusy(false);
    }
  }

  async function toggleMute() {
    if (!state?.in_talk) return;
    const next = !state.my_muted;
    setBusy(true);
    try {
      const stream = mediaRef.current || (await ensureMedia({ wantVideo: state.my_video }));
      if (stream) {
        stream.getAudioTracks().forEach((tr) => {
          tr.enabled = !next;
        });
      }
      const data = await spacesApi.talkUpdateMe(token, spaceId, { muted: next });
      setState(data);
    } catch (err) {
      setError(err.message || "Could not update mute");
    } finally {
      setBusy(false);
    }
  }

  async function toggleVideo() {
    if (!state?.in_talk) return;
    const next = !state.my_video;
    setBusy(true);
    try {
      if (next) {
        const stream = await ensureMedia({ wantVideo: true });
        if (!stream) {
          setBusy(false);
          return;
        }
        stream.getAudioTracks().forEach((tr) => {
          tr.enabled = !state.my_muted;
        });
      } else if (mediaRef.current) {
        mediaRef.current.getVideoTracks().forEach((tr) => tr.stop());
        if (localVideoRef.current) localVideoRef.current.srcObject = null;
        await ensureMedia({ wantVideo: false });
        if (mediaRef.current) {
          mediaRef.current.getAudioTracks().forEach((tr) => {
            tr.enabled = !state.my_muted;
          });
        }
      }
      const data = await spacesApi.talkUpdateMe(token, spaceId, { video_enabled: next });
      setState(data);
    } catch (err) {
      setError(err.message || "Could not update video");
    } finally {
      setBusy(false);
    }
  }

  async function togglePin(username, isPinned) {
    setBusy(true);
    try {
      const data = isPinned
        ? await spacesApi.talkUnpin(token, spaceId, username)
        : await spacesApi.talkPin(token, spaceId, username);
      setState(data);
      setMenuUser(null);
      setMoreOpen(false);
    } catch (err) {
      setError(err.message || "Could not update pin");
    } finally {
      setBusy(false);
    }
  }

  async function removeUser(username) {
    const reason = window.prompt(
      `Remove @${username} for a community guideline reason?`,
      "community guidelines"
    );
    if (!reason) return;
    setBusy(true);
    setMenuUser(null);
    try {
      const data = await spacesApi.talkRemove(token, spaceId, username, reason);
      setState(data);
    } catch (err) {
      setError(err.message || "Could not remove");
    } finally {
      setBusy(false);
    }
  }

  async function sendChat(e) {
    e.preventDefault();
    if (!chat.trim() || !state?.in_talk) return;
    setBusy(true);
    try {
      const data = await spacesApi.talkMessage(token, spaceId, chat.trim());
      setState(data);
      setChat("");
    } catch (err) {
      setError(err.message || "Message blocked");
      refresh();
    } finally {
      setBusy(false);
    }
  }

  async function react(emoji) {
    if (!state?.in_talk || busy) return;
    try {
      const data = await spacesApi.talkReact(token, spaceId, emoji);
      setState(data);
    } catch (err) {
      setError(err.message || "Could not react");
    }
  }

  const count = state?.participant_count ?? 0;
  const max = state?.max_participants ?? 15;
  const inTalk = !!state?.in_talk;
  const mePinned = (state?.pinned_usernames || []).includes(
    state?.participants?.find((p) => p.is_self)?.user?.username
  );

  return (
    <section id="live-talk-panel" className={`live-talk${inTalk ? " is-live" : ""}`} aria-label="Live conversation">
      <div className="live-talk-head">
        <div>
          <h2 className="live-talk-title">Live conversation</h2>
          <p className="live-talk-sub">
            Audio & video · {count}/{max} on call · profiles show when you join
          </p>
        </div>
        {!inTalk && (
          <button type="button" className="btn btn-primary" onClick={join} disabled={busy || !token}>
            {busy ? "Joining…" : "Join conversation"}
          </button>
        )}
      </div>

      {error && <div className="error">{error}</div>}

      <div className="live-talk-stage">
        <ul className="live-talk-grid">
          {(state?.participants || []).map((p) => (
            <li
              key={p.user.id}
              className={`live-talk-seat${p.is_pinned ? " is-pinned" : ""}${p.is_self ? " is-self" : ""}${
                !p.muted ? " is-speaking" : ""
              }`}
            >
              <button
                type="button"
                className="live-talk-seat-btn"
                onClick={() => setMenuUser(menuUser === p.user.username ? null : p.user.username)}
                aria-label={`@${p.user.username} options`}
              >
                {p.video_enabled && p.is_self && state.my_video ? (
                  <video
                    ref={localVideoRef}
                    className="live-talk-seat-video"
                    autoPlay
                    playsInline
                    muted
                  />
                ) : (
                  <Avatar
                    name={p.user.display_name}
                    username={p.user.username}
                    url={p.user.avatar_url}
                    size={72}
                  />
                )}
                <span className="live-talk-name">
                  {p.is_self ? "You" : p.user.display_name}
                  {p.is_host ? " · host" : ""}
                </span>
                <span className="live-talk-meta">
                  {p.muted ? "Muted" : "Mic on"}
                  {p.video_enabled ? " · Video" : ""}
                  {p.is_pinned ? " · Pinned" : ""}
                </span>
              </button>
              {menuUser === p.user.username && (
                <div className="live-talk-menu">
                  <button type="button" onClick={() => togglePin(p.user.username, p.is_pinned)} disabled={busy}>
                    {p.is_pinned ? "Unpin for me" : p.is_self ? "Pin myself" : "Pin for me"}
                  </button>
                  {!p.is_self && (
                    <>
                      <Link to={`/messages/${p.user.username}`} className="live-talk-menu-link">
                        Personal message
                      </Link>
                      <button type="button" onClick={() => removeUser(p.user.username)} disabled={busy}>
                        {isHost ? "Remove from call" : "Remove (guidelines)"}
                      </button>
                    </>
                  )}
                </div>
              )}
            </li>
          ))}
          {count === 0 && (
            <li className="live-talk-empty">
              <p className="hint">
                Tap <strong>Join conversation</strong> to go on audio. Then mute / unmute and turn video on or
                off. Max {max} people.
              </p>
            </li>
          )}
        </ul>

        <div className="live-talk-float-reacts" aria-hidden="true">
          {floatReacts.map((r) => (
            <span key={r.key} className="live-talk-float-react">
              {r.emoji}
            </span>
          ))}
        </div>
      </div>

      {inTalk && (
        <>
          <div className="live-talk-reactions" role="group" aria-label="Reactions">
            {REACTIONS.map((emoji) => (
              <button
                key={emoji}
                type="button"
                className="live-talk-react-btn"
                onClick={() => react(emoji)}
                disabled={busy}
                aria-label={`React ${emoji}`}
              >
                {emoji}
              </button>
            ))}
          </div>

          <div className="live-talk-bar" role="toolbar" aria-label="Call controls">
            <button
              type="button"
              className={`live-talk-bar-btn primary${state.my_muted ? " is-off" : " is-on"}`}
              onClick={toggleMute}
              disabled={busy}
            >
              {state.my_muted ? "Unmute" : "Mute"}
            </button>
            <button
              type="button"
              className={`live-talk-bar-btn primary${state.my_video ? " is-on" : " is-off"}`}
              onClick={toggleVideo}
              disabled={busy}
            >
              {state.my_video ? "Video on" : "Video off"}
            </button>

            <div className="live-talk-more-wrap" ref={moreRef}>
              <button
                type="button"
                className={`live-talk-bar-btn more${moreOpen ? " is-open" : ""}`}
                aria-haspopup="menu"
                aria-expanded={moreOpen}
                onClick={() => setMoreOpen((v) => !v)}
                aria-label="More options"
              >
                <span className="live-talk-dots" aria-hidden="true">
                  ···
                </span>
              </button>
              {moreOpen && (
                <div className="live-talk-more-menu" role="menu">
                  <button
                    type="button"
                    role="menuitem"
                    onClick={() => {
                      setShowChat((v) => !v);
                      setMoreOpen(false);
                    }}
                  >
                    {showChat ? "Hide messages" : "In-call messages"}
                  </button>
                  <button
                    type="button"
                    role="menuitem"
                    disabled={busy}
                    onClick={() => {
                      const me = state.participants?.find((p) => p.is_self);
                      if (me) togglePin(me.user.username, !!mePinned);
                    }}
                  >
                    {mePinned ? "Unpin myself" : "Pin myself"}
                  </button>
                  <button
                    type="button"
                    role="menuitem"
                    className="danger"
                    disabled={busy}
                    onClick={() => {
                      setMoreOpen(false);
                      leave();
                    }}
                  >
                    Leave conversation
                  </button>
                </div>
              )}
            </div>

            <button type="button" className="live-talk-bar-btn leave" onClick={leave} disabled={busy}>
              Leave
            </button>
          </div>
        </>
      )}

      {inTalk && showChat && (
        <div className="live-talk-chat">
          <p className="live-talk-chat-label">Messages only to people on this call</p>
          <ul className="live-talk-chat-list">
            {(state?.messages || []).map((m) => (
              <li key={m.id}>
                <strong>@{m.sender.username}</strong> {m.text}
              </li>
            ))}
            {(state?.messages || []).length === 0 && <li className="hint">No messages yet.</li>}
          </ul>
          <form className="live-talk-chat-form" onSubmit={sendChat}>
            <input
              type="text"
              value={chat}
              onChange={(e) => setChat(e.target.value)}
              placeholder="Message the call…"
              maxLength={500}
              disabled={busy}
            />
            <button type="submit" className="post-btn" disabled={busy || !chat.trim()}>
              Send
            </button>
          </form>
        </div>
      )}
    </section>
  );
});

export default LiveTalkPanel;
