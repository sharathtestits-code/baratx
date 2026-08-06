import { Link } from "react-router-dom";

/** Split post/reply text into plain + @mention/#hashtag links (matches backend text_parse). */
export function linkifyText(text) {
  const parts = String(text || "").split(/([@#][A-Za-z0-9][A-Za-z0-9._-]{1,39})/g);
  return parts.map((part, i) => {
    if (part.startsWith("@") && part.length >= 3) {
      const u = part.slice(1);
      return (
        <Link key={i} to={`/u/${encodeURIComponent(u)}`} className="text-link" onClick={(e) => e.stopPropagation()}>
          {part}
        </Link>
      );
    }
    if (part.startsWith("#") && part.length >= 3) {
      const tag = part.slice(1);
      return (
        <Link
          key={i}
          to={`/hashtag/${encodeURIComponent(tag)}`}
          className="text-link"
          onClick={(e) => e.stopPropagation()}
        >
          {part}
        </Link>
      );
    }
    return <span key={i}>{part}</span>;
  });
}
