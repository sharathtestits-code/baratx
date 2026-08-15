import { useCallback, useLayoutEffect, useState } from "react";
import { createPortal } from "react-dom";

/**
 * X / Facebook-style coach marks: spotlight the real UI + short tip card.
 * Primary action is Next / Got it — no “Skip tour” (that pattern trains people to ignore).
 * Tiny × dismisses the tip set (same as closing a Facebook tip).
 *
 * localStorage: bx_nav_tour_done=1
 */

const STEPS = [
  {
    id: "home",
    target: "[data-coach='nav-home']",
    title: "Home",
    body: "Your personal hub — continue arenas, see following activity, and peek at Live. Posting lives on Square.",
    path: "/home",
  },
  {
    id: "compose",
    target: "[data-coach='compose']",
    title: "Drop a take",
    body: "Start here — this is where you post on The Square. Early members (first 100–1,000) get a welcome reply from admin and the founder, plus a surprise gift revealed later (T&Cs apply).",
    path: "/feed",
  },
  {
    id: "square-nav",
    target: "[data-coach='nav-square']",
    title: "Square",
    body: "India's public feed. Use Square to post or read takes — including people you don’t follow (For you).",
    path: "/feed",
  },
  {
    id: "live",
    target: "[data-coach='nav-live']",
    title: "Live",
    body: "Open or join a room when the fight needs to happen now — sided debate, up to 15 voices, optional Live Talk audio.",
    path: "/spaces",
  },
  {
    id: "arenas",
    target: "[data-coach='nav-arenas']",
    title: "Arenas",
    body: "Pick a side on Sports, Politics, Entertainment, News, Spirituality, or Startups. Use Arenas when you want Agree/Disagree — not a group chat.",
    path: "/arenas",
  },
  {
    id: "you",
    target: "[data-coach='nav-you']",
    title: "You",
    body: "Your profile, settings, and appearance (themes). Alerts are in the top bell and the menu. Change look anytime under Settings → Appearance.",
    path: "/settings",
  },
];

const PAD = 8;

function markDone() {
  try {
    localStorage.setItem("bx_nav_tour_done", "1");
  } catch {
    /* ignore */
  }
}

export function shouldShowNavTour() {
  try {
    return localStorage.getItem("bx_nav_tour_done") !== "1";
  } catch {
    return false;
  }
}

export default function CoachMarks({ onDone }) {
  const [step, setStep] = useState(0);
  const [rect, setRect] = useState(null);
  const current = STEPS[step];
  const last = step >= STEPS.length - 1;

  const measure = useCallback(() => {
    const el = document.querySelector(current.target);
    if (!el) {
      setRect(null);
      return;
    }
    const r = el.getBoundingClientRect();
    setRect({
      top: r.top - PAD,
      left: r.left - PAD,
      width: r.width + PAD * 2,
      height: r.height + PAD * 2,
    });
    el.classList.add("coach-target-live");
    return () => el.classList.remove("coach-target-live");
  }, [current.target]);

  useLayoutEffect(() => {
    const cleanup = measure();
    window.addEventListener("resize", measure);
    window.addEventListener("scroll", measure, true);
    return () => {
      window.removeEventListener("resize", measure);
      window.removeEventListener("scroll", measure, true);
      if (typeof cleanup === "function") cleanup();
      document.querySelectorAll(".coach-target-live").forEach((n) => n.classList.remove("coach-target-live"));
    };
  }, [measure, step]);

  function finish() {
    markDone();
    onDone?.();
  }

  function next() {
    if (last) {
      finish();
      return;
    }
    setStep((s) => s + 1);
  }

  if (typeof document === "undefined") return null;

  const tipStyle = (() => {
    if (!rect) return { bottom: "5.5rem", left: "1rem", right: "1rem" };
    const spaceAbove = rect.top;
    const preferAbove = spaceAbove > 160;
    if (preferAbove) {
      return {
        top: Math.max(12, rect.top - 12),
        left: Math.min(Math.max(12, rect.left), window.innerWidth - 300),
        transform: "translateY(-100%)",
        maxWidth: "min(320px, calc(100vw - 24px))",
      };
    }
    return {
      top: rect.top + rect.height + 12,
      left: Math.min(Math.max(12, rect.left), window.innerWidth - 300),
      maxWidth: "min(320px, calc(100vw - 24px))",
    };
  })();

  return createPortal(
    <div className="coach-root" role="dialog" aria-modal="true" aria-labelledby="coach-title">
      <div className="coach-dim" aria-hidden="true">
        {rect ? (
          <div
            className="coach-hole"
            style={{
              top: rect.top,
              left: rect.left,
              width: rect.width,
              height: rect.height,
            }}
          />
        ) : null}
      </div>

      <div className="coach-tip" style={tipStyle}>
        <div className="coach-tip-top">
          <p className="coach-tip-progress">
            {step + 1}/{STEPS.length}
          </p>
          <button type="button" className="coach-tip-close" onClick={finish} aria-label="Close tip">
            ×
          </button>
        </div>
        <h2 id="coach-title" className="coach-tip-title">
          {current.title}
        </h2>
        <p className="coach-tip-body">{current.body}</p>
        <div className="coach-tip-dots" aria-hidden="true">
          {STEPS.map((s, i) => (
            <span key={s.id} className={`coach-dot${i === step ? " is-on" : ""}`} />
          ))}
        </div>
        <button type="button" className="btn btn-primary coach-tip-next" onClick={next}>
          {last ? "Got it" : "Next"}
        </button>
      </div>
    </div>,
    document.body
  );
}
