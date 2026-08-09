import { Link } from "react-router-dom";

/** Public Terms of Service — required for store soft launch. */
export default function Terms() {
  return (
    <article className="legal-doc">
      <h1>Terms of Service</h1>
      <p className="legal-updated">Last updated: 9 August 2026 · BaratX (barathx.com)</p>

      <p>
        By using BaratX (website or mobile apps), you agree to these terms. If you do
        not agree, do not use the service.
      </p>

      <h2>The service</h2>
      <p>
        BaratX is a public square for short posts and sided debates across Arenas
        (Sports, Politics, Entertainment, News, Startups, Spirituality). Features may
        change during soft launch.
      </p>

      <h2>Your account</h2>
      <ul>
        <li>You must provide accurate signup info (phone and/or email).</li>
        <li>You are responsible for activity on your account.</li>
        <li>One person, one account — no bots or fake rings.</li>
      </ul>

      <h2>Your content</h2>
      <ul>
        <li>You keep ownership of what you post.</li>
        <li>You grant BaratX a license to host, display, and distribute it on the service.</li>
        <li>Do not post illegal content, harassment, spam, impersonation, or sexual content involving minors.</li>
      </ul>

      <h2>Rules of the square</h2>
      <p>
        Pick a side and argue in good faith. We may remove content, limit features, or
        suspend accounts that break these terms or harm other users.
      </p>

      <h2>Soft launch</h2>
      <p>
        During early access / TestFlight / Play testing, the product may be unstable.
        We provide BaratX “as is” without warranties. We are not liable for indirect
        damages arising from use of the beta service.
      </p>

      <h2>Contact</h2>
      <p>
        <a href="mailto:hello@barathx.com">hello@barathx.com</a>
      </p>

      <p className="legal-back">
        <Link to="/">← Back to BaratX</Link>
      </p>
    </article>
  );
}
