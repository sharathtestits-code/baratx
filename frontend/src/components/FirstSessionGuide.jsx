import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { api, arenasApi, postsApi } from "../api";
import { markTopicOnboardingSeen } from "../topicsOnboarding";
import { markThemeChosen } from "../theme";
import Logo from "./Logo";

const ARENAS = [
  { key: "sports", label: "Sports" },
  { key: "politics", label: "Politics" },
  { key: "entertainment", label: "Entertainment" },
  { key: "news", label: "News" },
  { key: "spirituality", label: "Spirituality" },
  { key: "startups", label: "Startups" },
  { key: "campus-careers", label: "Campus & Careers" },
  { key: "builders", label: "Builders" },
];

const CITIES = ["Hyderabad", "Bangalore", "Delhi", "Mumbai", "Chennai", "Pune"];

const STANCES = [
  { id: "for", label: "Agree" },
  { id: "against", label: "Disagree" },
  { id: "depends", label: "It depends" },
];

const PROMPTS = [
  "What's one thing India gets wrong in public debate?",
  "Drop your hottest take on startups in India.",
  "Who should every BarathX user follow in your city?",
  "What should this public square never become?",
];

function readLandingTake() {
  try {
    const raw = sessionStorage.getItem("bx_landing_take");
    if (!raw) return null;
    const parsed = JSON.parse(raw);
    if (!parsed?.stance) return null;
    return parsed;
  } catch {
    return null;
  }
}

/**
 * First-session guarantee: side → take → city → post (human reply path stays on backend).
 */
