import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { arenasApi, communitiesApi, spacesApi, topicsApi } from "../api";
import { useAuth } from "../context/AuthContext";
import { arenaMeta } from "../arenas";
import PostCard from "../components/PostCard";
import MentionTextarea from "../components/MentionTextarea";
import SuggestionsStrip from "../components/SuggestionsStrip";

export default function ArenaDetail() {
  const { arenaKey } = useParams();
  const navigate = useNavigate();
  const { token } = useAuth();
  const meta = arenaMeta(arenaKey);
  const [arena, setArena] = useState(null);
  const [debates, setDebates] = useState([]);
  const [posts, setPosts] = useState([]);
  const [topics, setTopics] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [msg, setMsg] = useState("");
  const [text, setText] = useState("");
  const [posting, setPosting] = useState(false);
  const [debateTitle, setDebateTitle] = useState("");
  const [selectedTopicId, setSelectedTopicId] = useState("");
  const [creatingDebate, setCreatingDebate] = useState(false);
  const [busyJoin, setBusyJoin] = useState(false);
  const [topicBusy, setTopicBusy] = useState("");

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
    setError("");
    try {
      if (arena?.is_member) {
        // Leave is handled on Arenas list; keep detail as join-only if no leave API.
        setMsg("You’re in this arena. Pick a topic or open a debate below.");
        return;
      }
      const updated = await arenasApi.join(token, arenaKey);
      setArena(updated);
      setMsg(`Joined ${updated.name}`);
    } catch (err) {
      setError(err.message);
    } finally {
      setBusyJoin(false);
    }
  }

  function pickTopicForDebate(topic) {
    setSelectedTopicId(topic.id);
    setDebateTitle((prev) => {
      const trimmed = prev.trim();
      if (!trimmed || trimmed.endsWith(":")) return `${topic.name}: `;
      if (trimmed.startsWith(`${topic.name}:`)) return trimmed;
      return `${topic.name}: ${trimmed}`;
    });
    document.getElementById("arena-debate-title")?.focus();
  }

  /** Tap a lane: follow it (personalize) and wire it into the debate composer. */
  async function selectTopic(topic) {
    if (!token) {
      setError("Sign in to personalize topics and open debates");
      return;
    }
    if (topicBusy) return;
    setTopicBusy(topic.id);
    setError("");
    setMsg("");
    pickTopicForDebate(topic);
    try {
      if (!topic.is_following) {
        const mine = await topicsApi.mine(token);
        const mineIds = new Set((mine || []).map((t) => t.id));
        mineIds.add(topic.id);
        await topicsApi.setInterests(token, [...mineIds], true);
        setTopics((prev) =>
          prev.map((t) => (t.id === topic.id ? { ...t, is_following: true } : t))
        );
      }
      if (!arena?.is_member) {
        const updated = await arenasApi.join(token, arenaKey);
        setArena(updated);
      }
      setMsg(
        `${topic.name} saved — write your question below and tap Open For vs Against.`
      );
    } catch (err) {
      setError(err.message || "Could not save topic");
    } finally {
      setTopicBusy("");
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
    if (!token) {
      setError("Sign in to open a debate");
      return;
    }
    if (!debateTitle.trim() || !arena) return;
    setCreatingDebate(true);
    setError("");
    setMsg("");
    try {
      if (!arena.is_member) {
        const updated = await arenasApi.join(token, arenaKey);
        setArena(updated);
      }
      const created = await spacesApi.create(token, {
        title: debateTitle.trim(),
        kind: "debate",
        arena_key: arenaKey,
        topic_id: selectedTopicId || undefined,
        duration_hours: 168,
        side_for_label: meta?.debateFor,
        side_against_label: meta?.debateAgainst,
      });
      setDebates((prev) => [created, ...prev]);
      setDebateTitle("");
      setMsg("Debate opened — taking you in…");
      navigate(`/spaces/${created.id}`);
    } catch (err) {
      setError(err.message || "Could not open debate");
    } finally {
      setCreatingDebate(false);
    }
  }

  if (loading) {
    return (
      <div className="feed-wrap plaza-page">
        <p className="hint">Loading…</p>
      </div>
    );
  }

  if (!arena) {
    return (
      <div className="feed-wrap plaza-page">
        <div className="error">{error || "Arena not found"}</div>
        <Link to="/arenas">Back to Arenas</Link>
      </div>
    );
  }

  const followingCount = topics.filter((t) => t.is_following).length;

  return (
    <div className="feed-wrap surface-page arena-detail plaza-page">
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
      {msg && <p className="hint ok-hint">{msg}</p>}

      <SuggestionsStrip
        token={token}
        surface="arena"
        arenaKey={arenaKey}
        title={`Top problems · ${arena.name}`}
        onPick={(prompt) => {
          setText(prompt.slice(0, 500));
          setDebateTitle(prompt.slice(0, 120));
        }}
      />

      <section className="arena-section" id="arena-trending-topics">
        <h2 className="section-title">Trending topics</h2>
        <p className="hint surface-lead">
          {topics.length
            ? `${topics.length} India-trending lanes in ${arena.name}. Tap a topic to follow it and use it in a debate below.`
            : "Topics loading…"}
          {followingCount ? ` · ${followingCount} saved here.` : ""}
        </p>
        {topics.length > 0 ? (
          <div className="topic-chip-grid arena-topic-grid" role="list">
            {topics.map((t) => {
              const on = !!t.is_following;
              const active = selectedTopicId === t.id;
              return (
                <button
                  key={t.id}
                  type="button"
                  role="listitem"
                  className={`topic-chip${on ? " selected" : ""}${active ? " is-active-topic" : ""}`}
                  title={t.blurb || `Follow ${t.name} and use in debate`}
                  aria-pressed={on}
                  disabled={!!topicBusy}
                  onClick={() => selectTopic(t)}
                >
                  {t.name}
                  {t.open_debate_count > 0 ? (
                    <em className="topic-chip-count"> {t.open_debate_count}</em>
                  ) : null}
                </button>
              );
            })}
          </div>
        ) : (
          <p className="hint">No topics yet — try again in a moment.</p>
        )}
        <div className="arena-topic-actions">
          <button
            type="button"
            className="btn btn-secondary"
            disabled={!selectedTopicId}
            onClick={() => {
              const t = topics.find((x) => x.id === selectedTopicId);
              if (t) {
                pickTopicForDebate(t);
                setMsg(
                  `Topic set to ${t.name}. Write your debate question and open it.`
                );
                document.getElementById("arena-live-debates")?.scrollIntoView({
                  behavior: "smooth",
                  block: "start",
                });
              }
            }}
          >
            Use selected topic in debate
          </button>
          {token ? (
            <p className="hint arena-personalize-copy">
              <Link
                className="arena-personalize-link"
                to={`/onboarding/topics?arena=${encodeURIComponent(arenaKey)}&from=arena`}
              >
                Personalize your topics
              </Link>{" "}
              for home debates.
            </p>
          ) : (
            <p className="hint">
              <Link to="/login">Sign in</Link> to personalize topics.
            </p>
          )}
        </div>
      </section>

      <section className="arena-section" id="arena-live-debates">
        <h2 className="section-title">Live debates</h2>
        <p className="hint surface-lead">
          100 Founding spots, earned by opening a debate that gets real engagement, not by signing
          up.
        </p>
        <form className="surface-create arena-debate-form" onSubmit={startDebate}>
          <input
            id="arena-debate-title"
            type="text"
            placeholder={meta?.composeHint || `Start a ${arena.name} debate…`}
            value={debateTitle}
            onChange={(e) => setDebateTitle(e.target.value)}
            maxLength={140}
            required
            minLength={2}
            autoComplete="off"
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
            maxLength={500}
            rows={3}
          />
          <button
            type="submit"
            className="post-btn"
            disabled={posting || !text.trim() || text.trim().length > 500}
          >
            {posting ? "Posting…" : "Post"}
          </button>
        </form>
        {posts.length === 0 ? (
          <p className="hint">No posts in this arena yet.</p>
        ) : (
          <div className="post-list">
            {posts.map((post) => (
              <PostCard
                key={post.id}
                post={post}
                onDeleted={(id) => setPosts((p) => p.filter((x) => x.id !== id))}
              />
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
