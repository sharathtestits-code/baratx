import { useEffect, useState } from "react";
import { Link, NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { notificationsApi } from "../api";
import { IconBell, IconBookmark, IconHome, IconLogout, IconMessage, IconSearch, IconUser, IconMore } from "./Icons";
import Avatar from "./Avatar";
import Logo from "./Logo";

export default function Sidebar() {
  const { user, token, logout } = useAuth();
  const navigate = useNavigate();
  const [unread, setUnread] = useState(0);

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
        <Link to="/feed" className="sidebar-brand sidebar-brand-mark" aria-label="BaratX Home">
          <Logo variant="mark" className="sidebar-logo-mark" />
        </Link>
        <nav className="sidebar-nav" aria-label="Primary">
          <NavLink to="/feed" className={({ isActive }) => `sidebar-link ${isActive ? "active" : ""}`}>
            <IconHome className="sidebar-icon" />
            <span>Home</span>
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
            <span>Notifications</span>
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
        </nav>
        <button type="button" className="sidebar-post-btn" onClick={goCompose}>
          Post
        </button>
      </div>

      <div className="sidebar-user-wrap">
        <button type="button" className="sidebar-user" onClick={handleLogout} title="Log out">
          <Avatar name={user.display_name} username={user.username} url={user.avatar_url} size={40} />
          <div className="sidebar-user-info">
            <div className="sidebar-user-name">{user.display_name}</div>
            <div className="sidebar-user-username">@{user.username}</div>
          </div>
          <IconMore className="sidebar-more-icon" />
        </button>
        <button type="button" className="sidebar-logout-text" onClick={handleLogout}>
          <IconLogout className="sidebar-logout-icon" />
          Log out
        </button>
      </div>
    </aside>
  );
}
