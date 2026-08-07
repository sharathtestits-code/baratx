import { useEffect, useState } from "react";
import { Link, NavLink } from "react-router-dom";
import { usePlazaMenu } from "../context/PlazaMenuContext";
import { ARENA_TOPICS } from "../arenas";

/**
 * Change Arena left rail — docked on desktop (matches mockup), overlay on mobile.
 * Collapse/expand via the top-bar hamburger.
 */
export default function PlazaSideMenu() {
  const { open, close } = usePlazaMenu();
  const [isNarrow, setIsNarrow] = useState(() => {
    try {
      return window.matchMedia("(max-width: 899px)").matches;
    } catch {
      return false;
    }
  });

  useEffect(() => {
    const mq = window.matchMedia("(max-width: 899px)");
    function onChange(e) {
      setIsNarrow(e.matches);
    }
    setIsNarrow(mq.matches);
    mq.addEventListener("change", onChange);
    return () => mq.removeEventListener("change", onChange);
  }, []);

  useEffect(() => {
    if (!open || !isNarrow) return undefined;
    function onKey(e) {
      if (e.key === "Escape") close();
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open, isNarrow, close]);

  function onNavigate() {
    // Only auto-close on narrow screens (drawer). Keep docked rail open on desktop.
    if (isNarrow) close();
  }

  return (
    <>
      <div
        className={`plaza-menu-backdrop${open && isNarrow ? " is-open" : ""}`}
        onClick={close}
        aria-hidden={!open || !isNarrow}
      />
      <aside
        className={`plaza-side-menu${open ? " is-open" : ""}`}
        aria-hidden={!open}
        aria-label="Change arena"
      >
        <div className="plaza-side-head">
          <button type="button" className="plaza-side-arena-switch" aria-label="Current arena">
            <span className="plaza-side-arena-name">
              Bharat
              <svg className="plaza-side-chevron" viewBox="0 0 16 16" aria-hidden="true">
                <path
                  d="M4 6l4 4 4-4"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="1.75"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </svg>
            </span>
            <span className="plaza-side-change">Change Arena</span>
          </button>
          <button type="button" className="plaza-side-close" onClick={close} aria-label="Collapse menu">
            ×
          </button>
        </div>

        <nav className="plaza-side-arenas" aria-label="Arenas">
          <ul className="plaza-side-arena-list">
            {ARENA_TOPICS.map((a) => (
              <li key={a.key}>
                <NavLink
                  to={`/arenas/${a.key}`}
                  className={({ isActive }) => `plaza-side-arena${isActive ? " is-active" : ""}`}
                  style={{ "--arena-accent": a.accent }}
                  onClick={onNavigate}
                >
                  <span className="plaza-side-arena-bar" aria-hidden="true" />
                  <strong>{a.name}</strong>
                </NavLink>
              </li>
            ))}
          </ul>
        </nav>

        <Link to="/arenas" className="plaza-side-manage" onClick={onNavigate}>
          <span className="plaza-side-manage-copy">
            <strong>My Arenas</strong>
            <em>Manage your favourite arenas</em>
          </span>
          <svg className="plaza-side-manage-chevron" viewBox="0 0 16 16" aria-hidden="true">
            <path
              d="M6 4l4 4-4 4"
              fill="none"
              stroke="currentColor"
              strokeWidth="1.75"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        </Link>
      </aside>
    </>
  );
}
