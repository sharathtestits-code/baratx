import { Link } from "react-router-dom";

export default function Terms() {
  return (
    <div className="legal-page">
      <h1>Terms of Service</h1>
      <p className="legal-updated">Last updated: August 6, 2026</p>
      <p>
        By using BarathX (BX) at <strong>barathx.com</strong>, you agree to these terms. BarathX is an
        early product — features may change as we improve the square.
      </p>

      <h2>The basics</h2>
      <ul>
        <li>You must be 18 or older to create a BarathX account</li>
        <li>You’re responsible for what you post</li>
        <li>Don’t impersonate others or spam the square</li>
        <li>Don’t post illegal content, harassment, or doxxing</li>
      </ul>

      <h2>Your content</h2>
      <p>
        You own what you write. By posting on BarathX, you give us permission to display that content
        on the service so others can read and reply.
      </p>

      <h2>Our role</h2>
      <p>
        We provide the platform. We may remove content or suspend accounts that break these terms or
        harm other users. We’re not responsible for what other users say.
      </p>

      <h2>Accounts</h2>
      <p>
        Keep your login safe. Prefer Google sign-in or a strong password. If you use phone OTP, choose
        a clean username (letters, numbers, underscore/period/hyphen as allowed).
      </p>

      <h2>Early member welcome</h2>
      <p>
        During soft launch, some of the first 100–1,000 people who join and post may receive a
        welcome reply from BarathX admin and the founder, and may be eligible for a surprise gift
        whose details are revealed later. This is a limited promotional offer — not a purchase,
        lottery, or guarantee. Eligibility, timing, and fulfilment are at BarathX&apos;s discretion
        and may change or end without notice. Void where prohibited.{" "}
        <strong>T&amp;Cs apply</strong>.
      </p>

      <h2>Contact</h2>
      <p>
        Questions: <a href="mailto:hello@barathx.com">hello@barathx.com</a>
      </p>

      <p className="legal-back">
        <Link to="/">← Back to BarathX</Link>
        {" · "}
        <Link to="/privacy">Privacy Policy</Link>
      </p>
    </div>
  );
}
