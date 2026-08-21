import { Link } from "react-router-dom";
import { IconLive } from "./Icons";
import { useT } from "../context/LocaleContext";
import { debateHeadline, debateHeadlineContext, liveTakesLabel } from "../liveCopy";

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
          {rows.map((d) => {
            const head = debateHeadline(d.title);
            const context = debateHeadlineContext(d.title);
            const takes = liveTakesLabel(d.post_count, {
              firstVoice: t("live.firstVoice"),
            });
            return (
              <li key={d.id}>
                <Link to={`/spaces/${d.id}`} className="plaza-onair-card">
                  <span className="live-pill">{t("live.liveNow")}</span>
                  <strong>{head}</strong>
                  {context ? <span className="hint plaza-onair-context">{context}</span> : null}
                  <span className="hint">
                    {d.topic_name ||
                      d.arena_name ||
                      (d.host?.username ? `@${d.host.username}` : "Debate")}
                    {takes ? ` · ${takes}` : ""}
                  </span>
                </Link>
              </li>
            );
          })}
        </ul>
      )}
    </section>
  );
}
