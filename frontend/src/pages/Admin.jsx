import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { adminApi } from "../api";

const SECRET_KEY = "baratx_admin_secret";

const OFFICIAL_OPTIONS = [
  { value: "baratx", label: "@baratx — BaratX (blue)" },
  { value: "sharath", label: "@sharath — Sharath (blue)" },
  { value: "bharatvoices", label: "@bharatvoices — Bharat Voices (gold)" },
  { value: "indiatech", label: "@indiatech — India Tech Daily (gold)" },
];

const WELCOME_PROMPTS = [
  "Welcome to BaratX — glad you’re here. What’s your city?",
  "Nice first post. What made you join BaratX today?",
  "Welcome! Reply with one India take you wish more people heard.",
];

function formatWhen(iso) {
  if (!iso) return "—";
  try {
    return new Date(iso).toLocaleString(undefined, {
      dateStyle: "medium",
      timeStyle: "short",
    });
  } catch {
    return String(iso);
  }
}

function verifiedLabel(u) {
  const parts = [];
  if (u.is_email_verified) parts.push("email");
  if (u.is_phone_verified) parts.push("phone");
  return parts.length ? parts.join(" · ") : "—";
}

function OfficialSelect({ id, value, onChange }) {
  return (
    <select id={id} className="admin-select" value={value} onChange={(e) => onChange(e.target.value)}>
      {OFFICIAL_OPTIONS.map((opt) => (
        <option key={opt.value} value={opt.value}>
          {opt.label}
        </option>
      ))}
    </select>
  );
}

