import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { API_BASE, postsApi, socialApi } from "../api";
import { useAuth } from "../context/AuthContext";
import Avatar from "./Avatar";
import { IconBookmark, IconHeart, IconQuote, IconReply, IconRepost, IconTrash } from "./Icons";

function timeAgo(dateStr) {
  const date = new Date(dateStr);
  const diffMs = Date.now() - date.getTime();
  const sec = Math.floor(diffMs / 1000);
  if (sec < 60) return `${Math.max(sec, 1)}s`;
  const min = Math.floor(sec / 60);
  if (min < 60) return `${min}m`;
  const hr = Math.floor(min / 60);
  if (hr < 24) return `${hr}h`;
  const day = Math.floor(hr / 24);
  if (day < 7) return `${day}d`;
  return date.toLocaleDateString(undefined, { month: "short", day: "numeric" });
}

function linkifyText(text) {
  const parts = text.split(/([@#][A-Za-z0-9_]{2,40})/g);
  return parts.map((part, i) => {
    if (part.startsWith("@") && part.length > 3) {
      const u = part.slice(1);
      return (
        <Link key={i} to={`/u/${u}`} className="text-link" onClick={(e) => e.stopPropagation()}>
          {part}
        </Link>
      );
    }
    if (part.startsWith("#") && part.length > 2) {
      const tag = part.slice(1);
      return (
        <Link key={i} to={`/hashtag/${tag}`} className="text-link" onClick={(e) => e.stopPropagation()}>
          {part}
        </Link>
      );
    }
    return <span key={i}>{part}</span>;
  });
}

export default function PostCard({ post, repostedBy = null, onDeleted = () => {}, detailMode = false }) {
  const { token, user } = useAuth();
  const navigate = useNavigate();

  const [liked, setLiked] = useState(post.liked_by_me);
  const [likeCount, setLikeCount] = useState(post.like_count);
  const [likeBusy, setLikeBusy] = useState(false);

  const [reposted, setReposted] = useState(post.reposted_by_me);
  const [repostCount, setRepostCount] = useState(post.repost_count);
  const [repostBusy, setRepostBusy] = useState(false);

  const [bookmarked, setBookmarked] = useState(!!post.bookmarked_by_me);
  const [bookmarkBusy, setBookmarkBusy] = useState(false);

  const [deleted, setDeleted] = useState(false);
  const [deleteBusy, setDeleteBusy] = useState(false);
  const [replyCount] = useState(post.reply_count);

  const isMine = user && user.username === post.author.username;
  const postPath = `/posts/${post.id}`;

  async function toggleLike() {
    if (!token || likeBusy) return;
    setLikeBusy(true);
    const wasLiked = liked;
    setLiked(!wasLiked);
    setLikeCount((c) => (wasLiked ? c - 1 : c + 1));
    try {
      const updated = wasLiked
        ? await socialApi.unlike(token, post.id)
        : await socialApi.like(token, post.id);
      setLiked(updated.liked_by_me);
      setLikeCount(updated.like_count);
    } catch {
      setLiked(wasLiked);
      setLikeCount((c) => (wasLiked ? c + 1 : c - 1));
    } finally {
      setLikeBusy(false);
    }
  }

  async function toggleRepost() {
    if (!token || repostBusy) return;
    setRepostBusy(true);
    const wasReposted = reposted;
    setReposted(!wasReposted);
    setRepostCount((c) => (wasReposted ? c - 1 : c + 1));
    try {
      const updated = wasReposted
        ? await socialApi.unrepost(token, post.id)
        : await socialApi.repost(token, post.id);
      setReposted(updated.reposted_by_me);
      setRepostCount(updated.repost_count);
    } catch {
      setReposted(wasReposted);
      setRepostCount((c) => (wasReposted ? c + 1 : c - 1));
    } finally {
      setRepostBusy(false);
    }
  }

  async function toggleBookmark() {
    if (!token || bookmarkBusy) return;
    setBookmarkBusy(true);
    const was = bookmarked;
    setBookmarked(!was);
    try {
      const updated = was
        ? await socialApi.unbookmark(token, post.id)
        : await socialApi.bookmark(token, post.id);
      setBookmarked(!!updated.bookmarked_by_me);
    } catch {
      setBookmarked(was);
    } finally {
      setBookmarkBusy(false);
    }
  }

  async function handleDelete() {
    if (!token || deleteBusy) return;
    if (!window.confirm("Delete this post? This can't be undone.")) return;
    setDeleteBusy(true);
    try {
      await postsApi.remove(token, post.id);
      setDeleted(true);
      onDeleted(post.id);
    } catch (err) {
      window.alert(err.message);
    } finally {
      setDeleteBusy(false);
    }
  }

  function handleReplyClick() {
    if (detailMode) {
      document.getElementById("post-reply-composer")?.focus();
      return;
    }
    navigate(postPath);
  }

  async function handleReport() {
    if (!token) return;
    const reason = window.prompt("Why are you reporting this post?");
    if (!reason || reason.trim().length < 3) return;
    try {
      await socialApi.report(token, { reason: reason.trim(), target_post_id: post.id });
      window.alert("Report submitted. Thanks.");
    } catch (err) {
      window.alert(err.message);
    }
  }

  if (deleted) return null;

  return (
    <article className={`post${detailMode ? " post-detail-card" : ""}`}>
      {repostedBy && (
        <div className="repost-tag">
          <IconRepost className="repost-tag-icon" />
          Reposted by{" "}
          <Link to={`/u/${repostedBy.username}`}>
            {repostedBy.username === user?.username ? "you" : repostedBy.display_name}
          </Link>
        </div>
      )}
      <div className="post-row">
        <Link to={`/u/${post.author.username}`}>
          <Avatar name={post.author.display_name} username={post.author.username} url={post.author.avatar_url} size={44} />
        </Link>
        <div className="post-body">
          <div className="post-head">
            <Link to={`/u/${post.author.username}`} className="post-author">
              {post.author.display_name}
            </Link>
            <Link to={`/u/${post.author.username}`} className="post-username">
              @{post.author.username}
            </Link>
            <span className="post-dot">·</span>
            {detailMode ? (
              <span className="post-time">{timeAgo(post.created_at)}</span>
            ) : (
              <Link to={postPath} className="post-time" title="View post">
                {timeAgo(post.created_at)}
              </Link>
            )}
          </div>
          <p className="post-text">{linkifyText(post.text)}</p>
          {post.image_url && (
            <img className="post-image" src={`${API_BASE}${post.image_url}`} alt="" />
          )}
          {post.quoted_post && (
            <Link to={`/posts/${post.quoted_post.id}`} className="quoted-post" onClick={(e) => e.stopPropagation()}>
              <div className="quoted-head">
                <Avatar
                  name={post.quoted_post.author.display_name}
                  username={post.quoted_post.author.username}
                  url={post.quoted_post.author.avatar_url}
                  size={20}
                />
                <strong>{post.quoted_post.author.display_name}</strong>
                <span>@{post.quoted_post.author.username}</span>
              </div>
              <p>{post.quoted_post.text}</p>
            </Link>
          )}

          <div className="post-actions">
            <button
              type="button"
              className="action-btn reply-action"
              onClick={handleReplyClick}
              title={detailMode ? "Reply" : "View post & reply"}
            >
              <span className="action-icon-wrap">
                <IconReply />
              </span>
              <span>{replyCount}</span>
            </button>
            <button
              type="button"
              className={`action-btn repost-action ${reposted ? "active" : ""}`}
              onClick={toggleRepost}
              disabled={!token || repostBusy}
              title={token ? "Repost" : "Log in to repost"}
            >
              <span className="action-icon-wrap">
                <IconRepost />
              </span>
              <span>{repostCount}</span>
            </button>
            <button
              type="button"
              className="action-btn quote-action"
              onClick={() => navigate(`/feed?quote=${post.id}`)}
              disabled={!token}
              title="Quote"
            >
              <span className="action-icon-wrap">
                <IconQuote />
              </span>
            </button>
            <button
              type="button"
              className={`action-btn like-action ${liked ? "active" : ""}`}
              onClick={toggleLike}
              disabled={!token || likeBusy}
              title={token ? "Like" : "Log in to like"}
            >
              <span className="action-icon-wrap">
                <IconHeart filled={liked} />
              </span>
              <span>{likeCount}</span>
            </button>
            <button
              type="button"
              className={`action-btn bookmark-action ${bookmarked ? "active" : ""}`}
              onClick={toggleBookmark}
              disabled={!token || bookmarkBusy}
              title={token ? "Bookmark" : "Log in to bookmark"}
            >
              <span className="action-icon-wrap">
                <IconBookmark filled={bookmarked} />
              </span>
            </button>
            {isMine ? (
              <button
                type="button"
                className="action-btn delete-action"
                onClick={handleDelete}
                disabled={deleteBusy}
                title="Delete post"
              >
                <span className="action-icon-wrap">
                  <IconTrash />
                </span>
              </button>
            ) : (
              token && (
                <button type="button" className="action-btn report-action" onClick={handleReport} title="Report">
                  …
                </button>
              )
            )}
          </div>
        </div>
      </div>
    </article>
  );
}
