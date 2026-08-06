/** Blue / gold account identity — colored names, no generic checkmark. */

export function badgeOf(userOrAuthor) {
  if (!userOrAuthor) return "none";
  const b = (userOrAuthor.badge || "").toLowerCase();
  if (b === "blue" || b === "gold") return b;
  if (userOrAuthor.is_official) return "blue";
  return "none";
}

/** CSS class for a display name (and optional @handle). */
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
