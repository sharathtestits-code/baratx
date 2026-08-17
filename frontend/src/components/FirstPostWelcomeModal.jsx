import { useEffect } from "react";
import { Link } from "react-router-dom";
import { createPortal } from "react-dom";
import Logo from "./Logo";

const STORAGE_KEY = "bx_early_welcome_seen";

export function shouldShowFirstPostWelcome() {
  try {
    return localStorage.getItem(STORAGE_KEY) !== "1";
  } catch {
    return true;
  }
}

export function markFirstPostWelcomeSeen() {
  try {
    localStorage.setItem(STORAGE_KEY, "1");
  } catch {
    /* ignore */
  }
}

/**
 * New-user popup: post your first take, where to post, early-user welcome + surprise gift.
 */
export default function FirstPostWelcomeModal({ open, onShowWhere, onWriteHere, onDismiss }) {
  useEffect(() => {
    if (!open) return;
    function onKey(e) {
      if (e.key === "Escape") onDismiss?.();
    }
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, [open, onDismiss]);

  if (!open || typeof document === "undefined") return null;

  return createPortal(
    <div
      className="modal-backdrop first-post-welcome-backdrop"
      onClick={onDismiss}
      role="presentation"
    >
      <div
        className="modal-card first-post-welcome"
        role="dialog"
        aria-modal="true"
        aria-labelledby="first-post-welcome-title"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="modal-header">
          <div className="first-post-welcome-brand">
            <Logo variant="mark" className="first-post-welcome-logo" />
            <h2 id="first-post-welcome-title">Post your first take</h2>
          </div>
          <button type="button" className="modal-close" onClick={onDismiss} aria-label="Close">
            ×
          </button>
        </div>

        <div className="first-post-welcome-body">
          <p className="first-post-welcome-lead">
            Welcome to BarathX. India&apos;s public square. Your first post goes in{" "}
            <strong>The Square</strong>: the compose box at the top of the home feed.
          </p>

          <div className="first-post-welcome-where" aria-hidden="true">
            <div className="first-post-welcome-fake-compose">
              <span className="first-post-welcome-fake-avatar" />
              <span className="first-post-welcome-fake-line">What&apos;s your take?</span>
              <span className="first-post-welcome-fake-post">Post</span>
            </div>
            <p className="first-post-welcome-where-label">That&apos;s where you post → Square</p>
          </div>

          <div className="first-post-welcome-perk">
            <p className="first-post-welcome-perk-title">Early members (first 100–1,000)</p>
            <ul>
              <li>
                A <strong>welcome reply</strong> from BarathX admin and the founder on your first
                take
              </li>
              <li>
                A <strong>surprise gift</strong>, details revealed later
              </li>
            </ul>
            <p className="first-post-welcome-tc">
              Limited early-member offer. Eligibility and fulfilment may change.{" "}
              <strong>T&amp;Cs apply</strong>. See{" "}
              <Link to="/terms" onClick={onDismiss}>
                Terms
              </Link>
              .
            </p>
          </div>

          <div className="first-post-welcome-actions">
            <button type="button" className="btn btn-primary" onClick={onShowWhere}>
              Show me where to post
            </button>
            <button type="button" className="btn btn-secondary" onClick={onWriteHere}>
              Write my first take here
            </button>
          </div>
        </div>
      </div>
    </div>,
    document.body
  );
}
