import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { rewardsApi } from "../api";
import { useAuth } from "../context/AuthContext";

function Step({ done, current, label, detail }) {
  return (
    <li className={`rewards-step${done ? " is-done" : ""}${current ? " is-current" : ""}`}>
      <span className="rewards-step-dot" aria-hidden="true" />
      <div>
        <div className="rewards-step-label">{label}</div>
        {detail && <div className="rewards-step-detail">{detail}</div>}
      </div>
    </li>
  );
}

function daysLeft(endsAt) {
  if (!endsAt) return null;
  const ms = new Date(endsAt).getTime() - Date.now();
  if (ms <= 0) return 0;
  return Math.ceil(ms / 86400000);
}

/** One row per author, mirrors backend race_leaderboard dedupe. */
function dedupeRaceRows(rows) {
  const best = new Map();
  for (const row of rows || []) {
    const key = row.author_id || row.username;
    if (!key) continue;
    const prev = best.get(key);
    if (!prev || (row.like_count || 0) > (prev.like_count || 0)) {
      best.set(key, row);
    }
  }
  return Array.from(best.values()).sort((a, b) => (b.like_count || 0) - (a.like_count || 0));
}

/**
 * User progress page. Founding status + Square Race rank.
 * No links to the private ops console (owner opens that URL directly).
 */
export default function Rewards() {
  const { token, user } = useAuth();
  const [founding, setFounding] = useState(null);
  const [race, setRace] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!token) return undefined;
    let cancelled = false;
    Promise.all([rewardsApi.founding(token), rewardsApi.race(token)])
      .then(([f, r]) => {
        if (cancelled) return;
        setFounding(f);
        setRace(r);
      })
      .catch((err) => {
        if (!cancelled) setError(err.message || "Could not load rewards");
      });
    return () => {
      cancelled = true;
    };
  }, [token]);

  if (!user) {
    return (
      <div className="feed-wrap surface-page">
        <p className="hint">
          <Link to="/login">Log in</Link> to track Founding membership and Square Race progress.
        </p>
      </div>
    );
  }

  const q = founding?.my_quality || {};
  const status = founding?.my_status;
  const left = daysLeft(race?.ends_at);

  return (
    <div className="feed-wrap surface-page rewards-page">
      <header className="feed-topbar">
        <h1 className="feed-title">Rewards</h1>
      </header>
      <p className="hint surface-lead rewards-lead">
        You don’t rate yourself. India rates with likes and replies, this page shows your progress.
      </p>
      {error && <div className="error">{error}</div>}

      {founding && (
        <section className="rewards-card" aria-labelledby="founding-progress-title">
          <h2 id="founding-progress-title">Founding {founding.cap}</h2>
          <p className="rewards-card-sub">
            {founding.cap} Founding spots, earned by opening a debate that gets real engagement, not
            by signing up. {founding.slots_remaining} left.
          </p>
          {(status === "payable" || status === "paid") && founding.amount_inr != null && (
            <p className="hint ok-hint rewards-surprise">
              {status === "paid"
                ? `You're in. Thank-you sent, ₹${founding.amount_inr}, no strings.`
                : `You're in. Small thank-you on the way, ₹${founding.amount_inr}, no strings.`}
            </p>
          )}
          <ol className="rewards-steps">
            <Step
              done={!!status}
              current={!status && founding.open}
              label="1. Floor, do one real action"
              detail="Post a civic problem (≥50 chars + checkbox) or open any arena debate."
            />
            <Step
              done={status === "payable" || status === "paid"}
              current={status === "eligible"}
              label="2. Community rating"
              detail={
                status === "eligible"
                  ? founding.my_kind === "debate"
                    ? `Need ${q.need_stances || 2} stances or ${q.need_posts || 3} posts, now ${q.stance_count || 0} / ${q.post_count || 0}.`
                    : `Need ${q.need_likes || 25} likes or ${q.need_replies || 5} replies, now ${q.like_count || 0} likes / ${q.reply_count || 0} replies.`
                  : `Real engagement from people who aren’t official accounts, likes, replies, or debate stances.`
              }
            />
            {(status === "payable" || status === "paid") && (
              <Step
                done={status === "paid"}
                current={status === "payable"}
                label="3. You're in"
                detail={
                  status === "paid"
                    ? `Thank-you sent, ₹${founding.amount_inr}, no strings.`
                    : `Small thank-you on the way, ₹${founding.amount_inr}, no strings.`
                }
              />
            )}
          </ol>
          {!status && founding.open && (
            <div className="rewards-actions">
              <Link to="/feed?civic=1" className="founding-strip-cta">
                Post a problem
              </Link>
              <Link to="/arenas" className="founding-strip-link">
                Open a debate
              </Link>
            </div>
          )}
          {status && (
            <p className="rewards-status-pill" data-status={status}>
              Floor cleared · status: <strong>{status}</strong>
              {founding.my_kind ? ` · ${founding.my_kind}` : ""}
            </p>
          )}
          {!status && founding.open && (
            <p className="hint rewards-floor-hint">
              Floor stays open until you post a civic problem (≥50 characters with the checkbox) or start an arena debate.
            </p>
          )}
        </section>
      )}

      {race && (
        <section className="rewards-card" aria-labelledby="race-progress-title">
          <div className="race-strip-head">
            <h2 id="race-progress-title">Square Race · ₹{race.prize_min}–₹{race.prize_max}</h2>
            <p className="race-strip-meta">
              {left == null ? "" : left === 0 ? "Ends today" : `${left}d left`}
            </p>
          </div>
          <p className="rewards-card-sub">
            Every {race.cadence_days} days. Highest-liked Home post wins. Likes = the scoreboard. One entry per person.
          </p>
          <div className="rewards-my-race">
            {race.my_best ? (
              <p>
                Your best this period: <strong>{race.my_best.like_count} likes</strong>
                {race.my_rank ? ` · rank #${race.my_rank}` : ""}
                {race.my_best.prize_inr
                  ? ` · ~₹${race.my_best.prize_inr} if you win`
                  : ` · need ≥${race.min_likes_to_win} likes to qualify`}
              </p>
            ) : (
              <p>
                You have no Home post in this race yet.{" "}
                <Link to="/feed">Post on Square</Link> to enter.
              </p>
            )}
            {race.leader && (
              <p className="admin-muted">
                Leader: @{race.leader.username} · {race.leader.like_count} likes · ~₹
                {race.leader.prize_inr}
              </p>
            )}
          </div>
          {(race.leaderboard || []).length > 0 && (
            <ol className="rewards-board">
              {dedupeRaceRows(race.leaderboard)
                .slice(0, 10)
                .map((row, i) => (
                <li key={row.post_id || `${row.author_id}-${i}`} className={row.username === user.username ? "is-you" : ""}>
                  <span className="rewards-board-rank">#{i + 1}</span>
                  <span className="rewards-board-user">
                    <Link to={`/u/${row.username}`}>@{row.username}</Link>
                    {row.username === user.username ? " · you" : ""}
                  </span>
                  <span className="rewards-board-likes">{row.like_count} likes</span>
                  <span className="rewards-board-prize">
                    {row.prize_inr ? `₹${row.prize_inr}` : "-"}
                  </span>
                </li>
              ))}
            </ol>
          )}
        </section>
      )}
    </div>
  );
}
