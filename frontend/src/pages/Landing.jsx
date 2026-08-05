import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { LogoMark } from "../components/Logo";
import { IconPhone } from "../components/Icons";
import GoogleSignInButton from "../components/GoogleSignInButton";

/**
 * X-inspired landing: brand-dominant right column + auth actions on the left.
 * India theme via saffron CTAs / navy links (CSS tokens). App Store QR later.
 */
export default function Landing() {
  const navigate = useNavigate();
  const [emailOrUser, setEmailOrUser] = useState("");

  function handleNext(e) {
    e.preventDefault();
    const q = emailOrUser.trim();
    if (q) {
      navigate(`/login?email=${encodeURIComponent(q)}`);
    } else {
      navigate("/login");
    }
  }

  return (
    <div className="x-landing">
      <div className="x-landing-auth">
        <div className="x-landing-auth-inner">
          <LogoMark className="x-landing-mark-sm" title="BaratX" />
          <h1 className="x-landing-headline">Happening now</h1>
          <h2 className="x-landing-subhead">Join BaratX today.</h2>

          <div className="x-auth-stack">
            <button
              type="button"
              className="x-btn x-btn-phone"
              onClick={() => navigate("/signup?method=phone")}
            >
              <IconPhone className="x-btn-icon" />
              Continue with phone
            </button>

            <GoogleSignInButton label="Continue with Google" />

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
                Next
              </button>
            </form>

            <p className="x-legal">
              By signing up, you agree to the{" "}
              <a href="#terms">Terms of Service</a> and{" "}
              <a href="#privacy">Privacy Policy</a>, including Cookie Use.
            </p>

            <div className="x-have-account">
              <p>Already have an account?</p>
              <Link to="/login" className="x-btn x-btn-outline">
                Sign in
              </Link>
              <Link to="/signup" className="x-create-link">
                Create account with email
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
      </div>
    </div>
  );
}
