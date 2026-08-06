import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { rewardsApi } from "../api";
import { useAuth } from "../context/AuthContext";

/**
 * Quiet Founding 100 strip on Home — links to /rewards for full progress.
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
        <p>
          Founding {status.cap} — ₹{status.amount_inr} paid.{" "}
          <Link to="/rewards">See rewards</Link>
        </p>
      </section>
    );
  }

  if (status.my_status === "payable") {
    return (
      <section className="founding-strip founding-strip-done" aria-label="Founding reward">
        <p>
          You’re payable for Founding {status.cap} (₹{status.amount_inr}).{" "}
          <Link to="/rewards">Track payout</Link>
        </p>
      </section>
    );
  }

  if (status.my_status === "eligible") {
    const q = status.my_quality || {};
    const need =
      status.my_kind === "debate"
        ? `${q.stance_count || 0}/${q.need_stances || 2} stances · ${q.post_count || 0}/${q.need_posts || 3} posts`
        : `${q.like_count || 0}/${q.need_likes || 3} likes · ${q.reply_count || 0}/${q.need_replies || 1} replies`;
    return (
      <section className="founding-strip" aria-label="Founding reward">
        <p className="founding-strip-label">Founding {status.cap} — waiting on India</p>
        <p className="founding-strip-body">
          Floor cleared. Rating progress: {need}.{" "}
          <Link to="/rewards">Full progress</Link>
        </p>
      </section>
    );
  }

  if (!status.open || status.slots_remaining <= 0) return null;

  return (
    <section className="founding-strip" aria-label="Founding square">
      <p className="founding-strip-label">Founding {status.cap}</p>
      <p className="founding-strip-body">
        Post one real city problem or open any arena debate. First {status.cap} get ₹
        {status.amount_inr} after likes/replies — {status.slots_remaining} spots left.
      </p>
      <div className="founding-strip-actions">
        <button type="button" className="founding-strip-cta" onClick={() => onPostProblem?.()}>
          Post a real problem
        </button>
        <Link to="/rewards" className="founding-strip-link">
          How progress works
        </Link>
      </div>
    </section>
  );
}
