import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { rewardsApi } from "../api";
import { useAuth } from "../context/AuthContext";

/**
 * Quiet Founding 100 strip — only when slots remain and user hasn’t earned yet.
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
  if (status.my_status === "eligible" || status.my_status === "paid") {
    return (
      <section className="founding-strip founding-strip-done" aria-label="Founding reward">
        <p>
          You’re in the Founding {status.cap}. We’ll send ₹{status.amount_inr} via UPI
          {status.my_status === "paid" ? " — paid." : " — you’re on the payout list."}
        </p>
      </section>
    );
  }
  if (!status.open || status.slots_remaining <= 0) return null;

  return (
    <section className="founding-strip" aria-label="Founding square">
      <p className="founding-strip-label">Founding {status.cap}</p>
      <p className="founding-strip-body">
        Post one real city or civic problem (≥{status.min_problem_chars} chars), or open one Politics /
        News debate. First {status.cap} people get ₹{status.amount_inr} via UPI — {status.slots_remaining}{" "}
        spots left.
      </p>
      <div className="founding-strip-actions">
        <button type="button" className="founding-strip-cta" onClick={() => onPostProblem?.()}>
          Post a real problem
        </button>
        <Link to="/arenas/politics" className="founding-strip-link">
          Open a debate
        </Link>
      </div>
    </section>
  );
}
