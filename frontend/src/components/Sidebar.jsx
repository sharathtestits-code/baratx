import { Link, NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { IconHome, IconLogout, IconSearch, IconUser } from "./Icons";
import Avatar from "./Avatar";
import Logo from "./Logo";

export default function Sidebar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  if (!user) return null;

  function handleLogout() {
    logout();
    navigate("/login");
  }

  return (
    <aside className="sidebar">
      <div className="sidebar-top">
        <Link to="/feed" className="sidebar-brand" aria-label="BaratX Home">
          <Logo variant="mark" className="sidebar-logo-mark" />
          <Logo variant="wordmark" className="sidebar-logo-wordmark" />
        </Link>
        <nav className="sidebar-nav" aria-label="Primary">
          <NavLink to="/feed" className={({ isActive }) => `sidebar-link ${isActive ? "active" : ""}`}>
            <IconHome className="sidebar-icon" />
            <span>Home</span>
          </NavLink>
          <NavLink to="/search" className={({ isActive }) => `sidebar-link ${isActive ? "active" : ""}`}>
            <IconSearch className="sidebar-icon" />
            <span>Search</span>
          </NavLink>
          <NavLink to={`/u/${user.username}`} className={({ isActive }) => `sidebar-link ${isActive ? "active" : ""}`}>
            <IconUser className="sidebar-icon" />
            <span>Profile</span>
          </NavLink>
        </nav>
      </div>

      <button type="button" className="sidebar-user" onClick={handleLogout} title="Log out">
        <Avatar name={user.display_name} username={user.username} url={user.avatar_url} size={36} />
        <div className="sidebar-user-info">
          <div className="sidebar-user-name">{user.display_name}</div>
          <div className="sidebar-user-username">@{user.username}</div>
        </div>
        <IconLogout className="sidebar-logout-icon" />
      </button>
    </aside>
  );
}
