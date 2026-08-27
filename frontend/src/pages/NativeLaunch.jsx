import { Link } from "react-router-dom";
import Logo from "../components/Logo";
import AgeConsentFields from "../components/AgeConsentFields";
import GoogleSignInButton from "../components/GoogleSignInButton";
import TurnstileWidget, { useTurnstileConfig } from "../components/TurnstileWidget";
import { useState } from "react";

/**
 * Native-app-only entry. Browser keeps the marketing Landing;
 * Capacitor opens here so mobile feels like an app, not a dumped website.
 * Phone OTP first (soft launch). Privacy/terms + 18+ DOB with optional Google.
 */
export default function NativeLaunch() {
  const [acceptPrivacy, setAcceptPrivacy] = useState(false);
  const [dateOfBirth, setDateOfBirth] = useState("");
  const [confirmAge18, setConfirmAge18] = useState(false);
  const [turnstileToken, setTurnstileToken] = useState("");
  const { required: needBotCheck } = useTurnstileConfig();

  return (
    <div className="bx-native-launch">
      <div className="bx-native-launch-glow" aria-hidden="true" />
      <header className="bx-native-launch-top">
        <Logo variant="full" className="bx-native-launch-logo" title="BarathX" />
        <p className="bx-native-launch-tag">India&apos;s conversation network</p>
      </header>

      <main className="bx-native-launch-main">
        <p className="bx-native-launch-kicker">SOFT LAUNCH · APP · 18+</p>
        <h1 className="bx-native-launch-title">
          India has opinions.
          <span> Now it has a home.</span>
        </h1>
        <p className="bx-native-launch-copy">
          Pick a side, share your take, meet people who care about the same conversations. Real
          people. Real context. Respectful pushback. Human takes only.
        </p>

        <Link className="bx-native-launch-primary" to="/login?method=phone">
          Continue with phone
        </Link>
        <Link className="bx-native-launch-secondary" to="/login?method=email">
          Log in with email
        </Link>
        <Link className="bx-native-launch-secondary" to="/signup">
          Take today&apos;s side
        </Link>

        <p className="bx-native-launch-copy" style={{ marginTop: "0.55rem", marginBottom: "0.15rem" }}>
          Soft launch: phone OTP is the fastest way in (no bot check). New accounts need Privacy,
          Terms, and age (18+) confirmation — on signup or with Google below.
        </p>

        <details className="bx-native-launch-google">
          <summary>Optional — Continue with Google</summary>
          <div
            className="bx-native-launch-consent bx-home-consent-card"
            role="group"
            aria-label="Confirm before Google sign-in"
          >
            <AgeConsentFields
              idPrefix="native-google"
              dateOfBirth={dateOfBirth}
              onDateOfBirthChange={setDateOfBirth}
              confirmAge18={confirmAge18}
              onConfirmAge18Change={setConfirmAge18}
            />
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
          {needBotCheck ? (
            <TurnstileWidget
              onToken={(tok) => setTurnstileToken(tok || "")}
            />
          ) : null}
          <p className="bx-home-google-hint" aria-live="polite">
            {acceptPrivacy && confirmAge18 && dateOfBirth && (!needBotCheck || turnstileToken)
              ? "Ready — continue with Google"
              : needBotCheck
                ? "Confirm age, Privacy & security check, then Google"
                : "Confirm age + Privacy & Terms, then continue with Google"}
          </p>
          <GoogleSignInButton
            label="Continue with Google"
            acceptPrivacy={acceptPrivacy}
            requirePrivacyConfirm
            dateOfBirth={dateOfBirth}
            confirmAge18={confirmAge18}
            requireAgeConfirm
            turnstileToken={turnstileToken}
            requireTurnstile={needBotCheck}
          />
        </details>

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
