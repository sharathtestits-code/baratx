import { useEffect } from "react";
import { Link, useLocation } from "react-router-dom";
import { usePlazaMenu } from "../context/PlazaMenuContext";
import { ARENA_TOPICS } from "../arenas";

/**
 * Collapsible plaza side menu — matches the Change Arena rail mockup.
 * Opens/closes from the top-bar hamburger; not a fixed Twitter rail.
 */
export default function PlazaSideMenu() {
  const { open, close } = usePlazaMenu();
  const location = useLocation();

  useEffect(() => {
    close();
  }, [location.pathname, close]);

  useEffect(() => {
    if (!open) return undefined;
    function onKey(e) {
      if (e.key === "Escape") close();
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open, close]);

  return (
    <>
      <div
        className={`plaza-menu-backdrop${open ? " is-open" : ""}`}
        onClick={close}
        aria-hidden={!open}
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
          <button type="button" className="plaza-side-close" onClick={close} aria-label="Close menu">
            ×
          </button>
        </div>

        <nav className="plaza-side-arenas" aria-label="Arenas">
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
                  <strong>{a.name}</strong>
                </Link>
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
    </>
  );
}
