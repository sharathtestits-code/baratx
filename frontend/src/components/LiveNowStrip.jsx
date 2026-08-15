import { Link } from "react-router-dom";
import { IconLive } from "./Icons";
import { useT } from "../context/LocaleContext";

/**
 * Live rooms strip — rail (desktop) or horizontal scroll (mobile via plaza-layout CSS).
 */
export default function LiveNowStrip({
  items = [],
  title,
  seeAllTo = "/spaces",
  seeAllLabel,
  emptyHint = "",
  limit = 6,
}) {
  const t = useT();
  const resolvedTitle = title || t("square.liveNow");
  const resolvedSeeAll = seeAllLabel || t("square.enterLive");
  const rows = Array.isArray(items) ? items.slice(0, limit) : [];
  if (!rows.length && !emptyHint) return null;

  return (
    <section className="plaza-onair plaza-rail-live" aria-label={resolvedTitle}>
      <div className="plaza-onair-head">
        <h2>
          <IconLive className="plaza-onair-icon" aria-hidden="true" /> {resolvedTitle}
        </h2>
        <Link to={seeAllTo}>{resolvedSeeAll}</Link>
      </div>
      {rows.length === 0 ? (
        <p className="hint plaza-rail-empty">{emptyHint}</p>
      ) : (
        <ul className="plaza-onair-list plaza-onair-scroll">
          {rows.map((d) => (
            <li key={d.id}>
              <Link to={`/spaces/${d.id}`} className="plaza-onair-card">
                <span className="live-pill">{t("live.liveNow")}</span>
                <strong>{d.title}</strong>
                <span className="hint">
                  {d.topic_name || d.arena_name || (d.host?.username ? `@${d.host.username}` : "Debate")}
                  {typeof d.post_count === "number" ? ` · ${d.post_count}` : ""}
                </span>
              </Link>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
