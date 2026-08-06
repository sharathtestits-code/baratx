import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { arenasApi, communitiesApi, spacesApi, topicsApi } from "../api";
import { useAuth } from "../context/AuthContext";
import { arenaMeta } from "../arenas";
import PostCard from "../components/PostCard";
import MentionTextarea from "../components/MentionTextarea";

export default function ArenaDetail() {
  const { arenaKey } = useParams();
  const { token, user } = useAuth();
  const meta = arenaMeta(arenaKey);
  const [arena, setArena] = useState(null);
  const [debates, setDebates] = useState([]);
  const [posts, setPosts] = useState([]);
  const [topics, setTopics] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [text, setText] = useState("");
  const [posting, setPosting] = useState(false);
  const [debateTitle, setDebateTitle] = useState("");
  const [creatingDebate, setCreatingDebate] = useState(false);
  const [busyJoin, setBusyJoin] = useState(false);

  async function load() {
    setLoading(true);
    setError("");
    try {
      const [a, d, t] = await Promise.all([
        arenasApi.get(token, arenaKey),
        spacesApi.listDebates(token, arenaKey),
        topicsApi.list(token, arenaKey).catch(() => []),
      ]);
      setArena(a);
      setDebates(d);
      setTopics(Array.isArray(t) ? t : []);
      if (a?.slug) {
        const feed = await communitiesApi.feed(token, a.slug);
        setPosts(feed);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token, arenaKey]);

  async function join() {
    if (!token || busyJoin) return;
    setBusyJoin(true);
    try {
      const updated = await arenasApi.join(token, arenaKey);
      setArena(updated);
    } catch (err) {
      setError(err.message);
    } finally {
      setBusyJoin(false);
    }
  }

  async function submitPost(e) {
    e.preventDefault();
    if (!text.trim() || !arena) return;
    if (!arena.is_member) {
      setError("Join this arena to post");
      return;
    }
    setPosting(true);
    setError("");
    try {
      const post = await communitiesApi.post(token, arena.slug, text.trim());
      setPosts((prev) => [post, ...prev]);
      setText("");
    } catch (err) {
      setError(err.message);
    } finally {
      setPosting(false);
    }
  }

  async function startDebate(e) {
    e.preventDefault();
    if (!debateTitle.trim() || !arena) return;
    setCreatingDebate(true);
    setError("");
    try {
      if (!arena.is_member) await arenasApi.join(token, arenaKey);
      const created = await spacesApi.create(token, {
        title: debateTitle.trim(),
        kind: "debate",
        arena_key: arenaKey,
        duration_hours: 168,
      });
      setDebates((prev) => [created, ...prev]);
      setDebateTitle("");
    } catch (err) {
      setError(err.message);
    } finally {
      setCreatingDebate(false);
    }
  }

  if (loading) {
    return (
      <div className="feed-wrap">
        <p className="hint">Loading…</p>
      </div>
    );
  }

  if (!arena) {
    return (
      <div className="feed-wrap">
        <div className="error">{error || "Arena not found"}</div>
        <Link to="/arenas">Back to Arenas</Link>
      </div>
    );
  }

  return (
    <div className="feed-wrap surface-page arena-detail">
      <div className="feed-header surface-header-row">
        <div>
          <Link to="/arenas" className="back-link">
            ← Arenas
          </Link>
          <h1 style={{ color: meta?.accent }}>{arena.name}</h1>
          <p className="hint">{arena.description}</p>
          <p className="hint">
            {arena.member_count} joined · {arena.open_debate_count} live debate
            {arena.open_debate_count === 1 ? "" : "s"}
          </p>
        </div>
        <button
          type="button"
          className={`arena-join-btn${arena.is_member ? " is-joined" : ""}`}
          disabled={busyJoin}
          onClick={join}
        >
          {busyJoin ? "…" : arena.is_member ? "Joined" : "Join arena"}
        </button>
      </div>

      {error && <div className="error">{error}</div>}

      <section className="arena-section">
        <h2 className="section-title">Trending topics</h2>
        <p className="hint surface-lead">
          {topics.length
            ? `${topics.length} India-trending lanes in ${arena.name}. Pick debates that match.`
            : "Topics loading…"}
        </p>
        {topics.length > 0 && (
          <div className="topic-chip-grid arena-topic-grid">
            {topics.map((t) => (
              <span key={t.id} className="topic-chip" title={t.blurb || t.name}>
                {t.name}
                {t.open_debate_count > 0 ? (
                  <em className="topic-chip-count"> {t.open_debate_count}</em>
                ) : null}
              </span>
            ))}
          </div>
        )}
        {token && (
          <p className="hint">
            <Link to="/onboarding/topics">Personalize your topics</Link> for home debates.
          </p>
        )}
      </section>

      <section className="arena-section">
        <h2 className="section-title">Live debates</h2>
        {arenaKey === "spirituality" && (
          <p className="hint surface-lead">
            Faith, wellness, and modern practice — debate what resonates in India right now.
          </p>
        )}
        {(arenaKey === "politics" || arenaKey === "news") && (
          <p className="hint surface-lead">
            Open one real debate from your city or beat. First 100 people who do (or post one real
            problem on Home) get ₹150 via UPI.
          </p>
        )}
        <form className="surface-create" onSubmit={startDebate}>
          <input
            type="text"
            placeholder={meta?.composeHint || `Start a ${arena.name} debate…`}
            value={debateTitle}
            onChange={(e) => setDebateTitle(e.target.value)}
            maxLength={140}
          />
          <button
            type="submit"
            className="btn btn-primary"
            disabled={creatingDebate || !debateTitle.trim()}
          >
            {creatingDebate
              ? "Opening…"
              : meta?.openDebateLabel || "Open For vs Against"}
          </button>
        </form>
        {debates.length === 0 ? (
          <p className="hint">No live debates — be the first to open one.</p>
        ) : (
          <ul className="debate-list">
            {debates.map((d) => (
              <li key={d.id}>
                <Link to={`/spaces/${d.id}`} className="debate-row">
                  <span className="debate-title">{d.title}</span>
                  <span className="debate-sides hint">
                    {d.for_count} {d.side_for_label} · {d.against_count} {d.side_against_label}
                  </span>
                </Link>
              </li>
            ))}
          </ul>
        )}
      </section>

      <section className="arena-section">
        <h2 className="section-title">Arena talk</h2>
        <form className="compose surface-compose" onSubmit={submitPost}>
          <MentionTextarea
            value={text}
            onChange={setText}
            placeholder={`What’s your take on ${arena.name}? Type @ to tag`}
            maxLength={280}
            rows={3}
          />
          <button type="submit" className="post-btn" disabled={posting || !text.trim()}>
            {posting ? "Posting…" : "Post"}
          </button>
        </form>
        {posts.length === 0 ? (
          <p className="hint">No posts in this arena yet.</p>
        ) : (
          <div className="post-list">
            {posts.map((post) => (
              <PostCard key={post.id} post={post} onDeleted={(id) => setPosts((p) => p.filter((x) => x.id !== id))} />
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
