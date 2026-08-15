import { NavLink } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { useT } from "../context/LocaleContext";
import { IconArena, IconHome, IconLive, IconSquare, IconUser } from "./Icons";

/**
 * Thumb bar: Home · Square · Live · Arenas · You
 * Alerts stay in PlazaTopBar / hamburger (keeps 5 slots).
 */
export default function BottomNav() {
  const { user } = useAuth();
  const t = useT();

  if (!user) return null;

  return (
    <nav className="bottom-nav" aria-label={t("nav.main")}>
      <NavLink
        to="/home"
        className={({ isActive }) => `bottom-nav-link ${isActive ? "active" : ""}`}
        end
        aria-label={t("nav.home")}
        data-coach="nav-home"
      >
        <IconHome className="bottom-nav-icon" />
        <span className="bottom-nav-label">{t("nav.home")}</span>
      </NavLink>
      <NavLink
        to="/feed"
        className={({ isActive }) => `bottom-nav-link ${isActive ? "active" : ""}`}
        end
        aria-label={t("nav.square")}
        data-coach="nav-square"
      >
        <IconSquare className="bottom-nav-icon" />
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
