import { Link } from "react-router-dom";
import {
  isSoftLaunchWindow,
  SOFT_LAUNCH_BANNER,
  SOFT_LAUNCH_SHORT,
} from "../softLaunch";
import { isNativeApp } from "../native";

/**
 * Compact soft-launch strip for Square / logged-in chrome (browser).
 * Hidden in the native iOS/Android shells so the store listing does not say
 * "apps coming soon" inside the app itself.
 */
export default function SoftLaunchBanner({ compact = false }) {
  if (!isSoftLaunchWindow()) return null;
  if (isNativeApp()) return null;
  return (
    <div className={`bx-soft-launch${compact ? " is-compact" : ""}`} role="status">
      <span className="bx-soft-launch-label">
        {compact ? SOFT_LAUNCH_SHORT : SOFT_LAUNCH_BANNER}
      </span>
      {!compact ? (
        <Link to="/signup" className="bx-soft-launch-cta">
          Join early
        </Link>
      ) : null}
    </div>
  );
}
