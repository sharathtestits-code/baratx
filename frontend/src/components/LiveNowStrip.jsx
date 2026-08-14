import { Link } from "react-router-dom";
import { IconLive } from "./Icons";

/**
 * Live rooms strip — rail (desktop) or horizontal scroll (mobile via plaza-layout CSS).
 */
export default function LiveNowStrip({
  items = [],
  title = "Live now",
  seeAllTo = "/spaces",
  seeAllLabel = "Enter Live",
  emptyHint = "",
  limit = 6,
}) {
  const rows = Array.isArray(items) ? items.slice(0, limit) : [];
  if (!rows.length && !emptyHint) return null;

  return (
    <section className="plaza-onair plaza-rail-live" aria-label={title}>
      <div className="plaza-onair-head">
        <h2>
          <IconLive className="plaza-onair-icon" aria-hidden="true" /> {title}
        </h2>
        <Link to={seeAllTo}>{seeAllLabel}</Link>
      </div>
      {rows.length === 0 ? (
        <p className="hint plaza-rail-empty">{emptyHint}</p>
      ) : (
        <ul className="plaza-onair-list plaza-onair-scroll">
          {rows.map((d) => (
            <li key={d.id}>
              <Link to={`/spaces/${d.id}`} className="plaza-onair-card">
                <span className="live-pill">Live</span>
                <strong>{d.title}</strong>
                <span className="hint">
                  {d.topic_name || d.arena_name || (d.host?.username ? `@${d.host.username}` : "Debate")}
                  {typeof d.post_count === "number" ? ` · ${d.post_count} takes` : ""}
                </span>
              </Link>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
