import { Link } from "react-router-dom";
import { useState } from "react";
import Logo from "../components/Logo";
import GoogleSignInButton from "../components/GoogleSignInButton";

/**
 * Native-app-only entry. Browser keeps the marketing Landing;
 * Capacitor opens here so mobile feels like an app, not a dumped website.
 */
export default function NativeLaunch() {
  const [confirmAge18, setConfirmAge18] = useState(false);
  const [acceptPrivacy, setAcceptPrivacy] = useState(false);

  return (
    <div className="bx-native-launch">
      <div className="bx-native-launch-glow" aria-hidden="true" />
      <header className="bx-native-launch-top">
        <Logo variant="full" className="bx-native-launch-logo" title="BarathX" />
        <p className="bx-native-launch-tag">India&apos;s public square</p>
      </header>

      <main className="bx-native-launch-main">
        <p className="bx-native-launch-kicker">SOFT LAUNCH · APP</p>
        <h1 className="bx-native-launch-title">
          Pick a side.
          <span> Argue it live.</span>
        </h1>
        <p className="bx-native-launch-copy">
          Square · Arenas · Live. Human takes only. No AI slop.
        </p>

        <Link className="bx-native-launch-primary" to="/login?method=phone">
          Continue with phone
        </Link>
        <Link className="bx-native-launch-secondary" to="/login?method=email">
          Log in with email
        </Link>

        <p className="bx-native-launch-copy" style={{ marginTop: "0.35rem", marginBottom: "0.15rem" }}>
          Soft launch: phone OTP is the fastest way in.
        </p>

        <div className="bx-native-launch-consent bx-home-consent-card" role="group" aria-label="Confirm before Google sign-in">
          <label className="bx-home-consent">
            <input
              type="checkbox"
              checked={confirmAge18}
              onChange={(e) => setConfirmAge18(e.target.checked)}
            />
            <span>
              I am <strong>18+</strong>
            </span>
          </label>
          <label className="bx-home-consent">
            <input
              type="checkbox"
              checked={acceptPrivacy}
              onChange={(e) => setAcceptPrivacy(e.target.checked)}
            />
            <span>
              I accept the <Link to="/privacy">Privacy Policy</Link> (India DPDP) and{" "}
              <Link to="/terms">Terms</Link>
            </span>
          </label>
        </div>

        <p className="bx-home-google-hint" aria-live="polite">
          {confirmAge18 && acceptPrivacy
            ? "Optional — Google (opens once, then back)"
            : "Optional Google — tick both boxes first"}
        </p>

        <GoogleSignInButton
          label="Continue with Google"
          confirmAge18={confirmAge18}
          acceptPrivacy={acceptPrivacy}
          requireAgeConfirm
          requirePrivacyConfirm
        />

        <p className="bx-native-launch-switch">
          New here? <Link to="/signup">Create account</Link>
        </p>
      </main>

      <footer className="bx-native-launch-foot">
        <span>barathx.com in browser · this is the app</span>
      </footer>
    </div>
  );
}
