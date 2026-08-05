import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import Avatar from "./Avatar";
import { IconSearch } from "./Icons";

const SUGGESTED_PEOPLE = [
  {
    display_name: "BaratX",
    username: "baratx",
    blurb: "Official — product updates & India conversation prompts",
    official: true,
  },
  {
    display_name: "Bharat Voices",
    username: "bharatvoices",
    blurb: "Official BaratX — culture, ideas, everyday India",
    official: true,
  },
  {
    display_name: "India Tech Daily",
    username: "indiatech",
    blurb: "Official BaratX — startups, policy & builders",
    official: true,
  },
];

const TRENDING_TOPICS = [
  { label: "BaratX", query: "BaratX", meta: "On BaratX" },
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
        <form className="rail-search" onSubmit={handleSearch}>
          <IconSearch className="rail-search-icon" />
          <input
            type="search"
            placeholder="Search BaratX"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            aria-label="Search BaratX"
          />
        </form>

        <section className="rail-card">
          <h2 className="rail-card-title">Official BaratX</h2>
          <p className="rail-card-note">Seed accounts run by BaratX — not organic third parties.</p>
          <ul className="rail-people">
            {SUGGESTED_PEOPLE.map((person) => (
              <li key={person.username}>
                <Link to={`/search?q=${encodeURIComponent(person.username)}`} className="rail-person">
                  <Avatar name={person.display_name} username={person.username} size={40} />
                  <div className="rail-person-info">
                    <div className="rail-person-name">
                      {person.display_name}
                      {person.official && <span className="rail-official-badge">Official</span>}
                    </div>
                    <div className="rail-person-username">@{person.username}</div>
                    <div className="rail-person-blurb">{person.blurb}</div>
                  </div>
                </Link>
              </li>
            ))}
          </ul>
          <Link to="/search" className="rail-card-more">
            Explore people
          </Link>
        </section>

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
