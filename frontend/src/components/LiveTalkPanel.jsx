import { useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { spacesApi } from "../api";
import Avatar from "./Avatar";

/**
 * Live Talk — meeting-style seat under a Live room.
 * Avatars by default; mute; optional local video; pin for yourself;
 * in-call chat; personal DM link; guideline remove without waiting on admin.
 * Soft cap 15. Browser media is local for now (peer mesh / LiveKit later).
 */
export default function LiveTalkPanel({ spaceId, token, isHost }) {
  const [state, setState] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [chat, setChat] = useState("");
  const [menuUser, setMenuUser] = useState(null);
  const localVideoRef = useRef(null);
  const mediaRef = useRef(null);

  async function refresh() {
    if (!token || !spaceId) return;
    try {
      const data = await spacesApi.talkGet(token, spaceId);
      setState(data);
      setError("");
    } catch (err) {
      setError(err.message || "Could not load Talk");
    }
  }

  useEffect(() => {
    refresh();
    const t = setInterval(refresh, 4000);
    return () => clearInterval(t);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token, spaceId]);

  useEffect(() => {
    return () => {
      stopMedia();
    };
  }, []);

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
      setError("Microphone / camera permission needed for Talk");
      return null;
    }
  }

  async function join() {
    setBusy(true);
    setError("");
    try {
      const data = await spacesApi.talkJoin(token, spaceId);
      setState(data);
      await ensureMedia({ wantVideo: false });
      const stream = mediaRef.current;
      if (stream) {
        stream.getAudioTracks().forEach((tr) => {
          tr.enabled = false; // join muted
        });
      }
    } catch (err) {
      setError(err.message || "Could not join Talk");
    } finally {
      setBusy(false);
    }
  }

  async function leave() {
    setBusy(true);
    setError("");
    try {
      const data = await spacesApi.talkLeave(token, spaceId);
      setState(data);
      stopMedia();
    } catch (err) {
      setError(err.message || "Could not leave Talk");
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
        // Keep audio-only stream
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
    } catch (err) {
      setError(err.message || "Could not update pin");
    } finally {
      setBusy(false);
    }
  }

  async function removeUser(username) {
    const reason = window.prompt(
      `Remove @${username} from Talk for a community guideline reason?`,
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

  const count = state?.participant_count ?? 0;
  const max = state?.max_participants ?? 15;
  const inTalk = !!state?.in_talk;

  return (
    <section className="live-talk" aria-label="Live Talk">
      <div className="live-talk-head">
        <div>
          <h2 className="live-talk-title">Talk</h2>
          <p className="live-talk-sub">
            Audio conversation · {count}/{max} seats · avatars on by default
          </p>
        </div>
        <div className="live-talk-head-actions">
          {!inTalk ? (
            <button type="button" className="btn btn-primary" onClick={join} disabled={busy || !token}>
              {busy ? "Joining…" : "Join Talk"}
            </button>
          ) : (
            <button type="button" className="profile-edit-btn live-leave-btn" onClick={leave} disabled={busy}>
              Leave Talk
            </button>
          )}
        </div>
      </div>

      {error && <div className="error">{error}</div>}

      {inTalk && (
        <div className="live-talk-controls" role="group" aria-label="Talk controls">
          <button type="button" className={`live-talk-ctrl${state.my_muted ? " is-off" : ""}`} onClick={toggleMute} disabled={busy}>
            {state.my_muted ? "Unmute" : "Mute"}
          </button>
          <button type="button" className={`live-talk-ctrl${state.my_video ? "" : " is-off"}`} onClick={toggleVideo} disabled={busy}>
            {state.my_video ? "Video on" : "Add video"}
          </button>
          <video
            ref={localVideoRef}
            className={`live-talk-self-video${state.my_video ? " show" : ""}`}
            autoPlay
            playsInline
            muted
          />
        </div>
      )}

      <ul className="live-talk-grid">
        {(state?.participants || []).map((p) => (
          <li key={p.user.id} className={`live-talk-seat${p.is_pinned ? " is-pinned" : ""}${p.is_self ? " is-self" : ""}`}>
            <button
              type="button"
              className="live-talk-seat-btn"
              onClick={() => setMenuUser(menuUser === p.user.username ? null : p.user.username)}
              aria-label={`@${p.user.username} options`}
            >
              {p.video_enabled && p.is_self && state.my_video ? (
                <span className="live-talk-video-placeholder">You · video</span>
              ) : (
                <Avatar
                  name={p.user.display_name}
                  username={p.user.username}
                  url={p.user.avatar_url}
                  size={72}
                />
              )}
              <span className="live-talk-name">
                {p.user.display_name}
                {p.is_host ? " · host" : ""}
                {p.is_pinned ? " · pinned" : ""}
              </span>
              <span className="live-talk-meta">
                @{p.user.username}
                {p.muted ? " · muted" : " · speaking"}
                {p.video_enabled ? " · cam" : ""}
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
                      {isHost ? "Remove from Talk" : "Remove (guidelines)"}
                    </button>
                  </>
                )}
              </div>
            )}
          </li>
        ))}
        {count === 0 && (
          <li className="live-talk-empty">
            <p className="hint">No one on Talk yet — join to open the audio seat (max {max}).</p>
          </li>
        )}
      </ul>

      {inTalk && (
        <div className="live-talk-chat">
          <p className="live-talk-chat-label">In-call messages (only people on this Talk)</p>
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
}
