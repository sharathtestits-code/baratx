import { useEffect, useRef, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { api, searchApi } from "../api";
import { useAuth } from "../context/AuthContext";
import PostCard from "../components/PostCard";
import Avatar from "../components/Avatar";
import { IconSearch } from "../components/Icons";
import SuggestedFollows from "../components/SuggestedFollows";

const QUICK_SEARCHES = [
  { label: "BaratX", query: "BaratX" },
  { label: "Startup India", query: "StartupIndia" },
  { label: "IPL", query: "IPL" },
  { label: "Monsoon", query: "Monsoon" },
  { label: "Tech", query: "tech" },
];

export default function Search() {
  const { token, user } = useAuth();
  const [searchParams, setSearchParams] = useSearchParams();
  const q = searchParams.get("q") || "";
  const inputRef = useRef(null);

  const [inputValue, setInputValue] = useState(q);
  const [results, setResults] = useState({ users: [], posts: [] });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [followBusy, setFollowBusy] = useState("");
  const [followingMap, setFollowingMap] = useState({});

  useEffect(() => {
    setInputValue(q);
    if (q.trim()) {
      runSearch(q);
    } else {
      setResults({ users: [], posts: [] });
      inputRef.current?.focus();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [q]);

  async function runSearch(query) {
    setLoading(true);
    setError("");
    try {
      const data = await searchApi.search(query, token);
      setResults(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
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

  return (
    <div className="plaza-page plaza-explore">
      <section className="plaza-hero plaza-hero-compact">
        <p className="plaza-hero-kicker">Find the square</p>
        <h1 className="plaza-hero-title">Explore</h1>
        <p className="plaza-hero-sub">People, posts, and topics across India.</p>
      </section>

      <form className="plaza-search-form search-form" onSubmit={handleSubmit} role="search">
        <IconSearch className="search-form-icon" aria-hidden="true" />
        <input
          ref={inputRef}
          type="search"
          placeholder="Search people, posts, topics…"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          aria-label="Search BaratX"
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

      {!q.trim() ? (
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

          <h3 className="section-title">Posts</h3>
          {results.posts.length === 0 ? (
            <p className="hint search-status">No posts found.</p>
          ) : (
            <div className="post-list">
              {results.posts.map((post) => (
                <PostCard key={post.id} post={post} onDeleted={handleDeleted} />
              ))}
            </div>
          )}

          {results.users.length === 0 && results.posts.length === 0 && (
            <p className="hint search-status">No results for “{q}”.</p>
          )}
        </>
      )}
    </div>
  );
}
