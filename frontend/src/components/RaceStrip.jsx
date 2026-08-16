import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { rewardsApi } from "../api";
import { useAuth } from "../context/AuthContext";

function daysLeft(endsAt) {
  if (!endsAt) return null;
  const ms = new Date(endsAt).getTime() - Date.now();
  if (ms <= 0) return 0;
  return Math.ceil(ms / 86400000);
}

/**
 * Biweekly Square Race strip, your likes vs leader; full board on /rewards.
 */
export default function RaceStrip() {
  const { token } = useAuth();
  const [race, setRace] = useState(null);

  useEffect(() => {
    if (!token) return undefined;
    let cancelled = false;
    rewardsApi
      .race(token)
      .then((data) => {
        if (!cancelled) setRace(data);
      })
      .catch(() => {});
    return () => {
      cancelled = true;
    };
  }, [token]);

  if (!race) return null;

  const left = daysLeft(race.ends_at);
  const leader = race.leader;
  const mine = race.my_best;

  return (
    <section className="race-strip" aria-label="Square Race">
      <div className="race-strip-head">
        <p className="race-strip-label">Square Race · every {race.cadence_days} days</p>
        <p className="race-strip-meta">{left == null ? "" : left === 0 ? "Ends today" : `${left}d left`}</p>
      </div>
      <p className="race-strip-body">
        Highest-liked Home post wins ₹{race.prize_min}–₹{race.prize_max}. You don’t score yourself -
        likes do.
      </p>
      {leader ? (
        <p className="race-strip-leader">
          Leading: @{leader.username} · {leader.like_count} likes · ~₹{leader.prize_inr}
          {mine
            ? mine.post_id === leader.post_id
              ? " · You’re #1"
              : ` · You: ${mine.like_count} likes${race.my_rank ? ` (#${race.my_rank})` : ""}`
            : " · You: not entered yet"}
        </p>
      ) : (
        <p className="race-strip-leader">
          No leader yet, need ≥{race.min_likes_to_win} likes.
          {mine ? ` You have ${mine.like_count}.` : ""}
        </p>
      )}
      <Link to="/rewards" className="founding-strip-link">
        Open scoreboard
      </Link>
    </section>
  );
}
