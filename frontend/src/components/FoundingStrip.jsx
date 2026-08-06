import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { rewardsApi } from "../api";
import { useAuth } from "../context/AuthContext";

/**
 * Quiet Founding 100 strip — floor action + community rating explained lightly.
 */
export default function FoundingStrip({ onPostProblem }) {
  const { token } = useAuth();
  const [status, setStatus] = useState(null);

  useEffect(() => {
    if (!token) return undefined;
    let cancelled = false;
    rewardsApi
      .founding(token)
      .then((data) => {
        if (!cancelled) setStatus(data);
      })
      .catch(() => {});
    return () => {
      cancelled = true;
    };
  }, [token]);

  if (!status) return null;

  if (status.my_status === "paid") {
    return (
      <section className="founding-strip founding-strip-done" aria-label="Founding reward">
        <p>Founding {status.cap} — ₹{status.amount_inr} paid via UPI. Thanks for posting something real.</p>
      </section>
    );
  }

  if (status.my_status === "payable") {
    return (
      <section className="founding-strip founding-strip-done" aria-label="Founding reward">
        <p>
          You’re payable for Founding {status.cap}. India already rated your post — ₹{status.amount_inr}{" "}
          UPI is next.
        </p>
      </section>
    );
  }

  if (status.my_status === "eligible") {
    const q = status.my_quality || {};
    const need =
      status.my_kind === "debate"
        ? `Need ${q.need_stances || 2} stances or ${q.need_posts || 3} debate posts (now ${q.stance_count || 0} / ${q.post_count || 0}).`
        : `Need ${q.need_likes || 3} likes or ${q.need_replies || 1} real reply (now ${q.like_count || 0} likes / ${q.reply_count || 0} replies).`;
    return (
      <section className="founding-strip" aria-label="Founding reward">
        <p className="founding-strip-label">Founding {status.cap} — almost</p>
        <p className="founding-strip-body">
          Floor cleared. Community rating decides payout: {need}
        </p>
      </section>
    );
  }

  if (!status.open || status.slots_remaining <= 0) return null;

  return (
    <section className="founding-strip" aria-label="Founding square">
      <p className="founding-strip-label">Founding {status.cap}</p>
      <p className="founding-strip-body">
        Post one real city problem (≥{status.min_problem_chars} chars), or open a debate in any arena.
        First {status.cap} get ₹{status.amount_inr} after India rates it with likes/replies —{" "}
        {status.slots_remaining} spots left.
      </p>
      <div className="founding-strip-actions">
        <button type="button" className="founding-strip-cta" onClick={() => onPostProblem?.()}>
          Post a real problem
        </button>
        <Link to="/arenas" className="founding-strip-link">
          Open a debate
        </Link>
      </div>
    </section>
  );
}
