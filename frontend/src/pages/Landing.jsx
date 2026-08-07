import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import Logo, { LogoMark } from "../components/Logo";
import { IconPhone } from "../components/Icons";
import GoogleSignInButton from "../components/GoogleSignInButton";

/**
 * Public GTM entry — same split brand shell as Login (plain dark + orange BX).
 */
export default function Landing() {
  const navigate = useNavigate();
  const [emailOrUser, setEmailOrUser] = useState("");
  const [confirmAge18, setConfirmAge18] = useState(false);
  const [ageError, setAgeError] = useState("");

  function handleNext(e) {
    e.preventDefault();
    if (!confirmAge18) {
      setAgeError("You must be 18 or older to join BaratX. Confirm your age to continue.");
      return;
    }
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

  function goPhoneSignup() {
    if (!confirmAge18) {
      setAgeError("You must be 18 or older to join BaratX. Confirm your age to continue.");
      return;
    }
    navigate("/signup?method=phone");
  }

  return (
    <div className="bx-login-page">
      <aside className="bx-login-brand">
        <div className="bx-login-brand-inner">
          <Logo variant="full" className="bx-login-brand-logo" title="BaratX" />
          <p className="bx-login-tagline">India&apos;s public square</p>
        </div>
        <div className="bx-login-brand-dots" aria-hidden="true" />
      </aside>

      <main className="bx-login-main">
        <div className="bx-login-card">
          <div className="bx-login-card-head">
            <span className="bx-login-accent-line brand" aria-hidden="true" />
            <LogoMark className="bx-login-card-mark" title="" />
            <span className="bx-login-accent-line green" aria-hidden="true" />
          </div>

          <h1 className="bx-login-title">Join BaratX</h1>
          <p className="bx-login-sub">Short posts. Real replies. Start with Google.</p>

          <div className="x-auth-stack">
            <label className="age-gate">
              <input
                type="checkbox"
                checked={confirmAge18}
                onChange={(e) => {
                  setConfirmAge18(e.target.checked);
                  if (e.target.checked) setAgeError("");
                }}
              />
              <span>
                I confirm I am <strong>18 or older</strong>. BaratX is for adults only.
              </span>
            </label>

            <GoogleSignInButton
              label="Continue with Google"
              confirmAge18={confirmAge18}
              requireAgeConfirm
              onError={setAgeError}
            />

            <div className="x-auth-or bx-login-or" role="separator">
              <span>or continue with email</span>
            </div>

            <form className="bx-login-form" onSubmit={handleNext}>
              <label className="bx-field">
                Email or username
                <span className="bx-field-control">
                  <span className="bx-field-icon" aria-hidden="true">
                    <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="1.8">
                      <rect x="3" y="5" width="18" height="14" rx="2" />
                      <path d="M3 7l9 7 9-7" />
                    </svg>
                  </span>
                  <input
                    type="text"
                    value={emailOrUser}
                    onChange={(e) => setEmailOrUser(e.target.value)}
                    autoComplete="username"
                    placeholder="name@email.com"
                  />
                </span>
              </label>
              <button type="submit" className="bx-login-submit" disabled={!confirmAge18}>
                Continue with email
                <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2.2" aria-hidden>
                  <path d="M5 12h14M13 6l6 6-6 6" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
              </button>
            </form>

            <button
              type="button"
              className="x-btn x-btn-phone bx-landing-phone"
              onClick={goPhoneSignup}
              disabled={!confirmAge18}
            >
              <IconPhone className="x-btn-icon" />
              Continue with phone
            </button>

            {ageError && <p className="error">{ageError}</p>}

            <p className="x-legal bx-login-legal">
              By signing up, you confirm you are 18+ and agree to the{" "}
              <Link to="/terms">Terms of Service</Link> and{" "}
              <Link to="/privacy">Privacy Policy</Link>.
            </p>

            <p className="bx-login-switch">
              Already have an account? <Link to={signInPath()}>Sign in</Link>
            </p>
          </div>
        </div>

        <p className="bx-login-trust">
          <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden>
            <path d="M12 3l8 3v6c0 5-3.5 8.5-8 10-4.5-1.5-8-5-8-10V6l8-3z" />
          </svg>
          HTTPS · Passwords hashed · We don&apos;t sell your data · 18+
        </p>
      </main>
    </div>
  );
}
