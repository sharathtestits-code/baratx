import { Link, NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { IconHome, IconLogout, IconSearch, IconUser, IconMore } from "./Icons";
import Avatar from "./Avatar";
import Logo from "./Logo";

export default function Sidebar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  if (!user) return null;

  function handleLogout() {
    logout();
    navigate("/");
  }

  function goCompose() {
    navigate("/feed");
    // Focus compose after navigation
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
