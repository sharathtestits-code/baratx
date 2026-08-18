import { Link } from "react-router-dom";

export default function Privacy() {
  return (
    <div className="legal-page">
      <h1>Privacy Policy</h1>
      <p className="legal-updated">Last updated: August 18, 2026</p>
      <p>
        BarathX (BX) is India’s text-first public square at <strong>barathx.com</strong>. This page
        explains what we collect and how we use it, in plain language.
      </p>

      <h2>What we collect</h2>
      <ul>
        <li>Account details you provide: display name, username, email and/or phone</li>
        <li>Content you post: posts, replies, images you upload</li>
        <li>Basic technical data needed to run the service (login session, device/browser basics)</li>
      </ul>

      <h2>How we use it</h2>
      <ul>
        <li>To create and secure your account</li>
        <li>To show your posts and replies to other BarathX users</li>
        <li>To send verification or important account messages</li>
        <li>To keep the product working and safe (spam/abuse prevention)</li>
      </ul>

      <h2>What we don’t do</h2>
      <ul>
        <li>We don’t sell your personal data</li>
        <li>We don’t run ads based on selling your profile to brokers</li>
        <li>Passwords are stored hashed, we can’t read your password</li>
      </ul>

      <h2>Security</h2>
      <p>
        barathx.com is served over HTTPS. Sign-in uses secure session tokens. You can sign in with
        Google if you prefer not to create a new password.
      </p>

      <h2>Your choices</h2>
      <ul>
        <li>Edit your profile anytime</li>
        <li>Delete posts you create from the post menu</li>
        <li>Delete your account in Settings, or email us if you cannot sign in</li>
      </ul>

      <h2 id="account-deletion">Delete your account</h2>
      <p>
        You can delete your BarathX account yourself. This permanently removes the account and your
        posts.
      </p>
      <ol>
        <li>
          Sign in at <a href="https://barathx.com">barathx.com</a> or in the BarathX app
        </li>
        <li>Open Settings</li>
        <li>Under Delete account, type DELETE and confirm</li>
      </ol>
      <p>
        If you cannot sign in, email{" "}
        <a href="mailto:hello@barathx.com">hello@barathx.com</a> from the address or phone on the
        account and ask us to delete it.
      </p>

      <h2 id="data-deletion">Delete some data without deleting your account</h2>
      <p>You do not have to close the account to remove content.</p>
      <ul>
        <li>Delete any post you created: open the post → ··· → Delete</li>
        <li>Edit or clear profile fields (display name, bio, photos) on your profile</li>
        <li>
          For other data we hold, email{" "}
          <a href="mailto:hello@barathx.com">hello@barathx.com</a> and ask us to delete it. We will
          not require you to delete the whole account.
        </li>
      </ul>

      <h2>Contact</h2>
      <p>
        Questions about privacy:{" "}
        <a href="mailto:hello@barathx.com">hello@barathx.com</a>
      </p>

      <p className="legal-back">
        <Link to="/">← Back to BarathX</Link>
      </p>
    </div>
  );
}
