import { useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { spacesApi } from "../api";
import { useAuth } from "../context/AuthContext";
import PlazaPageHeader from "../components/PlazaPageHeader";
import LiveNowStrip from "../components/LiveNowStrip";
import { focusCompose } from "../focusCompose";
import { useT } from "../context/LocaleContext";

const SUGGESTED_DEBATES = [
  "Should WFH stay the default in India tech?",
  "Kohli or Rohit — who carries big games?",
  "One civic problem your city still ignores",
  "Is hustle culture burning junior talent?",
];

export default function Spaces() {
  const { token } = useAuth();
  const t = useT();
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [title, setTitle] = useState("");
  const [creating, setCreating] = useState(false);
  const titleRef = useRef(null);

  async function load() {
    setLoading(true);
    setError("");
    try {
      const data = await spacesApi.list(token, "open");
      setItems(data);
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

  async function createSpace(e) {
    e.preventDefault();
    if (!title.trim()) return;
    setCreating(true);
    setError("");
    try {
      const created = await spacesApi.create(token, { title: title.trim(), duration_hours: 24 });
      setItems((prev) => [created, ...prev]);
      setTitle("");
    } catch (err) {
      setError(err.message);
    } finally {
      setCreating(false);
    }
  }

  function startSuggested(topic) {
    setTitle(topic);
    focusCompose(titleRef);
  }

  const featured = items[0];
  const empty = !loading && items.length === 0;

  return (
    <div className="plaza-page plaza-live">
      <div className="plaza-layout">
        <div className="plaza-main-top">
          <PlazaPageHeader
            title={t("live.title")}
            sub={t("live.sub")}
          />
          <section className={`live-amphitheatre${empty ? " is-empty-hero" : ""}`}>
            <div className="live-amphitheatre-glow" aria-hidden="true" />
            <span className="live-pill">{empty ? t("live.startOne") : t("live.liveNow")}</span>
            <h2 className="live-amphitheatre-title">
              {featured
                ? featured.title
                : empty
                  ? t("live.noRooms")
                  : t("live.startRoom")}
            </h2>
            <p className="live-amphitheatre-sub">
              {featured
                ? t("live.hostTakes", {
                    user: featured.host?.username,
                    count: featured.post_count,
                  })
                : t("live.openTalk")}
            </p>
            {empty && (
              <button
                type="button"
                className="live-suggested-pill"
                onClick={() => startSuggested(SUGGESTED_DEBATES[0])}
              >
                {SUGGESTED_DEBATES[0]}
              </button>
            )}
            <div className="live-stage-wave" aria-hidden="true">
              <span />
              <span />
              <span />
              <span />
              <span />
              <span />
              <span />
            </div>
            <div className="live-amphitheatre-actions">
              {featured ? (
                <Link to={`/spaces/${featured.id}`} className="btn btn-primary">
                  {t("live.jumpIn")}
                </Link>
              ) : (
                <button
                  type="button"
                  className="btn btn-primary"
                  onClick={() => startSuggested(title.trim() || SUGGESTED_DEBATES[0])}
                >
                  {t("live.startLive")}
                </button>
              )}
              {featured ? (
                <a href="#go-live" className="btn btn-secondary">
                  {t("live.hostOwn")}
                </a>
              ) : (
                <Link to="/arenas" className="btn btn-secondary">
                  {t("live.browseArenas")}
                </Link>
              )}
            </div>
          </section>
        </div>

        <aside className="plaza-rail-stack" aria-label={t("live.topStarters")}>
          <section className="suggestions-strip plaza-rail-questions" aria-label={t("live.topStarters")}>
            <div className="suggestions-head">
              <div>
                <h2 className="suggestions-title">{t("live.topStarters")}</h2>
                <p className="suggestions-sub">{t("live.topStartersSub")}</p>
              </div>
            </div>
            <ul className="suggestions-list">
              {SUGGESTED_DEBATES.map((topic) => (
                <li key={topic}>
                  <button type="button" className="suggestions-chip" onClick={() => startSuggested(topic)}>
                    {topic}
                  </button>
                </li>
              ))}
            </ul>
          </section>
          <LiveNowStrip
            items={items}
            title={t("live.roomsLive")}
            seeAllLabel={t("live.seeAll")}
            limit={6}
            emptyHint={loading ? t("live.loading") : t("live.emptyRooms")}
          />
        </aside>

        <form id="go-live" className="plaza-studio live-create plaza-main-compose" onSubmit={createSpace}>
          <p className="plaza-studio-label">{t("live.composeLabel")}</p>
          <input
            ref={titleRef}
            type="text"
            placeholder={t("live.composePlaceholder")}
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            maxLength={100}
            required
          />
          <button type="submit" className="btn btn-primary" disabled={creating || !title.trim()}>
            {creating ? t("live.opening") : t("live.goLive")}
          </button>
        </form>

        {error && <div className="error plaza-main-feed">{error}</div>}

        <section className="plaza-takes plaza-main-feed">
          <div className="plaza-takes-head">
            <h2>{t("live.roomsLive")}</h2>
          </div>
          {loading ? (
            <p className="hint">{t("live.loading")}</p>
          ) : items.length === 0 ? (
            <div className="live-empty-suggest">
              <p className="live-empty-suggest-title">{t("live.suggestedTitle")}</p>
              <p className="hint">{t("live.suggestedHint")}</p>
              <div className="live-empty-chips">
                {SUGGESTED_DEBATES.map((topic) => (
                  <button
                    key={topic}
                    type="button"
                    className="live-empty-chip"
                    onClick={() => startSuggested(topic)}
                  >
                    {topic}
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <ul className="plaza-onair-list live-room-grid">
              {items.map((s) => (
                <li key={s.id}>
                  <Link to={`/spaces/${s.id}`} className="plaza-onair-card">
                    <span className="live-room-dot" aria-hidden="true" />
                    <strong>{s.title}</strong>
                    <span className="hint">
                      @{s.host?.username}
                      {s.is_host ? " · you" : ""} · {s.post_count} posts
                    </span>
                  </Link>
                </li>
              ))}
            </ul>
          )}
        </section>
      </div>
    </div>
  );
}
