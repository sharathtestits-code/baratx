import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { LogoMark } from "../components/Logo";
import { IconPhone } from "../components/Icons";
import GoogleSignInButton from "../components/GoogleSignInButton";

/**
 * Public GTM landing — Google-first for trust, then email, phone last.
 */
export default function Landing() {
  const navigate = useNavigate();
  const [emailOrUser, setEmailOrUser] = useState("");

  function handleNext(e) {
    e.preventDefault();
    const q = emailOrUser.trim();
    if (!q) {
      navigate("/signup?method=email");
      return;
    }
    if (q.includes("@")) {
      navigate(`/signup?method=email&email=${encodeURIComponent(q)}`);
    } else {
      navigate(`/signup?method=email&username=${encodeURIComponent(q)}`);
    }
  }

  function signInPath() {
    const q = emailOrUser.trim();
    if (!q) return "/login";
    if (q.includes("@")) return `/login?email=${encodeURIComponent(q)}`;
    return `/login?username=${encodeURIComponent(q)}`;
  }

  return (
    <div className="x-landing">
      <div className="x-landing-auth">
        <div className="x-landing-auth-inner">
          <LogoMark className="x-landing-mark-sm" title="BaratX" />
          <p className="x-landing-brand-line">BX · BaratX</p>
          <h1 className="x-landing-headline">India&apos;s public square</h1>
          <p className="x-landing-support">
            Short posts. Real replies. Start with Google — fastest and safest way in.
          </p>

          <div className="x-auth-stack">
            <GoogleSignInButton label="Continue with Google" />

            <p className="x-trust-row">HTTPS · Passwords hashed · We don’t sell your data</p>

            <div className="x-auth-or" role="separator">
              <span>or</span>
            </div>

            <form className="x-auth-email-form" onSubmit={handleNext}>
              <label className="x-field-simple">
                Email or username
                <input
                  type="text"
                  value={emailOrUser}
                  onChange={(e) => setEmailOrUser(e.target.value)}
                  autoComplete="username"
                  placeholder="name@email.com"
                />
              </label>
              <button type="submit" className="x-btn x-btn-next">
                Continue with email
              </button>
            </form>

            <button
              type="button"
              className="x-btn x-btn-phone"
              onClick={() => navigate("/signup?method=phone")}
            >
              <IconPhone className="x-btn-icon" />
              Continue with phone
            </button>

            <p className="x-legal">
              By signing up, you agree to the{" "}
              <Link to="/terms">Terms of Service</Link> and{" "}
              <Link to="/privacy">Privacy Policy</Link>.
            </p>

            <div className="x-have-account">
              <p>Already have an account?</p>
              <Link to={signInPath()} className="x-btn x-btn-outline">
                Sign in
              </Link>
              <Link to="/login?method=phone" className="x-create-link">
                Sign in with phone OTP
              </Link>
            </div>
          </div>
        </div>
      </div>

      <div className="x-landing-brand" aria-hidden="true">
        <div className="x-landing-brand-glow" />
        <LogoMark className="x-landing-mark-xl" title="" />
        <div className="x-landing-word">
          Barat<span className="x-landing-word-x">X</span>
        </div>
        <p className="x-landing-brand-tag">barathx.com</p>
      </div>
    </div>
  );
}
