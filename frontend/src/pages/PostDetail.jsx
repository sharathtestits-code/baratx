import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { postsApi, socialApi } from "../api";
import { useAuth } from "../context/AuthContext";
import PostCard from "../components/PostCard";
import Avatar from "../components/Avatar";
import ReplyItem from "../components/ReplyItem";

export default function PostDetail() {
  const { postId } = useParams();
  const { token, user } = useAuth();
  const navigate = useNavigate();

  const [post, setPost] = useState(null);
  const [replies, setReplies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [replyText, setReplyText] = useState("");
  const [parentReply, setParentReply] = useState(null);
  const [replyBusy, setReplyBusy] = useState(false);
  const [replyError, setReplyError] = useState("");

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [postId, token]);

  async function load() {
    setLoading(true);
    setError("");
    try {
      const [postData, replyData] = await Promise.all([
        postsApi.get(postId, token),
        socialApi.listReplies(postId),
      ]);
      setPost(postData);
      setReplies(replyData);
    } catch (err) {
      setError(err.message);
      setPost(null);
    } finally {
      setLoading(false);
    }
  }

  async function submitReply(e) {
    e.preventDefault();
    if (!replyText.trim() || !token) return;
    setReplyBusy(true);
    setReplyError("");
    try {
      const newReply = await socialApi.createReply(
        token,
        postId,
        replyText.trim(),
        parentReply?.id
      );
      setReplies((prev) => [...prev, newReply]);
      setPost((p) => (p ? { ...p, reply_count: (p.reply_count || 0) + 1 } : p));
      setReplyText("");
      setParentReply(null);
    } catch (err) {
      setReplyError(err.message);
    } finally {
      setReplyBusy(false);
    }
  }

  function handleDeleted() {
    navigate("/feed");
  }

  if (loading) return <div className="page-loading">Loading post...</div>;
  if (error && !post) {
    return (
      <div className="feed-wrap">
        <div className="post-detail-topbar">
          <button type="button" className="back-btn" onClick={() => navigate(-1)}>
            ← Back
          </button>
          <h1 className="feed-title">Post</h1>
        </div>
        <div className="error">{error}</div>
      </div>
    );
  }
  if (!post) return null;

  return (
    <div className="feed-wrap">
      <div className="post-detail-topbar">
        <button type="button" className="back-btn" onClick={() => navigate(-1)}>
          ← Back
        </button>
        <h1 className="feed-title">Post</h1>
      </div>

      <div className="post-list">
        <PostCard post={post} onDeleted={handleDeleted} detailMode />
      </div>

      <div className="post-detail-replies">
        <h2 className="section-title">Replies</h2>
        {replies.length === 0 ? (
          <p className="hint profile-posts-hint">No replies yet. Be the first.</p>
        ) : (
          <div className="detail-reply-list">
            {replies.map((r) => (
              <ReplyItem key={r.id} reply={r} onReplyTo={setParentReply} />
            ))}
          </div>
        )}

        {token ? (
          <form className="reply-form detail-reply-form" onSubmit={submitReply}>
            <Avatar name={user?.display_name} username={user?.username} url={user?.avatar_url} size={36} />
            <div className="reply-compose-col">
              {parentReply && (
                <div className="replying-to">
                  Replying to @{parentReply.author.username}{" "}
                  <button type="button" onClick={() => setParentReply(null)}>
                    Cancel
                  </button>
                </div>
              )}
              <input
                id="post-reply-composer"
                type="text"
                placeholder={parentReply ? `Reply to @${parentReply.author.username}` : "Post your reply"}
                value={replyText}
                onChange={(e) => setReplyText(e.target.value)}
                maxLength={500}
              />
            </div>
            <button type="submit" disabled={replyBusy || !replyText.trim()}>
              {replyBusy ? "..." : "Reply"}
            </button>
          </form>
        ) : (
          <p className="hint profile-posts-hint">
            <Link to="/login">Log in</Link> to reply.
          </p>
        )}
        {replyError && <div className="error">{replyError}</div>}
      </div>
    </div>
  );
}
