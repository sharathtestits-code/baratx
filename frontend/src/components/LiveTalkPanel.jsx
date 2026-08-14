import { forwardRef, useEffect, useImperativeHandle, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { spacesApi } from "../api";
import { useLiveTalkRtc } from "../hooks/useLiveTalkRtc";
import Avatar from "./Avatar";

const REACTIONS = ["👍", "❤️", "😂", "👏", "🔥", "😮", "🎉", "👎"];

/** Remote seat camera — muted here; audio plays via the WebRTC audio element. */
function RemoteSeatVideo({ stream, tick = 0 }) {
  const ref = useRef(null);
  useEffect(() => {
    const el = ref.current;
    if (!el) return undefined;
    el.srcObject = stream || null;
    const play = () => {
      el.play().catch(() => {});
    };
    play();
    if (!stream) return undefined;
    const onAdd = () => play();
    stream.addEventListener("addtrack", onAdd);
    stream.getVideoTracks().forEach((tr) => {
      tr.addEventListener("unmute", play);
    });
    return () => {
      stream.removeEventListener("addtrack", onAdd);
    };
  }, [stream, tick]);
  return <video ref={ref} className="live-talk-seat-video" autoPlay playsInline muted />;
}

/**
 * Live Talk — under Live rooms.
 * Join conversation → real WebRTC audio/video between seats; mute / video; pin, chat, DM, remove under ⋯.
 */
const LiveTalkPanel = forwardRef(function LiveTalkPanel(
  { spaceId, token, isHost, autoJoinToken = 0, onTalkChange },
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
  const [localStream, setLocalStream] = useState(null);
  const localVideoRef = useRef(null);
  const mediaRef = useRef(null);
  const seenReactIds = useRef(new Set());
  const moreRef = useRef(null);
  const reactInFlight = useRef(false);

  const inTalk = !!state?.in_talk;
  const myUserId = state?.my_user_id || null;

  const { remoteStreams, remoteTick, resumeRemoteAudio } = useLiveTalkRtc({
    spaceId,
    token,
    myUserId,
    inTalk,
    participants: state?.participants || [],
    localStream,
    myMuted: !!state?.my_muted,
  });

  function pushFloatReacts(items) {
    if (!items.length) return;
    setFloatReacts((prev) => [...prev, ...items].slice(-12));
    const keys = new Set(items.map((x) => x.key));
    setTimeout(() => {
      setFloatReacts((prev) => prev.filter((x) => !keys.has(x.key)));
    }, 2200);
  }

  function ingestReactions(reactions, { skipFloat = false } = {}) {
    const next = [];
    for (const r of reactions || []) {
      if (!r?.id || seenReactIds.current.has(r.id)) continue;
      seenReactIds.current.add(r.id);
      if (skipFloat) continue;
      next.push({
        key: `${r.id}-${Date.now()}`,
        emoji: r.emoji,
        name: r.user?.display_name || r.user?.username || "",
      });
    }
    pushFloatReacts(next);
  }

  async function refresh() {
    if (!token || !spaceId) return;
    try {
      const data = await spacesApi.talkGet(token, spaceId);
      setState(data);
      setError("");
      ingestReactions(data.reactions);
    } catch (err) {
      setError(err.message || "Could not load conversation audio");
    }
  }

  useEffect(() => {
    refresh();
    // Faster while on call so reactions / seats feel live
    const ms = inTalk ? 900 : 3000;
    const t = setInterval(refresh, ms);
    return () => clearInterval(t);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token, spaceId, inTalk]);

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
      localVideoRef.current.play().catch(() => {});
    }
  }, [state?.my_video, state?.participant_count, localStream]);

  useEffect(() => {
    onTalkChange?.(!!state?.in_talk);
  }, [state?.in_talk, onTalkChange]);

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
    setLocalStream(null);
    if (localVideoRef.current) localVideoRef.current.srcObject = null;
  }

  async function ensureMedia({ wantVideo, muted = true }) {
    try {
      // Prefer extending the existing stream so audio doesn't drop when video toggles
      if (mediaRef.current) {
        const stream = mediaRef.current;
        if (wantVideo && stream.getVideoTracks().length === 0) {
          const cam = await navigator.mediaDevices.getUserMedia({
            video: { facingMode: "user", width: { ideal: 640 } },
          });
          cam.getVideoTracks().forEach((tr) => stream.addTrack(tr));
        }
        if (!wantVideo) {
          stream.getVideoTracks().forEach((tr) => {
            tr.stop();
            stream.removeTrack(tr);
          });
        }
        stream.getAudioTracks().forEach((tr) => {
          tr.enabled = !muted;
        });
        // New MediaStream identity so WebRTC effect re-runs with updated tracks
        const next = new MediaStream(stream.getTracks());
        mediaRef.current = next;
        setLocalStream(next);
        if (localVideoRef.current) {
          localVideoRef.current.srcObject = wantVideo ? next : null;
        }
        return next;
      }

      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
        },
        video: wantVideo ? { facingMode: "user", width: { ideal: 640 } } : false,
      });
      stream.getAudioTracks().forEach((tr) => {
        tr.enabled = !muted;
      });
      mediaRef.current = stream;
      setLocalStream(stream);
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
      const stream = await ensureMedia({ wantVideo: false, muted: true });
      if (stream) {
        // Join muted by default — unmute publishes audio to peers
        stream.getAudioTracks().forEach((tr) => {
          tr.enabled = false;
        });
      }
      resumeRemoteAudio();
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
      const stream =
        mediaRef.current ||
        (await ensureMedia({ wantVideo: state.my_video, muted: next }));
      if (stream) {
        stream.getAudioTracks().forEach((tr) => {
          tr.enabled = !next;
        });
        setLocalStream(stream);
      }
      const data = await spacesApi.talkUpdateMe(token, spaceId, { muted: next });
      setState(data);
      // Unmute click is a user gesture — unlock remote audio autoplay
      resumeRemoteAudio();
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
        const stream = await ensureMedia({ wantVideo: true, muted: state.my_muted });
        if (!stream) {
          setBusy(false);
          return;
        }
      } else {
        await ensureMedia({ wantVideo: false, muted: state.my_muted });
      }
      const data = await spacesApi.talkUpdateMe(token, spaceId, { video_enabled: next });
      setState(data);
      resumeRemoteAudio();
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
    if (!state?.in_talk || reactInFlight.current) return;
    reactInFlight.current = true;
    // Optimistic float — don't wait for the round-trip / poll
    pushFloatReacts([
      {
        key: `local-${emoji}-${Date.now()}`,
        emoji,
        name: "You",
      },
    ]);
    try {
      const data = await spacesApi.talkReact(token, spaceId, emoji);
      // Mark server ids seen so the next poll doesn't replay the same emoji
      ingestReactions(data.reactions, { skipFloat: true });
      setState(data);
    } catch (err) {
      setError(err.message || "Could not react");
    } finally {
      reactInFlight.current = false;
    }
  }

  const count = state?.participant_count ?? 0;
  const max = state?.max_participants ?? 15;
  const mePinned = (state?.pinned_usernames || []).includes(
    state?.participants?.find((p) => p.is_self)?.user?.username
  );

  return (
    <section id="live-talk-panel" className={`live-talk${inTalk ? " is-live" : ""}`} aria-label="Live conversation">
      <div className="live-talk-head">
        <div>
          <h2 className="live-talk-title">Live conversation</h2>
          <p className="live-talk-sub">
            Audio & video · {count}/{max} on call · unmute to speak · turn video on to be seen
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
          {(state?.participants || []).map((p) => {
            const peerId = String(p.user.id);
            const remote = remoteStreams[peerId];
            const remoteHasLiveVideo = Boolean(
              remote?.getVideoTracks?.().some((t) => t.readyState === "live")
            );
            const showLocalVideo = p.is_self && (p.video_enabled || state.my_video) && state.my_video;
            const showRemoteVideo = !p.is_self && (p.video_enabled || remoteHasLiveVideo) && remote;
            return (
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
                {showLocalVideo ? (
                  <video
                    ref={localVideoRef}
                    className="live-talk-seat-video"
                    autoPlay
                    playsInline
                    muted
                  />
                ) : showRemoteVideo ? (
                  <RemoteSeatVideo stream={remote} tick={remoteTick} />
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
                  {p.video_enabled || remoteHasLiveVideo || showLocalVideo ? " · Video" : ""}
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
            );
          })}
          {count === 0 && (
            <li className="live-talk-empty">
              <p className="hint">
                Tap <strong>Join conversation</strong> to go on audio. Then unmute so others can hear you.
                Max {max} people.
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
