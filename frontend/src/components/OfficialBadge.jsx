/** Blue / gold verification badges */

export function badgeOf(userOrAuthor) {
  if (!userOrAuthor) return "none";
  const b = (userOrAuthor.badge || "").toLowerCase();
  if (b === "blue" || b === "gold") return b;
  if (userOrAuthor.is_official) return "blue";
  return "none";
}

export default function OfficialBadge({ user, className = "" }) {
  const badge = badgeOf(user);
  if (badge !== "blue" && badge !== "gold") return null;
  const label = badge === "blue" ? "Official blue account" : "Gold account";
  return (
    <span
      className={`official-badge official-badge-${badge}${className ? ` ${className}` : ""}`}
      title={label}
      aria-label={label}
    >
      <svg viewBox="0 0 24 24" width="1em" height="1em" aria-hidden="true">
        <path
          fill="currentColor"
          d="M12 2.5l1.6 1.2 1.9-.4.9 1.8 1.9.7-.2 2 1.5 1.3-1.1 1.7.5 1.9-1.8.8-.8 1.8-2-.1L12 21.5l-1.4-1.7-2 .1-.8-1.8-1.8-.8.5-1.9-1.1-1.7 1.5-1.3-.2-2 1.9-.7.9-1.8 1.9.4L12 2.5zm-1.1 12.2l5-5-1.4-1.4-3.6 3.6-1.8-1.8-1.4 1.4 3.2 3.2z"
        />
      </svg>
    </span>
  );
}
