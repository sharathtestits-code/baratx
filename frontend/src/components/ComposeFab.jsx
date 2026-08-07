import { useNavigate } from "react-router-dom";

/** Mobile floating compose — focuses the home composer (no separate /compose route). */
export default function ComposeFab() {
  const navigate = useNavigate();

  function goCompose() {
    navigate("/feed");
    requestAnimationFrame(() => {
      const el = document.querySelector(".compose textarea");
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
