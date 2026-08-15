/**
 * Parse API datetime strings. Backend often emits naive UTC without "Z".
 * Treat bare ISO datetimes as UTC so local timezone display is correct.
 */
export function parseApiDate(value) {
  if (!value) return null;
  if (value instanceof Date) {
    return Number.isNaN(value.getTime()) ? null : value;
  }
  const raw = String(value).trim();
  if (!raw) return null;
  const hasZone = /(?:Z|[+-]\d{2}:?\d{2})$/i.test(raw);
  const normalized = hasZone ? raw : `${raw}Z`;
  const date = new Date(normalized);
  return Number.isNaN(date.getTime()) ? null : date;
}

/** Relative label in the viewer's local clock (once parseApiDate is correct). */
export function timeAgo(dateStr, nowMs = Date.now()) {
  const date = parseApiDate(dateStr);
  if (!date) return "";
  const diffMs = nowMs - date.getTime();
  const sec = Math.floor(diffMs / 1000);
  if (sec < 60) return `${Math.max(sec, 1)}s`;
  const min = Math.floor(sec / 60);
  if (min < 60) return `${min}m`;
  const hr = Math.floor(min / 60);
  if (hr < 24) return `${hr}h`;
  const day = Math.floor(hr / 24);
  if (day < 7) return `${day}d`;
  return date.toLocaleDateString(undefined, { month: "short", day: "numeric" });
}

/** Absolute local timestamp for tooltips / titles. */
export function formatLocalWhen(dateStr) {
  const date = parseApiDate(dateStr);
  if (!date) return "";
  return date.toLocaleString(undefined, {
    month: "short",
    day: "numeric",
    year: date.getFullYear() !== new Date().getFullYear() ? "numeric" : undefined,
    hour: "numeric",
    minute: "2-digit",
  });
}
