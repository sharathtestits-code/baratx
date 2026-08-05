import { useEffect, useState } from "react";
import { NavLink } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { notificationsApi } from "../api";
import { IconBell, IconHome, IconSearch, IconUser } from "./Icons";

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
    <nav className="bottom-nav">
      <NavLink to="/feed" className={({ isActive }) => `bottom-nav-link ${isActive ? "active" : ""}`} end>
        <IconHome className="bottom-nav-icon" />
      </NavLink>
      <NavLink to="/search" className={({ isActive }) => `bottom-nav-link ${isActive ? "active" : ""}`}>
        <IconSearch className="bottom-nav-icon" />
      </NavLink>
      <NavLink
        to="/notifications"
        className={({ isActive }) => `bottom-nav-link ${isActive ? "active" : ""}`}
      >
        <span className="bottom-nav-icon-wrap">
          <IconBell className="bottom-nav-icon" />
          {unread > 0 && <span className="nav-badge nav-badge-sm">{unread > 9 ? "9+" : unread}</span>}
        </span>
      </NavLink>
      <NavLink to={`/u/${user.username}`} className={({ isActive }) => `bottom-nav-link ${isActive ? "active" : ""}`}>
        <IconUser className="bottom-nav-icon" />
      </NavLink>
    </nav>
  );
}
