import { useCallback, useEffect, useRef, useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { api, postsApi, spacesApi, topicsApi } from "../api";
import { useAuth } from "../context/AuthContext";
import PostCard from "../components/PostCard";
import Avatar from "../components/Avatar";
import FirstSessionGuide from "../components/FirstSessionGuide";
import FirstPostWelcomeModal, {
  markFirstPostWelcomeSeen,
  shouldShowFirstPostWelcome,
} from "../components/FirstPostWelcomeModal";
import CoachMarks, { shouldShowNavTour } from "../components/CoachMarks";
import FoundingChip from "../components/FoundingChip";
import SoftLaunchBanner from "../components/SoftLaunchBanner";
import SuggestionsStrip from "../components/SuggestionsStrip";
import LiveNowStrip from "../components/LiveNowStrip";
import EmptyState from "../components/EmptyState";
import TodaysSquare from "../components/TodaysSquare";
import MentionTextarea from "../components/MentionTextarea";
import { IconImage, IconClose } from "../components/Icons";
import { useInfiniteScroll } from "../hooks/useInfiniteScroll";
import { hasSeenTopicOnboarding, markTopicOnboardingSeen } from "../topicsOnboarding";
import { sanitizeUserText } from "../sanitizeUserText";
import { assertSafePublicText } from "../contentSafety";
import ContentSafetyNote from "../components/ContentSafetyNote";
import { focusCompose } from "../focusCompose";
import { useT } from "../context/LocaleContext";

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
  const t = useT();
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const quotePostId = searchParams.get("quote");
  const wantCivic = searchParams.get("civic") === "1";
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
  const [showFirstPostWelcome, setShowFirstPostWelcome] = useState(() => {
    try {
      return (
        localStorage.getItem("bx_first_post_done") !== "1" && shouldShowFirstPostWelcome()
      );
    } catch {
      return true;
    }
  });
  const [showNavTour, setShowNavTour] = useState(() => {
    try {
      if (localStorage.getItem("bx_first_post_done") !== "1" && sessionStorage.getItem("bx_welcome") === "1") {
        return false;
      }
      return shouldShowNavTour();
    } catch {
      return false;
    }
  });
  const [showStarters, setShowStarters] = useState(false);
  const [liveDebates, setLiveDebates] = useState([]);
  const [civicProblem, setCivicProblem] = useState(false);
  const [foundingRefresh, setFoundingRefresh] = useState(0);
  const [foundingNotice, setFoundingNotice] = useState("");
  const [civicHighlight, setCivicHighlight] = useState(false);

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
    if (!wantCivic) return undefined;
    setCivicProblem(true);
    setCivicHighlight(true);
    const t = window.setTimeout(() => {
      composeRef.current?.focus?.();
      document.querySelector(".compose-civic")?.scrollIntoView({ behavior: "smooth", block: "center" });
    }, 80);
    const clearHilite = window.setTimeout(() => setCivicHighlight(false), 4000);
    // Drop the query param so refresh doesn't keep flashing.
    setSearchParams(
      (prev) => {
        const next = new URLSearchParams(prev);
        next.delete("civic");
        return next;
      },
      { replace: true }
    );
    return () => {
      window.clearTimeout(t);
      window.clearTimeout(clearHilite);
    };
  }, [wantCivic, setSearchParams]);

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
      if (shouldShowFirstPostWelcome()) {
        setShowFirstPostWelcome(true);
      }
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
          if (shouldShowFirstPostWelcome()) setShowFirstPostWelcome(true);
        } else {
          localStorage.setItem("bx_first_post_done", "1");
          markFirstPostWelcomeSeen();
          setShowFirstSession(false);
          setShowFirstPostWelcome(false);
        }
      })
      .catch(() => {});
    return () => {
      cancelled = true;
    };
  }, [user, token]);

  async function finishFirstSession(result) {
    setShowFirstSession(false);
    markFirstPostWelcomeSeen();
    setShowFirstPostWelcome(false);
    markTopicOnboardingSeen();
    setFoundingRefresh((n) => n + 1);
    if (shouldShowNavTour()) {
      setShowNavTour(true);
    } else {
      await loadFeed(tab);
    }
    if (result?.skipped) {
      // Still nudge them toward compose when they skipped the guided take.
      window.setTimeout(() => composeRef.current?.focus?.(), 300);
    }
  }

  function dismissFirstPostWelcome() {
    markFirstPostWelcomeSeen();
    setShowFirstPostWelcome(false);
  }

  function showWhereToPost() {
    markFirstPostWelcomeSeen();
    setShowFirstPostWelcome(false);
    setShowFirstSession(false);
    markTopicOnboardingSeen();
    sessionStorage.removeItem("bx_welcome");
    setShowNavTour(true);
    window.setTimeout(() => {
      document.querySelector("[data-coach='compose']")?.scrollIntoView({
        behavior: "smooth",
        block: "center",
      });
      composeRef.current?.focus?.();
    }, 200);
  }

  function writeFirstTakeHere() {
    markFirstPostWelcomeSeen();
    setShowFirstPostWelcome(false);
    setShowFirstSession(true);
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
    setFoundingNotice("");
    if (!text.trim()) {
      setPostError("Write something first.");
      return;
    }
    if (text.trim().length > MAX_LEN) {
      setPostError(`Post must be ${MAX_LEN} characters or fewer`);
      return;
    }
    if (civicProblem && text.trim().length < 50) {
      setPostError("Civic problems need at least 50 characters to clear the First 100 floor.");
      setCivicHighlight(true);
      document.querySelector(".compose-civic")?.scrollIntoView({ behavior: "smooth", block: "center" });
      return;
    }
    setPosting(true);
    try {
      const cleanText = sanitizeUserText(text).trim();
      assertSafePublicText(cleanText);
      const newPost = await postsApi.create(token, {
        text: cleanText,
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
      if (newPost?.founding_message) {
        setFoundingNotice(newPost.founding_message);
      } else if (civicProblem) {
        setFoundingNotice("Posted.");
      }
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

  // First session: guided take, welcome popup can sit on top.
  if (showFirstSession) {
    return (
      <div className="plaza-page plaza-square plaza-square-first">
        <FirstPostWelcomeModal
          open={showFirstPostWelcome}
          onShowWhere={showWhereToPost}
          onWriteHere={writeFirstTakeHere}
          onDismiss={dismissFirstPostWelcome}
        />
        <FirstSessionGuide token={token} onComplete={finishFirstSession} />
      </div>
    );
  }

  function fillCompose(prompt, { asQuestion = false } = {}) {
    const next = asQuestion ? `${prompt}\n\n` : prompt.slice(0, MAX_LEN);
    setText(next.slice(0, MAX_LEN));
    setShowStarters(false);
    focusCompose(composeRef);
  }

  return (
    <div className="plaza-page plaza-square">
      <FirstPostWelcomeModal
        open={showFirstPostWelcome}
        onShowWhere={showWhereToPost}
        onWriteHere={writeFirstTakeHere}
        onDismiss={dismissFirstPostWelcome}
      />
      {showNavTour ? <CoachMarks onDone={() => setShowNavTour(false)} /> : null}
      <SoftLaunchBanner compact />

      <div className="plaza-layout">
        <div className="plaza-main-top">
          <header className="square-home-head">
            <div className="square-home-head-main">
              <p className="square-home-kicker">{t("square.kicker")}</p>
              <h1 className="square-home-title">{t("square.title")}</h1>
              <p className="square-home-sub">{t("square.sub")}</p>
            </div>
            <FoundingChip refreshKey={foundingRefresh} />
          </header>

          <TodaysSquare onAnswer={(question) => fillCompose(question, { asQuestion: true })} />
        </div>

        <aside className="plaza-rail-stack" aria-label="Discover">
          <SuggestionsStrip
            token={token}
            surface="square"
            title={t("square.topQuestions")}
            onPick={(prompt) => fillCompose(prompt)}
          />
          <LiveNowStrip items={liveDebates} limit={6} emptyHint="" />
        </aside>

        <form className="plaza-studio compose plaza-main-compose" onSubmit={handlePost} data-coach="compose">
          <div className="plaza-studio-head">
            <Avatar name={user?.display_name} username={user?.username} url={user?.avatar_url} size={44} />
            <div>
              <p className="plaza-studio-label">{t("square.dropTake")}</p>
              <p className="hint">{t("square.dropHint")}</p>
            </div>
          </div>
          <div className="compose-body">
            <MentionTextarea
              ref={composeRef}
              placeholder={
                quotePreview ? t("square.placeholderQuote") : t("square.placeholder")
              }
              value={text}
              onChange={(v) => {
                setPostError("");
                setText(sanitizeUserText(v));
              }}
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
                {t("square.photo")}
              </button>
              <button
                type="button"
                className={`compose-tile compose-tile-starters${showStarters ? " is-open" : ""}`}
                aria-expanded={showStarters}
                onClick={() => setShowStarters((v) => !v)}
                title="Starter prompts, not AI drafts"
              >
                {t("square.starters")}
              </button>
              <Link to="/spaces" className="compose-tile">
                {t("square.startLive")}
              </Link>
              <Link to="/communities" className="compose-tile">
                {t("square.community")}
              </Link>
            </div>
            {showStarters && (
              <div className="compose-starters-sheet" role="listbox" aria-label="Starter prompts">
                {STARTER_PROMPTS.map((prompt) => (
                  <button
                    key={prompt}
                    type="button"
                    className="compose-starter-chip"
                    onClick={() => fillCompose(prompt)}
                  >
                    {prompt}
                  </button>
                ))}
              </div>
            )}
            <label className={`compose-civic${civicHighlight ? " is-guided" : ""}`}>
              <input
                type="checkbox"
                checked={civicProblem}
                onChange={(e) => {
                  setCivicProblem(e.target.checked);
                  setCivicHighlight(false);
                }}
              />
              <span>
                {t("square.civic")}
                {civicProblem ? t("square.civicHint") : ""}
              </span>
            </label>
            {foundingNotice && <p className="hint ok-hint compose-founding-notice">{foundingNotice}</p>}
            <ContentSafetyNote compact />
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
              <button
                type="submit"
                className="post-btn"
                disabled={posting || !text.trim() || text.trim().length > MAX_LEN}
              >
                {posting ? t("square.posting") : t("square.post")}
              </button>
            </div>
          </div>
        </form>

        <section className="plaza-takes plaza-main-feed">
          <div className="plaza-takes-head">
            <h2>{t("square.takesTitle")}</h2>
            <div className="plaza-takes-tabs">
              <button
                type="button"
                className={tab === "global" ? "is-active" : ""}
                onClick={() => setTab("global")}
              >
                {t("square.forYou")}
              </button>
              <button
                type="button"
                className={tab === "following" ? "is-active" : ""}
                onClick={() => setTab("following")}
              >
                {t("square.following")}
              </button>
              <button
                type="button"
                className={tab === "mentions" ? "is-active" : ""}
                onClick={() => setTab("mentions")}
              >
                {t("square.mentions")}
              </button>
            </div>
          </div>
          {tab === "global" && (
            <p className="hint plaza-takes-hint">{t("square.forYouHint")}</p>
          )}
          {tab === "following" && (
            <p className="hint plaza-takes-hint">{t("square.followingHint")}</p>
          )}
          {tab === "mentions" && (
            <p className="hint plaza-takes-hint">{t("square.mentionsHint")}</p>
          )}

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
              title={
                tab === "following"
                  ? t("square.emptyFollowing")
                  : tab === "mentions"
                    ? t("square.emptyMentions")
                    : t("square.emptyTakes")
              }
              hint={
                tab === "following"
                  ? t("square.emptyFollowingHint")
                  : tab === "mentions"
                    ? t("square.emptyMentionsHint")
                    : t("square.emptyTakesHint")
              }
              primaryLabel={
                tab === "following"
                  ? t("square.explorePeople")
                  : tab === "mentions"
                    ? t("square.goAlerts")
                    : t("square.writeTake")
              }
              primaryTo={
                tab === "following" ? "/search" : tab === "mentions" ? "/notifications" : undefined
              }
              onPrimary={
                tab === "following" || tab === "mentions"
                  ? undefined
                  : () => focusCompose(composeRef)
              }
              secondaryLabel={t("square.startDebate")}
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
              {loadingMore && <p className="hint load-more-hint">{t("square.loadingMore")}</p>}
              {!hasMore && items.length > 0 && (
                <p className="hint load-more-hint">{t("square.caughtUp")}</p>
              )}
            </>
          )}
        </section>
      </div>
    </div>
  );
}
