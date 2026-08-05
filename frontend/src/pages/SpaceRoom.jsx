import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { spacesApi } from "../api";
import { useAuth } from "../context/AuthContext";
import PostCard from "../components/PostCard";
import Avatar from "../components/Avatar";

export default function SpaceRoom() {
  const { spaceId } = useParams();
  const { user, token } = useAuth();
  const [space, setSpace] = useState(null);
  const [posts, setPosts] = useState([]);
  const [text, setText] = useState("");
  const [loading, setLoading] = useState(true);
  const [posting, setPosting] = useState(false);
  const [closing, setClosing] = useState(false);
  const [error, setError] = useState("");

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

  async function submitPost(e) {
    e.preventDefault();
    if (!text.trim()) return;
    setPosting(true);
    setError("");
    try {
      const post = await spacesApi.post(token, spaceId, text.trim());
      setPosts((prev) => [...prev, post]);
      setText("");
    } catch (err) {
      setError(err.message);
    } finally {
      setPosting(false);
    }
  }

  async function closeSpace() {
    if (!window.confirm("Close this Space? People won’t be able to post anymore.")) return;
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
        <div className="error">{error || "Space not found"}</div>
        <Link to="/spaces">Back to Spaces</Link>
      </div>
    );
  }

  const open = space.status === "open";

  return (
    <div className="feed-wrap surface-page">
      <div className="feed-header surface-header-row">
        <div>
          <Link to="/spaces" className="back-link">
            ← Spaces
          </Link>
          <h1>{space.title}</h1>
          <p className="hint">
            Hosted by @{space.host?.username} · {space.status}
            {space.closes_at ? ` · closes ${new Date(space.closes_at).toLocaleString()}` : ""}
          </p>
        </div>
        {space.is_host && open && (
          <button type="button" className="btn btn-secondary" disabled={closing} onClick={closeSpace}>
            {closing ? "Closing…" : "Close Space"}
          </button>
        )}
      </div>

      {error && <div className="error">{error}</div>}

      {open ? (
        <form className="compose surface-compose" onSubmit={submitPost}>
          <div className="compose-row">
            <Avatar
              name={user?.display_name}
              username={user?.username}
              url={user?.avatar_url}
              size={40}
            />
            <div className="compose-body">
              <textarea
                placeholder="Share an update in this Space…"
                value={text}
                onChange={(e) => setText(e.target.value)}
                maxLength={280}
                rows={3}
              />
              <div className="compose-footer">
                <span className="hint">{text.length}/280</span>
                <button type="submit" className="btn btn-primary" disabled={posting || !text.trim()}>
                  {posting ? "Posting…" : "Post"}
                </button>
              </div>
            </div>
          </div>
        </form>
      ) : (
        <p className="hint">This Space is closed. You can still read the conversation.</p>
      )}

      {posts.length === 0 ? (
        <div className="empty-state">
          <p className="empty-state-title">No posts yet</p>
          <p className="hint">Say something to get the room going.</p>
        </div>
      ) : (
        <div className="post-list">
          {posts.map((post) => (
            <PostCard
              key={post.id}
              post={post}
              onDeleted={(id) => setPosts((p) => p.filter((x) => x.id !== id))}
            />
          ))}
        </div>
      )}
    </div>
  );
}
