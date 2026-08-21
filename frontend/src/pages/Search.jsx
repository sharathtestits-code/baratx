import { useEffect, useRef, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { api, searchApi, trendingApi } from "../api";
import { useAuth } from "../context/AuthContext";
import PostCard from "../components/PostCard";
import Avatar from "../components/Avatar";
import { IconSearch } from "../components/Icons";
import PlazaPageHeader from "../components/PlazaPageHeader";
import SuggestedFollows from "../components/SuggestedFollows";

/** Chips map to India-now lanes (news / cricket / politics…). */
const QUICK_SEARCHES = [
  { label: "News", query: "news" },
  { label: "Cricket", query: "cricket" },
  { label: "Politics", query: "politics" },
  { label: "India now", query: "trending in india" },
  { label: "Startups", query: "startups" },
  { label: "Sports", query: "sports" },
];

function normalizeResults(data) {
  return {
    users: Array.isArray(data?.users) ? data.users : [],
    posts: Array.isArray(data?.posts) ? data.posts : [],
    topics: Array.isArray(data?.topics) ? data.topics : [],
    arenas: Array.isArray(data?.arenas) ? data.arenas : [],
  };
}

/** Strip @/# so @arvi999 finds the same person as arvi999. */
function cleanSearchQuery(raw) {
  return String(raw || "")
    .trim()
    .replace(/^[@#]+/, "")
    .trim();
}

/** True when the query is meant to find people (@handle or matching usernames). */
function isPeopleSearch(raw, users) {
  const trimmed = String(raw || "").trim();
  if (!trimmed) return false;
  if (trimmed.startsWith("@")) return true;
  const cleaned = cleanSearchQuery(trimmed).toLowerCase();
  if (!cleaned || /\s/.test(cleaned)) return false;
  if (!/^[a-z0-9_]{2,32}$/i.test(cleaned)) return false;
  const list = Array.isArray(users) ? users : [];
  // Bare tokens only count as people when a username clearly matches — not topic words like "india".
  return list.some((u) => {
    const un = String(u.username || "").toLowerCase();
    return un === cleaned || un.startsWith(cleaned) || (cleaned.length >= 3 && cleaned.startsWith(un));
  });
}

function TrendingBlock({ trending, onSearchHeadline }) {
  if (!trending) return null;
  const topics = trending.topics || [];
  const headlines = trending.headlines || [];
  if (!topics.length && !headlines.length) return null;

  return (
    <section className="explore-trending" aria-label={trending.label || "Trending in India"}>
      <h3 className="section-title">
        {trending.label || "India now"}
        <span className="explore-trending-meta"> · live India headlines</span>
      </h3>
      {topics.length > 0 && (
        <div className="search-chips explore-trending-topics" aria-label="Trending topics">
          {topics.map((t) => (
            <Link
              key={`${t.arena_key}:${t.key}`}
              to={t.href || `/arenas/${encodeURIComponent(t.arena_key)}`}
              className="search-chip explore-topic-chip"
            >
              {t.name}
            </Link>
          ))}
        </div>
      )}
      {headlines.length > 0 && (
        <ul className="explore-headline-list">
          {headlines.map((h, i) => (
            <li key={`${h.title}-${i}`}>
              <button
                type="button"
                className="explore-headline"
                onClick={() => onSearchHeadline?.(h.search_q || h.title)}
              >
                <span className="explore-headline-title">{h.title}</span>
                {h.source ? <span className="explore-headline-source">{h.source}</span> : null}
              </button>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}

function PeopleResults({
  users,
  token,
  me,
  followingMap,
  followBusy,
  onToggleFollow,
}) {
  if (!users.length) return null;
  return (
    <>
      <h3 className="section-title">People</h3>
      <div className="user-results">
        {users.map((u) => {
          const isFollowing = !!(followingMap[u.username] ?? u.is_following);
          const isMe = u.username === me;
          return (
            <div key={u.id} className="user-result user-result-row">
              <Link to={`/u/${u.username}`} className="user-result-main">
                <Avatar name={u.display_name} username={u.username} url={u.avatar_url} size={44} />
                <div>
                  <div className="user-result-name">{u.display_name}</div>
                  <div className="user-result-username">@{u.username}</div>
                  {u.bio && <div className="user-result-bio">{u.bio}</div>}
                </div>
              </Link>
              {token && !isMe && (
                <button
                  type="button"
                  className={`follow-btn suggested-follow-btn${isFollowing ? " following" : ""}`}
                  disabled={followBusy === u.username}
                  onClick={() => onToggleFollow(u)}
                >
                  {followBusy === u.username ? "…" : isFollowing ? "Following" : "Follow"}
                </button>
              )}
            </div>
          );
        })}
      </div>
    </>
  );
}

function TopicArenaResults({ topics, arenas }) {
  return (
    <>
      {arenas.length > 0 && (
        <>
          <h3 className="section-title">Arenas</h3>
          <div className="user-results search-topic-results">
            {arenas.map((a) => (
              <Link key={a.key} to={`/arenas/${encodeURIComponent(a.key)}`} className="user-result user-result-row">
                <div>
                  <div className="user-result-name">{a.name}</div>
                  <div className="user-result-username">Arena · {a.key}</div>
                </div>
              </Link>
            ))}
          </div>
        </>
      )}
      {topics.length > 0 && (
        <>
          <h3 className="section-title">Topics</h3>
          <div className="user-results search-topic-results">
            {topics.map((t) => (
              <Link
                key={`${t.arena_key}:${t.key}:${t.id}`}
                to={`/arenas/${encodeURIComponent(t.arena_key)}`}
                className="user-result user-result-row"
              >
                <div>
                  <div className="user-result-name">{t.name}</div>
                  <div className="user-result-username">
                    {t.arena_key}
                    {t.blurb ? ` · ${t.blurb}` : ""}
                  </div>
                </div>
              </Link>
            ))}
          </div>
        </>
      )}
    </>
  );
}

export default function Search() {
  const { token, user } = useAuth();
  const [searchParams, setSearchParams] = useSearchParams();
  const q = searchParams.get("q") || "";
  const inputRef = useRef(null);
  const searchSeq = useRef(0);

  const [inputValue, setInputValue] = useState(q);
  const [results, setResults] = useState({ users: [], posts: [], topics: [], arenas: [] });
  const [trending, setTrending] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [followBusy, setFollowBusy] = useState("");
  const [followingMap, setFollowingMap] = useState({});

  useEffect(() => {
    setInputValue(q);
    const cleaned = cleanSearchQuery(q);
    if (cleaned) {
      if (cleaned !== q.trim() && !String(q).trim().startsWith("@")) {
        // Keep @ in the URL when the user typed it (people intent), else normalize.
        setSearchParams({ q: cleaned }, { replace: true });
        return;
      }
      if (cleaned !== q.trim() && String(q).trim().startsWith("@") && q.trim() !== `@${cleaned}`) {
        setSearchParams({ q: `@${cleaned}` }, { replace: true });
        return;
      }
      runSearch(q);
    } else {
      setResults({ users: [], posts: [], topics: [], arenas: [] });
      setTrending(null);
      setLoading(false);
      inputRef.current?.focus();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [q]);

  // Live Explore: debounce typing into the URL so results appear without a second tap.
  useEffect(() => {
    const raw = String(inputValue || "").trim();
    const nextClean = cleanSearchQuery(inputValue);
    const urlClean = cleanSearchQuery(q);
    const urlRaw = String(q || "").trim();
    if (raw.startsWith("@")) {
      const want = nextClean ? `@${nextClean}` : "";
      if (want === urlRaw) return undefined;
      const timer = window.setTimeout(() => {
        if (!want) setSearchParams({});
        else setSearchParams({ q: want });
      }, 350);
      return () => window.clearTimeout(timer);
    }
    if (nextClean === urlClean) return undefined;
    const timer = window.setTimeout(() => {
      if (!nextClean) {
        setSearchParams({});
        return;
      }
      setSearchParams({ q: nextClean });
    }, 350);
    return () => window.clearTimeout(timer);
  }, [inputValue, q, setSearchParams]);

  async function runSearch(query) {
    const seq = ++searchSeq.current;
    const cleaned = cleanSearchQuery(query);
    const peopleIntent = String(query || "").trim().startsWith("@");
    setLoading(true);
    setError("");
    try {
      const data = await searchApi.search(cleaned, token);
      if (seq !== searchSeq.current) return;
      const normalized = normalizeResults(data);
      setResults(normalized);
      // Headlines/topics lane only for topic exploration — never bury @people results.
      if (peopleIntent || isPeopleSearch(query, normalized.users)) {
        setTrending(null);
      } else {
        const trend = await trendingApi.list(token, { q: cleaned, limit: 8 }).catch(() => null);
        if (seq !== searchSeq.current) return;
        setTrending(trend);
      }
    } catch (err) {
      if (seq !== searchSeq.current) return;
      setError(err.message);
      setResults({ users: [], posts: [], topics: [], arenas: [] });
      setTrending(null);
    } finally {
      if (seq === searchSeq.current) setLoading(false);
    }
  }

  function handleSubmit(e) {
    e.preventDefault();
    const raw = String(inputValue || "").trim();
    const next = cleanSearchQuery(inputValue);
    if (!next) return;
    setSearchParams({ q: raw.startsWith("@") ? `@${next}` : next });
  }

  function clearQuery() {
    setInputValue("");
    setSearchParams({});
    inputRef.current?.focus();
  }

  async function toggleFollowUser(u) {
    if (!token || followBusy || u.username === user?.username) return;
    setFollowBusy(u.username);
    const was = !!(followingMap[u.username] ?? u.is_following);
    setFollowingMap((prev) => ({ ...prev, [u.username]: !was }));
    try {
      if (was) await api.unfollow(token, u.username);
      else await api.follow(token, u.username);
    } catch (err) {
      setFollowingMap((prev) => ({ ...prev, [u.username]: was }));
      setError(err.message);
    } finally {
      setFollowBusy("");
    }
  }

  function handleDeleted(postId) {
    setResults((r) => ({ ...r, posts: r.posts.filter((p) => p.id !== postId) }));
  }

  const hasQuery = !!q.trim();
  const peopleMode = hasQuery && isPeopleSearch(q, results.users);
  const emptyResults =
    hasQuery &&
    !loading &&
    results.users.length === 0 &&
    results.posts.length === 0 &&
    results.topics.length === 0 &&
    results.arenas.length === 0 &&
    !(trending?.topics?.length || trending?.headlines?.length);

  return (
    <div className="plaza-page plaza-explore">
      <PlazaPageHeader
        title="Explore"
        sub="Search people or topics. Human takes only — no AI slop."
      />

      <form className="plaza-search-form search-form" onSubmit={handleSubmit} role="search">
        <IconSearch className="search-form-icon" aria-hidden="true" />
        <input
          ref={inputRef}
          type="search"
          placeholder="Try @username, news, cricket, politics…"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          aria-label="Search BarathX"
          enterKeyHint="search"
          autoComplete="off"
        />
        {inputValue ? (
          <button type="button" className="search-clear" onClick={clearQuery} aria-label="Clear search">
            ×
          </button>
        ) : null}
        <button type="submit" className="search-submit" disabled={!inputValue.trim()}>
          Search
        </button>
      </form>

      {error && <div className="error">{error}</div>}

      {!hasQuery ? (
        <div className="search-empty plaza-explore-empty">
          <p className="hint search-status search-empty-lead">
            Type a @username to find people, or a topic like cricket / politics to explore India now.
          </p>
          <SuggestedFollows
            title="Who to follow"
            note="Tap a name to open their profile, or Follow to see their posts."
            onExplorePeople={() => {
              setInputValue("@");
              inputRef.current?.focus?.();
            }}
          />
          <div className="search-chips" aria-label="Suggested searches">
            {QUICK_SEARCHES.map((item) => (
              <button
                key={item.query}
                type="button"
                className="search-chip"
                onClick={() => setSearchParams({ q: item.query })}
              >
                {item.label}
              </button>
            ))}
          </div>
        </div>
      ) : loading ? (
        <p className="hint search-status">Searching…</p>
      ) : peopleMode ? (
        <>
          <PeopleResults
            users={results.users}
            token={token}
            me={user?.username}
            followingMap={followingMap}
            followBusy={followBusy}
            onToggleFollow={toggleFollowUser}
          />
          {results.users.length === 0 && (
            <div className="search-empty-results">
              <p className="hint search-status">No people for “{q}”.</p>
              <p className="hint search-status">Check the spelling, or try without spaces.</p>
            </div>
          )}
        </>
      ) : (
        <>
          <TopicArenaResults topics={results.topics} arenas={results.arenas} />

          <TrendingBlock
            trending={trending}
            onSearchHeadline={(text) => setSearchParams({ q: text })}
          />

          {results.users.length > 0 && (
            <PeopleResults
              users={results.users}
              token={token}
              me={user?.username}
              followingMap={followingMap}
              followBusy={followBusy}
              onToggleFollow={toggleFollowUser}
            />
          )}

          {(results.posts.length > 0 ||
            (results.users.length === 0 &&
              results.topics.length === 0 &&
              results.arenas.length === 0 &&
              !(trending?.topics?.length || trending?.headlines?.length))) && (
            <h3 className="section-title">Posts</h3>
          )}
          {results.posts.length === 0 ? (
            results.users.length === 0 &&
            results.topics.length === 0 &&
            results.arenas.length === 0 &&
            !(trending?.topics?.length || trending?.headlines?.length) ? null : (
              <p className="hint search-status">No posts found.</p>
            )
          ) : (
            <div className="post-list">
              {results.posts.map((post) => (
                <PostCard key={post.id} post={post} onDeleted={handleDeleted} />
              ))}
            </div>
          )}

          {emptyResults && (
            <div className="search-empty-results">
              <p className="hint search-status">No results for “{q}”.</p>
              <p className="hint search-status">Try news, cricket, politics, or a @username.</p>
              <div className="search-chips" aria-label="Try these searches">
                {QUICK_SEARCHES.map((item) => (
                  <button
                    key={`empty-${item.query}`}
                    type="button"
                    className="search-chip"
                    onClick={() => setSearchParams({ q: item.query })}
                  >
                    {item.label}
                  </button>
                ))}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}