export default function Admin() {
  const [secret, setSecret] = useState(() => sessionStorage.getItem(SECRET_KEY) || "");
  const [draft, setDraft] = useState("");
  const [stats, setStats] = useState(null);
  const [users, setUsers] = useState([]);
  const [total, setTotal] = useState(0);
  const [recentPosts, setRecentPosts] = useState([]);
  const [recentTotal, setRecentTotal] = useState(0);
  const [newUsersOnly, setNewUsersOnly] = useState(true);
  const [error, setError] = useState("");
  const [msg, setMsg] = useState("");
  const [busy, setBusy] = useState(false);
  const [postText, setPostText] = useState("");
  const [postAs, setPostAs] = useState("baratx");
  const [posting, setPosting] = useState(false);
  const [replyAs, setReplyAs] = useState("baratx");
  const [replyDrafts, setReplyDrafts] = useState({});
  const [replyingId, setReplyingId] = useState(null);
  const [deletingId, setDeletingId] = useState("");
  const [badgeBusyId, setBadgeBusyId] = useState("");
  const [notifyBadge, setNotifyBadge] = useState(true);
  const [founding, setFounding] = useState(null);
  const [race, setRace] = useState(null);
  const [payingId, setPayingId] = useState("");
  const [raceBusy, setRaceBusy] = useState(false);

  const load = useCallback(
    async (adminSecret) => {
      if (!adminSecret) return;
      setBusy(true);
      setError("");
      try {
        const [s, u, posts, fr, rr] = await Promise.all([
          adminApi.stats(adminSecret),
          adminApi.users(adminSecret, { limit: 100, offset: 0 }),
          adminApi.recentPosts(adminSecret, {
            limit: 30,
            newUsersOnly,
            days: 7,
          }),
          adminApi.foundingRewards(adminSecret),
          adminApi.raceRewards(adminSecret),
        ]);
        setStats(s);
        setUsers(u.users || []);
        setTotal(u.total || 0);
        setRecentPosts(posts.posts || []);
        setRecentTotal(posts.total || 0);
        setFounding(fr);
        setRace(rr);
      } catch (err) {
        setStats(null);
        setUsers([]);
        setTotal(0);
        setRecentPosts([]);
        setRecentTotal(0);
        setFounding(null);
        setRace(null);
        setError(err.message || "Could not load admin data");
      } finally {
        setBusy(false);
      }
    },
    [newUsersOnly]
  );

  useEffect(() => {
    if (secret) load(secret);
  }, [secret, load]);

  function handleUnlock(e) {
    e.preventDefault();
    const next = draft.trim();
    if (!next) {
      setError("Enter the admin secret");
      return;
    }
    sessionStorage.setItem(SECRET_KEY, next);
    setSecret(next);
  }

  function handleLock() {
    sessionStorage.removeItem(SECRET_KEY);
    setSecret("");
    setDraft("");
    setStats(null);
    setUsers([]);
    setTotal(0);
    setRecentPosts([]);
    setRecentTotal(0);
    setFounding(null);
    setRace(null);
    setError("");
    setMsg("");
    setReplyDrafts({});
  }

  async function handleMarkFoundingPaid(row) {
    if (!secret || !row?.id) return;
    const note = window.prompt("UPI reference / note (optional)", row.note || "") ?? null;
    if (note === null) return;
    setPayingId(row.id);
    setError("");
    setMsg("");
    try {
      await adminApi.markFoundingPaid(secret, row.id, note);
      setMsg(`Marked @${row.username} as paid ₹${row.amount_inr}`);
      load(secret);
    } catch (err) {
      setError(err.message || "Could not mark paid");
    } finally {
      setPayingId("");
    }
  }

  async function handleCloseRace() {
    if (!secret) return;
    setRaceBusy(true);
    setError("");
    setMsg("");
    try {
      const row = await adminApi.closeRace(secret, {});
      setMsg(
        `Locked Square Race winner @${row.username} — ${row.like_count} likes → ₹${row.amount_inr}`
      );
      load(secret);
    } catch (err) {
      setError(err.message || "Could not close race");
    } finally {
      setRaceBusy(false);
    }
  }

  async function handleMarkRacePaid(row) {
    if (!secret || !row?.id) return;
    const note = window.prompt("UPI reference / note (optional)", row.note || "") ?? null;
    if (note === null) return;
    setPayingId(row.id);
    setError("");
    setMsg("");
    try {
      await adminApi.markRacePaid(secret, row.id, note);
      setMsg(`Race paid @${row.username} ₹${row.amount_inr}`);
      load(secret);
    } catch (err) {
      setError(err.message || "Could not mark race paid");
    } finally {
      setPayingId("");
    }
  }

  async function handleAdminPost(e) {
    e.preventDefault();
    if (!postText.trim() || !secret) return;
    setPosting(true);
    setError("");
    setMsg("");
    try {
      const post = await adminApi.createPost(secret, {
        text: postText.trim(),
        username: postAs,
      });
      setPostText("");
      setMsg(`Posted as @${post.author?.username || postAs}`);
      load(secret);
    } catch (err) {
      setError(err.message || "Could not post");
    } finally {
      setPosting(false);
    }
  }

  async function handleAdminReply(e, post) {
    e.preventDefault();
    const text = (replyDrafts[post.id] || "").trim();
    if (!text || !secret) return;
    setReplyingId(post.id);
    setError("");
    setMsg("");
    try {
      const reply = await adminApi.createReply(secret, {
        post_id: post.id,
        text,
        username: replyAs,
      });
      setReplyDrafts((prev) => {
        const next = { ...prev };
        delete next[post.id];
        return next;
      });
      setMsg(`Commented as @${reply.author?.username || replyAs} on @${post.author?.username}'s post`);
      load(secret);
    } catch (err) {
      setError(err.message || "Could not comment");
    } finally {
      setReplyingId(null);
    }
  }

  function usePrompt(postId, prompt) {
    setReplyDrafts((prev) => ({ ...prev, [postId]: prompt }));
  }

  async function handleDeleteUser(u) {
    if (!secret) return;
    if (u.username === "baratx" || u.username === "sharath") {
      setError("Protected blue founders cannot be deleted");
      return;
    }
    if (
      !window.confirm(
        `Delete @${u.username}? This removes their account and posts if they are misleading.`
      )
    ) {
      return;
    }
    setDeletingId(`user:${u.id}`);
    setError("");
    setMsg("");
    try {
      const res = await adminApi.deleteUser(secret, u.id);
      setMsg(res.message || `Deleted @${u.username}`);
      load(secret);
    } catch (err) {
      setError(err.message || "Could not delete user");
    } finally {
      setDeletingId("");
    }
  }

  async function handleDeletePost(post) {
    if (!secret) return;
    if (
      !window.confirm(
        `Delete this post by @${post.author?.username}? Use this for misleading content.`
      )
    ) {
      return;
    }
    setDeletingId(`post:${post.id}`);
    setError("");
    setMsg("");
    try {
      const res = await adminApi.deletePost(secret, post.id);
      setMsg(res.message || "Post deleted");
      load(secret);
    } catch (err) {
      setError(err.message || "Could not delete post");
    } finally {
      setDeletingId("");
    }
  }

  async function handleSetBadge(u, badge) {
    if (!secret) return;
    const protectedBlue = u.username === "baratx" || u.username === "sharath";
    if (protectedBlue && badge !== "blue") {
      setError("Protected blue founders cannot be demoted");
      return;
    }
    const labels = { none: "no color", gold: "gold", blue: "blue" };
    if (
      !window.confirm(
        `Set @${u.username} badge to ${labels[badge] || badge}?${
          notifyBadge ? " User will be notified." : " User will NOT be notified."
        }`
      )
    ) {
      return;
    }
    setBadgeBusyId(u.id);
    setError("");
    setMsg("");
    try {
      const updated = await adminApi.setBadge(secret, u.id, badge, notifyBadge);
      setUsers((prev) => prev.map((row) => (row.id === updated.id ? { ...row, ...updated } : row)));
      setMsg(`@${u.username} is now ${updated.badge}`);
    } catch (err) {
      setError(err.message || "Could not update badge");
    } finally {
      setBadgeBusyId("");
    }
  }

  if (!secret) {
    return (
      <div className="admin-unlock">
        <h1>Registrations</h1>
        <p className="admin-lead">Enter the ADMIN_SECRET from Railway to view signups.</p>
        {error && <div className="admin-error">{error}</div>}
        <form className="admin-unlock-form" onSubmit={handleUnlock}>
          <label className="admin-field" htmlFor="admin-secret">
            Admin secret
          </label>
          <input
            id="admin-secret"
            type="password"
            value={draft}
            onChange={(e) => setDraft(e.target.value)}
            autoComplete="current-password"
            required
          />
          <button type="submit" className="admin-btn admin-btn-primary" disabled={busy}>
            {busy ? "Opening…" : "Open"}
          </button>
        </form>
      </div>
    );
  }

  const statItems = stats
    ? [
        { value: stats.total_users, label: "Total users" },
        { value: stats.users_with_posts ?? "—", label: "Users who posted" },
        { value: stats.posters_last_24h ?? "—", label: "Posters (24h)" },
        { value: stats.posts_last_24h ?? "—", label: "Posts (24h)" },
        { value: stats.total_posts ?? "—", label: "Total posts" },
        { value: stats.users_last_24h, label: "Signups (24h)" },
        { value: stats.email_verified, label: "Email verified" },
        { value: stats.with_phone, label: "With phone" },
      ]
    : [];

  return (
    <div className="admin-panel">
      <header className="admin-header">
        <div>
          <h1>Registrations</h1>
          <p className="admin-lead">Live BaratX signup overview</p>
        </div>
        <div className="admin-actions">
          <button
            type="button"
            className="admin-btn admin-btn-ghost"
            onClick={async () => {
              setBusy(true);
              setError("");
              setMsg("");
              try {
                const res = await adminApi.refreshPrompts(secret, true);
                setMsg(
                  `Prompts refreshed — created ${res.created || 0}, skipped ${res.skipped || 0}`
                );
                load(secret);
              } catch (err) {
                setError(err.message || "Refresh failed");
              } finally {
                setBusy(false);
              }
            }}
            disabled={busy}
          >
            Refresh debate prompts
          </button>
          <button
            type="button"
            className="admin-btn admin-btn-ghost"
            onClick={async () => {
              setBusy(true);
              setError("");
              setMsg("");
              try {
                const res = await adminApi.dailyDigest(secret, true);
                if (res.skipped) {
                  setMsg(`Daily digest skipped — ${res.reason || "already posted"}`);
                } else {
                  const arenas = (res.posts || [])
                    .map((p) => p.arena)
                    .filter(Boolean)
                    .join(", ");
                  setMsg(
                    `Daily digest — posted ${res.created || 0}/5` +
                      (arenas ? ` · ${arenas}` : "") +
                      ` (@${(res.authors || ["sharath", "baratx"]).join(", @")})`
                  );
                }
                load(secret);
              } catch (err) {
                setError(err.message || "Daily digest failed");
              } finally {
                setBusy(false);
              }
            }}
            disabled={busy}
          >
            Run daily digest now
          </button>
          <button
            type="button"
            className="admin-btn admin-btn-ghost"
            onClick={() => load(secret)}
            disabled={busy}
          >
            {busy ? "Refreshing…" : "Refresh"}
          </button>
          <button type="button" className="admin-btn admin-btn-ghost" onClick={handleLock}>
            Lock
          </button>
        </div>
      </header>

      {error && <div className="admin-error">{error}</div>}
      {msg && <p className="admin-ok">{msg}</p>}

      {founding && (
        <section className="admin-compose" aria-labelledby="admin-founding-title">
          <h2 id="admin-founding-title">Founding {founding.cap} — UPI payouts</h2>
          <p className="admin-lead">
            ₹{founding.amount_inr} for one problem post or any-arena debate. Floor → community rating
            (likes/replies) → you pay. {founding.slots_remaining} slots left · {founding.eligible_count}{" "}
            waiting on rating · {founding.payable_count || 0} payable · {founding.paid_count} paid.
          </p>
          {founding.eval?.rating && (
            <p className="admin-muted">Rating bar: {founding.eval.rating}</p>
          )}
          {(founding.rewards || []).length === 0 ? (
            <p className="admin-empty-inline">No qualifying posts yet.</p>
          ) : (
            <div className="admin-table-wrap">
              <table className="admin-table">
                <thead>
                  <tr>
                    <th>User</th>
                    <th>Kind</th>
                    <th>Status</th>
                    <th>Rating</th>
                    <th>When</th>
                    <th />
                  </tr>
                </thead>
                <tbody>
                  {founding.rewards.map((r) => {
                    const q = r.quality || {};
                    const rating =
                      r.kind === "debate"
                        ? `${q.stance_count ?? 0} stances · ${q.post_count ?? 0} posts`
                        : `${q.like_count ?? 0} likes · ${q.reply_count ?? 0} replies`;
                    return (
                      <tr key={r.id}>
                        <td>
                          <Link to={`/${r.username}`}>@{r.username}</Link>
                          <div className="admin-muted">{r.display_name}</div>
                        </td>
                        <td>{r.kind}</td>
                        <td>{r.status}</td>
                        <td>
                          {rating}
                          {q.meets_bar ? " ✓" : ""}
                        </td>
                        <td>{formatWhen(r.created_at)}</td>
                        <td>
                          {r.status === "paid" ? (
                            <span className="admin-muted">{r.note || "Paid"}</span>
                          ) : (
                            <button
                              type="button"
                              className="admin-btn admin-btn-primary"
                              disabled={payingId === r.id}
                              onClick={() => handleMarkFoundingPaid(r)}
                              title={
                                r.status === "eligible"
                                  ? "Bar not met yet — only pay after review if intentional"
                                  : "Ready to pay"
                              }
                            >
                              {payingId === r.id ? "Saving…" : "Mark paid"}
                            </button>
                          )}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </section>
      )}

      {race && (
        <section className="admin-compose" aria-labelledby="admin-race-title">
          <h2 id="admin-race-title">Square Race — biweekly likes</h2>
          <p className="admin-lead">
            Highest-liked Home post each {race.current?.cadence_days || 14} days wins ₹
            {race.current?.prize_min || 150}–₹{race.current?.prize_max || 500} (scaled by likes).
            Period {race.current?.period_key}.
          </p>
          {race.current?.leader ? (
            <p className="admin-muted">
              Current leader: @{race.current.leader.username} · {race.current.leader.like_count} likes ·
              ~₹{race.current.leader.prize_inr}
            </p>
          ) : (
            <p className="admin-muted">No qualifying leader yet (need enough likes).</p>
          )}
          <div className="admin-actions" style={{ marginBottom: "0.75rem" }}>
            <button
              type="button"
              className="admin-btn admin-btn-primary"
              disabled={raceBusy}
              onClick={handleCloseRace}
            >
              {raceBusy ? "Locking…" : "Lock current leader as winner"}
            </button>
          </div>
          {(race.current?.leaderboard || []).length > 0 && (
            <div className="admin-table-wrap">
              <table className="admin-table">
                <thead>
                  <tr>
                    <th>#</th>
                    <th>User</th>
                    <th>Likes</th>
                    <th>Prize</th>
                    <th>Post</th>
                  </tr>
                </thead>
                <tbody>
                  {race.current.leaderboard.slice(0, 8).map((row, i) => (
                    <tr key={row.post_id}>
                      <td>{i + 1}</td>
                      <td>
                        <Link to={`/${row.username}`}>@{row.username}</Link>
                      </td>
                      <td>{row.like_count}</td>
                      <td>₹{row.prize_inr || "—"}</td>
                      <td className="admin-muted">{row.text}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
          {(race.rewards || []).length > 0 && (
            <>
              <h3 className="admin-subhead">Locked winners</h3>
              <div className="admin-table-wrap">
                <table className="admin-table">
                  <thead>
                    <tr>
                      <th>Period</th>
                      <th>User</th>
                      <th>Likes</th>
                      <th>₹</th>
                      <th>Status</th>
                      <th />
                    </tr>
                  </thead>
                  <tbody>
                    {race.rewards.map((r) => (
                      <tr key={r.id}>
                        <td>{r.period_key}</td>
                        <td>@{r.username}</td>
                        <td>{r.like_count}</td>
                        <td>{r.amount_inr}</td>
                        <td>{r.status}</td>
                        <td>
                          {r.status === "payable" ? (
                            <button
                              type="button"
                              className="admin-btn admin-btn-primary"
                              disabled={payingId === r.id}
                              onClick={() => handleMarkRacePaid(r)}
                            >
                              {payingId === r.id ? "Saving…" : "Mark paid"}
                            </button>
                          ) : (
                            <span className="admin-muted">{r.note || "Paid"}</span>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </>
          )}
        </section>
      )}

      <section className="admin-compose" aria-labelledby="admin-compose-title">
        <h2 id="admin-compose-title">Post as BaratX</h2>
        <p className="admin-lead">Publish from an official account without logging into the app.</p>
        <form className="admin-compose-form" onSubmit={handleAdminPost}>
          <div className="admin-field-block">
            <label className="admin-field" htmlFor="admin-post-as">
              Account
            </label>
            <OfficialSelect id="admin-post-as" value={postAs} onChange={setPostAs} />
          </div>

          <div className="admin-field-block">
            <label className="admin-field" htmlFor="admin-post-text">
              Post
            </label>
            <textarea
              id="admin-post-text"
              className="admin-textarea"
              value={postText}
              onChange={(e) => setPostText(e.target.value)}
              maxLength={500}
              rows={4}
              placeholder="Say something India can reply to…"
              required
            />
          </div>

          <div className="admin-compose-footer">
            <span className="admin-char-count">{postText.length}/500</span>
            <button
              type="submit"
              className="admin-btn admin-btn-primary"
              disabled={posting || !postText.trim()}
            >
              {posting ? "Posting…" : "Post"}
            </button>
          </div>
        </form>
      </section>

      <section className="admin-compose admin-engage" aria-labelledby="admin-engage-title">
        <div className="admin-engage-head">
          <div>
            <h2 id="admin-engage-title">Comment on new users</h2>
            <p className="admin-lead">
              Welcome new joiners by replying to their posts — not only broadcasting.
            </p>
          </div>
          <label className="admin-toggle">
            <input
              type="checkbox"
              checked={newUsersOnly}
              onChange={(e) => setNewUsersOnly(e.target.checked)}
            />
            New joiners (7d) only
          </label>
        </div>

        <div className="admin-field-block admin-engage-account">
          <label className="admin-field" htmlFor="admin-reply-as">
            Reply as
          </label>
          <OfficialSelect id="admin-reply-as" value={replyAs} onChange={setReplyAs} />
        </div>

        {recentPosts.length === 0 && !busy && (
          <p className="admin-empty-inline">
            {newUsersOnly
              ? "No posts from users who joined in the last 7 days yet."
              : "No community posts to comment on yet."}
          </p>
        )}

        <ul className="admin-post-list">
          {recentPosts.map((post) => {
            const draftText = replyDrafts[post.id] || "";
            const busyReply = replyingId === post.id;
            return (
              <li key={post.id} className="admin-post-card">
                <div className="admin-post-meta">
                  <Link
                    className={`admin-user-link${
                      post.author?.badge === "blue" || post.author?.is_official
                        ? " admin-user-blue"
                        : post.author?.badge === "gold"
                          ? " admin-user-gold"
                          : " admin-user-reg"
                    }`}
                    to={`/u/${encodeURIComponent(post.author?.username || "")}`}
                  >
                    @{post.author?.username}
                  </Link>
                  <span className="admin-post-name">{post.author?.display_name}</span>
                  <span className="admin-post-time">{formatWhen(post.created_at)}</span>
                  <Link className="admin-post-open" to={`/posts/${post.id}`}>
                    Open
                  </Link>
                  <button
                    type="button"
                    className="admin-btn admin-btn-danger admin-btn-tiny"
                    disabled={deletingId === `post:${post.id}`}
                    onClick={() => handleDeletePost(post)}
                  >
                    {deletingId === `post:${post.id}` ? "Deleting…" : "Delete post"}
                  </button>
                </div>
                <p className="admin-post-text">{post.text}</p>
                <p className="admin-post-stats">
                  {post.reply_count ?? 0} replies · {post.like_count ?? 0} likes
                </p>

                <div className="admin-prompt-row">
                  {WELCOME_PROMPTS.map((prompt) => (
                    <button
                      key={prompt}
                      type="button"
                      className="admin-prompt-chip"
                      onClick={() => usePrompt(post.id, prompt)}
                    >
                      {prompt.length > 42 ? `${prompt.slice(0, 42)}…` : prompt}
                    </button>
                  ))}
                </div>

                <form className="admin-reply-form" onSubmit={(e) => handleAdminReply(e, post)}>
                  <textarea
                    className="admin-textarea admin-reply-textarea"
                    value={draftText}
                    onChange={(e) =>
                      setReplyDrafts((prev) => ({ ...prev, [post.id]: e.target.value }))
                    }
                    maxLength={220}
                    rows={3}
                    placeholder={`Comment as @${replyAs}… type @ to tag`}
                    required
                  />
                  <div className="admin-compose-footer">
                    <span className="admin-char-count">{draftText.length}/220</span>
                    <button
                      type="submit"
                      className="admin-btn admin-btn-primary"
                      disabled={busyReply || !draftText.trim()}
                    >
                      {busyReply ? "Commenting…" : "Comment"}
                    </button>
                  </div>
                </form>
              </li>
            );
          })}
        </ul>

        {recentPosts.length > 0 && (
          <p className="admin-count admin-engage-count">
            Showing {recentPosts.length} of {recentTotal} posts
            {newUsersOnly ? " from new joiners" : ""}
          </p>
        )}
      </section>

      {statItems.length > 0 && (
        <div className="admin-stats">
          {statItems.map((item) => (
            <div className="admin-stat" key={item.label}>
              <span className="admin-stat-value">{item.value}</span>
              <span className="admin-stat-label">{item.label}</span>
            </div>
          ))}
        </div>
      )}

      <p className="admin-count">
        Showing {users.length} of {total} users (newest first)
      </p>
      <label className="badge-notify-opt admin-badge-notify">
        <input
          type="checkbox"
          checked={notifyBadge}
          onChange={(e) => setNotifyBadge(e.target.checked)}
        />
        Notify user when changing badge
      </label>

      <div className="admin-table-wrap">
        <table className="admin-table">
          <thead>
            <tr>
              <th>Joined</th>
              <th>Username</th>
              <th>Name</th>
              <th>Badge</th>
              <th>Email</th>
              <th>Phone</th>
              <th>Method</th>
              <th>Verified</th>
              <th>Badge actions</th>
              <th>Moderation</th>
            </tr>
          </thead>
          <tbody>
            {users.length === 0 && !busy && (
              <tr>
                <td colSpan={10} className="admin-empty">
                  No registrations yet.
                </td>
              </tr>
            )}
            {users.map((u) => {
              const badge = u.badge || (u.is_official ? "blue" : "none");
              const protectedBlue = u.username === "baratx" || u.username === "sharath";
              const busyBadge = badgeBusyId === u.id;
              return (
                <tr
                  key={u.id}
                  className={
                    badge === "blue"
                      ? "admin-row-blue"
                      : badge === "gold"
                        ? "admin-row-gold"
                        : "admin-row-reg"
                  }
                >
                  <td>{formatWhen(u.created_at)}</td>
                  <td>
                    <Link
                      className={`admin-user-link${
                        badge === "blue"
                          ? " admin-user-blue"
                          : badge === "gold"
                            ? " admin-user-gold"
                            : " admin-user-reg"
                      }`}
                      to={`/u/${encodeURIComponent(u.username)}`}
                    >
                      @{u.username}
                    </Link>
                  </td>
                  <td>{u.display_name}</td>
                  <td>
                    <span className={`admin-badge-pill admin-badge-${badge}`}>{badge}</span>
                  </td>
                  <td>{u.email || "—"}</td>
                  <td>{u.phone || "—"}</td>
                  <td>{u.signup_method}</td>
                  <td>{verifiedLabel(u)}</td>
                  <td>
                    {protectedBlue ? (
                      <span className="admin-protected">Protected</span>
                    ) : (
                      <div className="admin-badge-actions">
                        {badge !== "gold" && (
                          <button
                            type="button"
                            className="admin-btn admin-btn-tiny"
                            disabled={busyBadge}
                            onClick={() => handleSetBadge(u, "gold")}
                          >
                            Gold
                          </button>
                        )}
                        {badge === "gold" && (
                          <button
                            type="button"
                            className="admin-btn admin-btn-tiny admin-btn-blue"
                            disabled={busyBadge}
                            onClick={() => handleSetBadge(u, "blue")}
                          >
                            Blue
                          </button>
                        )}
                        {badge === "blue" && (
                          <button
                            type="button"
                            className="admin-btn admin-btn-tiny"
                            disabled={busyBadge}
                            onClick={() => handleSetBadge(u, "gold")}
                          >
                            Demote
                          </button>
                        )}
                        {badge === "gold" && (
                          <button
                            type="button"
                            className="admin-btn admin-btn-tiny"
                            disabled={busyBadge}
                            onClick={() => handleSetBadge(u, "none")}
                          >
                            Clear
                          </button>
                        )}
                      </div>
                    )}
                  </td>
                  <td>
                    {protectedBlue ? (
                      <span className="admin-protected">Protected</span>
                    ) : (
                      <button
                        type="button"
                        className="admin-btn admin-btn-danger admin-btn-tiny"
                        disabled={deletingId === `user:${u.id}`}
                        onClick={() => handleDeleteUser(u)}
                      >
                        {deletingId === `user:${u.id}` ? "Deleting…" : "Delete"}
                      </button>
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
