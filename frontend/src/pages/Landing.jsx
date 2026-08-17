import { Link } from "react-router-dom";
import Logo, { LogoMark } from "../components/Logo";
import GoogleSignInButton from "../components/GoogleSignInButton";
import { isNativeApp } from "../native";
import { showGoogleSignIn } from "../nativeGoogleAuth";
import { APP_COMING_SOON_LINE, isSoftLaunchWindow, SOFT_LAUNCH_LINE } from "../softLaunch";

/**
 * Debate-first brand landing (audit Week 1).
 * Hero: brand + wedge + Answer today's question / Watch a live debate.
 * Founding 100 = earned membership (not a signup coupon). Arenas ≠ Communities.
 */
export default function Landing() {
  const softLaunch = isSoftLaunchWindow();
  const native = isNativeApp();
  const googleOn = showGoogleSignIn();
  return (
    <div className="bx-home">
      <header className="bx-home-nav">
        <Link to="/" className="bx-home-nav-brand" aria-label="BarathX home">
          <Logo variant="full" title="BarathX" />
        </Link>
        <div className="bx-home-nav-actions">
          <Link to="/login" className="bx-home-nav-signin">
            Sign in
          </Link>
          <Link to="/signup" className="btn btn-primary bx-home-nav-join">
            Join free
          </Link>
        </div>
      </header>

      <section className="bx-home-hero" aria-labelledby="bx-home-brand">
        <div className="bx-home-hero-glow" aria-hidden="true" />
        <div className="bx-home-hero-grain" aria-hidden="true" />
        <div className="bx-home-hero-inner">
          <div className="bx-home-hero-brand">
            <LogoMark className="bx-home-hero-mark" title="" />
            <h1 id="bx-home-brand" className="bx-home-hero-name">
              BarathX
            </h1>
          </div>
          <p className="bx-home-hero-tag">India&apos;s public square</p>
          {softLaunch ? (
            <p className="bx-home-hero-soft" role="status">
              {native ? "Official soft launch · Independence Day · 15 August" : SOFT_LAUNCH_LINE}
            </p>
          ) : null}
          <p className="bx-home-hero-line">Pick a side. Argue it live.</p>
          <p className="bx-home-hero-sub">
            The place people who actually have an opinion go, not another feed to like and leave.
            {native
              ? " Join with your phone or email."
              : ` Soft launch live in your browser (phone or desktop). ${APP_COMING_SOON_LINE}.`}
          </p>
          <p className="bx-home-hero-anti-ai">Human takes only. No AI slop.</p>
          <div className="bx-home-hero-ctas">
            <Link to="/signup" className="btn btn-primary bx-home-cta-primary">
              Answer today&apos;s question
            </Link>
            <Link to="/signup?next=/spaces" className="btn btn-secondary bx-home-cta-secondary">
              Watch a live debate
            </Link>
          </div>
          {googleOn ? (
            <div className="bx-home-hero-google">
              <GoogleSignInButton label="Continue with Google" confirmAge18 />
            </div>
          ) : null}
          <p className="bx-home-founding-chip">
            <Link to="/signup?next=/rewards">100 Founding spots</Link>, earned by opening a debate
            that gets real engagement, not by signing up.
          </p>
          <p className="bx-home-hero-legal">
            18+ · By joining you agree to the <Link to="/terms">Terms</Link> and{" "}
            <Link to="/privacy">Privacy</Link>.
          </p>
        </div>
      </section>

      <section className="bx-home-section" aria-labelledby="bx-home-why">
        <p className="bx-home-kicker">Why BarathX</p>
        <h2 id="bx-home-why">Not another feed to scroll</h2>
        <p className="bx-home-copy">
          Old way: argue in an Instagram thread that vanishes in an hour, or a WhatsApp group where
          fifteen people talk past each other. BarathX: a live, sided debate (Agree vs Disagree)
          where a real person answers you on the record. We&apos;re officially soft launching on
          Independence Day (15 August)
          {native
            ? ", early on purpose so those rooms stay real, not performed for growth numbers."
            : " in the browser (phone and desktop), early on purpose so those rooms stay real, not performed for growth numbers. Native apps for Apple and Android are coming soon."}
        </p>
      </section>

      {!native ? (
      <section className="bx-home-section bx-home-section-alt" aria-labelledby="bx-home-apps">
        <p className="bx-home-kicker">Apps</p>
        <h2 id="bx-home-apps">App coming soon: Apple &amp; Android</h2>
        <p className="bx-home-copy">
          Soft launch is live in the browser today. Join on your phone browser or desktop while we
          finish the App Store and Google Play builds.
        </p>
        <ul className="bx-home-app-soon" aria-label="Native apps coming soon">
          <li className="bx-home-app-soon-item">
            <span className="bx-home-app-soon-platform" aria-hidden="true">
              <svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor">
                <path d="M16.365 1.43c0 1.14-.433 2.207-1.226 3.038-.84.89-2.01 1.53-3.08 1.44-.13-1.1.4-2.25 1.18-3.1.86-.94 2.2-1.6 3.13-1.38zM20.5 17.2c-.58 1.34-.86 1.93-1.61 3.11-1.05 1.64-2.53 3.68-4.37 3.7-1.63.02-2.05-1.06-4.27-1.05-2.22.01-2.68 1.07-4.31 1.05-1.84-.02-3.25-1.86-4.3-3.5C-.1 17.2-1.3 12.6.9 9.4c1.1-1.6 2.84-2.6 4.54-2.6 1.7 0 2.77 1.1 4.18 1.1 1.37 0 2.2-1.1 4.2-1.1 1.5 0 3.08.82 4.18 2.23-3.67 2.01-3.08 7.25.5 8.17z" />
              </svg>
            </span>
            <span className="bx-home-app-soon-text">
              <strong>Apple</strong>
              <span>App Store · Coming soon</span>
            </span>
          </li>
          <li className="bx-home-app-soon-item">
            <span className="bx-home-app-soon-platform" aria-hidden="true">
              <svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor">
                <path d="M17.6 9.48l1.84-3.18a.5.5 0 0 0-.86-.5l-1.86 3.22A7.9 7.9 0 0 0 12 7.5c-1.7 0-3.27.53-4.72 1.52L5.42 5.8a.5.5 0 1 0-.86.5l1.84 3.18C4.1 11.05 3 13.12 3 15.5h18c0-2.38-1.1-4.45-3.4-6.02zM7.1 16.75a1 1 0 1 1 0-2 1 1 0 0 1 0 2zm9.8 0a1 1 0 1 1 0-2 1 1 0 0 1 0 2z" />
              </svg>
            </span>
            <span className="bx-home-app-soon-text">
              <strong>Android</strong>
              <span>Google Play · Coming soon</span>
            </span>
          </li>
        </ul>
        <Link to="/signup" className="btn btn-primary bx-home-inline-cta">
          Join in your browser
        </Link>
      </section>
      ) : null}

      <section className="bx-home-section" aria-labelledby="bx-home-how">
        <p className="bx-home-kicker">How it works</p>
        <h2 id="bx-home-how">Three steps. Real conversation.</h2>
        <ol className="bx-home-steps">
          <li>
            <strong>Answer today&apos;s question.</strong> One prompt, every day. Post your take in
            your own words.
          </li>
          <li>
            <strong>Pick a side, join the room.</strong> Live debates with a running tally, up to 15
            voices.
          </li>
          <li>
            <strong>Get real replies.</strong> People in your arena see you, not a buried timeline.
          </li>
        </ol>
      </section>

      <section className="bx-home-section bx-home-section-alt" aria-labelledby="bx-home-startups">
        <p className="bx-home-kicker">Start here</p>
        <h2 id="bx-home-startups">Startups Arena: Fund it or Pass</h2>
        <p className="bx-home-copy">
          Where India&apos;s builders argue about the pitch, the raise, and the exit, live, not in a
          comment thread three days later. That&apos;s where we&apos;re densest first.
        </p>
        <Link to="/signup?next=/arenas/startups" className="btn btn-primary bx-home-inline-cta">
          Join Startups Arena
        </Link>
      </section>

      <section className="bx-home-section" aria-labelledby="bx-home-arenas">
        <p className="bx-home-kicker">Arenas vs Communities</p>
        <h2 id="bx-home-arenas">Different jobs. Clear map.</h2>
        <div className="bx-home-diff">
          <div>
            <h3>Arenas</h3>
            <p>
              Pick a side and jump in: Sports, Politics, Entertainment, News, Spirituality,
              Startups. Agree/Disagree (or Fund it/Pass) live.
            </p>
          </div>
          <div>
            <h3>Communities</h3>
            <p>
              Smaller groups (city, craft, interest). Not the same six Arenas. Use them when you
              want a circle, not a national floor.
            </p>
          </div>
        </div>
      </section>

      <section className="bx-home-section bx-home-section-alt" aria-labelledby="bx-home-live">
        <p className="bx-home-kicker">Live</p>
        <h2 id="bx-home-live">The wedge X and Threads don&apos;t have</h2>
        <p className="bx-home-copy">
          Open a room, pick your side, mute/video/react. A capped 15-person call with a running
          tally. Built for conversation that happens now.
        </p>
      </section>

      <section className="bx-home-section" aria-labelledby="bx-home-founding">
        <p className="bx-home-kicker">Founding 100</p>
        <h2 id="bx-home-founding">100 Founding spots. Earned, not claimed.</h2>
        <p className="bx-home-copy">
          100 Founding spots, earned by opening a debate that gets real engagement, not by signing
          up. Getting in means something. We&apos;re early on purpose. Free forever for everyone
          else.
        </p>
        <Link to="/signup?next=/rewards" className="btn btn-secondary bx-home-inline-cta">
          How Founding works
        </Link>
      </section>

      <section className="bx-home-section bx-home-section-alt" aria-labelledby="bx-home-faq">
        <p className="bx-home-kicker">FAQ</p>
        <h2 id="bx-home-faq">Straight answers</h2>
        <dl className="bx-home-faq">
          <div>
            <dt>How is this different from X?</dt>
            <dd>
              X is built for scrolling followers. BarathX starts with one shared question and live
              rooms where you pick a side and argue in real time.
            </dd>
          </div>
          <div>
            <dt>Do I need camera or mic?</dt>
            <dd>
              No. Post a text take anytime. Live audio/video is optional when you want it.
            </dd>
          </div>
          <div>
            <dt>What are Arenas?</dt>
            <dd>
              Topic debate floors. Communities are separate member-run groups, not duplicate Arenas.
            </dd>
          </div>
          <div>
            <dt>What&apos;s Founding 100?</dt>
            <dd>
              100 Founding spots, earned by opening a debate that gets real engagement, not by
              signing up. Membership, not a signup bonus.
            </dd>
          </div>
          <div>
            <dt>Is this full of AI posts?</dt>
            <dd>No. Human takes only. No AI slop in the square.</dd>
          </div>
          <div>
            <dt>When is the soft launch?</dt>
            <dd>
              Official soft launch on Independence Day (15 August) in your browser on phone and
              desktop. iOS and Android apps are coming soon. Same BarathX, early on purpose.
            </dd>
          </div>
          <div>
            <dt>Is there a mobile app?</dt>
            <dd>
              Not yet. Soft launch is web-first. Open barathx.com in Safari, Chrome, or any browser.
              Native apps for Apple App Store and Google Play are coming soon.
            </dd>
          </div>
          <div>
            <dt>Hindi or Telugu?</dt>
            <dd>English is live today. Hindi and Telugu UI come after the English core loop is proven.</dd>
          </div>
          <div>
            <dt>Abuse or spam?</dt>
            <dd>
              Report any post from the ··· menu. Repeated reports can auto-remove content. Full house
              rules: <Link to="/guidelines">Community guidelines</Link>.
            </dd>
          </div>
        </dl>
      </section>

      <section className="bx-home-closing" aria-labelledby="bx-home-close">
        <LogoMark className="bx-home-closing-mark" title="" />
        <h2 id="bx-home-close">Post your take. Someone will talk back.</h2>
        <p className="bx-home-copy">BarathX. India&apos;s public square. Built by Indians. For India.</p>
        <div className="bx-home-hero-ctas">
          <Link to="/signup" className="btn btn-primary bx-home-cta-primary">
            Answer today&apos;s question
          </Link>
          <a
            className="btn btn-secondary bx-home-cta-secondary"
            href="https://whatsapp.com/channel/0029VbDMIgqHQbS9tfQo6u2o"
            target="_blank"
            rel="noreferrer"
          >
            WhatsApp community
          </a>
        </div>
        <p className="bx-home-closing-follow">
          Follow on X →{" "}
          <a href="https://x.com/getbaratx" target="_blank" rel="noreferrer">
            @getbaratx
          </a>
        </p>
      </section>

      <footer className="bx-home-foot">
        <span>© {new Date().getFullYear()} BarathX</span>
        <span className="bx-home-foot-links">
          <Link to="/guidelines">Guidelines</Link>
          <Link to="/terms">Terms</Link>
          <Link to="/privacy">Privacy</Link>
          <a href="https://barathx.com">barathx.com</a>
        </span>
      </footer>
    </div>
  );
}
