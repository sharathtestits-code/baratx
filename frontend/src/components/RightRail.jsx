import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { IconSearch } from "./Icons";
import SuggestedFollows from "./SuggestedFollows";

const TRENDING_ORBITS = [
  { label: "BarathX", query: "BarathX", meta: "On BarathX", members: "Official", energy: 92 },
  { label: "#StartupIndia", query: "StartupIndia", meta: "Builders", members: "Orbit", energy: 78 },
  { label: "#IPL", query: "IPL", meta: "Sports", members: "Hot", energy: 88 },
  { label: "Monsoon", query: "Monsoon", meta: "Local drops", members: "India today", energy: 64 },
  { label: "Politics", query: "Politics", meta: "Arena", members: "Debate", energy: 71 },
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
    <aside className="right-rail" aria-label="Discover">
      <div className="right-rail-inner">
        <form className="rail-search" onSubmit={handleSearch} role="search">
          <IconSearch className="rail-search-icon" aria-hidden="true" />
          <input
            type="search"
            placeholder="Search BarathX"
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
            note="Seed accounts run by BarathX — not organic third parties."
          />
        </div>

        <section className="rail-card">
          <h2 className="rail-card-title">Trending Orbits</h2>
          <ul className="rail-trends">
            {TRENDING_ORBITS.map((topic) => (
              <li key={topic.query}>
                <Link to={`/search?q=${encodeURIComponent(topic.query)}`} className="rail-trend">
                  <span className="rail-trend-meta">{topic.meta}</span>
                  <span className="rail-trend-label">{topic.label}</span>
                  <span className="rail-trend-members">{topic.members}</span>
                  <span className="orbit-energy" aria-hidden="true">
                    <span style={{ width: `${topic.energy}%` }} />
                  </span>
                </Link>
              </li>
            ))}
          </ul>
          <Link to="/arenas" className="rail-card-more">
            Browse arenas
          </Link>
        </section>
      </div>
    </aside>
  );
}
