import { useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { searchApi } from "../api";
import { useAuth } from "../context/AuthContext";
import PostCard from "../components/PostCard";
import Avatar from "../components/Avatar";
import { IconSearch } from "../components/Icons";

export default function Search() {
  const { token } = useAuth();
  const [searchParams, setSearchParams] = useSearchParams();
  const q = searchParams.get("q") || "";

  const [inputValue, setInputValue] = useState(q);
  const [results, setResults] = useState({ users: [], posts: [] });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    setInputValue(q);
    if (q.trim()) {
      runSearch(q);
    } else {
      setResults({ users: [], posts: [] });
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
    if (!inputValue.trim()) return;
    setSearchParams({ q: inputValue.trim() });
  }

  function handleDeleted(postId) {
    setResults((r) => ({ ...r, posts: r.posts.filter((p) => p.id !== postId) }));
  }

  return (
    <div className="feed-wrap">
      <form className="search-form" onSubmit={handleSubmit}>
        <IconSearch className="search-form-icon" />
        <input
          type="text"
          placeholder="Search people or posts..."
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
        />
        <button type="submit">Search</button>
      </form>

      {error && <div className="error">{error}</div>}

      {!q.trim() ? (
        <div className="empty-state">
          <p className="hint">Search for people by name or username, or posts by keyword.</p>
        </div>
      ) : loading ? (
        <p className="hint">Searching...</p>
      ) : (
        <>
          {results.users.length > 0 && (
            <>
              <h3 className="section-title">People</h3>
              <div className="user-results">
                {results.users.map((u) => (
                  <Link key={u.id} to={`/u/${u.username}`} className="user-result">
                    <Avatar name={u.display_name} username={u.username} url={u.avatar_url} size={44} />
                    <div>
                      <div className="user-result-name">{u.display_name}</div>
                      <div className="user-result-username">@{u.username}</div>
                      {u.bio && <div className="user-result-bio">{u.bio}</div>}
                    </div>
                  </Link>
                ))}
              </div>
            </>
          )}

          <h3 className="section-title">Posts</h3>
          {results.posts.length === 0 ? (
            <p className="hint">No posts found.</p>
          ) : (
            <div className="post-list">
              {results.posts.map((post) => (
                <PostCard key={post.id} post={post} onDeleted={handleDeleted} />
              ))}
            </div>
          )}

          {results.users.length === 0 && results.posts.length === 0 && (
            <p className="hint">No results for "{q}".</p>
          )}
        </>
      )}
    </div>
  );
}
