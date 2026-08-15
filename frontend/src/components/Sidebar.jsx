import { useEffect, useState } from "react";
import { Link, NavLink, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { notificationsApi } from "../api";
import { IconArena, IconBell, IconBookmark, IconHome, IconLive, IconLogout, IconMessage, IconSearch, IconSquare, IconUser, IconMore } from "./Icons";
import Avatar from "./Avatar";
import Logo from "./Logo";

const MORE_LINKS = [
  { to: "/rewards", label: "Rewards progress" },
  { to: "/lists", label: "Lists" },
  { to: "/communities", label: "Communities" },
  { to: "/settings", label: "Settings and privacy" },
];

const MORE_PATHS = MORE_LINKS.map((l) => l.to);

export default function Sidebar() {
  const { user, token, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const onMoreRoute = MORE_PATHS.some(
    (p) => location.pathname === p || location.pathname.startsWith(`${p}/`)
  );
  const [unread, setUnread] = useState(0);
  const [moreOpen, setMoreOpen] = useState(onMoreRoute);

  useEffect(() => {
    if (onMoreRoute) setMoreOpen(true);
  }, [onMoreRoute]);

  useEffect(() => {
    if (!token) return;
    let cancelled = false;

    async function refresh() {
      try {
        const data = await notificationsApi.unreadCount(token);
        if (!cancelled) setUnread(data.unread_count || 0);
      } catch {
        // ignore badge errors
      }
    }

    refresh();
    const onRead = () => setUnread(0);
    window.addEventListener("bx:notifications-read", onRead);
    const id = window.setInterval(refresh, 45000);
    return () => {
      cancelled = true;
      window.clearInterval(id);
      window.removeEventListener("bx:notifications-read", onRead);
    };
  }, [token]);

  if (!user) return null;

  function handleLogout() {
    logout();
    navigate("/");
  }

  function goCompose() {
    navigate("/feed");
    requestAnimationFrame(() => {
      const el = document.querySelector(".compose textarea");
      if (el) el.focus();
    });
  }

  return (
    <aside className="sidebar">
      <div className="sidebar-top">
        <Link to="/home" className="sidebar-brand" aria-label="BarathX Home">
          <Logo variant="full" className="sidebar-logo-full" title="BarathX" />
        </Link>
        <nav className="sidebar-nav" aria-label="Primary">
          <NavLink to="/home" className={({ isActive }) => `sidebar-link ${isActive ? "active" : ""}`}>
            <IconHome className="sidebar-icon" />
            <span>Home</span>
          </NavLink>
          <NavLink to="/feed" className={({ isActive }) => `sidebar-link ${isActive ? "active" : ""}`}>
            <IconSquare className="sidebar-icon" />
            <span>Square</span>
          </NavLink>
          <NavLink to="/spaces" className={({ isActive }) => `sidebar-link ${isActive ? "active" : ""}`}>
            <IconLive className="sidebar-icon" />
            <span>Live</span>
          </NavLink>
          <NavLink to="/arenas" className={({ isActive }) => `sidebar-link ${isActive ? "active" : ""}`}>
            <IconArena className="sidebar-icon" />
            <span>Arenas</span>
          </NavLink>
          <NavLink to="/search" className={({ isActive }) => `sidebar-link ${isActive ? "active" : ""}`}>
            <IconSearch className="sidebar-icon" />
            <span>Explore</span>
          </NavLink>
          <NavLink
            to="/notifications"
            className={({ isActive }) => `sidebar-link ${isActive ? "active" : ""}`}
          >
            <span className="sidebar-icon-wrap">
              <IconBell className="sidebar-icon" />
              {unread > 0 && <span className="nav-badge">{unread > 9 ? "9+" : unread}</span>}
            </span>
            <span>Alerts</span>
          </NavLink>
          <NavLink to="/messages" className={({ isActive }) => `sidebar-link ${isActive ? "active" : ""}`}>
            <IconMessage className="sidebar-icon" />
            <span>Messages</span>
          </NavLink>
          <NavLink to="/bookmarks" className={({ isActive }) => `sidebar-link ${isActive ? "active" : ""}`}>
            <IconBookmark className="sidebar-icon" />
            <span>Bookmarks</span>
          </NavLink>
          <NavLink to={`/u/${user.username}`} className={({ isActive }) => `sidebar-link ${isActive ? "active" : ""}`}>
            <IconUser className="sidebar-icon" />
            <span>Profile</span>
          </NavLink>

          <div className="sidebar-more-section">
            <button
              type="button"
              className={`sidebar-link sidebar-more-btn ${moreOpen || onMoreRoute ? "active" : ""}`}
              aria-expanded={moreOpen}
              onClick={() => setMoreOpen((v) => !v)}
            >
              <IconMore className="sidebar-icon" />
              <span>More</span>
            </button>
            {moreOpen && (
              <div className="sidebar-more-links" role="group" aria-label="More">
                {MORE_LINKS.map((item) => (
                  <NavLink
                    key={item.to}
                    to={item.to}
                    className={({ isActive }) =>
                      `sidebar-link sidebar-more-link ${isActive ? "active" : ""}`
                    }
                  >
                    <span>{item.label}</span>
                  </NavLink>
                ))}
              </div>
            )}
          </div>
        </nav>
        <button type="button" className="sidebar-post-btn" onClick={goCompose}>
          Post
        </button>
      </div>

      <div className="sidebar-user-wrap">
        <Link to={`/u/${user.username}`} className="sidebar-user" title="Your profile">
          <Avatar name={user.display_name} username={user.username} url={user.avatar_url} size={40} />
          <div className="sidebar-user-info">
            <div className="sidebar-user-name">{user.display_name}</div>
            <div className="sidebar-user-username">@{user.username}</div>
          </div>
        </Link>
        <button type="button" className="sidebar-logout-text" onClick={handleLogout}>
          <IconLogout className="sidebar-logout-icon" />
          Log out
        </button>
      </div>
    </aside>
  );
}
