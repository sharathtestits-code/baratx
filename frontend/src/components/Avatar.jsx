import { mediaUrl } from "../api";

const PALETTE = [
  "#ff671f",
  "#138808",
  "#000080",
  "#ff9933",
  "#0f766e",
  "#1d4ed8",
  "#b45309",
  "#7c3aed",
];

function colorFor(seed) {
  let hash = 0;
  for (let i = 0; i < seed.length; i++) {
    hash = seed.charCodeAt(i) + ((hash << 5) - hash);
  }
  return PALETTE[Math.abs(hash) % PALETTE.length];
}

function initialsFor(name) {
  if (!name) return "?";
  const parts = name.trim().split(/\s+/);
  if (parts.length === 1) return parts[0].slice(0, 2).toUpperCase();
  return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
}

export default function Avatar({ name, username, url = null, size = 44 }) {
  const seed = username || name || "?";

  if (url) {
    return (
      <img
        className="avatar avatar-photo"
        src={mediaUrl(url)}
        alt=""
        style={{ width: size, height: size, minWidth: size }}
      />
    );
  }

  const bg = colorFor(seed);
  const initials = initialsFor(name || username || "?");

  return (
    <div
      className="avatar"
      style={{
        width: size,
        height: size,
        minWidth: size,
        backgroundColor: bg,
        fontSize: Math.round(size * 0.4),
      }}
      aria-hidden="true"
    >
      {initials}
    </div>
  );
}
