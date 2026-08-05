import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import Avatar from "./Avatar";
import { IconSearch } from "./Icons";

const SUGGESTED_PEOPLE = [
  {
    display_name: "India Tech Daily",
    username: "indiatech",
    blurb: "Startups, policy & builders across India",
  },
  {
    display_name: "Bharat Voices",
    username: "bharatvoices",
    blurb: "Culture, ideas, and everyday India",
  },
  {
    display_name: "Desi Sports Desk",
    username: "desisports",
    blurb: "Cricket, football, and everything in between",
  },
];

const TRENDING_TOPICS = [
  { label: "BaratX", query: "BaratX", meta: "Trending in India" },
  { label: "#StartupIndia", query: "StartupIndia", meta: "12.4K posts" },
  { label: "#IPL", query: "IPL", meta: "Trending in Sports" },
  { label: "Monsoon", query: "Monsoon", meta: "Trending in News" },
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
          <h2 className="rail-card-title">Suggested for you</h2>
          <ul className="rail-people">
            {SUGGESTED_PEOPLE.map((person) => (
              <li key={person.username}>
                <Link to={`/search?q=${encodeURIComponent(person.username)}`} className="rail-person">
                  <Avatar name={person.display_name} username={person.username} size={40} />
                  <div className="rail-person-info">
                    <div className="rail-person-name">{person.display_name}</div>
                    <div className="rail-person-username">@{person.username}</div>
                    <div className="rail-person-blurb">{person.blurb}</div>
                  </div>
                </Link>
              </li>
            ))}
          </ul>
          <Link to="/search" className="rail-card-more">
            Show more
          </Link>
        </section>

        <section className="rail-card">
          <h2 className="rail-card-title">Trending in India</h2>
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
