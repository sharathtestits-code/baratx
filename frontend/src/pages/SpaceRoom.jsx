import { useEffect, useRef, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { spacesApi } from "../api";
import { useAuth } from "../context/AuthContext";
import PostCard from "../components/PostCard";
import Avatar from "../components/Avatar";
import MentionTextarea from "../components/MentionTextarea";
import LiveTalkPanel from "../components/LiveTalkPanel";

export default function SpaceRoom() {
  const { spaceId } = useParams();
  const { user, token } = useAuth();
  const [space, setSpace] = useState(null);
  const [posts, setPosts] = useState([]);
  const [text, setText] = useState("");
  const [loading, setLoading] = useState(true);
  const [posting, setPosting] = useState(false);
  const [closing, setClosing] = useState(false);
  const [stanceBusy, setStanceBusy] = useState(false);
  const [filter, setFilter] = useState("all"); // all | for | against
  const [error, setError] = useState("");
  const [stanceHint, setStanceHint] = useState(false);
  const composeRef = useRef(null);

  const isDebate = space?.kind === "debate";

  async function load() {
    setLoading(true);
    setError("");
    try {
      const [s, feed] = await Promise.all([
        spacesApi.get(token, spaceId),
        spacesApi.feed(token, spaceId),
      ]);
      setSpace(s);
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
  }, [token, spaceId]);

  async function pickSide(side) {
    if (!token || stanceBusy || !space) return;
    if (space.status !== "open") {
      setError("This debate is closed");
      return;
    }
    setStanceBusy(true);
    setError("");
    setStanceHint(false);
    // Optimistic — unlock typing / Post immediately
    setSpace((prev) => (prev ? { ...prev, my_side: side } : prev));
    try {
      const updated = await spacesApi.setStance(token, spaceId, side);
      setSpace(updated);
      requestAnimationFrame(() => {
        if (typeof composeRef.current?.focus === "function") composeRef.current.focus();
      });
    } catch (err) {
      setError(err.message || "Could not pick a side");
      load();
    } finally {
      setStanceBusy(false);
    }
  }

  async function submitPost(e) {
    e.preventDefault();
    if (!text.trim()) return;
    if (isDebate && !space?.my_side) {
      setError("Pick For or Against above, then post");
      setStanceHint(true);
      document.getElementById("debate-stance-panel")?.scrollIntoView({
        behavior: "smooth",
        block: "center",
      });
      return;
    }
    setPosting(true);
    setError("");
    try {
      const post = await spacesApi.post(token, spaceId, text.trim(), space?.my_side);
      setPosts((prev) => [...prev, post]);
      setText("");
    } catch (err) {
      setError(err.message);
    } finally {
      setPosting(false);
    }
  }

  async function leaveConversation() {
    if (!token || stanceBusy || !space?.my_side) return;
    setStanceBusy(true);
    setError("");
    setStanceHint(false);
    setSpace((prev) => (prev ? { ...prev, my_side: null } : prev));
    try {
      const updated = await spacesApi.clearStance(token, spaceId);
      setSpace(updated);
    } catch (err) {
      setError(err.message || "Could not leave conversation");
      load();
    } finally {
      setStanceBusy(false);
    }
  }

  function joinConversation() {
    if (isDebate && !space?.my_side) {
      setStanceHint(true);
      document.getElementById("debate-stance-panel")?.scrollIntoView({
        behavior: "smooth",
        block: "center",
      });
      return;
    }
    document.getElementById("live-compose")?.scrollIntoView({
      behavior: "smooth",
      block: "center",
    });
    requestAnimationFrame(() => {
      if (typeof composeRef.current?.focus === "function") composeRef.current.focus();
    });
  }

  async function closeSpace() {
    if (!window.confirm("Close this debate? People won’t be able to post anymore.")) return;
    setClosing(true);
    setError("");
    try {
      const updated = await spacesApi.close(token, spaceId);
      setSpace(updated);
    } catch (err) {
      setError(err.message);
    } finally {
      setClosing(false);
    }
  }

  if (loading) {
    return (
      <div className="feed-wrap plaza-page">
        <p className="hint">Loading…</p>
      </div>
    );
  }

  if (!space) {
    return (
      <div className="feed-wrap plaza-page">
        <div className="error">{error || "Not found"}</div>
        <Link to={isDebate ? "/arenas" : "/spaces"}>Back</Link>
      </div>
    );
  }

  const open = space.status === "open";
  const visiblePosts =
    !isDebate || filter === "all"
      ? posts
      : posts.filter((p) => p.debate_side === filter);

  return (
    <div className={`plaza-page plaza-live-room${isDebate ? " debate-room" : ""}`}>
      <div className="live-amphitheatre live-amphitheatre-room" aria-label="Live room stage">
        <div className="live-amphitheatre-glow" aria-hidden="true" />
        <div className="live-stage-top">
          <Link to={space.arena_key ? `/arenas/${space.arena_key}` : "/spaces"} className="back-link">
            ← {space.arena_name || (isDebate ? "Arenas" : "Live")}
          </Link>
          {open && <span className="live-pill">Live</span>}
        </div>
        {isDebate && space.arena_name && (
          <div className="debate-arena-tag">{space.arena_name} debate</div>
        )}
        <h1 className="live-amphitheatre-title">{space.title}</h1>
        <p className="live-amphitheatre-sub">
          Hosted by @{space.host?.username} · {space.status}
          {space.closes_at ? ` · closes ${new Date(space.closes_at).toLocaleString()}` : ""}
        </p>
        <div className="live-stage-wave" aria-hidden="true">
          <span />
          <span />
          <span />
          <span />
          <span />
          <span />
          <span />
        </div>
        <div className="live-stage-actions">
          {open && (
            <button type="button" className="btn btn-primary" onClick={joinConversation}>
              {isDebate && space.my_side ? "Back to compose" : "Join conversation"}
            </button>
          )}
          {open && isDebate && space.my_side && (
            <button
              type="button"
              className="profile-edit-btn live-leave-btn"
              onClick={leaveConversation}
              disabled={stanceBusy}
            >
              {stanceBusy ? "Leaving…" : "Leave conversation"}
            </button>
          )}
          {space.is_host && open && (
            <button type="button" className="profile-edit-btn live-close-btn" onClick={closeSpace} disabled={closing}>
              {closing ? "Closing…" : "Close room"}
            </button>
          )}
        </div>
      </div>

      {error && <div className="error">{error}</div>}

      {open && token && (
        <LiveTalkPanel spaceId={spaceId} token={token} isHost={!!space.is_host} />
      )}

      {isDebate && (
        <div
          id="debate-stance-panel"
          className={`debate-stance-panel${stanceHint && !space.my_side ? " needs-side" : ""}`}
        >
          <p className="debate-stance-lead">Pick a side to join the fight</p>
          <div className="debate-stance-row">
            <button
              type="button"
              className={`debate-side-btn for${space.my_side === "for" ? " active" : ""}`}
              disabled={!open || stanceBusy}
              aria-pressed={space.my_side === "for"}
              onClick={() => pickSide("for")}
            >
              <span className="debate-side-label">{space.side_for_label}</span>
              <span className="debate-side-count">{space.for_count}</span>
            </button>
            <button
              type="button"
              className={`debate-side-btn against${space.my_side === "against" ? " active" : ""}`}
              disabled={!open || stanceBusy}
              aria-pressed={space.my_side === "against"}
              onClick={() => pickSide("against")}
            >
              <span className="debate-side-label">{space.side_against_label}</span>
              <span className="debate-side-count">{space.against_count}</span>
            </button>
          </div>
          {space.my_side ? (
            <p className="hint ok-hint">
              You’re on <strong>{space.my_side === "for" ? space.side_for_label : space.side_against_label}</strong> —
              type your argument below.
            </p>
          ) : (
            <p className="hint">Tap For or Against, then type your take.</p>
          )}
          <div className="feed-tabs debate-filter-tabs">
            <button
              type="button"
              className={filter === "all" ? "feed-tab active" : "feed-tab"}
              onClick={() => setFilter("all")}
            >
              All
            </button>
            <button
              type="button"
              className={filter === "for" ? "feed-tab active" : "feed-tab"}
              onClick={() => setFilter("for")}
            >
              {space.side_for_label}
            </button>
            <button
              type="button"
              className={filter === "against" ? "feed-tab active" : "feed-tab"}
              onClick={() => setFilter("against")}
            >
              {space.side_against_label}
            </button>
          </div>
        </div>
      )}

      {open ? (
        <form id="live-compose" className="compose surface-compose" onSubmit={submitPost}>
          <div className="compose-row">
            <Avatar name={user?.display_name} username={user?.username} url={user?.avatar_url} size={40} />
            <div className="compose-body">
              <MentionTextarea
                ref={composeRef}
                value={text}
                onChange={(next) => {
                  setText(next);
                  if (isDebate && !space.my_side && next.trim()) setStanceHint(true);
                }}
                placeholder={
                  isDebate
                    ? space.my_side
                      ? `Argue for ${
                          space.my_side === "for" ? space.side_for_label : space.side_against_label
                        }… type @ to tag`
                      : "Type your take — pick For or Against above to post"
                    : "Say something in this Space — type @ to tag"
                }
                maxLength={280}
                rows={3}
              />
              <button
                type="submit"
                className="post-btn"
                disabled={posting || !text.trim() || (isDebate && !space.my_side)}
              >
                {posting
                  ? "Posting…"
                  : isDebate && !space.my_side
                    ? "Pick a side to post"
                    : "Post"}
              </button>
            </div>
          </div>
        </form>
      ) : (
        <p className="hint">This {isDebate ? "debate" : "Space"} is closed.</p>
      )}

      {visiblePosts.length === 0 ? (
        <div className="empty-state">
          <p className="empty-state-title">No posts yet</p>
          <p className="hint">{isDebate ? "Pick a side and make the first argument." : "Start the conversation."}</p>
        </div>
      ) : (
        <div className="post-list">
          {visiblePosts.map((post) => (
            <div key={post.id} className="debate-post-wrap">
              {isDebate && post.debate_side && (
                <span className={`debate-post-side ${post.debate_side}`}>
                  {post.debate_side === "for" ? space.side_for_label : space.side_against_label}
                </span>
              )}
              <PostCard post={post} onDeleted={(id) => setPosts((p) => p.filter((x) => x.id !== id))} />
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
