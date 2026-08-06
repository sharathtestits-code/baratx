import { useEffect, useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { api, arenasApi } from "../api";
import { useAuth } from "../context/AuthContext";
import GoogleSignInButton from "../components/GoogleSignInButton";
import PhoneField from "../components/PhoneField";
import { validateUsername } from "../username";

export default function Signup() {
  const [params] = useSearchParams();
  const [method, setMethod] = useState(params.get("method") === "email" ? "email" : "phone");
  const navigate = useNavigate();
  const { login } = useAuth();

  const [username, setUsername] = useState(params.get("username") || "");
  const [displayName, setDisplayName] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const [email, setEmail] = useState(params.get("email") || "");
  const [password, setPassword] = useState("");

  const [region, setRegion] = useState("IN");
  const [phone, setPhone] = useState("+91");
  const [otpSent, setOtpSent] = useState(false);
  const [otp, setOtp] = useState("");
  const [devOtp, setDevOtp] = useState("");
  const preferredArena = params.get("arena") || (typeof sessionStorage !== "undefined" ? sessionStorage.getItem("bx_arena") : "") || "";

  useEffect(() => {
    const a = params.get("arena");
    if (a) sessionStorage.setItem("bx_arena", a);
  }, [params]);

  async function joinArenaFromParams(accessToken) {
    const key = (preferredArena || "").trim().toLowerCase();
    if (!key) return;
    try {
      await arenasApi.join(accessToken, key);
      sessionStorage.removeItem("bx_arena");
    } catch {
      // non-blocking
    }
  }


  function goBackFromOtp() {
    setOtpSent(false);
    setOtp("");
    setDevOtp("");
    setError("");
  }

  async function handleEmailSignup(e) {
    e.preventDefault();
    const userErr = validateUsername(username);
    if (userErr) {
      setError(userErr);
      return;
    }
    setError("");
    setBusy(true);
    try {
      const res = await api.signupEmail({
        email,
        password,
        username,
        display_name: displayName,
      });
      if (res.dev_verify_url) {
        sessionStorage.setItem("bx_dev_verify_url", res.dev_verify_url);
      }
      login(res.access_token);
      await joinArenaFromParams(res.access_token);
      sessionStorage.setItem("bx_welcome", "1");
      navigate("/onboarding/topics");
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  async function handleRequestOtp(e) {
    e.preventDefault();
    if (!displayName.trim()) {
      setError("Enter your display name");
      return;
    }
    const userErr = validateUsername(username);
    if (userErr) {
      setError(userErr);
      return;
    }
    setError("");
    setBusy(true);
    try {
      const res = await api.signupPhoneRequestOtp(phone, region);
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
    const userErr = validateUsername(username);
    if (userErr) {
      setError(userErr);
      return;
    }
    setError("");
    setBusy(true);
    try {
      const { access_token } = await api.signupPhoneVerify({
        phone,
        otp,
        username,
        display_name: displayName,
        region,
      });
      login(access_token);
      await joinArenaFromParams(access_token);
      sessionStorage.setItem("bx_welcome", "1");
      navigate("/onboarding/topics");
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  const usernameHint = (
    <span className="hint">3–20 chars. Letters, numbers, _ . - (e.g. rahul_99 or john.doe)</span>
  );

  return (
    <div className="auth-card auth-card-x">
      <h1>Create your account</h1>

      {!otpSent && (
        <>
          <GoogleSignInButton label="Sign up with Google" onError={setError} />

          <div className="x-auth-or" role="separator">
            <span>or</span>
          </div>

          <div className="method-toggle">
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
          </div>
        </>
      )}

      {error && <div className="error">{error}</div>}

      {method === "email" ? (
        <form onSubmit={handleEmailSignup}>
          <label>
            Display name
            <input
              value={displayName}
              onChange={(e) => setDisplayName(e.target.value)}
              autoComplete="name"
              required
            />
          </label>
          <label>
            Username
            <input
              value={username}
              onChange={(e) => setUsername(e.target.value.replace(/\s/g, ""))}
              placeholder="rahul_99"
              autoComplete="username"
              inputMode="text"
              required
            />
          </label>
          {usernameHint}
          <label>
            Email
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              autoComplete="email"
              required
            />
          </label>
          <label>
            Password
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              minLength={8}
              autoComplete="new-password"
              required
            />
          </label>
          <button type="submit" disabled={busy}>
            {busy ? "Creating account..." : "Sign up"}
          </button>
        </form>
      ) : !otpSent ? (
        <form onSubmit={handleRequestOtp}>
          <label>
            Display name
            <input
              value={displayName}
              onChange={(e) => setDisplayName(e.target.value)}
              autoComplete="name"
              required
            />
          </label>
          <label>
            Username
            <input
              value={username}
              onChange={(e) => setUsername(e.target.value.replace(/\s/g, ""))}
              placeholder="rahul_99"
              autoComplete="username"
              inputMode="text"
              required
            />
          </label>
          {usernameHint}
          <PhoneField
            region={region}
            phone={phone}
            onRegionChange={setRegion}
            onPhoneChange={setPhone}
          />
          <button type="submit" disabled={busy}>
            {busy ? "Sending OTP..." : "Send OTP"}
          </button>
        </form>
      ) : (
        <form onSubmit={handleVerifyOtp}>
          <p className="hint">
            OTP sent to <strong>{phone}</strong>.{" "}
            {devOtp && (
              <>
                (Demo mode — your code is <b>{devOtp}</b>)
              </>
            )}
          </p>
          <label>
            Username
            <input
              value={username}
              onChange={(e) => setUsername(e.target.value.replace(/\s/g, ""))}
              placeholder="rahul_99"
              autoComplete="username"
              required
            />
          </label>
          {usernameHint}
          <label>
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
          <button type="submit" disabled={busy}>
            {busy ? "Verifying..." : "Verify & create account"}
          </button>
          <button type="button" className="auth-back-btn" onClick={goBackFromOtp} disabled={busy}>
            ← Change phone or details
          </button>
        </form>
      )}

      <p className="switch-link">
        Already have an account? <Link to="/login">Log in</Link>
      </p>
    </div>
  );
}
