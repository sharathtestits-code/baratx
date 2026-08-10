import { useLocation, useNavigate } from "react-router-dom";

/**
 * Mobile floating compose — hidden on Square (composer already there) and live rooms
 * so it cannot cover primary CTAs (audit P0 mobile overlap).
 */
export default function ComposeFab() {
  const navigate = useNavigate();
  const { pathname } = useLocation();

  const hide =
    pathname === "/feed" ||
    pathname.startsWith("/spaces/") ||
    pathname.startsWith("/onboarding") ||
    pathname === "/rewards" ||
    pathname === "/settings" ||
    pathname === "/guidelines" ||
    pathname === "/notifications" ||
    pathname === "/communities" ||
    pathname.startsWith("/communities/") ||
    pathname === "/messages" ||
    pathname.startsWith("/messages/") ||
    pathname === "/bookmarks" ||
    pathname === "/lists";

  if (hide) return null;

  function goCompose() {
    navigate("/feed");
    requestAnimationFrame(() => {
      const el = document.querySelector(".compose textarea, .plaza-studio textarea");
      if (el) {
        el.focus();
        window.scrollTo({ top: 0, behavior: "smooth" });
      }
    });
  }

  return (
    <button type="button" className="compose-fab" onClick={goCompose} aria-label="Compose">
      <svg viewBox="0 0 24 24" width="26" height="26" fill="none" stroke="currentColor" strokeWidth="2.4" aria-hidden>
        <path d="M12 5v14M5 12h14" strokeLinecap="round" />
      </svg>
    </button>
  );
}
