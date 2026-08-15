import { useEffect, useState } from "react";
import { NavLink } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { useT } from "../context/LocaleContext";
import { notificationsApi } from "../api";
import { IconArena, IconBell, IconHome, IconLive, IconUser } from "./Icons";

/**
 * Thumb bar: Square · Live · Arenas · Alerts · Profile
 * Explore stays in PlazaTopBar / hamburger (keeps 5 slots).
 */
export default function BottomNav() {
  const { user, token } = useAuth();
  const t = useT();
  const [unread, setUnread] = useState(0);

  useEffect(() => {
    if (!token) return;
    let cancelled = false;
    async function refresh() {
      try {
        const data = await notificationsApi.unreadCount(token);
        if (!cancelled) setUnread(data.unread_count || 0);
      } catch {
        // ignore
      }
    }
    refresh();
    const onRead = () => setUnread(0);
    window.addEventListener("bx:notifications-read", onRead);
    return () => {
      cancelled = true;
      window.removeEventListener("bx:notifications-read", onRead);
    };
  }, [token]);

  if (!user) return null;

  return (
    <nav className="bottom-nav" aria-label={t("nav.main")}>
      <NavLink
        to="/feed"
        className={({ isActive }) => `bottom-nav-link ${isActive ? "active" : ""}`}
        end
        aria-label={t("nav.square")}
        data-coach="nav-square"
      >
        <IconHome className="bottom-nav-icon" />
        <span className="bottom-nav-label">{t("nav.square")}</span>
      </NavLink>
      <NavLink
        to="/spaces"
        className={({ isActive }) => `bottom-nav-link ${isActive ? "active" : ""}`}
        aria-label={t("nav.live")}
        data-coach="nav-live"
      >
        <IconLive className="bottom-nav-icon" />
        <span className="bottom-nav-label">{t("nav.live")}</span>
      </NavLink>
      <NavLink
        to="/arenas"
        className={({ isActive }) => `bottom-nav-link ${isActive ? "active" : ""}`}
        aria-label={t("nav.arenas")}
        data-coach="nav-arenas"
      >
        <IconArena className="bottom-nav-icon" />
        <span className="bottom-nav-label">{t("nav.arenas")}</span>
      </NavLink>
      <NavLink
        to="/notifications"
        className={({ isActive }) => `bottom-nav-link ${isActive ? "active" : ""}`}
        aria-label={t("nav.alerts")}
        data-coach="nav-alerts"
      >
        <span className="bottom-nav-icon-wrap">
          <IconBell className="bottom-nav-icon" />
          {unread > 0 && <span className="nav-badge nav-badge-sm">{unread > 9 ? "9+" : unread}</span>}
        </span>
        <span className="bottom-nav-label">{t("nav.alerts")}</span>
      </NavLink>
      <NavLink
        to={`/u/${user.username}`}
        className={({ isActive }) => `bottom-nav-link ${isActive ? "active" : ""}`}
        aria-label={t("nav.profile")}
        data-coach="nav-you"
      >
        <IconUser className="bottom-nav-icon" />
        <span className="bottom-nav-label">{t("nav.you")}</span>
      </NavLink>
    </nav>
  );
}
