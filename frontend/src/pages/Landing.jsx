import { Link } from "react-router-dom";
import Logo, { LogoMark } from "../components/Logo";
import GoogleSignInButton from "../components/GoogleSignInButton";

/**
 * Debate-first brand landing (audit Week 1).
 * Hero: brand + wedge + Answer today's question / Watch a live debate.
 * Founding ₹150 within first scroll. Arenas ≠ Communities clarified.
 */
export default function Landing() {
  return (
    <div className="bx-home">
      <header className="bx-home-nav">
        <Link to="/" className="bx-home-nav-brand" aria-label="BaratX home">
          <Logo variant="full" title="BaratX" />
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
              BaratX
            </h1>
          </div>
          <p className="bx-home-hero-tag">India&apos;s public square</p>
          <p className="bx-home-hero-line">Pick a side. Argue it live.</p>
          <p className="bx-home-hero-sub">
            Short posts, live debate rooms, and real replies — not an algorithm burying you in a
            firehose.
          </p>
          <div className="bx-home-hero-ctas">
            <Link to="/signup" className="btn btn-primary bx-home-cta-primary">
              Answer today&apos;s question
            </Link>
            <Link to="/signup?next=/spaces" className="btn btn-secondary bx-home-cta-secondary">
              Watch a live debate
            </Link>
          </div>
          <div className="bx-home-hero-google">
            <GoogleSignInButton label="Continue with Google" confirmAge18 />
          </div>
          <p className="bx-home-founding-chip">
            <Link to="/signup?next=/rewards">Founding ₹150</Link> — first 100 who open a live debate
            that gets real engagement.
          </p>
          <p className="bx-home-hero-legal">
            18+ · By joining you agree to the <Link to="/terms">Terms</Link> and{" "}
            <Link to="/privacy">Privacy</Link>.
          </p>
        </div>
      </section>

      <section className="bx-home-section" aria-labelledby="bx-home-why">
        <p className="bx-home-kicker">Why BaratX</p>
        <h2 id="bx-home-why">Not another feed to scroll</h2>
        <p className="bx-home-copy">
          Most social apps bury your take in an algorithm. BaratX starts from one shared question and
          a live room where you pick Agree or Disagree and argue it — audio, video, or just your
          words — with people who showed up for the same debate.
        </p>
      </section>

      <section className="bx-home-section bx-home-section-alt" aria-labelledby="bx-home-how">
        <p className="bx-home-kicker">How it works</p>
        <h2 id="bx-home-how">Three steps. Real conversation.</h2>
        <ol className="bx-home-steps">
          <li>
            <strong>Answer today&apos;s question.</strong> One prompt, every day — post your take in
            your own words.
          </li>
          <li>
            <strong>Pick a side, join the room.</strong> Live debates with a running tally — up to 15
            voices.
          </li>
          <li>
            <strong>Get real replies.</strong> People in your arena see you — not a buried timeline.
          </li>
        </ol>
      </section>

      <section className="bx-home-section" aria-labelledby="bx-home-startups">
        <p className="bx-home-kicker">Start here</p>
        <h2 id="bx-home-startups">Startups Arena — Fund it or Pass</h2>
        <p className="bx-home-copy">
          Where India&apos;s builders argue about the pitch, the raise, and the exit — live, not in a
          comment thread three days later. That&apos;s where we&apos;re densest first.
        </p>
        <Link to="/signup?next=/arenas/startups" className="btn btn-primary bx-home-inline-cta">
          Join Startups Arena
        </Link>
      </section>

      <section className="bx-home-section bx-home-section-alt" aria-labelledby="bx-home-arenas">
        <p className="bx-home-kicker">Arenas vs Communities</p>
        <h2 id="bx-home-arenas">Different jobs. Clear map.</h2>
        <div className="bx-home-diff">
          <div>
            <h3>Arenas</h3>
            <p>
              Official topic floors for sided debate — Sports, Politics, Entertainment, News,
              Spirituality, Startups. Pick Agree/Disagree (or Fund it/Pass) and go live.
            </p>
          </div>
          <div>
            <h3>Communities</h3>
            <p>
              Member-run groups (city, craft, interest) you create or join. Not the same six Arenas —
              use them when you want a smaller circle, not a national floor.
            </p>
          </div>
        </div>
      </section>

      <section className="bx-home-section" aria-labelledby="bx-home-live">
        <p className="bx-home-kicker">Live</p>
        <h2 id="bx-home-live">The wedge X and Threads don&apos;t have</h2>
        <p className="bx-home-copy">
          Open a room, pick your side, mute/video/react — a capped 15-person call with a running
          tally. Built for conversation that happens now.
        </p>
      </section>

      <section className="bx-home-section bx-home-section-alt" aria-labelledby="bx-home-founding">
        <p className="bx-home-kicker">Founding creators</p>
        <h2 id="bx-home-founding">₹150 for the first 100 real rooms</h2>
        <p className="bx-home-copy">
          Open a live debate that gets real engagement and earn Founding creator status plus ₹150 —
          a thank-you for seeding the first rooms, not a business model. Free to use forever for
          everyone else.
        </p>
        <Link to="/signup?next=/rewards" className="btn btn-secondary bx-home-inline-cta">
          See Founding rewards
        </Link>
      </section>

      <section className="bx-home-section" aria-labelledby="bx-home-faq">
        <p className="bx-home-kicker">FAQ</p>
        <h2 id="bx-home-faq">Straight answers</h2>
        <dl className="bx-home-faq">
          <div>
            <dt>How is this different from X?</dt>
            <dd>
              X is built for scrolling followers. BaratX starts with one shared question and live
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
              Topic debate floors. Communities are separate member-run groups — not duplicate Arenas.
            </dd>
          </div>
          <div>
            <dt>What&apos;s Founding ₹150?</dt>
            <dd>
              First 100 people who open a live debate that gets real engagement earn Founding status
              and ₹150.
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
        <p className="bx-home-copy">BaratX — India&apos;s public square. Built by Indians. For India.</p>
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
        <span>© {new Date().getFullYear()} BaratX</span>
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
