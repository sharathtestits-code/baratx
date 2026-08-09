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
    id: "compose",
    target: "[data-coach='compose']",
    title: "Drop a take",
    body: "This is the Square. Write what you think — everyone can see it on For you.",
    path: "/feed",
  },
  {
    id: "square-nav",
    target: "[data-coach='nav-square']",
    title: "Square",
    body: "Your home feed. Takes from people you don’t follow still show under For you.",
    path: "/feed",
  },
  {
    id: "alerts",
    target: "[data-coach='nav-alerts']",
    title: "Alerts",
    body: "Replies and new posts land here. We’ll also email you so you can log back in.",
    path: "/notifications",
  },
  {
    id: "arenas",
    target: "[data-coach='nav-arenas']",
    title: "Arenas",
    body: "Pick a side on Sports, Politics, Startups, and more. Live rooms sit next door.",
    path: "/arenas",
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