export default function FirstSessionGuide({ token, onComplete }) {
  const landing = useMemo(() => readLandingTake(), []);
  const [arena, setArena] = useState("politics");
  const [stance, setStance] = useState(landing?.stance || "");
  const [city, setCity] = useState("Hyderabad");
  const [text, setText] = useState(() => {
    if (landing?.question && landing?.stance) {
      const label = STANCES.find((s) => s.id === landing.stance)?.label || landing.stance;
      return `On “${landing.question}” — I ${label.toLowerCase()} because `;
    }
    return "";
  });
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    markThemeChosen();
  }, []);

  function applyPrompt(prompt) {
    setText(prompt);
    setError("");
    window.requestAnimationFrame(() => {
      document.querySelector(".first-session-cta")?.scrollIntoView({
        behavior: "smooth",
        block: "center",
      });
    });
  }

  function pickArena(key) {
    setArena(key);
    setError("");
    window.requestAnimationFrame(() => {
      document.getElementById("first-session-stance-block")?.scrollIntoView({
        behavior: "smooth",
        block: "start",
      });
    });
  }

  function pickStance(id) {
    setStance(id);
    setError("");
    window.requestAnimationFrame(() => {
      document.querySelector(".first-session-take")?.focus?.();
      document.getElementById("first-session-take-block")?.scrollIntoView({
        behavior: "smooth",
        block: "start",
      });
    });
  }

  async function submit(e) {
    e.preventDefault();
    if (!stance) {
      setError("Pick Agree, Disagree, or It depends first.");
      return;
    }
    if (!text.trim()) {
      setError("Write your first take.");
      return;
    }
    if (!arena) {
      setError("Pick an arena.");
      return;
    }
    setBusy(true);
    setError("");
    try {
      const joins = [arena];
      if (city) joins.push("my-city");
      await arenasApi.joinMany(token, joins).catch(() => {});
      markTopicOnboardingSeen();
      const sideLabel = STANCES.find((s) => s.id === stance)?.label || stance;
      const body = [
        city ? `Hello from ${city}.` : "",
        `Side: ${sideLabel}.`,
        text.trim(),
      ]
        .filter(Boolean)
        .join("\n\n");
      await postsApi.create(token, { text: body.slice(0, 500) });
      localStorage.setItem("bx_first_post_done", "1");
      sessionStorage.removeItem("bx_welcome");
      sessionStorage.removeItem("bx_landing_take");
      api.bootstrapFollows(token).catch(() => {});
      window.dispatchEvent(new CustomEvent("bx:first-post"));
      onComplete?.();
    } catch (err) {
      setError(err.message || "Could not post yet");
    } finally {
      setBusy(false);
    }
  }

  function skip() {
    markTopicOnboardingSeen();
    markThemeChosen();
    sessionStorage.removeItem("bx_welcome");
    onComplete?.({ skipped: true });
  }

  return (
    <section className="first-session" aria-labelledby="first-session-title">
      <div className="first-session-head">
        <Logo variant="mark" className="first-session-logo" />
        <div>
          <h2 id="first-session-title">You&apos;re in. Take a side, then your take.</h2>
          <p className="first-session-step">Step 1 of 2 · Side + first take (then a quick nav tour)</p>
        </div>
      </div>

      {landing?.question ? (
        <p className="first-session-landing-echo hint">
          You picked a side on: <em>{landing.question}</em>
        </p>
      ) : null}

      <form className="first-session-form" onSubmit={submit}>
        <div className="first-session-block">
          <p className="first-session-label">1 · Pick your arena or Circle</p>
          <div className="first-session-arenas" role="group" aria-label="Arenas">
            {ARENAS.map((a) => (
              <button
                key={a.key}
                type="button"
                className={`first-session-arena${arena === a.key ? " is-selected" : ""}`}
                aria-pressed={arena === a.key}
                onClick={() => pickArena(a.key)}
              >
                {a.label}
              </button>
            ))}
          </div>
        </div>

        <div className="first-session-block" id="first-session-stance-block">
          <p className="first-session-label">2 · Pick your side</p>
          <div className="first-session-stances" role="group" aria-label="Stance">
            {STANCES.map((s) => (
              <button
                key={s.id}
                type="button"
                className={`first-session-stance${stance === s.id ? " is-selected" : ""}`}
                aria-pressed={stance === s.id}
                onClick={() => pickStance(s.id)}
              >
                {s.label}
              </button>
            ))}
          </div>
        </div>

        <div className="first-session-block" id="first-session-take-block">
          <p className="first-session-label">3 · Drop your first take</p>
          <textarea
            className="first-session-take"
            value={text}
            onChange={(e) => {
              setText(e.target.value.slice(0, 500));
              setError("");
            }}
            rows={4}
            maxLength={500}
            placeholder={PROMPTS[0]}
            aria-label="Your first take"
            disabled={!stance}
          />
          <p className="hint first-session-prompts-label">Or tap a starter take:</p>
          <div className="first-session-prompts">
            {PROMPTS.map((p) => (
              <button
                key={p}
                type="button"
                className={`first-session-prompt${text === p ? " is-selected" : ""}`}
                onClick={() => applyPrompt(p)}
                disabled={!stance}
              >
                {p}
              </button>
            ))}
          </div>
          <p className="hint first-session-count">{text.length}/500</p>
        </div>

        <div className="first-session-block">
          <p className="first-session-label">City (joins My City Circle)</p>
          <div className="first-session-cities">
            {CITIES.map((c) => (
              <button
                key={c}
                type="button"
                className={`first-session-city${city === c ? " is-selected" : ""}`}
                aria-pressed={city === c}
                onClick={() => setCity(c)}
              >
                {c}
              </button>
            ))}
          </div>
        </div>

        {error && <div className="error">{error}</div>}
        {!stance ? (
          <p className="hint first-session-next-hint">
            Pick <strong>Agree</strong>, <strong>Disagree</strong>, or <strong>It depends</strong>, then write your take.
          </p>
        ) : !text.trim() ? (
          <p className="hint first-session-next-hint">
            Tap a starter take above (or write your own), then <strong>Post &amp; enter</strong>.
          </p>
        ) : (
          <p className="hint first-session-next-hint">Ready, tap <strong>Post &amp; enter</strong> below.</p>
        )}

        <button
          type="submit"
          className="btn btn-primary first-session-cta"
          disabled={busy || !stance || !text.trim()}
        >
          {busy ? "Entering…" : stance && text.trim() ? "Post & enter →" : "Pick a side and take"}
        </button>
        <p className="first-session-founding">
          Early members (first 100–1,000): welcome reply from admin and the founder on your first
          take, plus a surprise gift revealed later. T&amp;Cs apply. Separately: 100 Founding spots,
          earned by opening a debate that gets real engagement, not by signing up.
        </p>
        <p className="first-session-foot">
          <Link to="/settings" className="first-session-settings">
            Appearance later in Settings
          </Link>
          <button type="button" className="first-session-skip" onClick={skip}>
            Skip for now
          </button>
        </p>
      </form>
    </section>
  );
}
