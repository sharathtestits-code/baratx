import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { communitiesApi } from "../api";
import { useAuth } from "../context/AuthContext";
import PostCard from "../components/PostCard";
import Avatar from "../components/Avatar";
import MentionTextarea from "../components/MentionTextarea";

export default function CommunityDetail() {
  const { slug } = useParams();
  const { user, token } = useAuth();
  const [community, setCommunity] = useState(null);
  const [posts, setPosts] = useState([]);
  const [text, setText] = useState("");
  const [loading, setLoading] = useState(true);
  const [posting, setPosting] = useState(false);
  const [joining, setJoining] = useState(false);
  const [error, setError] = useState("");

  async function load() {
    setLoading(true);
    setError("");
    try {
      const [c, feed] = await Promise.all([
        communitiesApi.get(token, slug),
        communitiesApi.feed(token, slug),
      ]);
      setCommunity(c);
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
  }, [token, slug]);

  async function toggleMembership() {
    if (!community) return;
    setJoining(true);
    setError("");
    try {
      const updated = community.is_member
        ? await communitiesApi.leave(token, slug)
        : await communitiesApi.join(token, slug);
      setCommunity(updated);
    } catch (err) {
      setError(err.message);
    } finally {
      setJoining(false);
    }
  }

  async function submitPost(e) {
    e.preventDefault();
    if (!text.trim()) return;
    setPosting(true);
    setError("");
    try {
      const post = await communitiesApi.post(token, slug, text.trim());
      setPosts((prev) => [post, ...prev]);
      setText("");
    } catch (err) {
      setError(err.message);
    } finally {
      setPosting(false);
    }
  }

  if (loading) {
    return (
      <div className="feed-wrap">
        <p className="hint">Loading…</p>
      </div>
    );
  }

  if (!community) {
    return (
      <div className="feed-wrap">
        <div className="error">{error || "Community not found"}</div>
        <Link to="/communities">Back to Communities</Link>
      </div>
    );
  }

  return (
    <div className="feed-wrap surface-page">
      <div className="feed-header surface-header-row">
        <div>
          <Link to="/communities" className="back-link">
            ← Communities
          </Link>
          <h1>{community.name}</h1>
          {community.description ? <p className="hint">{community.description}</p> : null}
          <p className="surface-meta">{community.member_count} members</p>
        </div>
        <button
          type="button"
          className={community.is_member ? "btn btn-secondary" : "btn btn-primary"}
          disabled={joining}
          onClick={toggleMembership}
        >
          {joining ? "…" : community.is_member ? "Leave" : "Join"}
        </button>
      </div>

      {error && <div className="error">{error}</div>}

      {community.is_member ? (
        <form className="compose surface-compose" onSubmit={submitPost}>
          <div className="compose-row">
            <Avatar
              name={user?.display_name}
              username={user?.username}
              url={user?.avatar_url}
              size={40}
            />
            <div className="compose-body">
              <MentionTextarea
                placeholder={`Share with ${community.name}… type @ to tag`}
                value={text}
                onChange={setText}
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
        <p className="hint">Join to post in this community.</p>
      )}

      {posts.length === 0 ? (
        <div className="empty-state">
          <p className="empty-state-title">No posts yet</p>
          <p className="hint">Be the first to start the conversation.</p>
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
