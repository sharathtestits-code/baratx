import { useEffect, useId, useRef, useState } from "react";
import { createPortal } from "react-dom";
import { useLocation, useNavigate } from "react-router-dom";
import { api } from "../api";
import { useAuth } from "../context/AuthContext";
import { usePlazaMenu } from "../context/PlazaMenuContext";
import { ARENA_TOPICS } from "../arenas";
import ThemePicker from "./ThemePicker";
import { applyTheme, getStoredTheme, markThemeChosen } from "../theme";

/**
 * Change Arena drawer — arenas first, then appearance themes.
 */
export default function PlazaSideMenu() {
  const { open, close } = usePlazaMenu();
  const { token, user, updateUser } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const pathRef = useRef(location.pathname);
  const listId = useId();
  const themeId = useId();
  const [pickerOpen, setPickerOpen] = useState(true);
  const [theme, setTheme] = useState(() => user?.theme || getStoredTheme());
  const [themeSaving, setThemeSaving] = useState(false);
  const [themeMsg, setThemeMsg] = useState("");
  const switchRef = useRef(null);

  useEffect(() => {
    if (user?.theme) setTheme(user.theme);
  }, [user?.theme]);

  // Close drawer only when the route actually changes (not on first mount).
  useEffect(() => {
    if (pathRef.current !== location.pathname) {
      pathRef.current = location.pathname;
      close();
    }
  }, [location.pathname, close]);

  // Reset picker open whenever the drawer opens.
  useEffect(() => {
    if (open) {
      setPickerOpen(true);
      setThemeMsg("");
    }
  }, [open]);

  useEffect(() => {
    document.body.classList.toggle("plaza-menu-is-open", open);
    return () => document.body.classList.remove("plaza-menu-is-open");
  }, [open]);

  useEffect(() => {
    if (!open) return undefined;
    function onKey(e) {
      if (e.key === "Escape") {
        if (pickerOpen) {
          setPickerOpen(false);
          return;
        }
        close();
      }
    }
    window.addEventListener("keydown", onKey);
    const prevOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => {
      window.removeEventListener("keydown", onKey);
      document.body.style.overflow = prevOverflow;
    };
  }, [open, close, pickerOpen]);

  function goArena(key) {
    setPickerOpen(false);
    close();
    navigate(`/arenas/${key}`);
  }

  function goMyArenas() {
    setPickerOpen(false);
    close();
    navigate("/arenas");
  }

  function goSettings() {
    close();
    navigate("/settings");
  }

  async function saveTheme(nextId) {
    setTheme(nextId);
    applyTheme(nextId);
    markThemeChosen();
    setThemeMsg("");
    if (!token) {
      setThemeMsg("Theme saved on this device.");
      return;
    }
    setThemeSaving(true);
    try {
      const updated = await api.updateMe(token, { theme: nextId });
      updateUser(updated);
      setThemeMsg("Appearance saved.");
    } catch {
      setThemeMsg("Saved on this device.");
    } finally {
      setThemeSaving(false);
    }
  }

  if (typeof document === "undefined") return null;

  const activeKey = location.pathname.startsWith("/arenas/")
    ? location.pathname.split("/")[2]
    : "";

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
        aria-label="Menu"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="plaza-side-head">
          <button
            ref={switchRef}
            type="button"
            className={`plaza-side-arena-switch${pickerOpen ? " is-open" : ""}`}
            aria-expanded={pickerOpen}
            aria-controls={listId}
            onClick={() => setPickerOpen((v) => !v)}
          >
            <span className="plaza-side-arena-name">
              Bharat
              <svg
                className={`plaza-side-chevron${pickerOpen ? " is-open" : ""}`}
                viewBox="0 0 16 16"
                aria-hidden="true"
              >
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

        <nav
          id={listId}
          className={`plaza-side-arenas${pickerOpen ? " is-open" : ""}`}
          aria-label="Arenas"
          hidden={!pickerOpen}
        >
          <ul className="plaza-side-arena-list">
            {ARENA_TOPICS.map((a) => {
              const isActive = activeKey === a.key;
              return (
                <li key={a.key}>
                  <button
                    type="button"
                    className={`plaza-side-arena${isActive ? " is-active" : ""}`}
                    style={{ "--arena-accent": a.accent }}
                    onClick={() => goArena(a.key)}
                  >
                    <span className="plaza-side-arena-bar" aria-hidden="true" />
                    <strong>{a.name}</strong>
                  </button>
                </li>
              );
            })}
          </ul>
        </nav>

        {!pickerOpen && (
          <p className="plaza-side-picker-hint">Tap Change Arena to pick Sports, Politics, and more.</p>
        )}

        <section className="plaza-side-theme" aria-labelledby={themeId}>
          <div className="plaza-side-theme-head">
            <h2 id={themeId}>Appearance</h2>
            <p>Pick your look — Midnight, Saffron, Monsoon, or Ink.</p>
          </div>
          <ThemePicker value={theme} onChange={saveTheme} compact />
          {(themeSaving || themeMsg) && (
            <p className="plaza-side-theme-status" role="status">
              {themeSaving ? "Saving…" : themeMsg}
            </p>
          )}
        </section>

        <button type="button" className="plaza-side-manage" onClick={goMyArenas}>
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
        </button>

        <button type="button" className="plaza-side-manage plaza-side-settings" onClick={goSettings}>
          <span className="plaza-side-manage-copy">
            <strong>Settings</strong>
            <em>Privacy, mutes, and more</em>
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
        </button>
      </aside>
    </>,
    document.body
  );
}
