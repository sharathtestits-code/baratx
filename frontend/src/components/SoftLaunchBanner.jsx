import { Link } from "react-router-dom";
import {
  isSoftLaunchWindow,
  SOFT_LAUNCH_BANNER,
  SOFT_LAUNCH_SHORT,
} from "../softLaunch";
import { WHATSAPP_COMMUNITY } from "../socialLinks";

/**
 * Compact soft-launch strip for Square / logged-in chrome (browser).
 * Native iOS & Android apps are coming soon.
 */
export default function SoftLaunchBanner({ compact = false }) {
  if (!isSoftLaunchWindow()) return null;
  return (
    <div className={`bx-soft-launch${compact ? " is-compact" : ""}`} role="status">
      <span className="bx-soft-launch-label">
        {compact ? SOFT_LAUNCH_SHORT : SOFT_LAUNCH_BANNER}
      </span>
      {!compact ? (
        <Link to="/signup" className="bx-soft-launch-cta">
          Join early
        </Link>
      ) : (
        <span className="bx-soft-launch-links">
          <Link to="/early-issues">Issues</Link>
          <a href={WHATSAPP_COMMUNITY} target="_blank" rel="noreferrer">
            WA
          </a>
        </span>
      )}
    </div>
  );
}
