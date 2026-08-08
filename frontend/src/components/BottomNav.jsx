import { useEffect, useState } from "react";
import { NavLink } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { notificationsApi } from "../api";
import { IconArena, IconBell, IconHome, IconLive, IconUser } from "./Icons";

/**
 * Thumb bar: Square · Live · Arenas · Alerts · Profile
 * Explore stays in PlazaTopBar / hamburger (keeps 5 slots).
 */
export default function BottomNav() {
  const { user, token } = useAuth();
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
    <nav className="bottom-nav" aria-label="Main">
      <NavLink to="/feed" className={({ isActive }) => `bottom-nav-link ${isActive ? "active" : ""}`} end aria-label="Square">
        <IconHome className="bottom-nav-icon" />
        <span className="bottom-nav-label">Square</span>
      </NavLink>
      <NavLink
        to="/spaces"
        className={({ isActive }) => `bottom-nav-link ${isActive ? "active" : ""}`}
        aria-label="Live"
      >
        <IconLive className="bottom-nav-icon" />
        <span className="bottom-nav-label">Live</span>
      </NavLink>
      <NavLink
        to="/arenas"
        className={({ isActive }) => `bottom-nav-link ${isActive ? "active" : ""}`}
        aria-label="Arenas"
      >
        <IconArena className="bottom-nav-icon" />
        <span className="bottom-nav-label">Arenas</span>
      </NavLink>
      <NavLink
        to="/notifications"
        className={({ isActive }) => `bottom-nav-link ${isActive ? "active" : ""}`}
        aria-label="Alerts"
      >
        <span className="bottom-nav-icon-wrap">
          <IconBell className="bottom-nav-icon" />
          {unread > 0 && <span className="nav-badge nav-badge-sm">{unread > 9 ? "9+" : unread}</span>}
        </span>
        <span className="bottom-nav-label">Alerts</span>
      </NavLink>
      <NavLink
        to={`/u/${user.username}`}
        className={({ isActive }) => `bottom-nav-link ${isActive ? "active" : ""}`}
        aria-label="Profile"
      >
        <IconUser className="bottom-nav-icon" />
        <span className="bottom-nav-label">You</span>
      </NavLink>
    </nav>
  );
}
