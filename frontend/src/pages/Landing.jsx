import { useEffect, useMemo, useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { api } from "../api";
import { useAuth } from "../context/AuthContext";
import GoogleSignInButton from "../components/GoogleSignInButton";
import PhoneField from "../components/PhoneField";
import Logo, { LogoMark } from "../components/Logo";
import { isSoftLaunchWindow, SOFT_LAUNCH_LINE } from "../softLaunch";
import { todaysSquareQuestion } from "../square";

/**
 * Facebook-style single-viewport home: brand left, log in right.
 * Theme-aware (midnight / saffron / monsoon / ink) via CSS variables.
 */
export default function Landing() {
  const softLaunch = isSoftLaunchWindow();
  const [params] = useSearchParams();
  const navigate = useNavigate();
  const { login } = useAuth();
  const question = useMemo(() => todaysSquareQuestion(), []);

  const preferPhone = params.get("method") === "phone";
  const [method, setMethod] = useState(preferPhone ? "phone" : "email");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  const [email, setEmail] = useState(params.get("email") || params.get("username") || "");
  const [password, setPassword] = useState("");
  const [region, setRegion] = useState("IN");
  const [phone, setPhone] = useState("+91");
  const [otpSent, setOtpSent] = useState(false);
  const [otp, setOtp] = useState("");
  const [devOtp, setDevOtp] = useState("");

  const nextPath = (() => {
    const raw = (params.get("next") || "").trim();
    if (raw.startsWith("/") && !raw.startsWith("//") && !raw.includes("://")) return raw;
    return "/home";
  })();

  useEffect(() => {
    try {
      if (nextPath && nextPath !== "/home" && nextPath !== "/feed") {
        sessionStorage.setItem("bx_next", nextPath);
      }
    } catch {
      /* ignore */
    }
  }, [nextPath]);

  function goBackFromOtp() {
    setOtpSent(false);
    setOtp("");
    setDevOtp("");
    setError("");
  }

  async function handleEmailLogin(e) {
    e.preventDefault();
    setError("");
    setBusy(true);
    try {
      const { access_token } = await api.loginEmail({ email: email.trim(), password });
      login(access_token);
      navigate(nextPath);
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  async function handleRequestOtp(e) {
    e.preventDefault();
    setError("");
    setBusy(true);
    try {
      const res = await api.loginPhoneRequestOtp(phone, region);
      setOtpSent(true);
      setDevOtp(res.dev_otp || "");
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  async function handleVerifyOtp(e) {
    e.preventDefault();
    setError("");
    setBusy(true);
    try {
      const { access_token } = await api.loginPhoneVerify({ phone, otp, region });
      login(access_token);
      navigate(nextPath);
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="bx-gate">
      <aside className="bx-gate-brand">
        <div className="bx-gate-brand-top">
          <Logo variant="full" className="bx-gate-logo" title="BarathX" />
          {softLaunch ? (
            <p className="bx-gate-soft" role="status">
              {SOFT_LAUNCH_LINE}
            </p>
          ) : null}
        </div>

        <div className="bx-gate-collage" aria-hidden="true">
          <div className="bx-gate-card bx-gate-card-a">
            <span className="bx-gate-card-kicker">Square</span>
            <p>{question}</p>
          </div>
          <div className="bx-gate-card bx-gate-card-b">
            <span>Campus · City · Builders</span>
          </div>
          <div className="bx-gate-card bx-gate-card-c">
            <span>Human takes only</span>
          </div>
          <ul className="bx-gate-sides">
            <li>Agree</li>
            <li>Disagree</li>
            <li>It depends</li>
          </ul>
        </div>

        <div className="bx-gate-headline">
          <p className="bx-gate-tag">India&apos;s conversation network</p>
          <h1>
            India has opinions.
            <span>
              {" "}
              Now it has a <em>home</em>.
            </span>
          </h1>
        </div>
      </aside>

      <main className="bx-gate-main">
        <div className="bx-gate-panel">
          <div className="bx-gate-panel-mark" aria-hidden="true">
            <LogoMark title="" />
          </div>
          <h2 className="bx-gate-title">Log into BarathX</h2>
          <p className="bx-gate-sub">Prefer phone OTP — real people only.</p>

          {!otpSent && (
            <div className="method-toggle bx-gate-methods">
              <button
                type="button"
                className={method === "phone" ? "active" : ""}
                onClick={() => {
                  setMethod("phone");
                  setError("");
                }}
              >
                Phone
              </button>
              <button
                type="button"
                className={method === "email" ? "active" : ""}
                onClick={() => {
                  setMethod("email");
                  setError("");
                }}
              >
                Email
              </button>
            </div>
          )}

          {error ? <div className="error">{error}</div> : null}

          {method === "email" ? (
            <form className="bx-gate-form" onSubmit={handleEmailLogin}>
              <label className="bx-field">
                Email or phone
                <input
                  type="text"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  autoComplete="username"
                  placeholder="Email or mobile number"
                  required
                />
              </label>
              <label className="bx-field">
                Password
                <span className="bx-field-control">
                  <input
                    type={showPassword ? "text" : "password"}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    autoComplete="current-password"
                    placeholder="Password"
                    required
                  />
                  <button
                    type="button"
                    className="bx-field-eye"
                    onClick={() => setShowPassword((v) => !v)}
                    aria-label={showPassword ? "Hide password" : "Show password"}
                  >
                    {showPassword ? "Hide" : "Show"}
                  </button>
                </span>
              </label>
              <button type="submit" className="bx-gate-submit" disabled={busy}>
                {busy ? "Logging in…" : "Log in"}
              </button>
              <p className="bx-gate-forgot">
                <Link to="/forgot-password">Forgot password?</Link>
              </p>
            </form>
          ) : !otpSent ? (
            <form className="bx-gate-form" onSubmit={handleRequestOtp}>
              <PhoneField
                region={region}
                phone={phone}
                onRegionChange={setRegion}
                onPhoneChange={setPhone}
              />
              <button type="submit" className="bx-gate-submit" disabled={busy}>
                {busy ? "Sending OTP…" : "Send OTP"}
              </button>
            </form>
          ) : (
            <form className="bx-gate-form" onSubmit={handleVerifyOtp}>
              <p className="hint">
                OTP sent to <strong>{phone}</strong>
                {devOtp ? (
                  <>
                    {" "}
                    (Demo: <b>{devOtp}</b>)
                  </>
                ) : null}
                .
              </p>
              <label className="bx-field">
                Enter OTP
                <input
                  value={otp}
                  onChange={(e) => setOtp(e.target.value.replace(/\D/g, "").slice(0, 6))}
                  inputMode="numeric"
                  autoComplete="one-time-code"
                  maxLength={6}
                  pattern="[0-9]{6}"
                  required
                />
              </label>
              <button type="submit" className="bx-gate-submit" disabled={busy}>
                {busy ? "Verifying…" : "Log in"}
              </button>
              <button type="button" className="auth-back-btn" onClick={goBackFromOtp} disabled={busy}>
                ← Change phone number
              </button>
            </form>
          )}

          {!otpSent ? (
            <>
              <div className="x-auth-or bx-gate-or" role="separator">
                <span>or</span>
              </div>
              <GoogleSignInButton label="Continue with Google" onError={setError} />
              <Link to="/signup" className="bx-gate-create">
                Create new account
              </Link>
            </>
          ) : null}
        </div>
      </main>
    </div>
  );
}
