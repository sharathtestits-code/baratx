import { useEffect, useState } from "react";
import { Link, NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { usePlazaMenu } from "../context/PlazaMenuContext";
import { useT } from "../context/LocaleContext";
import { notificationsApi } from "../api";
import Logo from "./Logo";
import Avatar from "./Avatar";
import { ARENA_TOPICS, CIRCLE_TOPICS } from "../arenas";
import { IconBell, IconSearch } from "./Icons";

/**
 * BarathX plaza chrome — top brand + orbit nav + menu toggle.
 */
export default function PlazaTopBar() {
  const { user, token } = useAuth();
  const navigate = useNavigate();
  const { open, toggle } = usePlazaMenu();
  const t = useT();
  const [unread, setUnread] = useState(0);

  useEffect(() => {
    if (!token) {
      setUnread(0);
      return undefined;
    }
    let cancelled = false;
    async function refresh() {
      try {
        const data = await notificationsApi.unreadCount(token);
        if (!cancelled) setUnread(data.unread_count || 0);
      } catch {
        /* ignore */
      }
    }
    refresh();
    const onRead = () => setUnread(0);
    window.addEventListener("bx:notifications-read", onRead);
    const id = window.setInterval(refresh, 45000);
    return () => {
      cancelled = true;
      window.removeEventListener("bx:notifications-read", onRead);
      window.clearInterval(id);
    };
  }, [token]);

  return (
    <header className="plaza-top">
      <div className="plaza-top-inner">
        <button
          type="button"
          className={`plaza-menu-toggle${open ? " is-open" : ""}`}
          onClick={(e) => {
            e.preventDefault();
            e.stopPropagation();
            toggle();
          }}
          aria-label={open ? t("nav.closeMenu") : t("nav.openMenu")}
          aria-expanded={open}
          aria-controls="plaza-side-menu"
        >
          <span />
          <span />
          <span />
        </button>

        <Link to="/home" className="plaza-brand" aria-label="BarathX">
          <Logo variant="full" className="plaza-brand-logo" title="BarathX" />
        </Link>

        <nav className="plaza-primary" aria-label={t("nav.plaza")}>
          <NavLink to="/home" className={({ isActive }) => `plaza-link${isActive ? " is-active" : ""}`} end>
            {t("nav.home")}
          </NavLink>
          <NavLink to="/feed" className={({ isActive }) => `plaza-link${isActive ? " is-active" : ""}`} end>
            {t("nav.square")}
          </NavLink>
          <NavLink to="/spaces" className={({ isActive }) => `plaza-link${isActive ? " is-active" : ""}`}>
            {t("nav.live")}
          </NavLink>
          <NavLink to="/arenas" className={({ isActive }) => `plaza-link${isActive ? " is-active" : ""}`}>
            {t("nav.arenas")}
          </NavLink>
          <NavLink to="/search" className={({ isActive }) => `plaza-link${isActive ? " is-active" : ""}`}>
            {t("nav.explore")}
          </NavLink>
        </nav>

        <div className="plaza-top-actions">
          <button
            type="button"
            className="plaza-search-btn"
            aria-label={t("nav.search")}
            onClick={() => navigate("/search")}
          >
            <IconSearch className="plaza-search-icon" />
          </button>
          {user && (
            <button
              type="button"
              className="plaza-alerts-btn"
              aria-label={t("nav.alerts")}
              onClick={() => navigate("/notifications")}
            >
              <span className="plaza-alerts-wrap">
                <IconBell className="plaza-alerts-icon" />
                {unread > 0 && (
                  <span className="nav-badge nav-badge-sm">{unread > 9 ? "9+" : unread}</span>
                )}
              </span>
            </button>
          )}
          {user && (
            <Link to={`/u/${user.username}`} className="plaza-avatar-link" aria-label={t("nav.profile")}>
              <Avatar name={user.display_name} username={user.username} url={user.avatar_url} size={34} />
            </Link>
          )}
        </div>
      </div>

      <nav className="plaza-orbits" aria-label="Orbits">
        {[...CIRCLE_TOPICS, ...ARENA_TOPICS].map((a) => (
          <Link
            key={a.key}
            to={`/arenas/${a.key}`}
            className="plaza-orbit"
            style={{ "--arena-accent": a.accent }}
          >
            {t(`arena.${a.key}`)}
          </Link>
        ))}
        <Link to="/spaces" className="plaza-orbit plaza-orbit-live">
          {t("square.liveNow")}
        </Link>
      </nav>
    </header>
  );
}
