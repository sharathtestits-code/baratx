import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { arenasApi, postsApi, spacesApi, topicsApi } from "../api";
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

/**
 * Personal hub — Welcome, Continue, Following activity, Your arenas, Live peek.
 * Public takes / compose live on Square (`/feed`).
 */
export default function Home() {
  const { token, user, loading } = useAuth();
  const t = useT();
  const navigate = useNavigate();

  const [arenas, setArenas] = useState([]);
  const [topics, setTopics] = useState([]);
  const [following, setFollowing] = useState([]);
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
        const [arenaRows, topicRows, followRows, liveRows] = await Promise.all([
          arenasApi.list(token).catch(() => []),
          topicsApi.mine(token).catch(() => []),
          postsApi.list(token, { feed: "following" }).catch(() => []),
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
        setFollowing(Array.isArray(followRows) ? followRows.slice(0, 8) : []);
        setLiveDebates(Array.isArray(liveRows) ? liveRows : []);
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
        </div>

        <aside className="plaza-rail-stack" aria-label={t("home.livePeek")}>
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

          <section className="home-section home-continue" aria-labelledby="home-continue-title">
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

          <section className="home-section home-following" aria-labelledby="home-following-title">
            <div className="home-section-head">
              <h2 id="home-following-title">{t("home.following")}</h2>
              <Link to="/feed">{t("home.seeAll")}</Link>
            </div>
            {busy ? (
              <p className="hint">{t("home.loading")}</p>
            ) : following.length === 0 ? (
              <EmptyState
                title={t("square.emptyFollowing")}
                hint={t("square.emptyFollowingHint")}
                primaryTo="/search"
                primaryLabel={t("square.explorePeople")}
              />
            ) : (
              <div className="feed home-following-feed">
                {following.map((item) => (
                  <PostCard
                    key={`home-${item.reposted_by?.username || "p"}-${item.post.id}`}
                    post={item.post}
                    repostedBy={item.reposted_by}
                    onDeleted={(id) =>
                      setFollowing((prev) => prev.filter((row) => row.post.id !== id))
                    }
                  />
                ))}
              </div>
            )}
          </section>

          <section className="home-section home-arenas" aria-labelledby="home-arenas-title">
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
        </div>
      </div>
    </div>
  );
}
