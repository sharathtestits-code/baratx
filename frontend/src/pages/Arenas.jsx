import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { arenasApi, communitiesApi, spacesApi } from "../api";
import { useAuth } from "../context/AuthContext";
import { ARENA_TOPICS, CIRCLE_TOPICS, arenaMeta } from "../arenas";
import PlazaPageHeader from "../components/PlazaPageHeader";
import LiveNowStrip from "../components/LiveNowStrip";
import { useT } from "../context/LocaleContext";

function TopicGrid({ topics, byKey, busyKey, toggleJoin, t }) {
  return (
    <div className="arena-grid">
      {topics.map((meta) => {
        const arena = byKey[meta.key];
        return (
          <div key={meta.key} className="arena-card" style={{ "--arena-accent": meta.accent }}>
            <Link to={`/arenas/${meta.key}`} className="arena-card-main">
              <div className="arena-card-name">{t(`arena.${meta.key}`)}</div>
              <p className="arena-card-blurb">{t(`arena.${meta.key}.blurb`)}</p>
              <div className="arena-card-meta">
                {arena
                  ? t(
                      arena.open_debate_count === 1 ? "arenas.meta" : "arenas.metaPlural",
                      {
                        members: arena.member_count,
                        debates: arena.open_debate_count,
                      }
                    )
                  : t("arenas.openingSoon")}
              </div>
            </Link>
            {arena && (
              <button
                type="button"
                className={`arena-join-btn${arena.is_member ? " is-joined" : ""}`}
                disabled={busyKey === meta.key}
                onClick={() => toggleJoin(arena)}
              >
                {busyKey === meta.key ? "…" : arena.is_member ? t("arenas.joined") : t("arenas.join")}
              </button>
            )}
          </div>
        );
      })}
    </div>
  );
}

export default function Arenas() {
  const { token } = useAuth();
  const t = useT();
  const [arenas, setArenas] = useState([]);
  const [debates, setDebates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [busyKey, setBusyKey] = useState("");

  async function load() {
    setLoading(true);
    setError("");
    try {
      const [a, d] = await Promise.all([
        arenasApi.list(token),
        spacesApi.listDebates(token),
      ]);
      setArenas(a);
      setDebates(d);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token]);

  async function toggleJoin(arena) {
    if (!token || busyKey) return;
    setBusyKey(arena.key);
    try {
      if (arena.is_member) {
        await communitiesApi.leave(token, arena.slug);
        setArenas((prev) =>
          prev.map((x) =>
            x.key === arena.key
              ? { ...x, is_member: false, member_count: Math.max(0, x.member_count - 1) }
              : x
          )
        );
      } else {
        const updated = await arenasApi.join(token, arena.key);
        setArenas((prev) => prev.map((x) => (x.key === updated.key ? updated : x)));
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setBusyKey("");
    }
  }

  const byKey = Object.fromEntries(arenas.map((a) => [a.key, a]));

  return (
    <div className="feed-wrap surface-page arenas-page plaza-page">
      <div className="plaza-layout">
        <div className="plaza-main-top">
          <PlazaPageHeader
            title={t("arenas.title")}
            sub={t("arenas.sub")}
          />

          <div className="arena-featured">
            <p className="arena-featured-kicker">{t("arenas.featuredKicker")}</p>
            <h2>{t("arenas.featuredTitle")}</h2>
            <p className="hint">{t("arenas.featuredHint")}</p>
            <div className="arena-featured-actions">
              <Link to="/arenas/startups" className="btn btn-primary">
                {t("arenas.enterStartups")}
              </Link>
              <Link to="/rewards" className="btn btn-secondary">
                {t("arenas.founding100")}
              </Link>
            </div>
          </div>
        </div>

        <aside className="plaza-rail-stack" aria-label={t("arenas.liveDebates")}>
          <section className="suggestions-strip plaza-rail-questions" aria-label={t("arenas.jumpTitle")}>
            <div className="suggestions-head">
              <div>
                <h2 className="suggestions-title">{t("arenas.jumpTitle")}</h2>
                <p className="suggestions-sub">{t("arenas.jumpSub")}</p>
              </div>
            </div>
            <ul className="suggestions-list">
              {[...ARENA_TOPICS, ...CIRCLE_TOPICS].slice(0, 9).map((meta) => (
                <li key={meta.key}>
                  <Link to={`/arenas/${meta.key}`} className="suggestions-chip suggestions-chip-link">
                    {t(`arena.${meta.key}`)}
                  </Link>
                </li>
              ))}
            </ul>
          </section>
          <LiveNowStrip
            items={debates}
            title={t("arenas.liveDebates")}
            seeAllTo="/spaces"
            seeAllLabel={t("arenas.enterLive")}
            limit={8}
            emptyHint={loading ? t("settings.loading") : t("arenas.noLiveHint")}
          />
        </aside>

        <div className="plaza-main-compose">
          {error && <div className="error">{error}</div>}
          {loading ? (
            <p className="hint">{t("arenas.loading")}</p>
          ) : (
            <>
              <h2 className="section-title arenas-section-title">{t("arenas.circlesTitle")}</h2>
              <p className="hint arenas-section-hint">{t("arenas.circlesSub")}</p>
              <TopicGrid
                topics={CIRCLE_TOPICS}
                byKey={byKey}
                busyKey={busyKey}
                toggleJoin={toggleJoin}
                t={t}
              />
              <h2 className="section-title arenas-section-title">{t("arenas.nationalTitle")}</h2>
              <p className="hint arenas-section-hint">{t("arenas.nationalSub")}</p>
              <TopicGrid
                topics={ARENA_TOPICS}
                byKey={byKey}
                busyKey={busyKey}
                toggleJoin={toggleJoin}
                t={t}
              />
            </>
          )}
        </div>

        <section className="plaza-main-feed">
          <h2 className="section-title">{t("arenas.liveDebates")}</h2>
          {loading ? null : debates.length === 0 ? (
            <div className="empty-state">
              <p className="empty-state-title">{t("arenas.emptyTitle")}</p>
              <p className="hint">{t("arenas.emptyHint")}</p>
            </div>
          ) : (
            <ul className="debate-list">
              {debates.map((d) => {
                const meta = arenaMeta(d.arena_key);
                return (
                  <li key={d.id}>
                    <Link to={`/spaces/${d.id}`} className="debate-row">
                      <span className="debate-arena-tag">
                        {d.arena_key
                          ? t(`arena.${d.arena_key}`)
                          : d.arena_name || meta?.name || t("nav.arenas")}
                      </span>
                      <span className="debate-title">{d.title}</span>
                      <span className="debate-sides hint">
                        {d.for_count} {d.side_for_label} · {d.against_count} {d.side_against_label}
                      </span>
                    </Link>
                  </li>
                );
              })}
            </ul>
          )}
        </section>
      </div>
    </div>
  );
}
