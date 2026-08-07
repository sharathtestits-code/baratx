import { useEffect, useRef } from "react";
import { createPortal } from "react-dom";
import { Link, NavLink, useLocation } from "react-router-dom";
import { usePlazaMenu } from "../context/PlazaMenuContext";
import { ARENA_TOPICS } from "../arenas";

/**
 * Change Arena drawer — portaled to document.body so stacking / overflow
 * never block open/close on Square, Explore, or other plaza pages.
 */
export default function PlazaSideMenu() {
  const { open, close } = usePlazaMenu();
  const location = useLocation();
  const pathRef = useRef(location.pathname);

  // Close only when the route actually changes (not on first mount).
  useEffect(() => {
    if (pathRef.current !== location.pathname) {
      pathRef.current = location.pathname;
      close();
    }
  }, [location.pathname, close]);

  useEffect(() => {
    document.body.classList.toggle("plaza-menu-is-open", open);
    return () => document.body.classList.remove("plaza-menu-is-open");
  }, [open]);

  useEffect(() => {
    if (!open) return undefined;
    function onKey(e) {
      if (e.key === "Escape") close();
    }
    window.addEventListener("keydown", onKey);
    const prevOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => {
      window.removeEventListener("keydown", onKey);
      document.body.style.overflow = prevOverflow;
    };
  }, [open, close]);

  if (typeof document === "undefined") return null;

  return createPortal(
    <>
      <div
        className={`plaza-menu-backdrop${open ? " is-open" : ""}`}
        onClick={close}
        aria-hidden={!open}
      />
      <aside
        id="plaza-side-menu"
        className={`plaza-side-menu${open ? " is-open" : ""}`}
        aria-hidden={!open}
        aria-label="Change arena"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="plaza-side-head">
          <div className="plaza-side-arena-switch">
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
          </div>
          <button type="button" className="plaza-side-close" onClick={close} aria-label="Close menu">
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
                  onClick={close}
                >
                  <span className="plaza-side-arena-bar" aria-hidden="true" />
                  <strong>{a.name}</strong>
                </NavLink>
              </li>
            ))}
          </ul>
        </nav>

        <Link to="/arenas" className="plaza-side-manage" onClick={close}>
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
    </>,
    document.body
  );
}
