import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { earlyIssuesApi } from "../api";
import { useAuth } from "../context/AuthContext";
import Avatar from "../components/Avatar";
import { WHATSAPP_CHANNEL, WHATSAPP_COMMUNITY } from "../socialLinks";
import { formatLocalWhen } from "../time";

const MAX_LEN = 500;

/**
 * First-1000 early members log bugs / concerns here.
 * Ops gets an email on every new issue. WhatsApp links for everyone.
 */
export default function EarlyIssues() {
  const { token, user } = useAuth();
  const [meta, setMeta] = useState(null);
  const [items, setItems] = useState([]);
  const [text, setText] = useState("");
  const [kind, setKind] = useState("bug");
  const [busy, setBusy] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [msg, setMsg] = useState("");

  async function refresh() {
    setLoading(true);
    setError("");
    try {
      const [m, list] = await Promise.all([
        earlyIssuesApi.meta(token),
        earlyIssuesApi.list(token),
      ]);
      setMeta(m);
      setItems(Array.isArray(list) ? list : []);
    } catch (err) {
      setError(err.message || "Could not load early issues");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    refresh();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token]);

  async function submit(e) {
    e.preventDefault();
    if (!token) {
      setError("Log in to post an issue.");
      return;
    }
    if (!text.trim() || busy) return;
    setBusy(true);
    setError("");
    setMsg("");
    try {
      const row = await earlyIssuesApi.create(token, { text: text.trim(), kind });
      setItems((prev) => [row, ...prev]);
      setText("");
      setMsg("Posted. BarathX ops was emailed. Thanks for helping.");
    } catch (err) {
      setError(err.message || "Could not post issue");
    } finally {
      setBusy(false);
    }
  }

  const canPost = Boolean(token && meta?.is_early_member);

  return (
    <div className="feed-wrap surface-page early-issues-page">
      <div className="feed-header">
        <h1>Early issues</h1>
        <p className="hint" style={{ margin: "0.35rem 0 0" }}>
          First {meta?.early_cap || 1000} members can log bugs and concerns here. We email ops on
          every new issue. Everyone can join WhatsApp to talk it through.
        </p>
      </div>

      <section className="early-wa-card" aria-label="WhatsApp">
        <h2>WhatsApp</h2>
        <p className="hint">Join to express concerns, share bugs, and stay close to the soft launch.</p>
        <div className="early-wa-actions">
          <a
            className="btn btn-primary"
            href={meta?.whatsapp_community || WHATSAPP_COMMUNITY}
            target="_blank"
            rel="noreferrer"
          >
            Join WhatsApp Community
          </a>
          <a
            className="btn btn-secondary"
            href={meta?.whatsapp_channel || WHATSAPP_CHANNEL}
            target="_blank"
            rel="noreferrer"
          >
            Follow WhatsApp Channel
          </a>
        </div>
      </section>

      {!token ? (
        <p className="hint">
          <Link to="/login?next=/early-issues">Log in</Link> if you&apos;re in the first{" "}
          {meta?.early_cap || 1000} to post an issue here.
        </p>
      ) : meta && !meta.is_early_member ? (
        <p className="hint">
          You&apos;re past the first {meta.early_cap} join slots for this board
          {meta.early_rank ? ` (you&apos;re #${meta.early_rank})` : ""}. Use WhatsApp above, or report
          a post from ···.
        </p>
      ) : meta?.is_early_member ? (
        <p className="hint ok-hint">
          You&apos;re early member #{meta.early_rank}. Post a bug or concern below.
        </p>
      ) : null}

      {canPost && (
        <form className="early-issue-form" onSubmit={submit}>
          <label className="early-kind">
            Type
            <select value={kind} onChange={(e) => setKind(e.target.value)}>
              <option value="bug">Bug</option>
              <option value="concern">Concern</option>
              <option value="idea">Idea</option>
            </select>
          </label>
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value.slice(0, MAX_LEN))}
            maxLength={MAX_LEN}
            rows={4}
            placeholder="What broke, or what’s worrying you? Be specific."
            required
          />
          <div className="early-issue-footer">
            <span className="hint">
              {text.length}/{MAX_LEN}
            </span>
            <button type="submit" className="btn btn-primary" disabled={busy || text.trim().length < 10}>
              {busy ? "Sending…" : "Post issue"}
            </button>
          </div>
        </form>
      )}

      {error && <div className="error">{error}</div>}
      {msg && <p className="hint ok-hint">{msg}</p>}

      {loading ? (
        <p className="hint">Loading issues…</p>
      ) : items.length === 0 ? (
        <p className="hint">No issues yet. Be the first early member to log one.</p>
      ) : (
        <ul className="early-issue-list">
          {items.map((row) => (
            <li key={row.id} className="early-issue-card">
              <div className="early-issue-head">
                <Avatar
                  name={row.author?.display_name}
                  username={row.author?.username}
                  url={row.author?.avatar_url}
                  size={36}
                />
                <div>
                  <strong>{row.author?.display_name || "Member"}</strong>
                  <span className="hint">
                    {" "}
                    @{row.author?.username} · {row.kind} · {formatLocalWhen(row.created_at)}
                  </span>
                </div>
              </div>
              <p>{row.text}</p>
            </li>
          ))}
        </ul>
      )}

      <p className="legal-back">
        <Link to={user ? "/home" : "/"}>← Back</Link>
        {" · "}
        <Link to="/guidelines">Guidelines</Link>
      </p>
    </div>
  );
}
