import { useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api";
import { useAuth } from "../context/AuthContext";
import Avatar from "./Avatar";
import { badgeNameClass } from "./OfficialBadge";

export const SUGGESTED_PEOPLE = [
  {
    display_name: "BaratX",
    username: "baratx",
    blurb: "Official blue — product updates & India conversation prompts",
    badge: "blue",
  },
  {
    display_name: "Sharath",
    username: "sharath",
    blurb: "Founder — building India’s public square",
    badge: "blue",
  },
  {
    display_name: "Bharat Voices",
    username: "bharatvoices",
    blurb: "Gold BaratX — culture, ideas, everyday India",
    badge: "gold",
  },
  {
    display_name: "India Tech Daily",
    username: "indiatech",
    blurb: "Gold BaratX — startups, policy & builders",
    badge: "gold",
  },
];

/**
 * Who-to-follow list with Follow buttons — shown on mobile feed/search
 * (right rail is desktop-only).
 */
export default function SuggestedFollows({ title = "Who to follow", note, dismissible = false }) {
  const { token, user } = useAuth();
  const [following, setFollowing] = useState({});
  const [busy, setBusy] = useState("");
  const [hidden, setHidden] = useState(
    () => dismissible && localStorage.getItem("bx_hide_suggested") === "1"
  );
  const [error, setError] = useState("");

  if (!token || hidden) return null;

  const people = SUGGESTED_PEOPLE.filter((p) => p.username !== user?.username);
  if (people.length === 0) return null;

  async function toggleFollow(username) {
    if (!token || busy) return;
    setBusy(username);
    setError("");
    const was = !!following[username];
    setFollowing((prev) => ({ ...prev, [username]: !was }));
    try {
      if (was) {
        await api.unfollow(token, username);
      } else {
        await api.follow(token, username);
      }
    } catch (err) {
      setFollowing((prev) => ({ ...prev, [username]: was }));
      setError(err.message || "Could not update follow");
    } finally {
      setBusy("");
    }
  }

  async function followAll() {
    if (!token || busy) return;
    setBusy("__all__");
    setError("");
    try {
      const res = await api.bootstrapFollows(token);
      const next = {};
      for (const p of people) next[p.username] = true;
      setFollowing((prev) => ({ ...prev, ...next }));
      if (res.message) setError(""); // clear
    } catch (err) {
      setError(err.message || "Could not follow accounts");
    } finally {
      setBusy("");
    }
  }

  function dismiss() {
    localStorage.setItem("bx_hide_suggested", "1");
    setHidden(true);
  }

  return (
    <section className="suggested-follows" aria-label={title}>
      <div className="suggested-follows-head">
        <div>
          <h2 className="suggested-follows-title">{title}</h2>
          {note ? <p className="hint suggested-follows-note">{note}</p> : null}
        </div>
        {dismissible ? (
          <button type="button" className="suggested-follows-dismiss" onClick={dismiss}>
            Hide
          </button>
        ) : null}
      </div>

      <ul className="suggested-follows-list">
        {people.map((person) => {
          const isFollowing = !!following[person.username];
          return (
            <li key={person.username} className="suggested-follows-row">
              <Link to={`/u/${encodeURIComponent(person.username)}`} className="suggested-follows-person">
                <Avatar name={person.display_name} username={person.username} size={40} />
                <div className="suggested-follows-info">
                  <div className={badgeNameClass(person, "suggested-follows-name")}>
                    {person.display_name}
                  </div>
                  <div className={badgeNameClass(person, "suggested-follows-username")}>@{person.username}</div>
                  {person.blurb ? <div className="suggested-follows-blurb">{person.blurb}</div> : null}
                </div>
              </Link>
              <button
                type="button"
                className={`follow-btn suggested-follow-btn${isFollowing ? " following" : ""}`}
                disabled={busy === person.username || busy === "__all__"}
                onClick={() => toggleFollow(person.username)}
              >
                {busy === person.username ? "…" : isFollowing ? "Following" : "Follow"}
              </button>
            </li>
          );
        })}
      </ul>

      <div className="suggested-follows-actions">
        <button
          type="button"
          className="welcome-follow-btn"
          onClick={followAll}
          disabled={busy === "__all__"}
        >
          {busy === "__all__" ? "Following…" : "Follow all official"}
        </button>
        <Link to="/search" className="rail-card-more suggested-explore">
          Explore people
        </Link>
      </div>
      {error ? <p className="error suggested-follows-error">{error}</p> : null}
    </section>
  );
}
