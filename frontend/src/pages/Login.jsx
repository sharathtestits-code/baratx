import { useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { api } from "../api";
import { useAuth } from "../context/AuthContext";
import GoogleSignInButton from "../components/GoogleSignInButton";
import PhoneField from "../components/PhoneField";
import Logo, { LogoMark } from "../components/Logo";
import { isNativeApp } from "../native";

export default function Login() {
  const [params] = useSearchParams();
  const initialId = params.get("email") || params.get("username") || "";
  const native = isNativeApp();
  const preferPhone = params.get("method") === "phone" || (native && params.get("method") !== "email");
  const [method, setMethod] = useState(preferPhone ? "phone" : "email");
  const navigate = useNavigate();
  const { login } = useAuth();

  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  const [email, setEmail] = useState(initialId);
  const [password, setPassword] = useState("");

  const [region, setRegion] = useState("IN");
  const [phone, setPhone] = useState("+91");
  const [otpSent, setOtpSent] = useState(false);
  const [otp, setOtp] = useState("");
  const [devOtp, setDevOtp] = useState("");

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
      navigate("/feed");
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
      navigate("/feed");
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="bx-login-page">
      <aside className="bx-login-brand" aria-hidden="false">
        <div className="bx-login-brand-inner">
          <Logo variant="full" className="bx-login-brand-logo" title="BarathX" />
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

          <h1 className="bx-login-title">Welcome back</h1>
          <p className="bx-login-sub">Log in to join BarathX</p>

          {!otpSent && (
            <div className="method-toggle bx-login-methods">
              <button
                className={method === "email" ? "active" : ""}
                onClick={() => {
                  setMethod("email");
                  setError("");
                }}
                type="button"
              >
                Email
              </button>
              <button
                className={method === "phone" ? "active" : ""}
                onClick={() => {
                  setMethod("phone");
                  setError("");
                }}
                type="button"
              >
                Phone
              </button>
            </div>
          )}

          {error && <div className="error">{error}</div>}

          {method === "email" ? (
            <form className="bx-login-form" onSubmit={handleEmailLogin}>
              <label className="bx-field">
                Email
                <span className="bx-field-control">
                  <span className="bx-field-icon" aria-hidden="true">
                    <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="1.8">
                      <rect x="3" y="5" width="18" height="14" rx="2" />
                      <path d="M3 7l9 7 9-7" />
                    </svg>
                  </span>
                  <input
                    type="text"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    autoComplete="username"
                    placeholder="you@example.com"
                    required
                  />
                </span>
              </label>
              <label className="bx-field">
                Password
                <span className="bx-field-control">
                  <span className="bx-field-icon" aria-hidden="true">
                    <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="1.8">
                      <rect x="5" y="11" width="14" height="10" rx="2" />
                      <path d="M8 11V8a4 4 0 018 0v3" />
                    </svg>
                  </span>
                  <input
                    type={showPassword ? "text" : "password"}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    autoComplete="current-password"
                    placeholder="••••••••"
                    required
                  />
                  <button
                    type="button"
                    className="bx-field-eye"
                    onClick={() => setShowPassword((v) => !v)}
                    aria-label={showPassword ? "Hide password" : "Show password"}
                  >
                    <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="1.8">
                      {showPassword ? (
                        <>
                          <path d="M3 3l18 18" />
                          <path d="M10.6 10.6A2 2 0 0012 14a2 2 0 001.4-.6" />
                          <path d="M9.9 5.1A10.4 10.4 0 0121 12c-.7 1.1-1.6 2.1-2.6 2.9M6.1 6.1C4.4 7.4 3 9.5 3 12c1.8 3.5 5.2 6 9 6 1.3 0 2.5-.3 3.6-.8" />
                        </>
                      ) : (
                        <>
                          <path d="M2 12s3.5-6 10-6 10 6 10 6-3.5 6-10 6S2 12 2 12z" />
                          <circle cx="12" cy="12" r="2.5" />
                        </>
                      )}
                    </svg>
                  </button>
                </span>
              </label>
              <p className="bx-login-forgot">
                <Link to="/forgot-password">Forgot password?</Link>
              </p>
              <button type="submit" className="bx-login-submit" disabled={busy}>
                {busy ? "Logging in…" : "Enter BarathX"}
                {!busy && (
                  <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2.2" aria-hidden>
                    <path d="M5 12h14M13 6l6 6-6 6" strokeLinecap="round" strokeLinejoin="round" />
                  </svg>
                )}
              </button>
            </form>
          ) : !otpSent ? (
            <form className="bx-login-form" onSubmit={handleRequestOtp}>
              <PhoneField
                region={region}
                phone={phone}
                onRegionChange={setRegion}
                onPhoneChange={setPhone}
              />
              <button type="submit" className="bx-login-submit" disabled={busy}>
                {busy ? "Sending OTP…" : "Send OTP"}
              </button>
            </form>
          ) : (
            <form className="bx-login-form" onSubmit={handleVerifyOtp}>
              <p className="hint">
                OTP sent to <strong>{phone}</strong>.{" "}
                {devOtp && (
                  <>
                    (Demo mode — your code is <b>{devOtp}</b>)
                  </>
                )}
              </p>
              <label className="bx-field">
                Enter OTP
                <span className="bx-field-control">
                  <input
                    value={otp}
                    onChange={(e) => setOtp(e.target.value.replace(/\D/g, "").slice(0, 6))}
                    inputMode="numeric"
                    autoComplete="one-time-code"
                    maxLength={6}
                    pattern="[0-9]{6}"
                    required
                  />
                </span>
              </label>
              <button type="submit" className="bx-login-submit" disabled={busy}>
                {busy ? "Verifying…" : "Verify & enter BarathX"}
              </button>
              <button type="button" className="auth-back-btn" onClick={goBackFromOtp} disabled={busy}>
                ← Change phone number
              </button>
            </form>
          )}

          {!otpSent && !native && (
            <>
              <div className="x-auth-or bx-login-or" role="separator">
                <span>or continue with</span>
              </div>
              <GoogleSignInButton label="Continue with Google" onError={setError} confirmAge18 />
            </>
          )}
          {!otpSent && native && (
            <p className="hint bx-login-native-hint">
              In the app, use phone OTP or email above. Google Sign-In lands in a later update.
            </p>
          )}

          <p className="bx-login-switch">
            New to BarathX? <Link to="/signup">Sign up</Link>
          </p>
        </div>

        <p className="bx-login-trust">
          <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden>
            <path d="M12 3l8 3v6c0 5-3.5 8.5-8 10-4.5-1.5-8-5-8-10V6l8-3z" />
          </svg>
          Secured &amp; trusted · BarathX Square UI
        </p>
      </main>
    </div>
  );
}
