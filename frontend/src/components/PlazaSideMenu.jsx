import { useEffect } from "react";
import { Link, NavLink, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { usePlazaMenu } from "../context/PlazaMenuContext";
import { ARENA_TOPICS } from "../arenas";
import { IconHome, IconLive, IconArena, IconSearch, IconUser, IconMore } from "./Icons";

/**
 * Collapsible plaza side menu — arenas + primary links.
 * Opens/closes from the top-bar control; not a fixed Twitter rail.
 */
export default function PlazaSideMenu() {
  const { user } = useAuth();
  const { open, close } = usePlazaMenu();
  const location = useLocation();

  useEffect(() => {
    close();
  }, [location.pathname, close]);

  return (
    <>
      <div
        className={`plaza-menu-backdrop${open ? " is-open" : ""}`}
        onClick={close}
        aria-hidden={!open}
      />
      <aside className={`plaza-side-menu${open ? " is-open" : ""}`} aria-hidden={!open} aria-label="Menu">
        <div className="plaza-side-head">
          <div>
            <p className="plaza-side-eyebrow">Arenas</p>
            <p className="plaza-side-title">{user?.display_name || "BaratX"}</p>
          </div>
          <button type="button" className="plaza-side-close" onClick={close} aria-label="Close menu">
            ×
          </button>
        </div>

        <nav className="plaza-side-primary" aria-label="Primary">
          <NavLink to="/feed" className={({ isActive }) => `plaza-side-link${isActive ? " is-active" : ""}`} end>
            <IconHome className="plaza-side-icon" />
            Square
          </NavLink>
          <NavLink to="/spaces" className={({ isActive }) => `plaza-side-link${isActive ? " is-active" : ""}`}>
            <IconLive className="plaza-side-icon" />
            Live
          </NavLink>
          <NavLink to="/arenas" className={({ isActive }) => `plaza-side-link${isActive ? " is-active" : ""}`}>
            <IconArena className="plaza-side-icon" />
            Arenas
          </NavLink>
          <NavLink to="/search" className={({ isActive }) => `plaza-side-link${isActive ? " is-active" : ""}`}>
            <IconSearch className="plaza-side-icon" />
            Explore
          </NavLink>
          {user && (
            <NavLink
              to={`/u/${user.username}`}
              className={({ isActive }) => `plaza-side-link${isActive ? " is-active" : ""}`}
            >
              <IconUser className="plaza-side-icon" />
              Profile
            </NavLink>
          )}
          <NavLink to="/settings" className={({ isActive }) => `plaza-side-link${isActive ? " is-active" : ""}`}>
            <IconMore className="plaza-side-icon" />
            More
          </NavLink>
        </nav>

        <div className="plaza-side-arenas">
          <p className="plaza-side-section-label">Change arena</p>
          <ul className="plaza-side-arena-list">
            {ARENA_TOPICS.map((a) => (
              <li key={a.key}>
                <Link
                  to={`/arenas/${a.key}`}
                  className="plaza-side-arena"
                  style={{ "--arena-accent": a.accent }}
                  onClick={close}
                >
                  <span className="plaza-side-arena-bar" aria-hidden="true" />
                  <span>
                    <strong>{a.name}</strong>
                    <em>{a.blurb}</em>
                  </span>
                </Link>
              </li>
            ))}
            <li>
              <Link
                to="/spaces"
                className="plaza-side-arena plaza-side-arena-live"
                style={{ "--arena-accent": "#ff9933" }}
                onClick={close}
              >
                <span className="plaza-side-arena-bar" aria-hidden="true" />
                <span>
                  <strong>Live / On air</strong>
                  <em>Airwaves rooms happening now</em>
                </span>
              </Link>
            </li>
          </ul>
        </div>

        <Link to="/arenas" className="plaza-side-manage" onClick={close}>
          <span>My Arenas</span>
          <span className="hint">Manage your favourite arenas →</span>
        </Link>
      </aside>
    </>
  );
}
