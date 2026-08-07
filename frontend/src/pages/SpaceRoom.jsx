import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { spacesApi } from "../api";
import { useAuth } from "../context/AuthContext";
import PostCard from "../components/PostCard";
import Avatar from "../components/Avatar";
import MentionTextarea from "../components/MentionTextarea";

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
    if (!token || stanceBusy) return;
    setStanceBusy(true);
    setError("");
    try {
      const updated = await spacesApi.setStance(token, spaceId, side);
      setSpace(updated);
    } catch (err) {
      setError(err.message);
    } finally {
      setStanceBusy(false);
    }
  }

  async function submitPost(e) {
    e.preventDefault();
    if (!text.trim()) return;
    if (isDebate && !space.my_side) {
      setError("Pick For or Against before posting");
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
      <div className="feed-wrap">
        <p className="hint">Loading…</p>
      </div>
    );
  }

  if (!space) {
    return (
      <div className="feed-wrap">
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
    <div className={`feed-wrap surface-page live-stage-page${isDebate ? " debate-room" : ""}`}>
      <div className="live-stage" aria-label="Live room stage">
        <div className="live-stage-top">
          <Link to={space.arena_key ? `/arenas/${space.arena_key}` : "/spaces"} className="back-link">
            ← {space.arena_name || (isDebate ? "Arenas" : "Live")}
          </Link>
          {open && (
            <span className="live-pill" aria-hidden="true">
              Live
            </span>
          )}
        </div>
        {isDebate && space.arena_name && (
          <div className="debate-arena-tag">{space.arena_name} debate</div>
        )}
        <h1 className="live-stage-title">{space.title}</h1>
        <p className="hint live-stage-meta">
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
        {space.is_host && open && (
          <button type="button" className="profile-edit-btn live-close-btn" onClick={closeSpace} disabled={closing}>
            {closing ? "Closing…" : "Close room"}
          </button>
        )}
      </div>

      {error && <div className="error">{error}</div>}

      {isDebate && (
        <div className="debate-stance-panel">
          <p className="debate-stance-lead">Pick a side to join the fight</p>
          <div className="debate-stance-row">
            <button
              type="button"
              className={`debate-side-btn for${space.my_side === "for" ? " active" : ""}`}
              disabled={!open || stanceBusy}
              onClick={() => pickSide("for")}
            >
              <span className="debate-side-label">{space.side_for_label}</span>
              <span className="debate-side-count">{space.for_count}</span>
            </button>
            <button
              type="button"
              className={`debate-side-btn against${space.my_side === "against" ? " active" : ""}`}
              disabled={!open || stanceBusy}
              onClick={() => pickSide("against")}
            >
              <span className="debate-side-label">{space.side_against_label}</span>
              <span className="debate-side-count">{space.against_count}</span>
            </button>
          </div>
          {space.my_side && (
            <p className="hint">
              You’re on <strong>{space.my_side === "for" ? space.side_for_label : space.side_against_label}</strong>
            </p>
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
        <form className="compose surface-compose" onSubmit={submitPost}>
          <div className="compose-row">
            <Avatar name={user?.display_name} username={user?.username} url={user?.avatar_url} size={40} />
            <div className="compose-body">
              <MentionTextarea
                value={text}
                onChange={setText}
                placeholder={
                  isDebate
                    ? space.my_side
                      ? `Argue for ${
                          space.my_side === "for" ? space.side_for_label : space.side_against_label
                        }… type @ to tag`
                      : "Pick a side above, then post"
                    : "Say something in this Space — type @ to tag"
                }
                maxLength={280}
                rows={3}
                disabled={isDebate && !space.my_side}
              />
              <button
                type="submit"
                className="post-btn"
                disabled={posting || !text.trim() || (isDebate && !space.my_side)}
              >
                {posting ? "Posting…" : "Post"}
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
