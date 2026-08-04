import { useState } from "react";
import { Link } from "react-router-dom";
import { socialApi } from "../api";
import { useAuth } from "../context/AuthContext";
import Avatar from "./Avatar";
import { IconHeart } from "./Icons";

export default function ReplyItem({ reply }) {
  const { token } = useAuth();
  const [liked, setLiked] = useState(reply.liked_by_me);
  const [likeCount, setLikeCount] = useState(reply.like_count);
  const [busy, setBusy] = useState(false);

  async function toggleLike() {
    if (!token || busy) return;
    setBusy(true);
    const wasLiked = liked;
    setLiked(!wasLiked);
    setLikeCount((c) => (wasLiked ? c - 1 : c + 1));
    try {
      const updated = wasLiked
        ? await socialApi.unlikeReply(token, reply.id)
        : await socialApi.likeReply(token, reply.id);
      setLiked(updated.liked_by_me);
      setLikeCount(updated.like_count);
    } catch (err) {
      setLiked(wasLiked);
      setLikeCount((c) => (wasLiked ? c + 1 : c - 1));
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="reply">
      <Link to={`/u/${reply.author.username}`}>
        <Avatar name={reply.author.display_name} username={reply.author.username} url={reply.author.avatar_url} size={32} />
      </Link>
      <div className="reply-body">
        <div className="reply-head">
          <Link to={`/u/${reply.author.username}`} className="reply-author">
            {reply.author.display_name}
          </Link>
          <Link to={`/u/${reply.author.username}`} className="reply-username">
            @{reply.author.username}
          </Link>
        </div>
        <p className="reply-text">{reply.text}</p>
        <button
          type="button"
          className={`reply-like-btn ${liked ? "active" : ""}`}
          onClick={toggleLike}
          disabled={!token || busy}
          title={token ? "Like" : "Log in to like"}
        >
          <IconHeart filled={liked} className="reply-like-icon" /> <span>{likeCount}</span>
        </button>
      </div>
    </div>
  );
}
