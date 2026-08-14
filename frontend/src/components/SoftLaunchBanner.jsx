import { Link } from "react-router-dom";
import { isSoftLaunchWindow, SOFT_LAUNCH_LINE, SOFT_LAUNCH_SHORT } from "../softLaunch";

/**
 * Compact soft-launch strip for Square / logged-in chrome.
 * Same React shell powers web + Capacitor mobile.
 */
export default function SoftLaunchBanner({ compact = false }) {
  if (!isSoftLaunchWindow()) return null;
  return (
    <div className={`bx-soft-launch${compact ? " is-compact" : ""}`} role="status">
      <span className="bx-soft-launch-label">{compact ? SOFT_LAUNCH_SHORT : SOFT_LAUNCH_LINE}</span>
      {!compact ? (
        <Link to="/signup" className="bx-soft-launch-cta">
          Join early
        </Link>
      ) : null}
    </div>
  );
}
