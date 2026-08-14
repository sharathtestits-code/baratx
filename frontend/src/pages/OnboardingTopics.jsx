import { useEffect, useMemo, useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { topicsApi } from "../api";
import { useAuth } from "../context/AuthContext";
import { markTopicOnboardingSeen } from "../topicsOnboarding";

const ARENA_ORDER = [
  "sports",
  "politics",
  "entertainment",
  "news",
  "spirituality",
  "startups",
];
const ARENA_LABEL = {
  sports: "Sports",
  politics: "Politics",
  entertainment: "Entertainment",
  news: "News",
  spirituality: "Spirituality",
  startups: "Startups",
};
const MIN_PICKS = 1;
const MAX_PICKS = 20;

/**
 * Interest picker — post-signup onboarding and arena “Personalize your topics”.
 */
export default function OnboardingTopics() {
  const { token } = useAuth();
  const navigate = useNavigate();
  const [params] = useSearchParams();
  const returnArena = (params.get("arena") || "").trim().toLowerCase();
  const fromArena = params.get("from") === "arena" && ARENA_ORDER.includes(returnArena);
  const [topics, setTopics] = useState([]);
  const [selected, setSelected] = useState(() => new Set());
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    // First-time onboarding only — arena personalize should not burn the welcome flag.
    if (!fromArena) markTopicOnboardingSeen();
  }, [fromArena]);

  useEffect(() => {
    if (!token) {
      navigate("/login");
      return;
    }
    let cancelled = false;
    (async () => {
      setLoading(true);
      setError("");
      try {
        const [rows, mine] = await Promise.all([
          topicsApi.list(token),
          topicsApi.mine(token).catch(() => []),
        ]);
        if (cancelled) return;
        setTopics(rows || []);
        const ids = (Array.isArray(mine) ? mine : [])
          .map((t) => String(t.id))
          .filter(Boolean);
        setSelected(new Set(ids));
      } catch (err) {
        if (!cancelled) setError(err.message);
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [token, navigate]);

  const byArena = useMemo(() => {
    const map = {};
    for (const t of topics) {
      const key = t.arena_key || "other";
      if (!map[key]) map[key] = [];
      map[key].push(t);
    }
    return map;
  }, [topics]);

  const orderedArenas = useMemo(() => {
    if (!fromArena) return ARENA_ORDER;
    return [returnArena, ...ARENA_ORDER.filter((k) => k !== returnArena)];
  }, [fromArena, returnArena]);

  function toggle(id) {
    const key = String(id);
    setSelected((prev) => {
      const next = new Set([...prev].map(String));
      if (next.has(key)) next.delete(key);
      else if (next.size < MAX_PICKS) next.add(key);
      return next;
    });
    setError("");
  }

  function leave(path) {
    if (fromArena) navigate(`/arenas/${returnArena}`, { replace: true });
    else navigate(path || "/feed?welcome=1", { replace: true });
  }

  async function saveAndContinue() {
    const ids = [...selected].map(String).filter(Boolean);
    if (ids.length < MIN_PICKS) {
      setError(`Pick at least ${MIN_PICKS} topic${MIN_PICKS === 1 ? "" : "s"}`);
      return;
    }
    setBusy(true);
    setError("");
    try {
      await topicsApi.setInterests(token, ids, true);
      markTopicOnboardingSeen();
      if (!fromArena) sessionStorage.setItem("bx_welcome", "1");
      leave(fromArena ? undefined : "/feed?welcome=1");
    } catch (err) {
      setError(err.message || "Could not save topics — try again");
    } finally {
      setBusy(false);
    }
  }

  function skip() {
    markTopicOnboardingSeen();
    leave(fromArena ? undefined : "/feed?welcome=1");
  }

  if (loading) return <div className="page-loading">Loading topics…</div>;

  return (
    <div className="feed-wrap surface-page onboarding-topics plaza-page">
      <div className="feed-header">
        {fromArena ? (
          <Link to={`/arenas/${returnArena}`} className="back-link">
            ← Back to {ARENA_LABEL[returnArena] || returnArena}
          </Link>
        ) : null}
        <h1>{fromArena ? "Personalize your topics" : "What do you want to fight about?"}</h1>
      </div>
      <p className="hint surface-lead">
        {fromArena
          ? `Pick lanes for ${ARENA_LABEL[returnArena] || returnArena} (and any other arena). Saved topics shape home debates.`
          : `Pick at least ${MIN_PICKS} topic once (up to ${MAX_PICKS}). We won’t ask again on every login — change anytime from Arenas.`}
      </p>
      {error && <div className="error">{error}</div>}

      {orderedArenas.map((arena) => (
        <section
          key={arena}
          id={`topic-arena-${arena}`}
          className={`topic-arena-block${fromArena && arena === returnArena ? " is-focus-arena" : ""}`}
        >
          <h2 className="topic-arena-title">{ARENA_LABEL[arena] || arena}</h2>
          <div className="topic-chip-grid">
            {(byArena[arena] || []).map((t) => {
              const on = selected.has(String(t.id));
              return (
                <button
                  key={t.id}
                  type="button"
                  className={`topic-chip${on ? " selected" : ""}`}
                  onClick={() => toggle(t.id)}
                  title={t.blurb}
                  aria-pressed={on}
                >
                  {t.name}
                </button>
              );
            })}
          </div>
        </section>
      ))}

      <div className="topic-onboarding-actions">
        <span className="hint">
          {selected.size}/{MAX_PICKS} selected
        </span>
        <button type="button" className="btn-secondary" onClick={skip} disabled={busy}>
          {fromArena ? "Back to arena" : "Skip for now"}
        </button>
        <button
          type="button"
          className="post-btn"
          onClick={saveAndContinue}
          disabled={busy || selected.size < MIN_PICKS}
        >
          {busy ? "Saving…" : fromArena ? "Save topics" : "Continue → See my debates"}
        </button>
        {selected.size < MIN_PICKS ? (
          <p className="hint topic-onboarding-hint">Tap a topic above, then Continue.</p>
        ) : null}
      </div>
    </div>
  );
}
