import { useEffect, useState } from "react";
import { socialApi } from "../api";
import { useAuth } from "../context/AuthContext";
import PostCard from "../components/PostCard";
import EmptyState from "../components/EmptyState";

export default function Bookmarks() {
  const { token } = useAuth();
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let cancelled = false;
    async function load() {
      setLoading(true);
      try {
        const data = await socialApi.listBookmarks(token);
        if (!cancelled) setPosts(data);
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
  }, [token]);

  return (
    <div className="feed-wrap">
      <div className="feed-header">
        <h1>Bookmarks</h1>
      </div>
      {loading ? (
        <p className="hint">Loading…</p>
      ) : error ? (
        <div className="error">{error}</div>
      ) : posts.length === 0 ? (
        <EmptyState
          title="No bookmarks yet"
          hint="Save posts with the bookmark icon to find them here."
          primaryTo="/feed"
          primaryLabel="Back to Square"
          secondaryTo="/search"
          secondaryLabel="Explore"
        />
      ) : (
        <div className="post-list">
          {posts.map((post) => (
            <PostCard key={post.id} post={post} onDeleted={(id) => setPosts((p) => p.filter((x) => x.id !== id))} />
          ))}
        </div>
      )}
    </div>
  );
}
