import { useCallback, useEffect, useRef, useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { api, postsApi, spacesApi, topicsApi } from "../api";
import { useAuth } from "../context/AuthContext";
import PostCard from "../components/PostCard";
import Avatar from "../components/Avatar";
import WelcomePanel from "../components/WelcomePanel";
import SuggestedFollows from "../components/SuggestedFollows";
import TodaysSquare from "../components/TodaysSquare";
import FoundingStrip from "../components/FoundingStrip";
import RaceStrip from "../components/RaceStrip";
import MentionTextarea from "../components/MentionTextarea";
import { ARENA_TOPICS } from "../arenas";
import { IconImage, IconClose } from "../components/Icons";
import { useInfiniteScroll } from "../hooks/useInfiniteScroll";
import { hasSeenTopicOnboarding, markTopicOnboardingSeen } from "../topicsOnboarding";

const MAX_LEN = 500;
const PAGE_SIZE = 20;

function feedItemKey(item) {
  const prefix = item.reposted_by ? "repost-" + item.reposted_by.username + "-" : "post-";
  return prefix + item.post.id;
}

export default function Feed() {
  const { token, user, logout, loading } = useAuth();
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
  const [showWelcome, setShowWelcome] = useState(wantWelcome);
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
    disabled: feedLoading || loadingMore || !hasMore || items.length === 0 || !user,
    onLoadMore: loadMore,
  });

  useEffect(() => {
    if (!token) return undefined;
    let cancelled = false;
    // Prefer debates matched to the user's topic picks; fall back to all open debates.
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
    // One-time nudge only — Arenas tab is where people manage topics after this.
    topicsApi
      .mine(token)
      .then((rows) => {
        if (!rows || rows.length === 0) {
          // First empty-interests visit only — OnboardingTopics marks seen on mount.
          navigate("/onboarding/topics");
        } else {
          markTopicOnboardingSeen();
        }
      })
      .catch(() => {
        // Don't trap users in a loop if topics API fails.
        markTopicOnboardingSeen();
      });
  }, [token, user, navigate]);

  useEffect(() => {
    if (wantWelcome) {
      sessionStorage.setItem("bx_welcome", "1");
      setShowWelcome(true);
    }
  }, [wantWelcome]);

  useEffect(() => {
    if (!loading && token && !user) return;
    if (!loading && !token) {
      navigate("/login");
    }
  }, [loading, token, user, navigate]);

  useEffect(() => {
    if (user) loadFeed(tab);
  }, [user, tab, loadFeed]);

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
        // Prefill @tag so quote/repost can notify the original author.
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
    if (localStorage.getItem("bx_first_post_done") === "1") return;
    let cancelled = false;
    api
      .getUserPosts(user.username, token)
      .then((posts) => {
        if (cancelled) return;
        if (!Array.isArray(posts) || posts.length === 0) {
          setShowWelcome(true);
        } else {
          localStorage.setItem("bx_first_post_done", "1");
        }
      })
      .catch(() => {});
    return () => {
      cancelled = true;
    };
  }, [user, token]);

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
      setShowWelcome(false);
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

  return (
    <div className="feed-wrap">
      <div className="feed-topbar">
        <h1 className="feed-title">Home</h1>
        <button
          type="button"
          className="mobile-logout"
          onClick={() => {
            logout();
            navigate("/login");
          }}
        >
          Log out
        </button>
      </div>

      <form className="compose" onSubmit={handlePost}>
        <div className="compose-row">
          <Avatar name={user?.display_name} username={user?.username} url={user?.avatar_url} size={44} />
          <div className="compose-body">
            <MentionTextarea
              ref={composeRef}
              placeholder={
                quotePreview
                  ? "Add a comment and tag people with @…"
                  : showWelcome
                    ? "Say hello with your city…"
                    : "What is happening? Type @ to tag someone"
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
        </div>
      </form>

      <FoundingStrip
        key={foundingRefresh}
        onPostProblem={() => {
          setCivicProblem(true);
          if (!text.trim()) {
            setText("In my city, the real problem is ");
          }
          composeRef.current?.focus?.();
          window.scrollTo({ top: 0, behavior: "smooth" });
        }}
      />

      <RaceStrip key={`race-${foundingRefresh}`} />

      <TodaysSquare
        onAnswer={(question) => {
          setText(`${question}\n\n`);
          composeRef.current?.focus?.();
          window.scrollTo({ top: 0, behavior: "smooth" });
        }}
      />

      <section className="arena-home-strip" aria-label="Arenas">
        <div className="arena-home-strip-head">
          <h2>Arenas</h2>
          <Link to="/arenas" className="rail-card-more">
            See all
          </Link>
        </div>
        <div className="arena-home-chips">
          {ARENA_TOPICS.map((a) => (
            <Link key={a.key} to={`/arenas/${a.key}`} className="arena-home-chip" style={{ "--arena-accent": a.accent }}>
              {a.name}
            </Link>
          ))}
        </div>
        {liveDebates.length > 0 && (
          <ul className="debate-list debate-list-compact">
            {liveDebates.slice(0, 5).map((d) => (
              <li key={d.id}>
                <Link to={`/spaces/${d.id}`} className="debate-row">
                  <span className="debate-arena-tag">
                    {d.topic_name || d.arena_name || "Debate"}
                  </span>
                  <span className="debate-title">{d.title}</span>
                </Link>
              </li>
            ))}
          </ul>
        )}
        <div className="arena-home-strip-foot">
          <Link to="/onboarding/topics" className="rail-card-more">
            Edit topics
          </Link>
        </div>
      </section>

      {showWelcome && (
        <WelcomePanel token={token} text={text} setText={setText} onPostedFlag composeRef={composeRef} />
      )}

      <div className="suggested-follows-mobile">
        <SuggestedFollows
          title="Who to follow"
          note="Start with official BaratX accounts — then Explore for more."
          dismissible
        />
      </div>

      <div className="feed-tabs">
        <button
          type="button"
          className={tab === "global" ? "feed-tab active" : "feed-tab"}
          onClick={() => setTab("global")}
        >
          For you
        </button>
        <button
          type="button"
          className={tab === "following" ? "feed-tab active" : "feed-tab"}
          onClick={() => setTab("following")}
        >
          Following
        </button>
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
        <div className="empty-state">
          <p className="empty-state-title">
            {tab === "following" ? "Nothing here yet" : "No posts yet"}
          </p>
          <p className="hint">
            {tab === "following"
              ? "Tap Follow official BaratX above, or find people in Explore."
              : "Be the first to say something."}
          </p>
        </div>
      ) : (
        <>
          <div className="post-list">
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
    </div>
  );
}
