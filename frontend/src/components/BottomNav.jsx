import { NavLink } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { IconHome, IconSearch, IconUser } from "./Icons";

export default function BottomNav() {
  const { user } = useAuth();
  if (!user) return null;

  return (
    <nav className="bottom-nav">
      <NavLink to="/feed" className={({ isActive }) => `bottom-nav-link ${isActive ? "active" : ""}`} end>
        <IconHome className="bottom-nav-icon" />
      </NavLink>
      <NavLink to="/search" className={({ isActive }) => `bottom-nav-link ${isActive ? "active" : ""}`}>
        <IconSearch className="bottom-nav-icon" />
      </NavLink>
      <NavLink to={`/u/${user.username}`} className={({ isActive }) => `bottom-nav-link ${isActive ? "active" : ""}`}>
        <IconUser className="bottom-nav-icon" />
      </NavLink>
    </nav>
  );
}
