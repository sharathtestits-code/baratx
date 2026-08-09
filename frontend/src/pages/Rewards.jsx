import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { rewardsApi } from "../api";
import { useAuth } from "../context/AuthContext";
import { canManageBadges } from "../components/OfficialBadge";

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

/**
 * User progress page — see your Founding status + Square Race rank.
 * Blue accounts also get a read-only ops queue (payouts stay on /admin).
 */
export default function Rewards() {
  const { token, user } = useAuth();
  const [founding, setFounding] = useState(null);
  const [race, setRace] = useState(null);
  const [ops, setOps] = useState(null);
  const [error, setError] = useState("");
  const isBlue = canManageBadges(user);

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

    if (isBlue) {
      rewardsApi
        .ops(token)
        .then((data) => {
          if (!cancelled) setOps(data);
        })
        .catch(() => {
          /* non-blue or misconfigured — ignore */
        });
    }
    return () => {
      cancelled = true;
    };
  }, [token, isBlue]);

  if (!user) {
    return (
      <div className="feed-wrap surface-page">
        <p className="hint">
          <Link to="/login">Log in</Link> to track Founding 100 and Square Race progress.
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
        You don’t rate yourself. India rates with likes and replies — this page shows your progress.
      </p>
      {error && <div className="error">{error}</div>}

      {founding && (
        <section className="rewards-card" aria-labelledby="founding-progress-title">
          <h2 id="founding-progress-title">Founding {founding.cap} · ₹{founding.amount_inr}</h2>
          <p className="rewards-card-sub">
            First {founding.cap} people · {founding.slots_remaining} spots left. One payout per person.
          </p>
          <ol className="rewards-steps">
            <Step
              done={!!status}
              current={!status && founding.open}
              label="1. Floor — do one real action"
              detail="Post a civic problem (≥50 chars + checkbox) or open any arena debate."
            />
            <Step
              done={status === "payable" || status === "paid"}
              current={status === "eligible"}
              label="2. Community rating"
              detail={
                status === "eligible"
                  ? founding.my_kind === "debate"
                    ? `Need ${q.need_stances || 2} stances or ${q.need_posts || 3} posts — now ${q.stance_count || 0} / ${q.post_count || 0}.`
                    : `Need ${q.need_likes || 25} likes or ${q.need_replies || 5} replies — now ${q.like_count || 0} likes / ${q.reply_count || 0} replies.`
                  : `≥${founding.eval?.min_likes || 25} likes or ≥${founding.eval?.min_replies || 5} human replies (official welcome doesn’t count).`
              }
            />
            <Step
              done={status === "paid"}
              current={status === "payable"}
              label="3. UPI payout"
              detail={
                status === "paid"
                  ? "Paid — you’re in."
                  : status === "payable"
                    ? "You’re on the payable list. BarathX sends ₹150 via UPI."
                    : "Admin pays after the rating bar is met."
              }
            />
          </ol>
          {!status && founding.open && (
            <div className="rewards-actions">
              <Link to="/feed" className="founding-strip-cta">
                Post a problem
              </Link>
              <Link to="/arenas" className="founding-strip-link">
                Open a debate
              </Link>
            </div>
          )}
          {status && (
            <p className="rewards-status-pill">
              Your status: <strong>{status}</strong>
              {founding.my_kind ? ` · ${founding.my_kind}` : ""}
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
            Every {race.cadence_days} days. Highest-liked Home post wins. Likes = the scoreboard.
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
                <Link to="/feed">Post on Home</Link> to enter.
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
              {race.leaderboard.slice(0, 10).map((row, i) => (
                <li key={row.post_id} className={row.username === user.username ? "is-you" : ""}>
                  <span className="rewards-board-rank">#{i + 1}</span>
                  <span className="rewards-board-user">
                    <Link to={`/u/${row.username}`}>@{row.username}</Link>
                    {row.username === user.username ? " · you" : ""}
                  </span>
                  <span className="rewards-board-likes">{row.like_count} likes</span>
                  <span className="rewards-board-prize">
                    {row.prize_inr ? `₹${row.prize_inr}` : "—"}
                  </span>
                </li>
              ))}
            </ol>
          )}
        </section>
      )}

      {isBlue && (
        <section className="rewards-card rewards-ops" aria-labelledby="ops-title">
          <h2 id="ops-title">Blue ops view (read-only)</h2>
          <p className="rewards-card-sub">
            Review who cleared the floor and who’s leading the race.{" "}
            <strong>Mark paid / lock winner</strong> stays on{" "}
            <Link to="/admin">/admin</Link> with the admin secret (money actions).
          </p>
          {!ops && <p className="hint">Loading ops queue…</p>}
          {ops && (
            <>
              <h3 className="admin-subhead">
                Founding queue · {ops.founding.payable_count || 0} payable ·{" "}
                {ops.founding.eligible_count} waiting on rating
              </h3>
              {(ops.founding.rewards || []).length === 0 ? (
                <p className="admin-empty-inline">No Founding entries yet.</p>
              ) : (
                <ul className="rewards-ops-list">
                  {ops.founding.rewards.slice(0, 25).map((r) => {
                    const qrow = r.quality || {};
                    const rating =
                      r.kind === "debate"
                        ? `${qrow.stance_count ?? 0} stances · ${qrow.post_count ?? 0} posts`
                        : `${qrow.like_count ?? 0} likes · ${qrow.reply_count ?? 0} replies`;
                    return (
                      <li key={r.id}>
                        <Link to={`/u/${r.username}`}>@{r.username}</Link> · {r.kind} ·{" "}
                        <strong>{r.status}</strong> · {rating}
                      </li>
                    );
                  })}
                </ul>
              )}
              <h3 className="admin-subhead">Race top right now</h3>
              <ul className="rewards-ops-list">
                {(ops.race.leaderboard || []).slice(0, 8).map((row, i) => (
                  <li key={row.post_id}>
                    #{i + 1} @{row.username} · {row.like_count} likes · ₹{row.prize_inr || "—"}
                  </li>
                ))}
              </ul>
            </>
          )}
        </section>
      )}
    </div>
  );
}
