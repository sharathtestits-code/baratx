import { Link } from "react-router-dom";
import { MIN_AGE_YEARS } from "../ageConsent";

/**
 * Consent notice for collecting date of birth (age eligibility).
 * Linked from signup before DOB is submitted.
 */
export default function AgeConsent() {
  return (
    <div className="legal-page">
      <h1>Age &amp; date of birth consent</h1>
      <p className="legal-updated">Notice version 2026-08-27-age · BarathX</p>

      <p>
        Before you create a BarathX account we ask for your <strong>date of birth</strong> and a
        clear confirmation that you are at least <strong>{MIN_AGE_YEARS}</strong>. This page explains
        why — under India&apos;s DPDP Act and US child-protection rules (including COPPA for under
        13).
      </p>

      <h2>1. Why we ask for date of birth</h2>
      <ul>
        <li>
          To check you meet our <strong>{MIN_AGE_YEARS}+</strong> eligibility rule (debate network;
          not designed for minors)
        </li>
        <li>
          To avoid knowingly collecting personal data from children without the protections the law
          requires
        </li>
        <li>To keep a consent record that you attested your age accurately</li>
      </ul>

      <h2>2. How we use it</h2>
      <ul>
        <li>
          <strong>Purpose:</strong> age eligibility and child-protection compliance only
        </li>
        <li>
          <strong>Not public:</strong> date of birth is never shown on your profile or in feeds
        </li>
        <li>
          <strong>Not for ads:</strong> we do not sell DOB or use it to build advertising profiles
        </li>
        <li>
          <strong>Retention:</strong> kept while your account is active for this purpose; erased with
          account deletion except where law requires a short hold
        </li>
      </ul>

      <h2>3. Your consent</h2>
      <p>By continuing signup and ticking the age boxes you confirm that:</p>
      <ul>
        <li>The date of birth you enter is yours and accurate</li>
        <li>
          You are {MIN_AGE_YEARS} or older (or you will not create an account if you are younger)
        </li>
        <li>
          You consent to BarathX processing your date of birth for the purpose above, under our{" "}
          <Link to="/privacy">Privacy Policy</Link> (India DPDP) and <Link to="/terms">Terms</Link>
        </li>
      </ul>
      <p>
        You may withdraw by deleting your account (Settings). Questions:{" "}
        <a href="mailto:privacy@barathx.com">privacy@barathx.com</a>.
      </p>

      <h2>4. If you are under {MIN_AGE_YEARS}</h2>
      <p>
        Do not create an account. If a parent or guardian believes a minor has an account, email{" "}
        <a href="mailto:privacy@barathx.com">privacy@barathx.com</a> and we will erase it.
      </p>

      <p className="legal-back">
        <Link to="/signup">← Back to sign up</Link>
      </p>
    </div>
  );
}
