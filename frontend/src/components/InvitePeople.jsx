import { Link } from "react-router-dom";
import { CIRCLE_TOPICS } from "../arenas";
import { IG_PROFILE, WHATSAPP_CHANNEL, WHATSAPP_COMMUNITY, X_PROFILE } from "../socialLinks";
import { useT } from "../context/LocaleContext";

const INVITE_TEXT =
  "Join me on BarathX — India's conversation network. Real people, real sides, no AI slop. https://barathx.com";

/**
 * Acquisition surface: invite real people via WhatsApp / IG / X + Circles.
 */
export default function InvitePeople({ compact = false }) {
  const t = useT();
  const waShare = `https://wa.me/?text=${encodeURIComponent(INVITE_TEXT)}`;

  async function copyInvite() {
    try {
      await navigator.clipboard.writeText(INVITE_TEXT);
      window.alert("Invite link copied.");
    } catch {
      window.prompt("Copy this invite:", INVITE_TEXT);
    }
  }

  return (
    <section className={`bx-invite${compact ? " is-compact" : ""}`} aria-labelledby="bx-invite-title">
      <h2 id="bx-invite-title" className={compact ? "bx-invite-title-sm" : undefined}>
        Invite real people
      </h2>
      <p className="hint">
        BarathX works when humans show up. Share with friends, campus, or your city — not bots.
      </p>
      <div className="bx-invite-actions">
        <a className="btn btn-primary" href={waShare} target="_blank" rel="noopener noreferrer">
          WhatsApp invite
        </a>
        <a className="btn btn-secondary" href={WHATSAPP_CHANNEL} target="_blank" rel="noopener noreferrer">
          WA channel
        </a>
        <a className="btn btn-secondary" href={WHATSAPP_COMMUNITY} target="_blank" rel="noopener noreferrer">
          WA community
        </a>
        <a className="btn btn-secondary" href={IG_PROFILE} target="_blank" rel="noopener noreferrer">
          Instagram
        </a>
        <a className="btn btn-secondary" href={X_PROFILE} target="_blank" rel="noopener noreferrer">
          X
        </a>
        <button type="button" className="btn btn-secondary" onClick={copyInvite}>
          Copy link
        </button>
      </div>
      <div className="bx-invite-circles">
        <p className="bx-invite-circles-label">Or join a Circle</p>
        <ul className="bx-invite-circle-list">
          {CIRCLE_TOPICS.map((c) => (
            <li key={c.key}>
              <Link to={`/arenas/${c.key}`} style={{ "--arena-accent": c.accent }}>
                {t(`arena.${c.key}`)}
              </Link>
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}
