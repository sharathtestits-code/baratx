import { useMemo, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import Logo, { LogoMark } from "../components/Logo";
import { APP_COMING_SOON_LINE, isSoftLaunchWindow, SOFT_LAUNCH_LINE } from "../softLaunch";
import { WHATSAPP_CHANNEL, WHATSAPP_COMMUNITY, X_PROFILE, IG_PROFILE } from "../socialLinks";
import { todaysSquareQuestion } from "../square";
import InvitePeople from "../components/InvitePeople";

const STANCES = [
  { id: "for", label: "Agree" },
  { id: "against", label: "Disagree" },
  { id: "depends", label: "It depends" },
];

/**
 * Conversion-first brand landing.
 * Value first (today’s question + stance), then signup. Age/terms stay on account creation.
 */
export default function Landing() {
  const softLaunch = isSoftLaunchWindow();
  const navigate = useNavigate();
  const question = useMemo(() => todaysSquareQuestion(), []);
  const [stance, setStance] = useState("");

  function continueWithStance(nextStance) {
    const side = nextStance || stance;
    if (!side) return;
    try {
      sessionStorage.setItem(
        "bx_landing_take",
        JSON.stringify({ question, stance: side, at: Date.now() })
      );
    } catch {
      /* ignore */
    }
    navigate(`/signup?next=${encodeURIComponent("/feed?welcome=1")}`);
  }

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
          <p className="bx-home-hero-tag">India&apos;s conversation network</p>
          {softLaunch ? (
            <p className="bx-home-hero-soft" role="status">
              {SOFT_LAUNCH_LINE}
            </p>
          ) : null}
          <p className="bx-home-hero-line">India has opinions. Now it has a home.</p>
          <p className="bx-home-hero-sub">
            Pick a side, share your take, and meet people who care about the same conversations.
            Real people. Real context. Respectful pushback.
          </p>
          <p className="bx-home-hero-anti-ai">Human takes only. No AI slop.</p>
          <div className="bx-home-hero-ctas">
            <a href="#todays-take" className="btn btn-primary bx-home-cta-primary">
              Take today&apos;s side
            </a>
            <Link to="/signup?next=/spaces" className="btn btn-secondary bx-home-cta-secondary">
              Watch the debate
            </Link>
          </div>
          <p className="bx-home-hero-legal">
            Soft launch in your browser (phone or desktop). {APP_COMING_SOON_LINE}. Privacy and terms
            confirmation happens when you create an account — not before you know why BarathX
            matters.
          </p>
        </div>
      </section>

      <section className="bx-home-proof" aria-label="What is happening on BarathX">
        <ul className="bx-home-proof-list">
          <li>
            <strong>Today&apos;s question</strong>
            <span>One shared prompt for India</span>
          </li>
          <li>
            <strong>Agree · Disagree · It depends</strong>
            <span>Room for nuance, not only binary fights</span>
          </li>
          <li>
            <strong>Live rooms</strong>
            <span>Sided talk with real context</span>
          </li>
          <li>
            <strong>Founding 100</strong>
            <span>Early voices with real perks</span>
          </li>
        </ul>
      </section>

      <section
        id="todays-take"
        className="bx-home-section bx-home-take"
        aria-labelledby="bx-home-take-title"
      >
        <p className="bx-home-kicker">Try it first</p>
        <h2 id="bx-home-take-title">Today&apos;s question</h2>
        <p className="bx-home-take-q">{question}</p>
        <p className="bx-home-copy">
          Pick a side to continue. You&apos;ll create an account only when you&apos;re ready to post,
          reply, or join a room.
        </p>
        <div className="bx-home-stance-row" role="group" aria-label="Pick your side">
          {STANCES.map((s) => (
            <button
              key={s.id}
              type="button"
              className={`bx-home-stance-btn${stance === s.id ? " active" : ""}`}
              aria-pressed={stance === s.id}
              onClick={() => setStance(s.id)}
            >
              {s.label}
            </button>
          ))}
        </div>
        <div className="bx-home-hero-ctas">
          <button
            type="button"
            className="btn btn-primary bx-home-cta-primary"
            disabled={!stance}
            onClick={() => continueWithStance()}
          >
            {stance ? "Continue with your side" : "Pick a side to continue"}
          </button>
          <Link to="/signup?next=/spaces" className="btn btn-secondary bx-home-cta-secondary">
            Watch the debate
          </Link>
        </div>
      </section>

      <section className="bx-home-section bx-home-section-alt" aria-labelledby="bx-home-why">
        <p className="bx-home-kicker">Why BarathX</p>
        <h2 id="bx-home-why">India&apos;s conversation network for people with a point of view</h2>
        <p className="bx-home-copy">
          Take a side, meet your community, and turn your voice into opportunity. Not another feed
          to like and leave — and not a place built only for political fights. College, careers,
          creators, culture, and live sided talk, with respectful pushback.
        </p>
      </section>

      <section className="bx-home-section" aria-labelledby="bx-home-how">
        <p className="bx-home-kicker">How it works</p>
        <h2 id="bx-home-how">Value first. Account when you need it.</h2>
        <ol className="bx-home-steps">
          <li>
            <strong>See today&apos;s question.</strong> One shared prompt so you know what India is
            talking about.
          </li>
          <li>
            <strong>Pick Agree, Disagree, or It depends.</strong> Nuance is welcome.
          </li>
          <li>
            <strong>Join the room or post your reason.</strong> Sign up when you reply, vote, join a
            Circle, or host.
          </li>
        </ol>
      </section>

      <section className="bx-home-section bx-home-section-alt" aria-labelledby="bx-home-wedges">
        <p className="bx-home-kicker">Find your people</p>
        <h2 id="bx-home-wedges">Arenas now. Circles next.</h2>
        <p className="bx-home-copy">
          Start in Arenas (Startups, Sports, Politics, Entertainment, News, Spirituality). Coming
          Circles under them: Campus &amp; Careers, Builders, Creator Corner, My City, Desi Internet,
          Wellbeing, and Regional Rooms (Hindi, Telugu, Tamil, Malayalam, Marathi, Bengali,
          Hinglish).
        </p>
        <div className="bx-home-diff">
          <div>
            <h3>Arenas</h3>
            <p>National floors with sided talk — Agree / Disagree / It depends (or Fund it / Pass).</p>
          </div>
          <div>
            <h3>Circles</h3>
            <p>
              Narrower communities by college, city, language, career, and fandom — so you find your
              people fast.
            </p>
          </div>
        </div>
        <Link to="/signup?next=/arenas" className="btn btn-primary bx-home-inline-cta">
          Explore Arenas
        </Link>
      </section>

      <section className="bx-home-section" aria-labelledby="bx-home-founding">
        <p className="bx-home-kicker">Founding 100</p>
        <h2 id="bx-home-founding">Be one of BarathX&apos;s first recognized voices</h2>
        <div className="bx-home-founding-card">
          <p className="bx-home-copy">
            Early status should mean reach, access, and opportunity — not only controversy.
          </p>
          <ul className="bx-home-founding-perks">
            <li>Founder badge on your profile</li>
            <li>Priority visibility in your favorite Arena</li>
            <li>Invite to private creator / community rooms</li>
            <li>Early access to new features</li>
            <li>Eligibility for creator and ambassador opportunities</li>
          </ul>
          <p className="bx-home-copy bx-home-founding-paths">
            Multiple paths in: high-quality takes, helpful replies, community hosting, creator
            referrals, and consistent participation.
          </p>
        </div>
        <Link to="/signup?next=/rewards" className="btn btn-secondary bx-home-inline-cta">
          How Founding works
        </Link>
      </section>

      <section className="bx-home-section bx-home-section-alt" aria-labelledby="bx-home-invite">
        <p className="bx-home-kicker">People</p>
        <InvitePeople />
      </section>

      <section className="bx-home-section bx-home-section-alt" aria-labelledby="bx-home-apps">
        <p className="bx-home-kicker">Apps</p>
        <h2 id="bx-home-apps">Soft launch in browser · apps coming soon</h2>
        <p className="bx-home-copy">
          Join on phone or desktop browser today. Apple App Store and Google Play builds are on the
          way. Android soft-launch APK: <Link to="/get-app">barathx.com/get-app</Link>.
        </p>
        <Link to="/signup" className="btn btn-primary bx-home-inline-cta">
          Join in your browser
        </Link>
      </section>

      <section className="bx-home-section" aria-labelledby="bx-home-faq">
        <p className="bx-home-kicker">FAQ</p>
        <h2 id="bx-home-faq">Straight answers</h2>
        <dl className="bx-home-faq">
          <div>
            <dt>How is this different from X?</dt>
            <dd>
              X is built for scrolling followers. BarathX starts with a shared question, sided talk
              (including It depends), and live rooms with real context.
            </dd>
          </div>
          <div>
            <dt>Do I need to accept terms before trying it?</dt>
            <dd>
              No. See today&apos;s question and pick a side first. Privacy / Terms confirm at account
              creation. Prefer phone OTP — email and Google use a bot check.
            </dd>
          </div>
          <div>
            <dt>How do you keep bots and AI slop out?</dt>
            <dd>
              Phone OTP for humans, Turnstile on email/Google when configured, AI paste rejected or
              demoted, and report / mute / block for the community.
            </dd>
          </div>
          <div>
            <dt>What&apos;s Founding 100?</dt>
            <dd>
              Early recognized voices with badge, visibility, private rooms, early features, and
              creator/ambassador eligibility — earned through quality participation, not signup
              alone.
            </dd>
          </div>
          <div>
            <dt>Is this only politics?</dt>
            <dd>
              No. Politics is one Arena. The stronger everyday wedge is college, careers, creators,
              and culture — with live sided conversation.
            </dd>
          </div>
          <div>
            <dt>Is this full of AI posts?</dt>
            <dd>No. Human takes only. No AI slop in the square.</dd>
          </div>
          <div>
            <dt>Hindi or other languages?</dt>
            <dd>
              English UI is live; Hindi and Telugu UI are already in product. More language lanes
              (Tamil, Malayalam, Marathi, Bengali, Hinglish) are next for Circles.
            </dd>
          </div>
        </dl>
      </section>

      <section className="bx-home-closing" aria-labelledby="bx-home-close">
        <LogoMark className="bx-home-closing-mark" title="" />
        <h2 id="bx-home-close">Take a side. Meet your community.</h2>
        <p className="bx-home-copy">
          BarathX is India&apos;s conversation network for people with a point of view.
        </p>
        <div className="bx-home-hero-ctas">
          <a href="#todays-take" className="btn btn-primary bx-home-cta-primary">
            Take today&apos;s side
          </a>
          <a
            className="btn btn-secondary bx-home-cta-secondary"
            href={WHATSAPP_COMMUNITY}
            target="_blank"
            rel="noreferrer"
          >
            WhatsApp Community
          </a>
        </div>
        <p className="bx-home-closing-follow">
          Channel →{" "}
          <a href={WHATSAPP_CHANNEL} target="_blank" rel="noreferrer">
            WhatsApp Channel
          </a>
          {" · "}
          X →{" "}
          <a href={X_PROFILE} target="_blank" rel="noreferrer">
            @getbaratx
          </a>
          {" · "}
          IG →{" "}
          <a href={IG_PROFILE} target="_blank" rel="noreferrer">
            @getbaratx
          </a>
          {" · "}
          <Link to="/early-issues">Early issues</Link>
        </p>
      </section>

      <footer className="bx-home-foot">
        <span>© {new Date().getFullYear()} BarathX</span>
        <span className="bx-home-foot-links">
          <Link to="/guidelines">Guidelines</Link>
          <Link to="/early-issues">Early issues</Link>
          <Link to="/terms">Terms</Link>
          <Link to="/privacy">Privacy</Link>
          <a href="https://barathx.com">barathx.com</a>
        </span>
      </footer>
    </div>
  );
}
