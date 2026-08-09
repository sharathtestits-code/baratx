import { useCallback, useEffect, useRef, useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { api, postsApi, spacesApi, topicsApi } from "../api";
import { useAuth } from "../context/AuthContext";
import PostCard from "../components/PostCard";
import Avatar from "../components/Avatar";
import FirstSessionGuide from "../components/FirstSessionGuide";
import FoundingChip from "../components/FoundingChip";
import EmptyState from "../components/EmptyState";
import TodaysSquare from "../components/TodaysSquare";
import MentionTextarea from "../components/MentionTextarea";
import { IconImage, IconClose, IconLive } from "../components/Icons";
import { useInfiniteScroll } from "../hooks/useInfiniteScroll";
import { hasSeenTopicOnboarding, markTopicOnboardingSeen } from "../topicsOnboarding";

const MAX_LEN = 500;
const PAGE_SIZE = 20;

const STARTER_PROMPTS = [
  "What's one thing India gets wrong in public debate?",
  "Drop your hottest take on startups in India.",
  "Who should every BarathX user follow in your city?",
  "What should this public square never become?",
  "In my city, the real problem is ",
];

function feedItemKey(item) {
  const prefix = item.reposted_by ? "repost-" + item.reposted_by.username + "-" : "post-";
  return prefix + item.post.id;
}

export default function Feed() {
  const { token, user, loading } = useAuth();
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const quotePostId = searchParams.get("quote");
  const wantWelcome =
    searchParams.get("welcome") === "1" || sessionStorage.getItem("bx_welcome") === "1";

  const [tab, setTab] = useState("global");
  const [items, setItems] = useState([]);
  const [feedLoading, setFeedLoading] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [hasMore, setHasMore] = useState(true);
  const [feedError, setFeedError] = useState("");

  const [text, setText] = useState("");
  const [imageFile, setImageFile] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [quotePreview, setQuotePreview] = useState(null);
  const [posting, setPosting] = useState(false);
  const [postError, setPostError] = useState("");
  const [showFirstSession, setShowFirstSession] = useState(() => {
    try {
      return localStorage.getItem("bx_first_post_done") !== "1";
    } catch {
      return true;
    }
  });
  const [showStarters, setShowStarters] = useState(false);
  const [liveDebates, setLiveDebates] = useState([]);
  const [civicProblem, setCivicProblem] = useState(false);
  const [foundingRefresh, setFoundingRefresh] = useState(0);

  const fileInputRef = useRef(null);
  const composeRef = useRef(null);
  const loadingMoreRef = useRef(false);

  const loadFeed = useCallback(
    async (nextTab) => {
      if (!token) return;
      setFeedLoading(true);
      setFeedError("");
      setHasMore(true);
      try {
        const data = await postsApi.list(token, { feed: nextTab });
        setItems(Array.isArray(data) ? data : []);
        setHasMore((Array.isArray(data) ? data : []).length >= PAGE_SIZE);
      } catch (err) {
        setFeedError(err.message);
        setItems([]);
        setHasMore(false);
      } finally {
        setFeedLoading(false);
      }
    },
    [token]
  );

  const loadMore = useCallback(async () => {
    if (!token || loadingMoreRef.current || !hasMore || items.length === 0) return;
    loadingMoreRef.current = true;
    setLoadingMore(true);
    const before = items[items.length - 1]?.item_time;
    try {
      const data = await postsApi.list(token, { feed: tab, before });
      setItems((prev) => {
        const seen = new Set(prev.map((i) => i.post.id));
        const next = [...prev];
        for (const item of data || []) {
          if (!seen.has(item.post.id)) {
            seen.add(item.post.id);
            next.push(item);
          }
        }
        return next;
      });
      setHasMore((data || []).length >= PAGE_SIZE);
    } catch (err) {
      setFeedError(err.message);
    } finally {
      loadingMoreRef.current = false;
      setLoadingMore(false);
    }
  }, [token, hasMore, items, tab]);

  const setSentinel = useInfiniteScroll({
    disabled:
      showFirstSession || feedLoading || loadingMore || !hasMore || items.length === 0 || !user,
    onLoadMore: loadMore,
  });

  useEffect(() => {
    if (!token) return undefined;
    let cancelled = false;
    spacesApi
      .listForYou(token)
      .then((rows) => {
        if (cancelled) return;
        if (rows && rows.length > 0) {
          setLiveDebates(rows);
          return;
        }
        return spacesApi.listDebates(token);
      })
      .then((rows) => {
        if (!cancelled && Array.isArray(rows)) setLiveDebates(rows);
      })
      .catch(() => {});
    return () => {
      cancelled = true;
    };
  }, [token]);

  useEffect(() => {
    if (!token || !user) return;
    if (hasSeenTopicOnboarding()) return;
    topicsApi
      .mine(token)
      .then((rows) => {
        if (rows && rows.length > 0) markTopicOnboardingSeen();
      })
      .catch(() => {
        markTopicOnboardingSeen();
      });
  }, [token, user]);

  useEffect(() => {
    if (wantWelcome) {
      sessionStorage.setItem("bx_welcome", "1");
      setShowFirstSession(true);
    }
  }, [wantWelcome]);

  useEffect(() => {
    if (!loading && token && !user) return;
    if (!loading && !token) {
      navigate("/login");
    }
  }, [loading, token, user, navigate]);

  useEffect(() => {
    if (user && !showFirstSession) loadFeed(tab);
  }, [user, tab, loadFeed, showFirstSession]);

  useEffect(() => {
    let cancelled = false;
    async function loadQuote() {
      if (!quotePostId || !token) {
        setQuotePreview(null);
        return;
      }
      try {
        const post = await postsApi.get(quotePostId, token);
        if (cancelled) return;
        setQuotePreview(post);
        setText((prev) => {
          const tag = `@${post.author.username} `;
          if (!prev.trim()) return tag;
          if (prev.includes(`@${post.author.username}`)) return prev;
          return `${tag}${prev}`.slice(0, MAX_LEN);
        });
      } catch {
        if (!cancelled) setQuotePreview(null);
      }
    }
    loadQuote();
    return () => {
      cancelled = true;
    };
  }, [quotePostId, token]);

  useEffect(() => {
    if (!user || !token) return;
    if (localStorage.getItem("bx_first_post_done") === "1") {
      setShowFirstSession(false);
      return;
    }
    let cancelled = false;
    api
      .getUserPosts(user.username, token)
      .then((posts) => {
        if (cancelled) return;
        if (!Array.isArray(posts) || posts.length === 0) {
          setShowFirstSession(true);
        } else {
          localStorage.setItem("bx_first_post_done", "1");
          setShowFirstSession(false);
        }
      })
      .catch(() => {});
    return () => {
      cancelled = true;
    };
  }, [user, token]);

  async function finishFirstSession() {
    setShowFirstSession(false);
    markTopicOnboardingSeen();
    setFoundingRefresh((n) => n + 1);
    await loadFeed(tab);
  }

  function handleImageChange(e) {
    const file = e.target.files?.[0];
    if (!file) return;
    setImageFile(file);
    setImagePreview(URL.createObjectURL(file));
  }

  function clearImage() {
    setImageFile(null);
    setImagePreview(null);
    if (fileInputRef.current) fileInputRef.current.value = "";
  }

  async function handlePost(e) {
    e.preventDefault();
    setPostError("");
    if (!text.trim()) {
      setPostError("Write something first.");
      return;
    }
    setPosting(true);
    try {
      const newPost = await postsApi.create(token, {
        text: text.trim(),
        image: imageFile,
        quotePostId: quotePostId || undefined,
        civicProblem: civicProblem || undefined,
      });
      setItems((prev) => [{ post: newPost, reposted_by: null, item_time: newPost.created_at }, ...prev]);
      setText("");
      setCivicProblem(false);
      clearImage();
      if (quotePostId) {
        setSearchParams({});
        setQuotePreview(null);
      }
      localStorage.setItem("bx_first_post_done", "1");
      sessionStorage.removeItem("bx_welcome");
      setShowFirstSession(false);
      setFoundingRefresh((n) => n + 1);
      window.dispatchEvent(new CustomEvent("bx:first-post"));
      api.bootstrapFollows(token).catch(() => {});
    } catch (err) {
      setPostError(err.message);
    } finally {
      setPosting(false);
    }
  }

  function handleDeleted(postId) {
    setItems((prev) => prev.filter((i) => i.post.id !== postId));
  }

  if (loading || (token && !user)) {
    return <div className="page-loading">Loading…</div>;
  }

  if (!user) {
    return null;
  }

  const remaining = MAX_LEN - text.length;
  const charCountClass = remaining < 20 ? "char-count char-count-low" : "char-count";

  // First session: one guided screen only — no stacked strips / feed.
  if (showFirstSession) {
    return (
      <div className="plaza-page plaza-square plaza-square-first">
        <FirstSessionGuide token={token} onComplete={finishFirstSession} />
      </div>
    );
  }

  return (
    <div className="plaza-page plaza-square">
      <header className="square-home-head">
        <div className="square-home-head-main">
          <p className="square-home-kicker">India&apos;s public square</p>
          <h1 className="square-home-title">Square</h1>
          <p className="square-home-sub">One question. Your take. No Reels required.</p>
        </div>
        <FoundingChip refreshKey={foundingRefresh} />
      </header>

      <TodaysSquare
        onAnswer={(question) => {
          setText(`${question}\n\n`);
          composeRef.current?.focus?.();
          window.scrollTo({ top: 0, behavior: "smooth" });
        }}
      />

      <form className="plaza-studio compose" onSubmit={handlePost}>
        <div className="plaza-studio-head">
          <Avatar name={user?.display_name} username={user?.username} url={user?.avatar_url} size={44} />
          <div>
            <p className="plaza-studio-label">Drop a take</p>
            <p className="hint">Short post. Real replies.</p>
          </div>
        </div>
        <div className="compose-body">
          <MentionTextarea
            ref={composeRef}
            placeholder={
              quotePreview ? "Add a comment and tag people with @…" : "What's your take?"
            }
            value={text}
            onChange={setText}
            maxLength={MAX_LEN}
            rows={3}
          />
          {imagePreview && (
            <div className="image-preview">
              <img src={imagePreview} alt="attachment preview" />
              <button type="button" className="remove-image" onClick={clearImage}>
                <IconClose />
              </button>
            </div>
          )}
          {quotePreview && (
            <div className="quoted-post compose-quote">
              <div className="quoted-head">
                Quoting @{quotePreview.author.username}
                <button
                  type="button"
                  className="remove-image"
                  onClick={() => {
                    setSearchParams({});
                    setQuotePreview(null);
                  }}
                >
                  <IconClose />
                </button>
              </div>
              <p>{quotePreview.text}</p>
            </div>
          )}
          {postError && <div className="error">{postError}</div>}
          <div className="compose-studio-tiles" aria-label="Create studio">
            <button type="button" className="compose-tile" onClick={() => fileInputRef.current?.click()}>
              Photo
            </button>
            <button
              type="button"
              className={`compose-tile compose-tile-starters${showStarters ? " is-open" : ""}`}
              aria-expanded={showStarters}
              onClick={() => setShowStarters((v) => !v)}
              title="Starter prompts — not AI drafts"
            >
              Hot take starters
            </button>
            <Link to="/spaces" className="compose-tile">
              Start a live
            </Link>
            <Link to="/communities" className="compose-tile">
              Community
            </Link>
          </div>
          {showStarters && (
            <div className="compose-starters-sheet" role="listbox" aria-label="Starter prompts">
              {STARTER_PROMPTS.map((prompt) => (
                <button
                  key={prompt}
                  type="button"
                  className="compose-starter-chip"
                  onClick={() => {
                    setText(prompt);
                    setShowStarters(false);
                    composeRef.current?.focus?.();
                  }}
                >
                  {prompt}
                </button>
              ))}
            </div>
          )}
          <label className="compose-civic">
            <input
              type="checkbox"
              checked={civicProblem}
              onChange={(e) => setCivicProblem(e.target.checked)}
            />
            <span>This is a real civic / city problem</span>
          </label>
          <div className="compose-footer">
            <label className="attach-btn" title="Add image">
              <IconImage />
              <input
                ref={fileInputRef}
                type="file"
                accept="image/png,image/jpeg,image/gif,image/webp"
                onChange={handleImageChange}
                hidden
              />
            </label>
            {text.length > 0 && <span className={charCountClass}>{remaining}</span>}
            <button type="submit" className="post-btn" disabled={posting || !text.trim()}>
              {posting ? "Posting..." : "Post"}
            </button>
          </div>
        </div>
      </form>

      {liveDebates.length > 0 && (
        <section className="plaza-onair" aria-label="Live now">
          <div className="plaza-onair-head">
            <h2>
              <IconLive className="plaza-onair-icon" aria-hidden="true" /> Live now
            </h2>
            <Link to="/spaces">Enter Live</Link>
          </div>
          <ul className="plaza-onair-list">
            {liveDebates.slice(0, 3).map((d) => (
              <li key={d.id}>
                <Link to={`/spaces/${d.id}`} className="plaza-onair-card">
                  <span className="live-pill">Live</span>
                  <strong>{d.title}</strong>
                  <span className="hint">{d.topic_name || d.arena_name || "Debate"}</span>
                </Link>
              </li>
            ))}
          </ul>
        </section>
      )}

      <section className="plaza-takes">
        <div className="plaza-takes-head">
          <h2>Takes from the square</h2>
          <div className="plaza-takes-tabs">
            <button
              type="button"
              className={tab === "global" ? "is-active" : ""}
              onClick={() => setTab("global")}
            >
              For you
            </button>
            <button
              type="button"
              className={tab === "following" ? "is-active" : ""}
              onClick={() => setTab("following")}
            >
              Following
            </button>
          </div>
        </div>

        {feedError && <div className="error">{feedError}</div>}
        {feedLoading ? (
          <div className="skeleton-list">
            {[1, 2, 3].map((i) => (
              <div className="skeleton-post" key={i}>
                <div className="skeleton-avatar" />
                <div className="skeleton-lines">
                  <div className="skeleton-line short" />
                  <div className="skeleton-line" />
                  <div className="skeleton-line medium" />
                </div>
              </div>
            ))}
          </div>
        ) : items.length === 0 ? (
          <EmptyState
            title={tab === "following" ? "Nothing here yet" : "No takes yet"}
            hint={
              tab === "following"
                ? "Follow people in Explore, then come back."
                : "Be the first voice in the square."
            }
            primaryLabel={tab === "following" ? "Explore people" : "Write a take"}
            primaryTo={tab === "following" ? "/search" : undefined}
            onPrimary={
              tab === "following"
                ? undefined
                : () => {
                    composeRef.current?.focus?.();
                    window.scrollTo({ top: 0, behavior: "smooth" });
                  }
            }
            secondaryLabel="Start a debate"
            secondaryTo="/spaces"
          />
        ) : (
          <>
            <div className="post-list plaza-take-list">
              {items.map((item) => (
                <PostCard
                  key={feedItemKey(item)}
                  post={item.post}
                  repostedBy={item.reposted_by}
                  onDeleted={handleDeleted}
                />
              ))}
            </div>
            <div ref={setSentinel} className="scroll-sentinel" aria-hidden="true" />
            {loadingMore && <p className="hint load-more-hint">Loading more...</p>}
            {!hasMore && items.length > 0 && (
              <p className="hint load-more-hint">You are all caught up.</p>
            )}
          </>
        )}
      </section>
    </div>
  );
}
