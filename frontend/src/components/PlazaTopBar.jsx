import { Link, NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import Logo from "./Logo";
import Avatar from "./Avatar";
import { ARENA_TOPICS } from "../arenas";
import { IconSearch } from "./Icons";

/**
 * BaratX plaza chrome — top brand + orbit nav.
 * Replaces the Twitter-style left icon rail on Square / Profile / Live.
 */
export default function PlazaTopBar() {
  const { user } = useAuth();
  const navigate = useNavigate();

  return (
    <header className="plaza-top">
      <div className="plaza-top-inner">
        <Link to="/feed" className="plaza-brand" aria-label="BaratX Square">
          <Logo variant="full" className="plaza-brand-logo" title="BaratX" />
        </Link>

        <nav className="plaza-primary" aria-label="Plaza">
          <NavLink to="/feed" className={({ isActive }) => `plaza-link${isActive ? " is-active" : ""}`} end>
            Square
          </NavLink>
          <NavLink to="/spaces" className={({ isActive }) => `plaza-link${isActive ? " is-active" : ""}`}>
            Live
          </NavLink>
          <NavLink to="/arenas" className={({ isActive }) => `plaza-link${isActive ? " is-active" : ""}`}>
            Arenas
          </NavLink>
          <NavLink to="/search" className={({ isActive }) => `plaza-link${isActive ? " is-active" : ""}`}>
            Explore
          </NavLink>
        </nav>

        <div className="plaza-top-actions">
          <button
            type="button"
            className="plaza-search-btn"
            aria-label="Search"
            onClick={() => navigate("/search")}
          >
            <IconSearch className="plaza-search-icon" />
          </button>
          {user && (
            <Link to={`/u/${user.username}`} className="plaza-avatar-link" aria-label="Profile">
              <Avatar name={user.display_name} username={user.username} url={user.avatar_url} size={34} />
            </Link>
          )}
        </div>
      </div>

      <nav className="plaza-orbits" aria-label="Orbits">
        {ARENA_TOPICS.map((a) => (
          <Link
            key={a.key}
            to={`/arenas/${a.key}`}
            className="plaza-orbit"
            style={{ "--arena-accent": a.accent }}
          >
            {a.name}
          </Link>
        ))}
        <Link to="/spaces" className="plaza-orbit plaza-orbit-live">
          On air
        </Link>
      </nav>
    </header>
  );
}
