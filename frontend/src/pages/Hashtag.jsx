import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { socialApi } from "../api";
import { useAuth } from "../context/AuthContext";
import PostCard from "../components/PostCard";

export default function Hashtag() {
  const { tag } = useParams();
  const { token } = useAuth();
  const navigate = useNavigate();
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let cancelled = false;
    async function load() {
      setLoading(true);
      try {
        const data = await socialApi.hashtag(tag, token);
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
  }, [tag, token]);

  return (
    <div className="feed-wrap">
      <div className="feed-header follow-list-header">
        <button type="button" className="back-btn" onClick={() => navigate(-1)}>
          ←
        </button>
        <div>
          <h1>#{tag}</h1>
        </div>
      </div>
      {loading ? (
        <p className="hint">Loading…</p>
      ) : error ? (
        <div className="error">{error}</div>
      ) : posts.length === 0 ? (
        <div className="empty-state">
          <p className="empty-state-title">No posts with #{tag}</p>
        </div>
      ) : (
        <div className="post-list">
          {posts.map((post) => (
            <PostCard key={post.id} post={post} />
          ))}
        </div>
      )}
    </div>
  );
}
