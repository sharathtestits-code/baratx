import { Link } from "react-router-dom";

/**
 * Plain-language house rules — audit Week 1 (moderation was missing from product).
 */
export default function Guidelines() {
  return (
    <div className="page page-auth">
      <article className="legal-doc guidelines-doc">
        <p className="hint">
          <Link to="/">← BaratX</Link>
        </p>
        <h1>Community guidelines</h1>
        <p className="legal-lead">
          BaratX is India&apos;s public square for short posts and live debate. Argue hard. Don&apos;t
          abuse people.
        </p>

        <h2>Do</h2>
        <ul>
          <li>Pick a side and make a clear case — text or live.</li>
          <li>Reply to takes you disagree with; that&apos;s the product.</li>
          <li>Report spam, impersonation, and harassment from the ··· menu on any post.</li>
        </ul>

        <h2>Don&apos;t</h2>
        <ul>
          <li>Threats, doxxing, sexual content involving minors, or illegal activity.</li>
          <li>Spam, scams, or bot farms posting the same take everywhere.</li>
          <li>Hate that targets people for who they are (not ideas you disagree with).</li>
        </ul>

        <h2>How reporting works</h2>
        <p>
          Open any post → ··· → Report. Give a short reason. Multiple independent reports in a short
          window can auto-remove content. Serious cases may suspend accounts.
        </p>

        <h2>Badges</h2>
        <ul>
          <li>
            <strong>Blue official</strong> — BaratX staff / platform accounts.
          </li>
          <li>
            <strong>Gold BaratX</strong> — BaratX brand voices (seeded topic accounts), not personal
            verification.
          </li>
        </ul>

        <h2>Founding ₹150</h2>
        <p>
          Early creators who open a live debate that shows real engagement can earn Founding status
          and ₹150. Details on <Link to="/rewards">Rewards</Link> after you join.
        </p>

        <p className="hint">
          Questions:{" "}
          <a href="mailto:hello@barathx.com">hello@barathx.com</a> ·{" "}
          <Link to="/terms">Terms</Link> · <Link to="/privacy">Privacy</Link>
        </p>
      </article>
    </div>
  );
}
