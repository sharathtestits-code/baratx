import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { trendingApi } from "../api";
import { useAuth } from "../context/AuthContext";
import { IconSearch } from "./Icons";
import SuggestedFollows from "./SuggestedFollows";

const FALLBACK_ORBITS = [
  { label: "News", query: "news", meta: "India now", members: "Live" },
  { label: "Cricket", query: "cricket", meta: "Sports", members: "Hot" },
  { label: "Politics", query: "politics", meta: "Arena", members: "Debate" },
  { label: "Startups", query: "startups", meta: "Builders", members: "Orbit" },
  { label: "BarathX", query: "BarathX", meta: "On BarathX", members: "Official" },
];

export default function RightRail() {
  const navigate = useNavigate();
  const { token } = useAuth();
  const [query, setQuery] = useState("");
  const [orbits, setOrbits] = useState(FALLBACK_ORBITS);

  useEffect(() => {
    let cancelled = false;
    trendingApi
      .list(token, { q: "trending in india", limit: 5 })
      .then((data) => {
        if (cancelled) return;
        const topics = Array.isArray(data?.topics) ? data.topics : [];
        if (!topics.length) return;
        setOrbits(
          topics.slice(0, 5).map((t, i) => ({
            label: t.name,
            query: t.name,
            meta: t.arena_key || "India",
            members: i === 0 ? "Hot" : "Orbit",
            energy: Math.max(55, 95 - i * 8),
          }))
        );
      })
      .catch(() => {});
    return () => {
      cancelled = true;
    };
  }, [token]);

  function handleSearch(e) {
    e.preventDefault();
    const q = query.trim();
    if (!q) return;
    navigate(`/search?q=${encodeURIComponent(q)}`);
  }

  return (
    <aside className="right-rail" aria-label="Discover">
      <div className="right-rail-inner">
        <form className="rail-search" onSubmit={handleSearch} role="search">
          <IconSearch className="rail-search-icon" aria-hidden="true" />
          <input
            type="search"
            placeholder="News, cricket, politics…"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            aria-label="Search BarathX"
            enterKeyHint="search"
            autoComplete="off"
          />
          {query ? (
            <button
              type="button"
              className="rail-search-clear"
              onClick={() => setQuery("")}
              aria-label="Clear search"
            >
              ×
            </button>
          ) : null}
        </form>

        <div className="rail-card rail-card-suggested">
          <SuggestedFollows
            title="Official BarathX"
            note="Seed accounts run by BarathX, not organic third parties."
          />
        </div>

        <section className="rail-card">
          <h2 className="rail-card-title">Trending in India</h2>
          <ul className="rail-trends">
            {orbits.map((topic) => (
              <li key={topic.query}>
                <Link to={`/search?q=${encodeURIComponent(topic.query)}`} className="rail-trend">
                  <span className="rail-trend-meta">{topic.meta}</span>
                  <span className="rail-trend-label">{topic.label}</span>
                  <span className="rail-trend-members">{topic.members}</span>
                  <span className="orbit-energy" aria-hidden="true">
                    <span style={{ width: `${topic.energy || 70}%` }} />
                  </span>
                </Link>
              </li>
            ))}
          </ul>
          <Link to="/search?q=trending%20in%20india" className="rail-card-more">
            Explore India now
          </Link>
        </section>
      </div>
    </aside>
  );
}
