import { useEffect, useState } from "react";
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
];

const CITIES = ["Hyderabad", "Bangalore", "Delhi", "Mumbai", "Chennai", "Pune"];

const PROMPTS = [
  "What's one thing India gets wrong in public debate?",
  "Drop your hottest take on startups in India.",
  "Who should every BaratX user follow in your city?",
  "What should this public square never become?",
];

/**
 * Single first-session screen: arena → take → city → post.
 * Replaces stacked topics redirect + theme modal + welcome panel.
 */
export default function FirstSessionGuide({ token, onComplete }) {
  const [arena, setArena] = useState("politics");
  const [city, setCity] = useState("Hyderabad");
  const [text, setText] = useState(PROMPTS[0]);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    // Theme stays in Settings — don't stack a modal on first run.
    markThemeChosen();
  }, []);

  function applyPrompt(prompt) {
    setText(prompt);
  }

  async function submit(e) {
    e.preventDefault();
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
      await arenasApi.joinMany(token, [arena]).catch(() => {});
      markTopicOnboardingSeen();
      const body = city ? `Hello from ${city}.\n\n${text.trim()}` : text.trim();
      await postsApi.create(token, { text: body.slice(0, 500) });
      localStorage.setItem("bx_first_post_done", "1");
      sessionStorage.removeItem("bx_welcome");
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
    // Don't mark first post done — they can still use Starters later.
    onComplete?.({ skipped: true });
  }

  return (
    <section className="first-session" aria-labelledby="first-session-title">
      <div className="first-session-head">
        <Logo variant="mark" className="first-session-logo" />
        <div>
          <h2 id="first-session-title">Welcome to the Square</h2>
          <p className="first-session-step">1 of 1 · Get in</p>
        </div>
      </div>

      <form className="first-session-form" onSubmit={submit}>
        <div className="first-session-block">
          <p className="first-session-label">1 · Pick your arena</p>
          <div className="first-session-arenas" role="group" aria-label="Arenas">
            {ARENAS.map((a) => (
              <button
                key={a.key}
                type="button"
                className={`first-session-arena${arena === a.key ? " is-selected" : ""}`}
                aria-pressed={arena === a.key}
                onClick={() => setArena(a.key)}
              >
                {a.label}
              </button>
            ))}
          </div>
        </div>

        <div className="first-session-block">
          <p className="first-session-label">2 · Drop your first take</p>
          <textarea
            className="first-session-take"
            value={text}
            onChange={(e) => setText(e.target.value.slice(0, 500))}
            rows={4}
            maxLength={500}
            placeholder="What's your take?"
          />
          <div className="first-session-prompts">
            {PROMPTS.map((p) => (
              <button key={p} type="button" className="first-session-prompt" onClick={() => applyPrompt(p)}>
                {p}
              </button>
            ))}
          </div>
          <p className="hint first-session-count">{text.length}/500</p>
        </div>

        <div className="first-session-block">
          <p className="first-session-label">City (your base)</p>
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

        <button type="submit" className="btn btn-primary first-session-cta" disabled={busy || !text.trim()}>
          {busy ? "Entering…" : "Post & enter Square"}
        </button>
        <p className="first-session-founding">
          Founding ₹150 — open a live debate that gets real engagement. Details in Rewards after you
          enter.
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
