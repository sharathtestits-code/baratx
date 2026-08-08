import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { IconSearch } from "./Icons";
import SuggestedFollows from "./SuggestedFollows";

const TRENDING_TOPICS = [
  { label: "BharatX", query: "BharatX", meta: "On BharatX" },
  { label: "#StartupIndia", query: "StartupIndia", meta: "Explore" },
  { label: "#IPL", query: "IPL", meta: "Sports" },
  { label: "Monsoon", query: "Monsoon", meta: "India today" },
];

export default function RightRail() {
  const navigate = useNavigate();
  const [query, setQuery] = useState("");

  function handleSearch(e) {
    e.preventDefault();
    const q = query.trim();
    if (!q) return;
    navigate(`/search?q=${encodeURIComponent(q)}`);
  }

  return (
    <aside className="right-rail" aria-label="Explore">
      <div className="right-rail-inner">
        <form className="rail-search" onSubmit={handleSearch} role="search">
          <IconSearch className="rail-search-icon" aria-hidden="true" />
          <input
            type="search"
            placeholder="Search BharatX"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            aria-label="Search BharatX"
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
            title="Official BharatX"
            note="Seed accounts run by BharatX — not organic third parties."
          />
        </div>

        <section className="rail-card">
          <h2 className="rail-card-title">Trending topics</h2>
          <ul className="rail-trends">
            {TRENDING_TOPICS.map((topic) => (
              <li key={topic.query}>
                <Link to={`/search?q=${encodeURIComponent(topic.query)}`} className="rail-trend">
                  <span className="rail-trend-meta">{topic.meta}</span>
                  <span className="rail-trend-label">{topic.label}</span>
                </Link>
              </li>
            ))}
          </ul>
          <Link to="/search" className="rail-card-more">
            Show more
          </Link>
        </section>
      </div>
    </aside>
  );
}
