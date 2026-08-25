import { useEffect, useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { api } from "../api";
import { useAuth } from "../context/AuthContext";
import Logo, { LogoMark } from "../components/Logo";
import PhoneField from "../components/PhoneField";
import { applyGuestShellTheme } from "../theme";

/**
 * Facebook-style home gate — matches approved midnight mockup.
 * Outside is always dark; theme picker only in Settings after signup.
 */
export default function Landing() {
  const [params] = useSearchParams();
  const navigate = useNavigate();
  const { login } = useAuth();

  const [mode, setMode] = useState(params.get("method") === "phone" ? "phone" : "email");
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
    applyGuestShellTheme();
  }, []);

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
        <Logo variant="full" className="bx-gate-logo" title="BarathX" />

        <div className="bx-gate-collage" aria-hidden="true">
          <img className="bx-gate-shot bx-gate-shot-1" src="/gate/p1.jpg" alt="" />
          <img className="bx-gate-shot bx-gate-shot-2" src="/gate/p2.jpg" alt="" />
          <img className="bx-gate-shot bx-gate-shot-3" src="/gate/p3.jpg" alt="" />
          <img className="bx-gate-shot bx-gate-shot-4" src="/gate/p4.jpg" alt="" />
          <span className="bx-gate-chip bx-gate-chip-agree">Agree</span>
          <span className="bx-gate-chip bx-gate-chip-disagree">Disagree</span>
          <span className="bx-gate-chip bx-gate-chip-depends">It depends</span>
        </div>

        <h1 className="bx-gate-headline">
          India has opinions.
          <br />
          Now it has a <em>home.</em>
        </h1>
      </aside>

      <main className="bx-gate-main">
        <div className="bx-gate-panel">
          <h2 className="bx-gate-title">Log into BarathX</h2>

          {error ? <div className="error">{error}</div> : null}

          {mode === "email" ? (
            <form className="bx-gate-form" onSubmit={handleEmailLogin}>
              <label className="bx-gate-field">
                <span className="bx-gate-field-icon" aria-hidden="true">
                  <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="1.8">
                    <circle cx="12" cy="8" r="3.5" />
                    <path d="M5 19c1.8-3.2 4.2-4.5 7-4.5s5.2 1.3 7 4.5" />
                  </svg>
                </span>
                <input
                  type="text"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  autoComplete="username"
                  placeholder="Email or phone"
                  required
                />
              </label>
              <label className="bx-gate-field">
                <span className="bx-gate-field-icon" aria-hidden="true">
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
                  placeholder="Password"
                  required
                />
                <button
                  type="button"
                  className="bx-gate-eye"
                  onClick={() => setShowPassword((v) => !v)}
                  aria-label={showPassword ? "Hide password" : "Show password"}
                >
                  <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="1.8">
                    {showPassword ? (
                      <path d="M3 3l18 18M10.6 10.6A2 2 0 0012 14M9.9 5.1A10 10 0 0121 12c-.7 1-1.6 2-2.6 2.8M6 6.2C4.4 7.5 3 9.5 3 12c1.8 3.5 5.2 6 9 6 1.2 0 2.4-.2 3.5-.7" />
                    ) : (
                      <>
                        <path d="M2 12s3.5-6 10-6 10 6 10 6-3.5 6-10 6S2 12 2 12z" />
                        <circle cx="12" cy="12" r="2.5" />
                      </>
                    )}
                  </svg>
                </button>
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
              <button
                type="button"
                className="bx-gate-text-switch"
                onClick={() => {
                  setMode("email");
                  setError("");
                }}
              >
                Use email instead
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
              </p>
              <label className="bx-gate-field bx-gate-field-plain">
                <input
                  value={otp}
                  onChange={(e) => setOtp(e.target.value.replace(/\D/g, "").slice(0, 6))}
                  inputMode="numeric"
                  autoComplete="one-time-code"
                  maxLength={6}
                  pattern="[0-9]{6}"
                  placeholder="Enter OTP"
                  required
                />
              </label>
              <button type="submit" className="bx-gate-submit" disabled={busy}>
                {busy ? "Verifying…" : "Log in"}
              </button>
              <button type="button" className="bx-gate-text-switch" onClick={goBackFromOtp} disabled={busy}>
                ← Change phone number
              </button>
            </form>
          )}

          {mode === "email" || !otpSent ? (
            <Link to="/signup" className="bx-gate-create">
              Create new account
            </Link>
          ) : null}

          {mode === "email" ? (
            <p className="bx-gate-otp-hint">
              Prefer phone OTP?{" "}
              <button
                type="button"
                className="bx-gate-otp-link"
                onClick={() => {
                  setMode("phone");
                  setError("");
                }}
              >
                Log in with phone
              </button>
            </p>
          ) : null}

          <div className="bx-gate-foot">
            <span className="bx-gate-foot-line" aria-hidden="true" />
            <LogoMark className="bx-gate-foot-mark" title="" />
            <span className="bx-gate-foot-line" aria-hidden="true" />
          </div>
        </div>
      </main>
    </div>
  );
}
