import { Link } from "react-router-dom";
import Logo, { LogoMark } from "../components/Logo";
import GoogleSignInButton from "../components/GoogleSignInButton";

/**
 * Brand landing — explains BaratX before auth.
 * Hero: brand + tagline + one line + CTAs. Sections: Square · Arenas · Live · join.
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
          <p className="bx-home-hero-line">Everyone&apos;s got a take. Few will post it.</p>
          <p className="bx-home-hero-sub">
            Short posts. Real conversation. Arenas for the fights that matter.
          </p>
          <div className="bx-home-hero-ctas">
            <Link to="/signup" className="btn btn-primary bx-home-cta-primary">
              Join free
            </Link>
            <Link to="/login" className="btn btn-secondary bx-home-cta-secondary">
              Sign in
            </Link>
          </div>
          <div className="bx-home-hero-google">
            <GoogleSignInButton label="Continue with Google" confirmAge18 />
          </div>
          <p className="bx-home-hero-legal">
            18+ · By joining you agree to the <Link to="/terms">Terms</Link> and{" "}
            <Link to="/privacy">Privacy</Link>.
          </p>
        </div>
      </section>

      <section className="bx-home-section" aria-labelledby="bx-home-square">
        <p className="bx-home-kicker">Square</p>
        <h2 id="bx-home-square">One feed. Your city. Your take.</h2>
        <p className="bx-home-copy">
          Drop short posts, reply hard, and follow voices from Hyderabad to Delhi — not a foreign
          firehose.
        </p>
      </section>

      <section className="bx-home-section bx-home-section-alt" aria-labelledby="bx-home-arenas">
        <p className="bx-home-kicker">Arenas</p>
        <h2 id="bx-home-arenas">Pick your fight.</h2>
        <p className="bx-home-copy">
          Sports · Politics · Entertainment · News · Spirituality · Startups — join an arena and argue
          like you mean it.
        </p>
        <ul className="bx-home-arena-row" aria-label="Arenas">
          {["Sports", "Politics", "Entertainment", "News", "Spirituality", "Startups"].map((name) => (
            <li key={name}>{name}</li>
          ))}
        </ul>
      </section>

      <section className="bx-home-section" aria-labelledby="bx-home-live">
        <p className="bx-home-kicker">Live</p>
        <h2 id="bx-home-live">When text isn&apos;t enough — talk.</h2>
        <p className="bx-home-copy">
          Open a room, join conversation, mute, video, reactions — up to 15 voices in the amphitheatre.
        </p>
      </section>

      <section className="bx-home-closing" aria-labelledby="bx-home-close">
        <LogoMark className="bx-home-closing-mark" title="" />
        <h2 id="bx-home-close">Get in. It&apos;s free.</h2>
        <p className="bx-home-copy">BaratX — India&apos;s public square. Built by Indians. For India.</p>
        <div className="bx-home-hero-ctas">
          <Link to="/signup" className="btn btn-primary bx-home-cta-primary">
            Join free
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
          <Link to="/terms">Terms</Link>
          <Link to="/privacy">Privacy</Link>
          <a href="https://barathx.com">barathx.com</a>
        </span>
      </footer>
    </div>
  );
}
