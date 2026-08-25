import { useCallback, useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { adminApi } from "../api";

const SECRET_KEY = "baratx_admin_secret";
const TAB_KEY = "baratx_admin_tab";

const TABS = [
  { id: "overview", label: "Overview" },
  { id: "users", label: "Users" },
  { id: "engage", label: "Engage" },
  { id: "post", label: "Post" },
  { id: "payouts", label: "Payouts" },
  { id: "tools", label: "Tools" },
];

const OFFICIAL_OPTIONS = [
  { value: "baratx", label: "@baratx. BarathX (blue)" },
  { value: "sharath", label: "@sharath. Sharath (blue)" },
  { value: "bharatvoices", label: "@bharatvoices. Bharat Voices (gold)" },
  { value: "indiatech", label: "@indiatech. India Tech Daily (gold)" },
];

const WELCOME_PROMPTS = [
  "Welcome to BarathX, glad you’re here. What’s your city?",
  "Nice first post. What made you join BarathX today?",
  "Welcome! Reply with one India take you wish more people heard.",
];

function formatWhen(iso) {
  if (!iso) return "-";
  try {
    return new Date(iso).toLocaleString(undefined, {
      dateStyle: "medium",
      timeStyle: "short",
    });
  } catch {
    return String(iso);
  }
}

function formatShortWhen(iso) {
  if (!iso) return "-";
  try {
    return new Date(iso).toLocaleDateString(undefined, {
      month: "short",
      day: "numeric",
    });
  } catch {
    return String(iso);
  }
}

function verifiedLabel(u) {
  const parts = [];
  if (u.email) {
    parts.push(u.is_email_verified ? "email verified" : "email unverified");
  }
  if (u.phone) {
    parts.push(u.is_phone_verified ? "phone verified" : "phone unverified");
  }
  return parts.length ? parts.join(" · ") : "-";
}

function emailDisplay(u) {
  if (!u.email) return "-";
  return u.is_email_verified ? u.email : `${u.email} (unverified)`;
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

function readStoredTab() {
  try {
    const t = sessionStorage.getItem(TAB_KEY);
    if (TABS.some((tab) => tab.id === t)) return t;
  } catch {
    /* ignore */
  }
  return "overview";
}

export default function Admin() {
  const [secret, setSecret] = useState(() => sessionStorage.getItem(SECRET_KEY) || "");
  const [draft, setDraft] = useState("");
  const [tab, setTab] = useState(readStoredTab);
  const [stats, setStats] = useState(null);
  const [users, setUsers] = useState([]);
  const [total, setTotal] = useState(0);
  const [recentPosts, setRecentPosts] = useState([]);
  const [recentTotal, setRecentTotal] = useState(0);
  const [newUsersOnly, setNewUsersOnly] = useState(true);
  const [userQuery, setUserQuery] = useState("");
  const [expandedUserId, setExpandedUserId] = useState("");
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

  useEffect(() => {
    // Keep this surface out of search indexes; unlock copy must not name hosting/env vars.
    let robots = document.querySelector('meta[name="robots"]');
    const prev = robots?.getAttribute("content") || "";
    if (!robots) {
      robots = document.createElement("meta");
      robots.setAttribute("name", "robots");
      document.head.appendChild(robots);
    }
    robots.setAttribute("content", "noindex, nofollow");
    return () => {
      if (prev) robots.setAttribute("content", prev);
      else robots.remove();
    };
  }, []);

  const goTab = useCallback((id) => {
    setTab(id);
    try {
      sessionStorage.setItem(TAB_KEY, id);
    } catch {
      /* ignore */
    }
    window.scrollTo({ top: 0, behavior: "smooth" });
  }, []);

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
        const msg = err.message || "Could not load admin data";
        setError(msg);
        // Wrong / revoked secret, drop session so unlock screen returns.
        if (/admin secret|unauthorized|401/i.test(msg)) {
          sessionStorage.removeItem(SECRET_KEY);
          setSecret("");
        }
      } finally {
        setBusy(false);
      }
    },
    [newUsersOnly]
  );

  useEffect(() => {
    if (secret) load(secret);
  }, [secret, load]);

  const filteredUsers = useMemo(() => {
    const q = userQuery.trim().toLowerCase();
    if (!q) return users;
    return users.filter((u) => {
      const hay = [u.username, u.display_name, u.email, u.phone, u.signup_method, u.badge]
        .filter(Boolean)
        .join(" ")
        .toLowerCase();
      return hay.includes(q);
    });
  }, [users, userQuery]);

  const payableFounding = useMemo(
    () => (founding?.rewards || []).filter((r) => r.status === "payable"),
    [founding]
  );
  const payableRace = useMemo(
    () => (race?.rewards || []).filter((r) => r.status === "payable"),
    [race]
  );
  const needsAttention =
    (founding?.payable_count || payableFounding.length || 0) + payableRace.length;

  async function handleUnlock(e) {
    e.preventDefault();
    const next = draft.trim();
    if (!next) {
      setError("Enter your unlock code");
      return;
    }
    setBusy(true);
    setError("");
    try {
      // Validate before persisting, wrong secrets never stick in sessionStorage.
      await adminApi.stats(next);
      sessionStorage.setItem(SECRET_KEY, next);
      setSecret(next);
    } catch (err) {
      sessionStorage.removeItem(SECRET_KEY);
      setError(err.message || "Could not unlock admin");
    } finally {
      setBusy(false);
    }
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
    setUserQuery("");
    setExpandedUserId("");
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
        `Locked Square Race winner @${row.username}, ${row.like_count} likes → ₹${row.amount_inr}`
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
        <h1>Ops</h1>
        <p className="admin-lead">Enter your unlock code to open the console.</p>
        {error && <div className="admin-error">{error}</div>}
        <form className="admin-unlock-form" onSubmit={handleUnlock}>
          <label className="admin-field" htmlFor="admin-secret">
            Unlock code
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
        { value: stats.total_users, label: "Total users", tab: "users" },
        { value: stats.users_last_24h, label: "Signups (24h)", tab: "users" },
        { value: stats.users_with_posts ?? "-", label: "Users who posted", tab: "engage" },
        { value: stats.posters_last_24h ?? "-", label: "Posters (24h)", tab: "engage" },
        { value: stats.posts_last_24h ?? "-", label: "Posts (24h)", tab: "engage" },
        { value: stats.total_posts ?? "-", label: "Total posts", tab: "engage" },
        { value: stats.email_verified, label: "Email verified", tab: "users" },
        { value: stats.with_phone, label: "With phone", tab: "users" },
      ]
    : [];

  const tabBadges = {
    users: total || null,
    engage: recentTotal || null,
    payouts: needsAttention || null,
  };

  return (
    <div className="admin-panel">
      <header className="admin-header">
        <div>
          <h1>Ops</h1>
          <p className="admin-lead">Jump to what you need, no endless scroll.</p>
        </div>
        <div className="admin-actions">
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

      <nav className="admin-tabs" aria-label="Ops sections">
        {TABS.map((t) => {
          const badge = tabBadges[t.id];
          return (
            <button
              key={t.id}
              type="button"
              className={`admin-tab${tab === t.id ? " is-active" : ""}`}
              onClick={() => goTab(t.id)}
              aria-current={tab === t.id ? "page" : undefined}
            >
              <span>{t.label}</span>
              {badge != null && badge > 0 ? (
                <span className="admin-tab-badge" aria-label={`${badge}`}>
                  {badge > 99 ? "99+" : badge}
                </span>
              ) : null}
            </button>
          );
        })}
      </nav>

      {error && <div className="admin-error">{error}</div>}
      {msg && <p className="admin-ok">{msg}</p>}

      {tab === "overview" && (
        <div className="admin-tab-panel">
          {statItems.length > 0 && (
            <div className="admin-stats">
              {statItems.map((item) => (
                <button
                  type="button"
                  className="admin-stat admin-stat-btn"
                  key={item.label}
                  onClick={() => goTab(item.tab)}
                >
                  <span className="admin-stat-value">{item.value}</span>
                  <span className="admin-stat-label">{item.label}</span>
                </button>
              ))}
            </div>
          )}

          <section className="admin-compose" aria-labelledby="admin-attention-title">
            <h2 id="admin-attention-title">Needs attention</h2>
            <div className="admin-attention-grid">
              <button type="button" className="admin-attention-card" onClick={() => goTab("payouts")}>
                <span className="admin-attention-value">
                  {founding?.payable_count ?? payableFounding.length}
                </span>
                <span className="admin-attention-label">Founding ready to pay</span>
                <span className="admin-attention-meta">
                  {founding?.slots_remaining ?? "-"} slots left · {founding?.eligible_count ?? 0} waiting
                </span>
              </button>
              <button type="button" className="admin-attention-card" onClick={() => goTab("payouts")}>
                <span className="admin-attention-value">{payableRace.length}</span>
                <span className="admin-attention-label">Race winners to pay</span>
                <span className="admin-attention-meta">
                  {race?.current?.leader
                    ? `Leader @${race.current.leader.username} · ${race.current.leader.like_count} likes`
                    : "No leader yet"}
                </span>
              </button>
              <button type="button" className="admin-attention-card" onClick={() => goTab("engage")}>
                <span className="admin-attention-value">{recentTotal}</span>
                <span className="admin-attention-label">New-joiner posts</span>
                <span className="admin-attention-meta">Welcome / comment queue</span>
              </button>
              <button type="button" className="admin-attention-card" onClick={() => goTab("users")}>
                <span className="admin-attention-value">{stats?.users_last_24h ?? "-"}</span>
                <span className="admin-attention-label">Signups today</span>
                <span className="admin-attention-meta">{total} total users</span>
              </button>
            </div>
          </section>

          <section className="admin-compose">
            <h2>Quick jumps</h2>
            <div className="admin-quick-row">
              <button type="button" className="admin-btn admin-btn-primary" onClick={() => goTab("users")}>
                Find a user
              </button>
              <button type="button" className="admin-btn" onClick={() => goTab("engage")}>
                Comment on new users
              </button>
              <button type="button" className="admin-btn" onClick={() => goTab("post")}>
                Post as official
              </button>
              <button type="button" className="admin-btn" onClick={() => goTab("payouts")}>
                Pay founding / race
              </button>
              <button type="button" className="admin-btn admin-btn-ghost" onClick={() => goTab("tools")}>
                Digest · IG · prompts
              </button>
            </div>
          </section>

          {(users.slice(0, 8).length > 0) && (
            <section className="admin-compose">
              <div className="admin-section-head">
                <h2>Newest signups · review</h2>
                <button type="button" className="admin-link-btn" onClick={() => goTab("users")}>
                  View all →
                </button>
              </div>
              <p className="admin-lead">
                Flag no-posts, unverified email, and multi-reports. Prefer phone OTP humans.
              </p>
              <ul className="admin-user-cards admin-user-cards--compact">
                {users.slice(0, 8).map((u) => {
                  const badge = u.badge || (u.is_official ? "blue" : "none");
                  const flags = Array.isArray(u.review_flags) ? u.review_flags : [];
                  return (
                    <li key={u.id} className={`admin-user-card admin-user-card--${badge}`}>
                      <div className="admin-user-card-main">
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
                        <span className="admin-user-card-name">{u.display_name}</span>
                        <span className={`admin-badge-pill admin-badge-${badge}`}>{badge}</span>
                      </div>
                      <div className="admin-user-card-meta">
                        <span>{formatShortWhen(u.created_at)}</span>
                        <span>{u.email || u.phone || u.signup_method}</span>
                        <span>
                          {u.has_posted_once || u.post_count > 0
                            ? `${u.post_count || 0} posts`
                            : "no posts yet"}
                        </span>
                      </div>
                      {flags.length > 0 ? (
                        <div className="admin-review-flags">
                          {flags.map((f) => (
                            <span key={f} className="admin-review-flag">
                              {f}
                            </span>
                          ))}
                        </div>
                      ) : (
                        <p className="admin-muted admin-review-ok">Looks fine</p>
                      )}
                    </li>
                  );
                })}
              </ul>
            </section>
          )}
        </div>
      )}

      {tab === "users" && (
        <div className="admin-tab-panel">
          <section className="admin-compose" aria-labelledby="admin-users-title">
            <div className="admin-section-head">
              <div>
                <h2 id="admin-users-title">Users</h2>
                <p className="admin-lead">
                  Showing {filteredUsers.length}
                  {userQuery.trim() ? ` match${filteredUsers.length === 1 ? "" : "es"}` : ""} of{" "}
                  {users.length} loaded · {total} total (newest first)
                </p>
              </div>
            </div>

            <div className="admin-toolbar">
              <label className="admin-search" htmlFor="admin-user-search">
                <span className="visually-hidden">Search users</span>
                <input
                  id="admin-user-search"
                  type="search"
                  value={userQuery}
                  onChange={(e) => setUserQuery(e.target.value)}
                  placeholder="Search username, name, email, phone…"
                  autoComplete="off"
                />
              </label>
              <label className="badge-notify-opt admin-badge-notify">
                <input
                  type="checkbox"
                  checked={notifyBadge}
                  onChange={(e) => setNotifyBadge(e.target.checked)}
                />
                Notify on badge change
              </label>
            </div>

            <p className="hint admin-hint">
              Tap a row for email / phone / badge actions. Delete misleading accounts anytime.
            </p>

            {filteredUsers.length === 0 && !busy ? (
              <p className="admin-empty-inline">
                {userQuery.trim() ? "No users match that search." : "No registrations yet."}
              </p>
            ) : (
              <ul className="admin-user-cards">
                {filteredUsers.map((u) => {
                  const badge = u.badge || (u.is_official ? "blue" : "none");
                  const protectedBlue = u.username === "baratx" || u.username === "sharath";
                  const busyBadge = badgeBusyId === u.id;
                  const open = expandedUserId === u.id;
                  return (
                    <li key={u.id} className={`admin-user-card admin-user-card--${badge}${open ? " is-open" : ""}`}>
                      <button
                        type="button"
                        className="admin-user-card-toggle"
                        onClick={() => setExpandedUserId(open ? "" : u.id)}
                        aria-expanded={open}
                      >
                        <div className="admin-user-card-main">
                          <span
                            className={`admin-user-link${
                              badge === "blue"
                                ? " admin-user-blue"
                                : badge === "gold"
                                  ? " admin-user-gold"
                                  : " admin-user-reg"
                            }`}
                          >
                            @{u.username}
                          </span>
                          <span className="admin-user-card-name">{u.display_name}</span>
                          <span className={`admin-badge-pill admin-badge-${badge}`}>{badge}</span>
                        </div>
                        <div className="admin-user-card-meta">
                          <span>Joined {formatShortWhen(u.created_at)}</span>
                          <span>{emailDisplay(u)}</span>
                          <span>{verifiedLabel(u)}</span>
                          <span className="admin-user-card-chevron" aria-hidden>
                            {open ? "▴" : "▾"}
                          </span>
                        </div>
                      </button>

                      {open && (
                        <div className="admin-user-card-detail">
                          <dl className="admin-detail-grid">
                            <div>
                              <dt>Email</dt>
                              <dd>{emailDisplay(u)}</dd>
                            </div>
                            <div>
                              <dt>Phone</dt>
                              <dd>
                                {u.phone
                                  ? u.is_phone_verified
                                    ? u.phone
                                    : `${u.phone} (unverified)`
                                  : "-"}
                              </dd>
                            </div>
                            <div>
                              <dt>Joined</dt>
                              <dd>{formatWhen(u.created_at)}</dd>
                            </div>
                            <div>
                              <dt>Verified</dt>
                              <dd>{verifiedLabel(u)}</dd>
                            </div>
                          </dl>

                          <div className="admin-user-card-actions">
                            <Link
                              className="admin-btn admin-btn-ghost admin-btn-tiny"
                              to={`/u/${encodeURIComponent(u.username)}`}
                            >
                              Open profile
                            </Link>
                            {protectedBlue ? (
                              <span className="admin-protected">Protected founder</span>
                            ) : (
                              <>
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
                                <button
                                  type="button"
                                  className="admin-btn admin-btn-danger admin-btn-tiny"
                                  disabled={deletingId === `user:${u.id}`}
                                  onClick={() => handleDeleteUser(u)}
                                >
                                  {deletingId === `user:${u.id}` ? "Deleting…" : "Delete"}
                                </button>
                              </>
                            )}
                          </div>
                        </div>
                      )}
                    </li>
                  );
                })}
              </ul>
            )}
          </section>
        </div>
      )}

      {tab === "engage" && (
        <div className="admin-tab-panel">
          <section className="admin-compose admin-engage" aria-labelledby="admin-engage-title">
            <div className="admin-engage-head">
              <div>
                <h2 id="admin-engage-title">Comment on new users</h2>
                <p className="admin-lead">
                  Auto-replies: one human voice per post (@baratx or @sharath), content-aware -
                  bug reports get support questions, not growth-bait. Use this tab for an extra
                  manual comment when you want.
                </p>
                <p className="admin-lead">
                  <button
                    type="button"
                    className="admin-btn admin-btn-danger"
                    disabled={busy}
                    onClick={async () => {
                      if (
                        !window.confirm(
                          "Delete all @baratx / @sharath auto-replies on posts? Digests (posts) stay."
                        )
                      ) {
                        return;
                      }
                      setBusy(true);
                      setError("");
                      setMsg("");
                      try {
                        const res = await adminApi.purgeEngageSlop(secret, false);
                        setMsg(`Purged ${res.deleted ?? 0} official engage replies`);
                        load(secret);
                      } catch (err) {
                        setError(err.message || "Could not purge engage replies");
                      } finally {
                        setBusy(false);
                      }
                    }}
                  >
                    Delete bot auto-replies
                  </button>
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
                        maxLength={500}
                        rows={3}
                        placeholder={`Comment as @${replyAs}… type @ to tag`}
                        required
                      />
                      <div className="admin-compose-footer">
                        <span className="admin-char-count">{draftText.length}/500</span>
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
        </div>
      )}

      {tab === "post" && (
        <div className="admin-tab-panel">
          <section className="admin-compose" aria-labelledby="admin-compose-title">
            <h2 id="admin-compose-title">Post as BarathX</h2>
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
        </div>
      )}

      {tab === "payouts" && (
        <div className="admin-tab-panel">
          {founding && (
            <section className="admin-compose" aria-labelledby="admin-founding-title">
              <h2 id="admin-founding-title">Founding {founding.cap}. UPI payouts</h2>
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
                          <tr key={r.id} className={r.status === "payable" ? "admin-row-attention" : undefined}>
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
                                      ? "Bar not met yet, only pay after review if intentional"
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
              <h2 id="admin-race-title">Square Race, biweekly likes</h2>
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
                          <td>₹{row.prize_inr || "-"}</td>
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
                          <tr key={r.id} className={r.status === "payable" ? "admin-row-attention" : undefined}>
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

          {!founding && !race && !busy && (
            <p className="admin-empty-inline">Payout data unavailable. Try Refresh.</p>
          )}
        </div>
      )}

      {tab === "tools" && (
        <div className="admin-tab-panel">
          <section className="admin-compose" aria-labelledby="admin-tools-title">
            <h2 id="admin-tools-title">Ops tools</h2>
            <p className="admin-lead">One-shot jobs. Results show in the green message above.</p>
            <div className="admin-tools-grid">
              <button
                type="button"
                className="admin-tool-card"
                onClick={async () => {
                  setBusy(true);
                  setError("");
                  setMsg("");
                  try {
                    const res = await adminApi.refreshPrompts(secret, true);
                    setMsg(
                      `Prompts refreshed, created ${res.created || 0}, skipped ${res.skipped || 0}`
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
                <strong>Refresh debate prompts</strong>
                <span>Pull / regenerate arena debate prompts</span>
              </button>

              <button
                type="button"
                className="admin-tool-card"
                onClick={async () => {
                  setBusy(true);
                  setError("");
                  setMsg("");
                  try {
                    const res = await adminApi.dailyDigest(secret, true);
                    if (res.skipped) {
                      setMsg(
                        `Peak digest skipped, ${res.reason || "already posted"} (${res.slot || "slot"})`
                      );
                    } else {
                      const arenas = (res.pairs || res.posts || [])
                        .map((p) => p.arena)
                        .filter(Boolean)
                        .join(", ");
                      setMsg(
                        `Peak digest · ${res.slot || "slot"}, ${res.created_pairs || 0} topic pair(s)` +
                          ` (${res.created || 0} posts)` +
                          (arenas ? ` · ${arenas}` : "") +
                          " · @baratx + @sharath replies + likes"
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
                <strong>Run peak digest now</strong>
                <span>Force the multi-arena digest slot</span>
              </button>

              <button
                type="button"
                className="admin-tool-card"
                onClick={async () => {
                  setBusy(true);
                  setError("");
                  setMsg("");
                  try {
                    const res = await adminApi.instagramCarousel(secret, "evening");
                    setMsg(
                      `Instagram carousel posted` +
                        (res.media_id ? ` · media ${res.media_id}` : "") +
                        ` (@getbaratx)`
                    );
                  } catch (err) {
                    setError(err.message || "Instagram publish failed");
                  } finally {
                    setBusy(false);
                  }
                }}
                disabled={busy}
              >
                <strong>Post IG carousel now</strong>
                <span>Publish evening pack to @getbaratx</span>
              </button>
            </div>
          </section>
        </div>
      )}
    </div>
  );
}
