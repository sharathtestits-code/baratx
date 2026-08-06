import { useEffect, useState } from "react";
import { api } from "../api";

const CITIES = ["Hyderabad", "Bangalore", "Delhi", "Mumbai", "Chennai", "Pune"];

const PROMPTS = [
  "What’s one civic problem your city still pretends isn’t real?",
  "Drop your hottest take on public debate in India.",
  "Who should every BaratX user from your city follow?",
  "What should this public square never become?",
];

/**
 * Aggressive first-session panel: city chip → prompt → post, plus follow bootstrap.
 */
export default function WelcomePanel({ token, setText, onPostedFlag, composeRef }) {
  const [dismissed, setDismissed] = useState(
    () => localStorage.getItem("bx_first_post_done") === "1"
  );
  const [followBusy, setFollowBusy] = useState(false);
  const [followMsg, setFollowMsg] = useState("");
  const [followDone, setFollowDone] = useState(false);

  useEffect(() => {
    if (localStorage.getItem("bx_first_post_done") === "1") {
      setDismissed(true);
    }
  }, []);

  useEffect(() => {
    if (!onPostedFlag) return undefined;
    const handler = () => {
      localStorage.setItem("bx_first_post_done", "1");
      sessionStorage.removeItem("bx_welcome");
      setDismissed(true);
    };
    window.addEventListener("bx:first-post", handler);
    return () => window.removeEventListener("bx:first-post", handler);
  }, [onPostedFlag]);

  function applyCity(city) {
    setText(`Hello from ${city}. `);
    composeRef?.current?.focus();
  }

  function applyPrompt(prompt) {
    setText(prompt);
    composeRef?.current?.focus();
  }

  async function followOfficial() {
    setFollowBusy(true);
    setFollowMsg("");
    try {
      const res = await api.bootstrapFollows(token);
      setFollowMsg(res.message || "Following official BaratX accounts.");
      setFollowDone(true);
    } catch (err) {
      setFollowMsg(err.message || "Could not follow yet");
    } finally {
      setFollowBusy(false);
    }
  }

  function skip() {
    setDismissed(true);
    sessionStorage.removeItem("bx_welcome");
  }

  if (dismissed) return null;

  return (
    <div className="welcome-panel">
      <div className="welcome-panel-head">
        <div>
          <h2 className="welcome-title">Make your first post</h2>
          <p className="welcome-sub">
            Density starts with you. Pick a city or prompt, then hit Post above.
          </p>
        </div>
        <button type="button" className="welcome-skip" onClick={skip}>
          Later
        </button>
      </div>

      <div className="welcome-section">
        <div className="welcome-label">Your city</div>
        <div className="welcome-chips">
          {CITIES.map((city) => (
            <button key={city} type="button" className="welcome-chip" onClick={() => applyCity(city)}>
              {city}
            </button>
          ))}
        </div>
      </div>

      <div className="welcome-section">
        <div className="welcome-label">Or start from a prompt</div>
        <div className="welcome-chips welcome-chips-prompts">
          {PROMPTS.map((prompt) => (
            <button
              key={prompt}
              type="button"
              className="welcome-chip welcome-chip-prompt"
              onClick={() => applyPrompt(prompt)}
            >
              {prompt}
            </button>
          ))}
        </div>
      </div>

      <div className="welcome-follow">
        <button
          type="button"
          className="welcome-follow-btn"
          onClick={followOfficial}
          disabled={followBusy || followDone}
        >
          {followBusy ? "Following…" : followDone ? "Following official accounts" : "Follow official BaratX"}
        </button>
        {followMsg && <p className="hint welcome-follow-msg">{followMsg}</p>}
      </div>
    </div>
  );
}
