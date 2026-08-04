import { Link } from "react-router-dom";
import Logo, { LogoMark } from "../components/Logo";

export default function Landing() {
  return (
    <div className="landing">
      <div className="landing-hero">
        <LogoMark className="landing-logo-mark" title="BaratX" />
        <h1 className="landing-logo-title">
          <Logo variant="wordmark" />
        </h1>
        <p className="landing-tagline">
          A place to speak, built for India — in Telugu, Hindi, and English.
        </p>
        <p className="landing-sub">
          Your posts, your language, your community — moderated by rules you
          can see, not a black box on the other side of the world.
        </p>
        <div className="landing-cta">
          <Link to="/signup" className="btn-primary">
            Create account
          </Link>
          <Link to="/login" className="btn-secondary">
            Log in
          </Link>
        </div>
      </div>

      <div className="landing-features">
        <div className="feature">
          <span className="feature-icon">🗣️</span>
          <h3>Your language</h3>
          <p>Post and read in Telugu, Hindi, or English — more languages coming.</p>
        </div>
        <div className="feature">
          <span className="feature-icon">🇮🇳</span>
          <h3>Built for India</h3>
          <p>A community platform for everyone, across every region and belief.</p>
        </div>
        <div className="feature">
          <span className="feature-icon">🛡️</span>
          <h3>Clear rules</h3>
          <p>Moderation you can understand, with a real appeals process — not a mystery.</p>
        </div>
      </div>
    </div>
  );
}
