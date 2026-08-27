import { Link } from "react-router-dom";

/**
 * Privacy notice aligned to India’s Digital Personal Data Protection Act, 2023
 * and DPDP Rules, 2025 (plain-language Data Principal notice).
 */
export default function Privacy() {
  return (
    <div className="legal-page">
      <h1>Privacy Policy</h1>
      <p className="legal-updated">Last updated: August 27, 2026 · Notice version 2026-08-27b-dpdp</p>
      <p>
        BarathX (&quot;BX&quot;, &quot;we&quot;) operates <strong>barathx.com</strong>, India&apos;s text-first public
        square. Under the <strong>Digital Personal Data Protection Act, 2023</strong> (DPDP Act) and
        the DPDP Rules, 2025, we are a <strong>Data Fiduciary</strong> and you are a{" "}
        <strong>Data Principal</strong> when we process your digital personal data.
      </p>
      <p>
        <strong>We save your information</strong> to run your account and the square (login, profile,
        posts, safety). <strong>We do not sell your personal information</strong> — not to advertisers,
        data brokers, or anyone else. We do not build third-party advertising profiles from your
        BarathX activity.
      </p>
      <p>
        This notice stands on its own. It explains what personal data we collect, why, how long we
        keep it, your rights, and how to complain. We follow Indian DPDP norms first. Where helpful,
        we also apply strong GDPR-style safeguards (access, erasure, security).
      </p>

      <h2>1. What personal data we collect</h2>
      <ul>
        <li>
          <strong>Account data</strong>: display name, username, email and/or phone, date of birth
          (age eligibility only — never public), language, theme, bio, avatar/cover if you upload them
        </li>
        <li>
          <strong>Content you create</strong>: posts, replies, images, likes, follows, messages you
          send on BarathX
        </li>
        <li>
          <strong>Security &amp; session data</strong>: hashed password (never plain text), hashed
          OTPs, sign-in tokens, basic device/browser signals needed to stop abuse
        </li>
        <li>
          <strong>Consent records</strong>: when you accepted this notice, age/DOB consent, and which
          versions
        </li>
      </ul>
      <p>
        We <strong>store</strong> the personal data listed above to provide BarathX. We do{" "}
        <strong>not</strong> sell personal data. We do not run third-party advertising profiles from
        your BarathX activity.
      </p>

      <h2>2. Purpose (why we process it)</h2>
      <p>We process personal data only for these specified purposes:</p>
      <ul>
        <li>Create and secure your account (including verification, age eligibility, and fraud/spam prevention)</li>
        <li>Show your public posts and replies in the square so others can read and reply</li>
        <li>Send account-critical messages (verification, password reset) and optional activity emails you control</li>
        <li>Provide Settings features you choose (theme, language, mutes, blocks)</li>
        <li>Meet legal obligations and keep the service safe</li>
      </ul>
      <p>
        Lawful basis under DPDP: <strong>your consent</strong> (clear affirmative action at signup),
        plus processing needed to provide the service you asked for. You may withdraw consent by
        deleting your account or turning off optional emails in Settings.
      </p>

      <h2>3. Data minimisation &amp; storage</h2>
      <ul>
        <li>We only ask for data needed for the purposes above</li>
        <li>Email and phone are private to you, not shown on public profiles</li>
        <li>
          Date of birth is private, used only to enforce our 18+ rule; it is never shown on profiles
          or feeds
        </li>
        <li>Passwords and OTPs are stored hashed</li>
        <li>
          <strong>Retention</strong>: account and public content stay while your account is active
          for the square purpose. Expired OTPs and used verification/reset tokens are deleted when
          their purpose is finished (typically within hours to a few days). After account deletion we
          erase personal data we hold, except where Indian law requires a short legal hold
        </li>
        <li>
          Hosting may use cloud infrastructure that stores data outside India. We use providers under
          contracts and security controls appropriate for personal data
        </li>
      </ul>

      <h2>4. Children</h2>
      <p>
        BarathX is for people <strong>18 and older</strong>. Under India&apos;s DPDP Act, under-18s are
        treated as children; US COPPA also restricts collection from under-13. We require date of birth
        and an age attestation at signup so we do not knowingly onboard minors. See the{" "}
        <Link to="/age-consent">age &amp; date of birth consent notice</Link>. If a parent or guardian
        believes a minor has an account, email{" "}
        <a href="mailto:privacy@barathx.com">privacy@barathx.com</a> and we will erase it.
      </p>

      <h2>4a. Email notifications</h2>
      <p>
        Optional <strong>activity emails</strong> (likes, replies, follows, mentions) default on when
        you have an email address. You can:
      </p>
      <ul>
        <li>
          <strong>Unsubscribe</strong>: link in every activity email footer, or Settings → Email
          notifications (uncheck)
        </li>
        <li>
          <strong>Re-subscribe</strong>: Settings → Email notifications (check &quot;Send me activity
          emails&quot;)
        </li>
      </ul>
      <p>
        Transactional emails (verify account, password reset) are account security and are not
        optional. We do not send marketing newsletters unless we add a separate opt-in later.
      </p>

      <h2>5. Your rights (Data Principal)</h2>
      <ul>
        <li>
          <strong>Access</strong>: download a copy of your personal data from Settings → Download my
          data
        </li>
        <li>
          <strong>Correction</strong>: edit profile fields in Settings / profile
        </li>
        <li>
          <strong>Erasure</strong>: delete your account in Settings (removes personal data we hold)
        </li>
        <li>
          <strong>Withdraw consent</strong>: turn off activity emails anytime; delete account to stop
          processing for the square purpose
        </li>
        <li>
          <strong>Grievance redressal</strong>: write to{" "}
          <a href="mailto:privacy@barathx.com">privacy@barathx.com</a>, we aim to respond within{" "}
          <strong>7 days</strong> (and in any case within timelines under the DPDP Rules)
        </li>
        <li>
          After exhausting our grievance process, you may approach the Data Protection Board of India
          as provided under the DPDP Act
        </li>
      </ul>

      <h2>6. Security</h2>
      <p>
        barathx.com is served over HTTPS. We use rate limits, session invalidation, content
        sanitisation, and access controls. No method is perfect; report suspected breaches to{" "}
        <a href="mailto:privacy@barathx.com">privacy@barathx.com</a>.
      </p>

      <h2>7. Contact</h2>
      <p>
        Data protection / privacy:{" "}
        <a href="mailto:privacy@barathx.com">privacy@barathx.com</a>
        <br />
        General support: <a href="mailto:hello@barathx.com">hello@barathx.com</a>
      </p>

      <p className="legal-back">
        <Link to="/">← Back to BarathX</Link>
        {" · "}
        <Link to="/terms">Terms</Link>
        {" · "}
        <Link to="/age-consent">Age consent</Link>
        {" · "}
        <Link to="/settings">Settings</Link>
      </p>
    </div>
  );
}
