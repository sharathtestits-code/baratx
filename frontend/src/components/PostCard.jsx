import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { postsApi, socialApi, mediaUrl } from "../api";
import { useAuth } from "../context/AuthContext";
import Avatar from "./Avatar";
import { badgeNameClass } from "./OfficialBadge";
import { IconBookmark, IconHeart, IconQuote, IconReply, IconRepost, IconTrash } from "./Icons";
import { linkifyText } from "./linkifyText";
import { formatLocalWhen, timeAgo } from "../time";

export default function PostCard({ post, repostedBy = null, onDeleted = () => {}, detailMode = false }) {
  const { token, user } = useAuth();
  const navigate = useNavigate();

  const [liked, setLiked] = useState(post.liked_by_me);
  const [likeCount, setLikeCount] = useState(post.like_count);
  const [likeBusy, setLikeBusy] = useState(false);

  const [myReactions, setMyReactions] = useState(() =>
    Array.isArray(post.my_reactions) ? post.my_reactions : []
  );
  const [reactionCounts, setReactionCounts] = useState({
    helpful: post.reaction_helpful || 0,
    counterpoint: post.reaction_counterpoint || 0,
    mind_changed: post.reaction_mind_changed || 0,
  });
  const [reactionBusy, setReactionBusy] = useState("");

  const [reposted, setReposted] = useState(post.reposted_by_me);
  const [repostCount, setRepostCount] = useState(post.repost_count);
  const [repostBusy, setRepostBusy] = useState(false);

  const [bookmarked, setBookmarked] = useState(!!post.bookmarked_by_me);
  const [bookmarkBusy, setBookmarkBusy] = useState(false);

  const [deleted, setDeleted] = useState(false);
  const [deleteBusy, setDeleteBusy] = useState(false);
  const [confirmDelete, setConfirmDelete] = useState(false);
  const [replyCount] = useState(post.reply_count);
  const [nowMs, setNowMs] = useState(() => Date.now());

  const isMine =
    !!user &&
    (user.id === post.author?.id || user.username === post.author?.username);
  const postPath = `/posts/${post.id}`;
  const whenLabel = timeAgo(post.created_at, nowMs);
  const whenTitle = formatLocalWhen(post.created_at);

  useEffect(() => {
    const id = window.setInterval(() => setNowMs(Date.now()), 60000);
    return () => window.clearInterval(id);
  }, []);

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

  async function toggleReaction(kind) {
    if (!token || reactionBusy || isMine) return;
    setReactionBusy(kind);
    const had = myReactions.includes(kind);
    setMyReactions((prev) => (had ? prev.filter((k) => k !== kind) : [...prev, kind]));
    setReactionCounts((prev) => ({
      ...prev,
      [kind]: Math.max(0, (prev[kind] || 0) + (had ? -1 : 1)),
    }));
    try {
      const updated = had
        ? await socialApi.removeReaction(token, post.id, kind)
        : await socialApi.addReaction(token, post.id, kind);
      setMyReactions(Array.isArray(updated.my_reactions) ? updated.my_reactions : []);
      setReactionCounts({
        helpful: updated.reaction_helpful || 0,
        counterpoint: updated.reaction_counterpoint || 0,
        mind_changed: updated.reaction_mind_changed || 0,
      });
    } catch {
      setMyReactions((prev) => (had ? [...prev, kind] : prev.filter((k) => k !== kind)));
      setReactionCounts((prev) => ({
        ...prev,
        [kind]: Math.max(0, (prev[kind] || 0) + (had ? 1 : -1)),
      }));
    } finally {
      setReactionBusy("");
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
    if (!confirmDelete) {
      setConfirmDelete(true);
      return;
    }
    setDeleteBusy(true);
    try {
      await postsApi.remove(token, post.id);
      setDeleted(true);
      onDeleted(post.id);
    } catch (err) {
      window.alert(err.message || "Could not delete this post. Try again.");
      setConfirmDelete(false);
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

  const [reportOpen, setReportOpen] = useState(false);
  const [reportBusy, setReportBusy] = useState(false);

  async function handleReport(reason) {
    if (!token || reportBusy) return;
    setReportBusy(true);
    try {
      await socialApi.report(token, { reason, target_post_id: post.id });
      setReportOpen(false);
      window.alert("Report submitted. Thanks — humans review this.");
    } catch (err) {
      window.alert(err.message);
    } finally {
      setReportBusy(false);
    }
  }

  if (deleted) return null;

  return (
    <article className={`post${detailMode ? " post-detail-card" : ""}${post.mentions_me ? " post-tagged-me" : ""}`}>
      {post.mentions_me && (
        <div className="mention-tag">
          Tagged you
        </div>
      )}
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
            <Link to={`/u/${post.author.username}`} className={badgeNameClass(post.author, "post-author")}>
              {post.author.display_name}
            </Link>
            <Link to={`/u/${post.author.username}`} className={badgeNameClass(post.author, "post-username")}>
              @{post.author.username}
            </Link>
            {post.likely_ai ? <span className="ai-draft-tag">Possible AI draft</span> : null}
            <span className="post-dot">·</span>
            {detailMode ? (
              <span className="post-time" title={whenTitle}>
                {whenLabel}
              </span>
            ) : (
              <Link to={postPath} className="post-time" title={whenTitle || "View post"}>
                {whenLabel}
              </Link>
            )}
          </div>
          <p className="post-text">{linkifyText(post.text)}</p>
          {post.image_url && (
            <img className="post-image" src={mediaUrl(post.image_url)} alt="" />
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
                <strong className={badgeNameClass(post.quoted_post.author)}>{post.quoted_post.author.display_name}</strong>
                <span className={badgeNameClass(post.quoted_post.author)}>@{post.quoted_post.author.username}</span>
              </div>
              <p>{post.quoted_post.text}</p>
            </Link>
          )}

          <div className="post-actions">
            <button
              type="button"
              className="action-btn reply-action"
              onClick={handleReplyClick}
              title={detailMode ? "Join conversation" : "Join conversation"}
              aria-label="Join conversation"
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
              title={token ? "Echo" : "Log in to echo"}
              aria-label="Echo"
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
              title={token ? "Spark" : "Log in to spark"}
              aria-label="Spark"
            >
              <span className="action-icon-wrap">
                <IconHeart filled={liked} />
              </span>
              <span>{likeCount}</span>
            </button>
            {token && !isMine ? (
              <div className="substance-reactions" role="group" aria-label="Substance reactions">
                <button
                  type="button"
                  className={`action-btn reaction-btn${myReactions.includes("helpful") ? " active" : ""}`}
                  onClick={() => toggleReaction("helpful")}
                  disabled={!!reactionBusy}
                  title="Helpful"
                >
                  Helpful{reactionCounts.helpful ? ` ${reactionCounts.helpful}` : ""}
                </button>
                <button
                  type="button"
                  className={`action-btn reaction-btn${myReactions.includes("counterpoint") ? " active" : ""}`}
                  onClick={() => toggleReaction("counterpoint")}
                  disabled={!!reactionBusy}
                  title="Best counterpoint"
                >
                  Counter{reactionCounts.counterpoint ? ` ${reactionCounts.counterpoint}` : ""}
                </button>
                <button
                  type="button"
                  className={`action-btn reaction-btn${myReactions.includes("mind_changed") ? " active" : ""}`}
                  onClick={() => toggleReaction("mind_changed")}
                  disabled={!!reactionBusy}
                  title="Changed my mind"
                >
                  Mind{reactionCounts.mind_changed ? ` ${reactionCounts.mind_changed}` : ""}
                </button>
              </div>
            ) : (reactionCounts.helpful || reactionCounts.counterpoint || reactionCounts.mind_changed) ? (
              <p className="hint substance-reaction-summary">
                {[
                  reactionCounts.helpful ? `Helpful ${reactionCounts.helpful}` : null,
                  reactionCounts.counterpoint ? `Counter ${reactionCounts.counterpoint}` : null,
                  reactionCounts.mind_changed ? `Mind ${reactionCounts.mind_changed}` : null,
                ]
                  .filter(Boolean)
                  .join(" · ")}
              </p>
            ) : null}
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
                className={`action-btn delete-action${confirmDelete ? " is-confirm" : ""}`}
                onClick={handleDelete}
                disabled={deleteBusy}
                title={confirmDelete ? "Tap again to confirm delete" : "Delete post"}
                aria-label={confirmDelete ? "Confirm delete post" : "Delete post"}
              >
                <span className="action-icon-wrap">
                  <IconTrash />
                </span>
                {confirmDelete ? <span className="delete-confirm-label">Delete?</span> : null}
              </button>
            ) : (
              token && (
                <button
                  type="button"
                  className="action-btn report-action"
                  onClick={() => setReportOpen((v) => !v)}
                  title="Report"
                  aria-expanded={reportOpen}
                >
                  …
                </button>
              )
            )}
          </div>
          {reportOpen ? (
            <div className="post-report-sheet" role="group" aria-label="Report reasons">
              <p className="hint">Why report this take?</p>
              {[
                "AI / bot slop",
                "Spam or promo",
                "Harassment",
                "Impersonation",
                "Illegal / unsafe",
              ].map((reason) => (
                <button
                  key={reason}
                  type="button"
                  className="btn btn-secondary post-report-reason"
                  disabled={reportBusy}
                  onClick={() => handleReport(reason)}
                >
                  {reason}
                </button>
              ))}
              <button type="button" className="text-btn" onClick={() => setReportOpen(false)}>
                Cancel
              </button>
            </div>
          ) : null}
          {isMine && confirmDelete ? (
            <p className="hint post-delete-hint">
              Tap Delete? again to remove this post.{" "}
              <button type="button" className="text-btn" onClick={() => setConfirmDelete(false)}>
                Cancel
              </button>
            </p>
          ) : null}
        </div>
      </div>
    </article>
  );
}
