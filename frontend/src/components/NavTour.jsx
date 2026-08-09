import { useState } from "react";
import { useNavigate } from "react-router-dom";

const STEPS = [
  {
    id: "square",
    title: "Square — For you",
    body: "Everyone’s takes show here. You don’t need to follow someone first.",
    cta: "Open Square",
    path: "/feed",
  },
  {
    id: "alerts",
    title: "Alerts",
    body: "When someone replies to you or posts, you’ll see it here — and we’ll email you so you can log back in.",
    cta: "Open Alerts",
    path: "/notifications",
  },
  {
    id: "arenas",
    title: "Arenas & Live",
    body: "Pick a side in Arenas, or jump into Live rooms. Menu (☰) switches floors anytime.",
    cta: "See Arenas",
    path: "/arenas",
  },
];

/**
 * Optional 3-step navigation tour after first session (or skip).
 * localStorage: bx_nav_tour_done=1
 */
export default function NavTour({ onDone }) {
  const navigate = useNavigate();
  const [step, setStep] = useState(0);
  const current = STEPS[step];
  const last = step >= STEPS.length - 1;

  function finish() {
    try {
      localStorage.setItem("bx_nav_tour_done", "1");
    } catch {
      /* ignore */
    }
    onDone?.();
  }

  function skipAll() {
    finish();
  }

  function next() {
    if (last) {
      finish();
      navigate(current.path);
      return;
    }
    setStep((s) => s + 1);
  }

  function goCta() {
    finish();
    navigate(current.path);
  }

  return (
    <section className="nav-tour" aria-labelledby="nav-tour-title">
      <p className="nav-tour-step">
        Tour {step + 1} of {STEPS.length}
      </p>
      <h2 id="nav-tour-title">{current.title}</h2>
      <p className="nav-tour-body">{current.body}</p>
      <div className="nav-tour-actions">
        <button type="button" className="btn btn-primary" onClick={goCta}>
          {current.cta}
        </button>
        <button type="button" className="btn btn-secondary" onClick={next}>
          {last ? "Done" : "Next"}
        </button>
        <button type="button" className="nav-tour-skip" onClick={skipAll}>
          Skip tour
        </button>
      </div>
    </section>
  );
}

export function shouldShowNavTour() {
  try {
    return localStorage.getItem("bx_nav_tour_done") !== "1";
  } catch {
    return false;
  }
}
