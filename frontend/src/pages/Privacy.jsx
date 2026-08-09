import { Link } from "react-router-dom";

/** Public Privacy Policy — required for Play Store / App Store soft launch. */
export default function Privacy() {
  return (
    <article className="legal-doc">
      <h1>Privacy Policy</h1>
      <p className="legal-updated">Last updated: 9 August 2026 · BaratX (barathx.com)</p>

      <p>
        BaratX (“we”, “us”) is India’s public square for short posts and sided debates.
        This policy explains what we collect and how we use it when you use barathx.com
        or the BaratX Android / iOS apps.
      </p>

      <h2>What we collect</h2>
      <ul>
        <li>Account info: phone number and/or email, username, display name, bio, avatar</li>
        <li>Content you post: posts, replies, votes/sides, messages, community activity</li>
        <li>Usage data: device type, app/browser, approximate region, crash/diagnostic logs</li>
        <li>Optional: contacts you choose to follow; topic interests you pick at onboarding</li>
      </ul>

      <h2>How we use it</h2>
      <ul>
        <li>To create and secure your account (including OTP / email verification)</li>
        <li>To show your posts and profile to other users on BaratX</li>
        <li>To operate feed, Arenas, notifications, and safety tools</li>
        <li>To improve the product and prevent abuse</li>
      </ul>

      <h2>Sharing</h2>
      <p>
        We do not sell your personal data. We may share data with infrastructure providers
        (hosting, email/SMS delivery) only to run BaratX, or when required by law.
        Content you post publicly is visible to other BaratX users.
      </p>

      <h2>Retention & deletion</h2>
      <p>
        We keep account and content data while your account is active. Contact us to
        request account deletion; we will remove or anonymize personal data except where
        we must retain it for legal or safety reasons.
      </p>

      <h2>Children</h2>
      <p>BaratX is not directed at children under 13. Soft-launch testers should be 18+.</p>

      <h2>Contact</h2>
      <p>
        Questions or deletion requests:{" "}
        <a href="mailto:hello@barathx.com">hello@barathx.com</a>
      </p>

      <p className="legal-back">
        <Link to="/">← Back to BaratX</Link>
      </p>
    </article>
  );
}
