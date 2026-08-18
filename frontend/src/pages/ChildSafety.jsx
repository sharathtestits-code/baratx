import { Link } from "react-router-dom";

/**
 * Public CSAE / child safety standards for Google Play Social-category apps.
 * Must stay logged-out reachable at https://barathx.com/child-safety
 */
export default function ChildSafety() {
  return (
    <div className="legal-page">
      <h1>Child safety standards</h1>
      <p className="legal-updated">Last updated: August 18, 2026</p>
      <p>
        <strong>BarathX</strong> (BX) is India’s public square at{" "}
        <strong>barathx.com</strong> and in the BarathX Android app. This page is our published
        standard against child sexual abuse and exploitation (CSAE), including child sexual abuse
        material (CSAM).
      </p>

      <h2>Zero tolerance</h2>
      <p>
        BarathX prohibits CSAE and CSAM. You may not create, upload, share, solicit, or link to
        sexual content involving anyone 17 or under, including fictional or AI-generated depictions.
        Grooming, child sexual exploitation, and trafficking content are banned.
      </p>
      <p>BarathX is 18+ only. You must be 18 or older to create an account.</p>

      <h2>How to report in the app</h2>
      <ol>
        <li>Open the post, message, Live room, or profile</li>
        <li>Tap ··· → Report</li>
        <li>
          Write a reason. For child safety, write <strong>child safety</strong> or{" "}
          <strong>CSAM</strong>
        </li>
      </ol>
      <p>
        You can also email{" "}
        <a href="mailto:hello@barathx.com">hello@barathx.com</a> with the subject{" "}
        <strong>Child safety</strong>. Include links or usernames if you have them. Do not email
        illegal images.
      </p>

      <h2>What we do when we learn of CSAM</h2>
      <ul>
        <li>Remove the content and lock or delete the account</li>
        <li>Preserve records needed for a lawful report</li>
        <li>
          Report confirmed CSAM to the National Center for Missing &amp; Exploited Children
          (NCMEC CyberTipline) and/or India’s National Cyber Crime Reporting Portal
          (cybercrime.gov.in), as the law requires
        </li>
        <li>Cooperate with lawful requests from authorities</li>
      </ul>

      <h2>Point of contact</h2>
      <p>
        Child safety / CSAM reports and Google Play CSAE notices:{" "}
        <a href="mailto:hello@barathx.com">hello@barathx.com</a>
      </p>

      <p className="legal-back">
        <Link to="/">← Back to BarathX</Link>
        {" · "}
        <Link to="/guidelines">Guidelines</Link>
        {" · "}
        <Link to="/terms">Terms</Link>
        {" · "}
        <Link to="/privacy">Privacy</Link>
      </p>
    </div>
  );
}
