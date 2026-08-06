import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { topicsApi } from "../api";
import { useAuth } from "../context/AuthContext";

const ARENA_ORDER = ["sports", "politics", "entertainment", "news"];
const ARENA_LABEL = {
  sports: "Sports",
  politics: "Politics",
  entertainment: "Entertainment",
  news: "News",
};
const MIN_PICKS = 1;
const MAX_PICKS = 12;

/**
 * Post-signup interest picker — maps users to topic feeds (Path C).
 */
export default function OnboardingTopics() {
  const { token } = useAuth();
  const navigate = useNavigate();
  const [topics, setTopics] = useState([]);
  const [selected, setSelected] = useState(() => new Set());
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!token) {
      navigate("/login");
      return;
    }
    let cancelled = false;
    topicsApi
      .list(token)
      .then((rows) => {
        if (!cancelled) setTopics(rows || []);
      })
      .catch((err) => {
        if (!cancelled) setError(err.message);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [token, navigate]);

  const byArena = useMemo(() => {
    const map = {};
    for (const t of topics) {
      if (!map[t.arena_key]) map[t.arena_key] = [];
      map[t.arena_key].push(t);
    }
    return map;
  }, [topics]);

  function toggle(id) {
    setSelected((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else if (next.size < MAX_PICKS) next.add(id);
      return next;
    });
  }

  async function saveAndContinue() {
    if (selected.size < MIN_PICKS) {
      setError(`Pick at least ${MIN_PICKS} topics`);
      return;
    }
    setBusy(true);
    setError("");
    try {
      await topicsApi.setInterests(token, [...selected], true);
      sessionStorage.setItem("bx_topics_done", "1");
      sessionStorage.setItem("bx_welcome", "1");
      navigate("/feed?welcome=1");
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  function skip() {
    sessionStorage.setItem("bx_topics_done", "1");
    navigate("/feed?welcome=1");
  }

  if (loading) return <div className="page-loading">Loading topics…</div>;

  return (
    <div className="feed-wrap surface-page onboarding-topics">
      <div className="feed-header">
        <h1>What do you want to fight about?</h1>
      </div>
      <p className="hint surface-lead">
        Pick at least {MIN_PICKS} topic (up to {MAX_PICKS}). We’ll fill your home with debates
        and prompts from those lanes — not a random firehose.
      </p>
      {error && <div className="error">{error}</div>}

      {ARENA_ORDER.map((arena) => (
        <section key={arena} className="topic-arena-block">
          <h2 className="topic-arena-title">{ARENA_LABEL[arena] || arena}</h2>
          <div className="topic-chip-grid">
            {(byArena[arena] || []).map((t) => {
              const on = selected.has(t.id);
              return (
                <button
                  key={t.id}
                  type="button"
                  className={`topic-chip${on ? " selected" : ""}`}
                  onClick={() => toggle(t.id)}
                  title={t.blurb}
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
          Skip for now
        </button>
        <button
          type="button"
          className="post-btn"
          onClick={saveAndContinue}
          disabled={busy || selected.size < MIN_PICKS}
        >
          {busy ? "Saving…" : "See my debates"}
        </button>
      </div>
    </div>
  );
}
