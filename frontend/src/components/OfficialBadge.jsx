/** Blue / gold account identity — colored names only. New users stay default (no tint). */

export function badgeOf(userOrAuthor) {
  if (!userOrAuthor) return "none";
  const b = (userOrAuthor.badge || "").toLowerCase().trim();
  if (b === "blue") return "blue";
  if (b === "gold") return "gold";
  // Legacy: is_official alone only counts when badge is missing/none and explicitly official.
  if (!b || b === "none") {
    if (userOrAuthor.is_official) return "blue";
    return "none";
  }
  return "none";
}

/** Blue founders / blue badge holders can manage other accounts' badges. */
export function canManageBadges(user) {
  if (!user) return false;
  if (badgeOf(user) === "blue") return true;
  const u = (user.username || "").toLowerCase();
  return u === "sharath" || u === "baratx";
}

/** CSS class for a display name (and optional @handle). Empty tier = normal theme color. */
export function badgeNameClass(userOrAuthor, base = "") {
  const badge = badgeOf(userOrAuthor);
  const tier =
    badge === "blue" ? "name-badge-blue" : badge === "gold" ? "name-badge-gold" : "";
  return [base, tier].filter(Boolean).join(" ");
}

export function badgeLabel(userOrAuthor) {
  const badge = badgeOf(userOrAuthor);
  if (badge === "blue") return "Blue official";
  if (badge === "gold") return "Gold account";
  return "";
}
