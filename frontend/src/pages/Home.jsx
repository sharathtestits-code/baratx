import { useEffect, useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { arenasApi, notificationsApi, postsApi, spacesApi, topicsApi } from "../api";
import { useAuth } from "../context/AuthContext";
import { useT } from "../context/LocaleContext";
import { arenaMeta } from "../arenas";
import Avatar from "../components/Avatar";
import FoundingChip from "../components/FoundingChip";
import LiveNowStrip from "../components/LiveNowStrip";
import PlazaPageHeader from "../components/PlazaPageHeader";
import PostCard from "../components/PostCard";
import SoftLaunchBanner from "../components/SoftLaunchBanner";
import EmptyState from "../components/EmptyState";

const HOME_TABS = ["overview", "tagged", "following", "mine"];
const OVERVIEW_PREVIEW = 3;

/**
 * Personal hub. Welcome, Continue, then segmented:
 * Overview · Tagged · Following · My posts.
 * Public takes / compose live on Square (`/feed`).
 */
export default function Home() {
  const { token, user, loading } = useAuth();
  const t = useT();
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();

  const rawTab = (searchParams.get("tab") || "overview").toLowerCase();
  const tab = HOME_TABS.includes(rawTab) ? rawTab : "overview";

  const [arenas, setArenas] = useState([]);
  const [topics, setTopics] = useState([]);
  const [mentions, setMentions] = useState([]);
  const [following, setFollowing] = useState([]);
  const [mine, setMine] = useState([]);
  const [liveDebates, setLiveDebates] = useState([]);
  const [busy, setBusy] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!loading && !token) navigate("/login");
  }, [loading, token, navigate]);

  useEffect(() => {
    if (!token) return undefined;
    let cancelled = false;
    async function load() {
      setBusy(true);
      setError("");
      try {
        const [arenaRows, topicRows, mentionRows, followRows, mineRows, liveRows] =
          await Promise.all([
            arenasApi.list(token).catch(() => []),
            topicsApi.mine(token).catch(() => []),
            postsApi.list(token, { feed: "mentions" }).catch(() => []),
            postsApi.list(token, { feed: "following" }).catch(() => []),
            postsApi.list(token, { feed: "mine" }).catch(() => []),
            spacesApi
              .listForYou(token)
              .then(async (rows) => {
                if (rows && rows.length > 0) return rows;
                return spacesApi.listDebates(token);
              })
              .catch(() => []),
          ]);
        if (cancelled) return;
        setArenas(Array.isArray(arenaRows) ? arenaRows : []);
        setTopics(Array.isArray(topicRows) ? topicRows : []);
        setMentions(Array.isArray(mentionRows) ? mentionRows.slice(0, 40) : []);
        setFollowing(Array.isArray(followRows) ? followRows.slice(0, 40) : []);
        setMine(Array.isArray(mineRows) ? mineRows.slice(0, 40) : []);
        setLiveDebates(Array.isArray(liveRows) ? liveRows : []);
        notificationsApi.unreadCount(token).catch(() => {});
      } catch (err) {
        if (!cancelled) setError(err.message || t("home.loadError"));
      } finally {
        if (!cancelled) setBusy(false);
      }
    }
    load();
    return () => {
      cancelled = true;
    };
  }, [token, t]);

  function setTab(next) {
    const nextTab = HOME_TABS.includes(next) ? next : "overview";
    if (nextTab === "overview") {
      setSearchParams({}, { replace: true });
    } else {
      setSearchParams({ tab: nextTab }, { replace: true });
    }
  }

  if (loading || (token && !user)) {
    return <div className="page-loading">{t("home.loading")}</div>;
  }
  if (!user) return null;

  const joinedArenas = arenas.filter((a) => a.is_member);
  const arenaPills = (joinedArenas.length > 0 ? joinedArenas : arenas).slice(0, 8);

  const continueCards = [];
  for (const a of joinedArenas.slice(0, 4)) {
    const meta = arenaMeta(a.key);
    continueCards.push({
      key: `arena-${a.key}`,
      title: t(`arena.${a.key}`),
      sub: meta?.blurb ? t(`arena.${a.key}.blurb`) : t("home.continueArena"),
      to: `/arenas/${a.key}`,
      accent: meta?.accent || "#ff9933",
      kind: "arena",
    });
  }
  for (const topic of topics.slice(0, 4)) {
    if (continueCards.length >= 6) break;
    const arenaKey = topic.arena_key || topic.arena?.key;
    const topicName = topic.name || topic.title || topic.slug;
    if (!topicName) continue;
    continueCards.push({
      key: `topic-${topic.id || topicName}`,
      title: topicName,
      sub: arenaKey ? t(`arena.${arenaKey}`) : t("home.continueTopic"),
      to: arenaKey ? `/arenas/${arenaKey}` : "/arenas",
      accent: arenaMeta(arenaKey)?.accent || "#ff9933",
      kind: "topic",
    });
  }
  if (continueCards.length === 0) {
    continueCards.push(
      {
        key: "square",
        title: t("nav.square"),
        sub: t("home.continueSquareHint"),
        to: "/feed",
        accent: "#ff9933",
        kind: "square",
      },
      {
        key: "arenas",
        title: t("nav.arenas"),
        sub: t("home.continueArenasHint"),
        to: "/arenas",
        accent: "#0d9488",
        kind: "arena",
      },
      {
        key: "live",
        title: t("nav.live"),
        sub: t("home.continueLiveHint"),
        to: "/spaces",
        accent: "#c2410c",
        kind: "live",
      }
    );
  }

  const firstName =
    (user.display_name || user.username || "").trim().split(/\s+/)[0] || user.username;

  const mentionPreview = mentions.slice(0, OVERVIEW_PREVIEW);
  const followingPreview = following.slice(0, OVERVIEW_PREVIEW);
  const minePreview = mine.slice(0, OVERVIEW_PREVIEW);

  function renderFeedList(items, emptyNode, onDeleted) {
    if (busy) return <p className="hint">{t("home.loading")}</p>;
    if (items.length === 0) return emptyNode;
    return (
      <div className="feed home-hub-feed">
        {items.map((item) => (
          <PostCard
            key={`home-${item.reposted_by?.username || "p"}-${item.post.id}`}
            post={item.post}
            repostedBy={item.reposted_by}
            onDeleted={(id) => onDeleted(id)}
          />
        ))}
      </div>
    );
  }

  const mentionsEmpty = <p className="hint">{t("home.mentionsEmpty")}</p>;
  const followingEmpty = (
    <EmptyState
      title={t("square.emptyFollowing")}
      hint={t("square.emptyFollowingHint")}
      primaryTo="/search"
      primaryLabel={t("square.explorePeople")}
    />
  );
  const mineEmpty = (
    <EmptyState
      title={t("home.mineEmpty")}
      hint={t("home.mineEmptyHint")}
      primaryTo="/feed"
      primaryLabel={t("home.goSquare")}
    />
  );

  return (
    <div className="plaza-page plaza-home">
      <SoftLaunchBanner compact />

      <div className="plaza-layout">
        <div className="plaza-main-top">
          <header className="home-hub-head">
            <div className="home-hub-head-main">
              <PlazaPageHeader title={t("home.title")} sub={t("home.sub")} />
            </div>
            <FoundingChip />
          </header>

          <section className="home-welcome" aria-label={t("home.welcomeAria")}>
            <Avatar
              name={user.display_name}
              username={user.username}
              url={user.avatar_url}
              size={48}
            />
            <div className="home-welcome-copy">
              <h2>{t("home.welcome", { name: firstName })}</h2>
              <p className="hint">{t("home.welcomeHint")}</p>
            </div>
            <Link to="/feed" className="btn btn-primary home-welcome-cta">
              {t("home.goSquare")}
            </Link>
          </section>

          {/* Tabs sit in main-top so mobile browser shows them before Live peek */}
          <div className="home-hub-tabs" role="tablist" aria-label={t("home.tabsAria")}>
            <button
              type="button"
              className={`home-hub-tab${tab === "overview" ? " active" : ""}`}
              role="tab"
              aria-selected={tab === "overview"}
              onClick={() => setTab("overview")}
            >
              {t("home.tabOverview")}
            </button>
            <button
              type="button"
              className={`home-hub-tab${tab === "tagged" ? " active" : ""}`}
              role="tab"
              aria-selected={tab === "tagged"}
              onClick={() => setTab("tagged")}
            >
              {t("home.tabTagged")}
              {mentions.length > 0 ? (
                <span className="home-tab-count">{mentions.length}</span>
              ) : null}
            </button>
            <button
              type="button"
              className={`home-hub-tab${tab === "following" ? " active" : ""}`}
              role="tab"
              aria-selected={tab === "following"}
              onClick={() => setTab("following")}
            >
              {t("home.tabFollowing")}
              {following.length > 0 ? (
                <span className="home-tab-count">{following.length}</span>
              ) : null}
            </button>
            <button
              type="button"
              className={`home-hub-tab${tab === "mine" ? " active" : ""}`}
              role="tab"
              aria-selected={tab === "mine"}
              onClick={() => setTab("mine")}
            >
              {t("home.tabMine")}
              {mine.length > 0 ? <span className="home-tab-count">{mine.length}</span> : null}
            </button>
          </div>
        </div>

        <aside className="plaza-rail-stack home-hub-rail" aria-label={t("home.livePeek")}>
          <LiveNowStrip
            items={liveDebates}
            title={t("home.livePeek")}
            seeAllTo="/spaces"
            seeAllLabel={t("square.enterLive")}
            emptyHint={t("home.liveEmpty")}
            limit={4}
          />
        </aside>

        <div className="plaza-main-feed home-hub-body">
          {error ? <div className="error">{error}</div> : null}

          {tab === "overview" ? (
            <>
              <section className="home-section home-section-card home-continue" aria-labelledby="home-continue-title">
                <div className="home-section-head">
                  <h2 id="home-continue-title">{t("home.continue")}</h2>
                  <Link to="/arenas">{t("home.seeAll")}</Link>
                </div>
                <ul className="home-continue-scroll">
                  {continueCards.map((card) => (
                    <li key={card.key}>
                      <Link
                        to={card.to}
                        className="home-continue-card"
                        style={{ "--home-card-accent": card.accent }}
                      >
                        <strong>{card.title}</strong>
                        <span className="hint">{card.sub}</span>
                        <span className="home-continue-bar" aria-hidden="true" />
                      </Link>
                    </li>
                  ))}
                </ul>
              </section>

              <section className="home-section home-section-card home-mentions" aria-labelledby="home-mentions-title">
                <div className="home-section-head">
                  <h2 id="home-mentions-title">{t("home.mentions")}</h2>
                  <button type="button" className="home-see-all-btn" onClick={() => setTab("tagged")}>
                    {t("home.seeAll")}
                  </button>
                </div>
                {renderFeedList(mentionPreview, mentionsEmpty, (id) =>
                  setMentions((prev) => prev.filter((row) => row.post.id !== id))
                )}
              </section>

              <section
                className="home-section home-section-card home-following"
                aria-labelledby="home-following-title"
              >
                <div className="home-section-head">
                  <h2 id="home-following-title">{t("home.following")}</h2>
                  <button
                    type="button"
                    className="home-see-all-btn"
                    onClick={() => setTab("following")}
                  >
                    {t("home.seeAll")}
                  </button>
                </div>
                {renderFeedList(followingPreview, followingEmpty, (id) =>
                  setFollowing((prev) => prev.filter((row) => row.post.id !== id))
                )}
              </section>

              <section className="home-section home-section-card home-mine" aria-labelledby="home-mine-title">
                <div className="home-section-head">
                  <h2 id="home-mine-title">{t("home.mine")}</h2>
                  <button type="button" className="home-see-all-btn" onClick={() => setTab("mine")}>
                    {t("home.seeAll")}
                  </button>
                </div>
                {renderFeedList(minePreview, mineEmpty, (id) =>
                  setMine((prev) => prev.filter((row) => row.post.id !== id))
                )}
              </section>

              <section className="home-section home-section-card home-arenas" aria-labelledby="home-arenas-title">
                <div className="home-section-head">
                  <h2 id="home-arenas-title">{t("home.yourArenas")}</h2>
                  <Link to="/arenas">{t("home.seeAll")}</Link>
                </div>
                {arenaPills.length === 0 ? (
                  <p className="hint">{t("home.arenasEmpty")}</p>
                ) : (
                  <ul className="home-arena-pills">
                    {arenaPills.map((a) => {
                      const meta = arenaMeta(a.key);
                      return (
                        <li key={a.key}>
                          <Link
                            to={`/arenas/${a.key}`}
                            className="home-arena-pill"
                            style={{ "--arena-accent": meta?.accent || "#ff9933" }}
                          >
                            <span className="home-arena-dot" aria-hidden="true" />
                            {t(`arena.${a.key}`)}
                          </Link>
                        </li>
                      );
                    })}
                  </ul>
                )}
              </section>

              <section className="home-section home-section-card home-live-inline" aria-labelledby="home-live-title">
                <div className="home-section-head">
                  <h2 id="home-live-title">{t("home.livePeek")}</h2>
                  <Link to="/spaces">{t("home.seeAll")}</Link>
                </div>
                {liveDebates[0] ? (
                  <Link to={`/spaces/${liveDebates[0].id}`} className="home-live-card">
                    <span className="live-pill">{t("live.liveNow")}</span>
                    <strong>{liveDebates[0].title}</strong>
                    <span className="hint">
                      {liveDebates[0].host?.username
                        ? `@${liveDebates[0].host.username}`
                        : t("nav.live")}
                      {typeof liveDebates[0].post_count === "number"
                        ? liveDebates[0].post_count > 0
                          ? ` · ${liveDebates[0].post_count}`
                          : ` · ${t("live.firstVoice")}`
                        : ""}
                    </span>
                  </Link>
                ) : (
                  <p className="hint">{t("home.liveEmpty")}</p>
                )}
              </section>
            </>
          ) : null}

          {tab === "tagged"
            ? renderFeedList(mentions, mentionsEmpty, (id) =>
                setMentions((prev) => prev.filter((row) => row.post.id !== id))
              )
            : null}

          {tab === "following"
            ? renderFeedList(following, followingEmpty, (id) =>
                setFollowing((prev) => prev.filter((row) => row.post.id !== id))
              )
            : null}

          {tab === "mine"
            ? renderFeedList(mine, mineEmpty, (id) =>
                setMine((prev) => prev.filter((row) => row.post.id !== id))
              )
            : null}
        </div>
      </div>
    </div>
  );
}
