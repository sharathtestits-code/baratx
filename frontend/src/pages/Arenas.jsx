import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { arenasApi, communitiesApi, spacesApi } from "../api";
import { useAuth } from "../context/AuthContext";
import { ARENA_TOPICS, arenaMeta } from "../arenas";

export default function Arenas() {
  const { token } = useAuth();
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
    <div className="feed-wrap surface-page arenas-page">
      <div className="feed-header">
        <h1>Arenas</h1>
      </div>
      <p className="hint surface-lead arenas-lead">
        Not another firehose. Pick a topic, pick a side, and debate Sports, Politics, Entertainment,
        or News.
      </p>

      {error && <div className="error">{error}</div>}

      {loading ? (
        <p className="hint">Loading arenas…</p>
      ) : (
        <>
          <div className="arena-grid">
            {ARENA_TOPICS.map((meta) => {
              const arena = byKey[meta.key];
              return (
                <div key={meta.key} className="arena-card" style={{ "--arena-accent": meta.accent }}>
                  <Link to={`/arenas/${meta.key}`} className="arena-card-main">
                    <div className="arena-card-name">{meta.name}</div>
                    <p className="arena-card-blurb">{meta.blurb}</p>
                    <div className="arena-card-meta">
                      {arena
                        ? `${arena.member_count} joined · ${arena.open_debate_count} live debate${
                            arena.open_debate_count === 1 ? "" : "s"
                          }`
                        : "Opening soon"}
                    </div>
                  </Link>
                  {arena && (
                    <button
                      type="button"
                      className={`arena-join-btn${arena.is_member ? " is-joined" : ""}`}
                      disabled={busyKey === meta.key}
                      onClick={() => toggleJoin(arena)}
                    >
                      {busyKey === meta.key ? "…" : arena.is_member ? "Joined" : "Join"}
                    </button>
                  )}
                </div>
              );
            })}
          </div>

          <h2 className="section-title">Live debates</h2>
          {debates.length === 0 ? (
            <div className="empty-state">
              <p className="empty-state-title">No live debates yet</p>
              <p className="hint">Open an arena and start the first fight.</p>
            </div>
          ) : (
            <ul className="debate-list">
              {debates.map((d) => {
                const meta = arenaMeta(d.arena_key);
                return (
                  <li key={d.id}>
                    <Link to={`/spaces/${d.id}`} className="debate-row">
                      <span className="debate-arena-tag">{d.arena_name || meta?.name || "Arena"}</span>
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
        </>
      )}
    </div>
  );
}
