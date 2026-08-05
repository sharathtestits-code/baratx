import { useEffect, useRef, useState } from "react";
import { Link, NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { notificationsApi } from "../api";
import { IconBell, IconBookmark, IconHome, IconMessage, IconSearch, IconUser, IconMore } from "./Icons";
import Avatar from "./Avatar";
import Logo from "./Logo";

const MORE_LINKS = [
  { to: "/lists", label: "Lists" },
  { to: "/communities", label: "Communities" },
  { to: "/spaces", label: "Spaces" },
  { to: "/settings", label: "Settings and privacy" },
];

export default function Sidebar() {
  const { user, token, logout } = useAuth();
  const navigate = useNavigate();
  const [unread, setUnread] = useState(0);
  const [moreOpen, setMoreOpen] = useState(false);
  const moreRef = useRef(null);

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

  useEffect(() => {
    if (!moreOpen) return;
    function onDoc(e) {
      const t = e.target;
      if (t.closest?.(".sidebar-more-btn") || t.closest?.(".sidebar-user")) return;
      if (moreRef.current && !moreRef.current.contains(t)) {
        setMoreOpen(false);
      }
    }
    function onKey(e) {
      if (e.key === "Escape") setMoreOpen(false);
    }
    document.addEventListener("mousedown", onDoc);
    document.addEventListener("keydown", onKey);
    return () => {
      document.removeEventListener("mousedown", onDoc);
      document.removeEventListener("keydown", onKey);
    };
  }, [moreOpen]);

  if (!user) return null;

  function handleLogout() {
    setMoreOpen(false);
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

  function toggleMore() {
    setMoreOpen((v) => !v);
  }

  const moreMenu = moreOpen ? (
    <div className="more-menu" role="menu">
      {MORE_LINKS.map((item) => (
        <Link
          key={item.to}
          to={item.to}
          role="menuitem"
          className="more-menu-item"
          onClick={() => setMoreOpen(false)}
        >
          {item.label}
        </Link>
      ))}
      <button
        type="button"
        role="menuitem"
        className="more-menu-item more-menu-logout"
        onClick={handleLogout}
      >
        Log out @{user.username}
      </button>
    </div>
  ) : null;

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

          <div className="sidebar-more-wrap">
            <button
              type="button"
              className={`sidebar-link sidebar-more-btn ${moreOpen ? "active" : ""}`}
              aria-haspopup="menu"
              aria-expanded={moreOpen}
              onClick={toggleMore}
            >
              <IconMore className="sidebar-icon" />
              <span>More</span>
            </button>
          </div>
        </nav>
        <button type="button" className="sidebar-post-btn" onClick={goCompose}>
          Post
        </button>
      </div>

      <div className="sidebar-user-wrap" ref={moreRef}>
        <button
          type="button"
          className="sidebar-user"
          aria-haspopup="menu"
          aria-expanded={moreOpen}
          title="Account and more"
          onClick={toggleMore}
        >
          <Avatar name={user.display_name} username={user.username} url={user.avatar_url} size={40} />
          <div className="sidebar-user-info">
            <div className="sidebar-user-name">{user.display_name}</div>
            <div className="sidebar-user-username">@{user.username}</div>
          </div>
          <IconMore className="sidebar-more-icon" />
        </button>
        {moreMenu}
      </div>
    </aside>
  );
}
