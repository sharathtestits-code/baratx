import { Link } from "react-router-dom";

export default function Terms() {
  return (
    <div className="legal-page">
      <h1>Terms of Service</h1>
      <p className="legal-updated">Last updated: August 27, 2026</p>
      <p>
        By using BarathX (BX) at <strong>barathx.com</strong>, you agree to these terms. BarathX is an
        early product, features may change as we improve the square. Personal data is handled under
        our <Link to="/privacy">Privacy Policy</Link> and India&apos;s Digital Personal Data
        Protection Act, 2023 (DPDP). You must be <strong>18 or older</strong> to create an account.
      </p>

      <h2>The basics</h2>
      <ul>
        <li>You must be 18+; date of birth is collected only for eligibility (see{" "}
          <Link to="/age-consent">age consent</Link>)</li>
        <li>You&apos;re responsible for what you post</li>
        <li>Don&apos;t impersonate others or spam the square</li>
        <li>Don&apos;t post illegal content, harassment, or doxxing</li>
        <li>Human takes only, don&apos;t flood the square with AI slop</li>
      </ul>

      <h2>Your content</h2>
      <p>
        You own what you write. By posting on BarathX, you give us permission to display that content
        on the service so others can read and reply. You can delete your posts or erase your account
        (and personal data we hold) under the Privacy Policy.
      </p>

      <h2>Our role</h2>
      <p>
        We provide the platform as a Data Fiduciary for account personal data. We may remove content
        or suspend accounts that break these terms or harm other users. We&apos;re not responsible
        for what other users say.
      </p>

      <h2>Accounts</h2>
      <p>
        Keep your login safe. Prefer Google sign-in or a strong password. If you use phone OTP, choose
        a clean username (letters, numbers, underscore/period/hyphen as allowed). Use Settings → Sign
        out everywhere if a device or token may be compromised.
      </p>

      <h2>Early member welcome</h2>
      <p>
        During soft launch, some of the first 100–1,000 people who join and post may receive a
        welcome reply from BarathX admin and the founder, and may be eligible for a surprise gift
        whose details are revealed later. This is a limited promotional offer, not a purchase,
        lottery, or guarantee. Eligibility, timing, and fulfilment are at BarathX&apos;s discretion
        and may change or end without notice. Void where prohibited.{" "}
        <strong>T&amp;Cs apply</strong>.
      </p>

      <h2>Contact</h2>
      <p>
        Questions: <a href="mailto:hello@barathx.com">hello@barathx.com</a>
        <br />
        Privacy / DPDP: <a href="mailto:privacy@barathx.com">privacy@barathx.com</a>
      </p>

      <p className="legal-back">
        <Link to="/">← Back to BarathX</Link>
        {" · "}
        <Link to="/privacy">Privacy Policy</Link>
      </p>
    </div>
  );
}
