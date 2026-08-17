import { useEffect, useRef, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { api, searchApi } from "../api";
import { useAuth } from "../context/AuthContext";
import PostCard from "../components/PostCard";
import Avatar from "../components/Avatar";
import { IconSearch } from "../components/Icons";
import PlazaPageHeader from "../components/PlazaPageHeader";
import SuggestedFollows from "../components/SuggestedFollows";

/** Chips use queries that match live posts/topics. */
const QUICK_SEARCHES = [
  { label: "Politics", query: "politics" },
  { label: "Geopolitics", query: "Geopolitics" },
  { label: "BarathX", query: "BarathX" },
  { label: "Startups", query: "startups" },
  { label: "Sports", query: "sports" },
  { label: "News", query: "news" },
];

function normalizeResults(data) {
  return {
    users: Array.isArray(data?.users) ? data.users : [],
    posts: Array.isArray(data?.posts) ? data.posts : [],
    topics: Array.isArray(data?.topics) ? data.topics : [],
    arenas: Array.isArray(data?.arenas) ? data.arenas : [],
  };
}

export default function Search() {
  const { token, user } = useAuth();
  const [searchParams, setSearchParams] = useSearchParams();
  const q = searchParams.get("q") || "";
  const inputRef = useRef(null);
  const searchSeq = useRef(0);

  const [inputValue, setInputValue] = useState(q);
  const [results, setResults] = useState({ users: [], posts: [], topics: [], arenas: [] });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [followBusy, setFollowBusy] = useState("");
  const [followingMap, setFollowingMap] = useState({});

  useEffect(() => {
    setInputValue(q);
    if (q.trim()) {
      runSearch(q);
    } else {
      setResults({ users: [], posts: [], topics: [], arenas: [] });
      setLoading(false);
      inputRef.current?.focus();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [q]);

  // Live Explore: debounce typing into the URL so results appear without a second tap.
  useEffect(() => {
    const next = inputValue.trim();
    if (next === q.trim()) return undefined;
    const timer = window.setTimeout(() => {
      if (!next) {
        setSearchParams({});
        return;
      }
      setSearchParams({ q: next });
    }, 350);
    return () => window.clearTimeout(timer);
  }, [inputValue, q, setSearchParams]);

  async function runSearch(query) {
    const seq = ++searchSeq.current;
    setLoading(true);
    setError("");
    try {
      const data = await searchApi.search(query, token);
      if (seq !== searchSeq.current) return;
      setResults(normalizeResults(data));
    } catch (err) {
      if (seq !== searchSeq.current) return;
      setError(err.message);
      setResults({ users: [], posts: [], topics: [], arenas: [] });
    } finally {
      if (seq === searchSeq.current) setLoading(false);
    }
  }

  function handleSubmit(e) {
    e.preventDefault();
    const next = inputValue.trim();
    if (!next) return;
    setSearchParams({ q: next });
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
  const emptyResults =
    hasQuery &&
    !loading &&
    results.users.length === 0 &&
    results.posts.length === 0 &&
    results.topics.length === 0 &&
    results.arenas.length === 0;

  return (
    <div className="plaza-page plaza-explore">
      <PlazaPageHeader
        title="Explore"
        sub="People, posts, and topics across India."
      />

      <form className="plaza-search-form search-form" onSubmit={handleSubmit} role="search">
        <IconSearch className="search-form-icon" aria-hidden="true" />
        <input
          ref={inputRef}
          type="search"
          placeholder="Search people, posts, topics…"
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
          <SuggestedFollows
            title="Who to follow"
            note="Tap Follow to start seeing their posts."
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
      ) : (
        <>
          {results.arenas.length > 0 && (
            <>
              <h3 className="section-title">Arenas</h3>
              <div className="user-results search-topic-results">
                {results.arenas.map((a) => (
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

          {results.topics.length > 0 && (
            <>
              <h3 className="section-title">Topics</h3>
              <div className="user-results search-topic-results">
                {results.topics.map((t) => (
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

          {results.users.length > 0 && (
            <>
              <h3 className="section-title">People</h3>
              <div className="user-results">
                {results.users.map((u) => {
                  const isFollowing = !!(followingMap[u.username] ?? u.is_following);
                  const isMe = u.username === user?.username;
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
                          onClick={() => toggleFollowUser(u)}
                        >
                          {followBusy === u.username ? "…" : isFollowing ? "Following" : "Follow"}
                        </button>
                      )}
                    </div>
                  );
                })}
              </div>
            </>
          )}

          {(results.posts.length > 0 ||
            (results.users.length === 0 && results.topics.length === 0 && results.arenas.length === 0)) && (
            <h3 className="section-title">Posts</h3>
          )}
          {results.posts.length === 0 ? (
            results.users.length === 0 && results.topics.length === 0 && results.arenas.length === 0 ? null : (
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
              <p className="hint search-status">Try politics, startups, sports, news, or a @username.</p>
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
