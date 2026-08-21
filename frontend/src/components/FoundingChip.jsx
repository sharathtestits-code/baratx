import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { rewardsApi } from "../api";
import { useAuth } from "../context/AuthContext";

/**
 * Compact Founding 100 chip for Square home header, membership, not a coupon.
 */
export default function FoundingChip({ refreshKey = 0 }) {
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
  }, [token, refreshKey]);

  if (!status) return null;

  if (status.my_status === "paid") {
    return (
      <Link to="/rewards" className="founding-chip founding-chip-done" aria-label="Founding membership, thank-you sent">
        <span className="founding-chip-star" aria-hidden="true">
          ★
        </span>
        <span>Founding {status.cap}</span>
        <span className="founding-chip-sep" aria-hidden="true">
          ·
        </span>
        <span>You&apos;re in</span>
      </Link>
    );
  }

  if (status.my_status === "payable") {
    return (
      <Link to="/rewards" className="founding-chip founding-chip-done" aria-label="Founding membership, you're in">
        <span className="founding-chip-star" aria-hidden="true">
          ★
        </span>
        <span>Founding {status.cap}</span>
        <span className="founding-chip-sep" aria-hidden="true">
          ·
        </span>
        <span>You&apos;re in</span>
      </Link>
    );
  }

  if (status.my_status === "eligible") {
    const q = status.my_quality || {};
    const progress =
      status.my_kind === "debate"
        ? `${q.stance_count || 0}/${q.need_stances || 2} stances`
        : `${q.like_count || 0}/${q.need_likes || 25} likes`;
    return (
      <Link to="/rewards" className="founding-chip" aria-label="Founding membership progress">
        <span className="founding-chip-star" aria-hidden="true">
          ★
        </span>
        <span>Founding {status.cap}</span>
        <span className="founding-chip-sep" aria-hidden="true">
          ·
        </span>
        <span>{progress}</span>
      </Link>
    );
  }

  if (!status.open || status.slots_remaining <= 0) return null;

  return (
    <Link to="/rewards" className="founding-chip" aria-label="Founding membership">
      <span className="founding-chip-star" aria-hidden="true">
        ★
      </span>
      <span>Founding {status.cap}</span>
      <span className="founding-chip-sep" aria-hidden="true">
        ·
      </span>
        <span>{status.slots_remaining} left · earn with quality</span>
    </Link>
  );
}
