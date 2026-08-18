import { Link } from "react-router-dom";

/**
 * Plain-language house rules, audit Week 1 (moderation was missing from product).
 */
export default function Guidelines() {
  return (
    <div className="page page-auth">
      <article className="legal-doc guidelines-doc">
        <p className="hint">
          <Link to="/">← BarathX</Link>
        </p>
        <h1>Community guidelines</h1>
        <p className="legal-lead">
          BarathX is India&apos;s public square for short posts and live debate. Argue hard. Don&apos;t
          abuse people.
        </p>

        <h2>Do</h2>
        <ul>
          <li>Pick a side and make a clear case, text or live.</li>
          <li>Reply to takes you disagree with; that&apos;s the product.</li>
          <li>Report spam, impersonation, and harassment from the ··· menu on any post.</li>
        </ul>

        <h2>Don&apos;t</h2>
        <ul>
          <li>
            Threats, doxxing, child sexual abuse and exploitation (CSAE / CSAM), sexual content
            involving minors, or illegal activity. Full standard:{" "}
            <Link to="/child-safety">Child safety</Link>.
          </li>
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
            <strong>Blue official</strong>. BarathX staff / platform accounts.
          </li>
          <li>
            <strong>Gold BarathX</strong>. BarathX brand voices (seeded topic accounts), not personal
            verification.
          </li>
        </ul>

        <h2>Early members</h2>
        <p>
          Among the first 100–1,000 people who join and post, BarathX admin and the founder may leave
          a welcome reply. A surprise gift may apply, details revealed later. Limited offer;{" "}
          <strong>T&amp;Cs apply</strong> (
          <Link to="/terms">Terms</Link>). Founding 100 is separate: 100 spots earned by opening a
          debate that gets real engagement, not by signing up. Details on{" "}
          <Link to="/rewards">Rewards</Link> after you join.
        </p>

        <p className="hint">
          Questions:{" "}
          <a href="mailto:hello@barathx.com">hello@barathx.com</a> ·{" "}
          <Link to="/terms">Terms</Link> · <Link to="/privacy">Privacy</Link> ·{" "}
          <Link to="/child-safety">Child safety</Link>
        </p>
      </article>
    </div>
  );
}
