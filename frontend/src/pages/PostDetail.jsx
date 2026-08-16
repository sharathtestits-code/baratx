import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { postsApi, socialApi } from "../api";
import { useAuth } from "../context/AuthContext";
import PostCard from "../components/PostCard";
import Avatar from "../components/Avatar";
import ReplyItem from "../components/ReplyItem";
import MentionTextarea from "../components/MentionTextarea";

const MAX_REPLY_LEN = 220;

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

  function handleReplyTo(reply) {
    setParentReply(reply);
    const tag = `@${reply.author.username} `;
    setReplyText((prev) => (prev.trim().startsWith(`@${reply.author.username}`) ? prev : tag));
  }

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

  function goBack() {
    if (window.history.length > 1) navigate(-1);
    else navigate("/feed");
  }

  if (loading) return <div className="page-loading">Loading post...</div>;
  if (error && !post) {
    return (
      <div className="feed-wrap">
        <div className="post-detail-topbar">
          <button type="button" className="post-detail-back" onClick={goBack} aria-label="Go back">
            <svg viewBox="0 0 24 24" className="post-detail-back-icon" aria-hidden="true">
              <path
                d="M15 18l-6-6 6-6"
                fill="none"
                stroke="currentColor"
                strokeWidth="2.2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          </button>
          <h1 className="post-detail-title">Post</h1>
        </div>
        <div className="error">{error}</div>
      </div>
    );
  }
  if (!post) return null;

  return (
    <div className="feed-wrap">
      <div className="post-detail-topbar">
        <button type="button" className="post-detail-back" onClick={goBack} aria-label="Go back">
          <svg viewBox="0 0 24 24" className="post-detail-back-icon" aria-hidden="true">
            <path
              d="M15 18l-6-6 6-6"
              fill="none"
              stroke="currentColor"
              strokeWidth="2.2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        </button>
        <h1 className="post-detail-title">Post</h1>
      </div>

      <div className="post-list post-detail-main">
        <PostCard post={post} onDeleted={handleDeleted} detailMode />
      </div>

      {token ? (
        <form className="detail-reply-composer" onSubmit={submitReply}>
          <div className="detail-reply-composer-row">
            <Avatar
              name={user?.display_name}
              username={user?.username}
              url={user?.avatar_url}
              size={44}
            />
            <div className="detail-reply-composer-body">
              {parentReply && (
                <div className="replying-to">
                  Replying to @{parentReply.author.username}{" "}
                  <button type="button" onClick={() => setParentReply(null)}>
                    Cancel
                  </button>
                </div>
              )}
              <MentionTextarea
                id="post-reply-composer"
                placeholder={
                  parentReply
                    ? `Reply to @${parentReply.author.username}`
                    : "Post your reply, type @ to tag someone"
                }
                value={replyText}
                onChange={setReplyText}
                maxLength={MAX_REPLY_LEN}
                rows={3}
              />
              <div className="detail-reply-composer-footer">
                <span className="hint">{replyText.length}/{MAX_REPLY_LEN}</span>
                <button
                  type="submit"
                  className="btn btn-primary detail-reply-submit"
                  disabled={replyBusy || !replyText.trim()}
                >
                  {replyBusy ? "Replying…" : "Reply"}
                </button>
              </div>
            </div>
          </div>
          {replyError && <div className="error">{replyError}</div>}
        </form>
      ) : (
        <p className="hint profile-posts-hint detail-reply-login">
          <Link to="/login">Log in</Link> to reply.
        </p>
      )}

      <div className="post-detail-replies">
        <h2 className="section-title">Replies</h2>
        {replies.length === 0 ? (
          <p className="hint profile-posts-hint">No replies yet. Be the first.</p>
        ) : (
          <div className="detail-reply-list">
            {replies.map((r) => (
              <ReplyItem key={r.id} reply={r} onReplyTo={handleReplyTo} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
