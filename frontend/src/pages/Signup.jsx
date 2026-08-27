import { useEffect, useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { api, arenasApi } from "../api";
import { useAuth } from "../context/AuthContext";
import AgeConsentFields from "../components/AgeConsentFields";
import GoogleSignInButton from "../components/GoogleSignInButton";
import PhoneField from "../components/PhoneField";
import TurnstileWidget, { useTurnstileConfig } from "../components/TurnstileWidget";
import { parseDobAndAge } from "../ageConsent";
import { validateUsername } from "../username";
import { safeNextPath } from "../safeNextPath";

export default function Signup() {
  const [params] = useSearchParams();
  const [method, setMethod] = useState(params.get("method") === "email" ? "email" : "phone");
  const navigate = useNavigate();
  const { login } = useAuth();
  const { required: needBotCheck } = useTurnstileConfig();

  const [username, setUsername] = useState(params.get("username") || "");
  const [displayName, setDisplayName] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [acceptPrivacy, setAcceptPrivacy] = useState(false);
  const [dateOfBirth, setDateOfBirth] = useState("");
  const [confirmAge18, setConfirmAge18] = useState(false);
  const [turnstileToken, setTurnstileToken] = useState("");

  const [email, setEmail] = useState(params.get("email") || "");
  const [password, setPassword] = useState("");

  const [region, setRegion] = useState("IN");
  const [phone, setPhone] = useState("+91");
  const [otpSent, setOtpSent] = useState(false);
  const [otp, setOtp] = useState("");
  const [devOtp, setDevOtp] = useState("");
  const preferredArena =
    params.get("arena") ||
    (typeof sessionStorage !== "undefined" ? sessionStorage.getItem("bx_arena") : "") ||
    "";
  const nextPath = safeNextPath(params.get("next") || "", "");

  useEffect(() => {
    const a = params.get("arena");
    if (a) sessionStorage.setItem("bx_arena", a);
    if (nextPath) sessionStorage.setItem("bx_next", nextPath);
  }, [params, nextPath]);

  function afterJoinPath() {
    const stored =
      (typeof sessionStorage !== "undefined" && sessionStorage.getItem("bx_next")) || nextPath;
    const safe = safeNextPath(stored || "", "/feed?welcome=1");
    sessionStorage.removeItem("bx_next");
    return safe;
  }

  function goAfterSignup() {
    sessionStorage.setItem("bx_welcome", "1");
    const dest = afterJoinPath();
    if (dest === "/feed" || dest.startsWith("/feed?")) {
      navigate(dest.includes("welcome") ? dest : "/feed?welcome=1");
      return;
    }
    navigate(dest);
  }

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

  function requireConsent({ needTurnstile = false } = {}) {
    if (!acceptPrivacy) {
      setError("Accept the Privacy Policy (DPDP) to create an account.");
      return false;
    }
    const dobCheck = parseDobAndAge(dateOfBirth);
    if (!dobCheck.ok) {
      setError(dobCheck.error);
      return false;
    }
    if (!confirmAge18) {
      setError("Confirm you are 18 or older and that your date of birth is accurate.");
      return false;
    }
    if (needTurnstile && needBotCheck && !turnstileToken) {
      setError("Complete the security check (or use phone OTP — no bot check needed).");
      return false;
    }
    return true;
  }

  function goBackFromOtp() {
    setOtpSent(false);
    setOtp("");
    setDevOtp("");
    setError("");
  }

  async function handleEmailSignup(e) {
    e.preventDefault();
    if (!requireConsent({ needTurnstile: true })) return;
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
        date_of_birth: dateOfBirth,
        confirm_age_18: true,
        accept_privacy: true,
        ...(turnstileToken ? { turnstile_token: turnstileToken } : {}),
      });
      if (res.dev_verify_url) {
        sessionStorage.setItem("bx_dev_verify_url", res.dev_verify_url);
      }
      login(res.access_token);
      await joinArenaFromParams(res.access_token);
      goAfterSignup();
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  async function handleRequestOtp(e) {
    e.preventDefault();
    if (!requireConsent()) return;
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
    if (!requireConsent()) return;
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
        date_of_birth: dateOfBirth,
        confirm_age_18: true,
        accept_privacy: true,
      });
      login(access_token);
      await joinArenaFromParams(access_token);
      goAfterSignup();
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  const usernameHint = (
    <span className="hint">3–20 chars. Letters, numbers, _ . - (e.g. rahul_99 or john.doe)</span>
  );

  const ageGate = (
    <AgeConsentFields
      idPrefix="signup"
      dateOfBirth={dateOfBirth}
      onDateOfBirthChange={(v) => {
        setDateOfBirth(v);
        setError("");
      }}
      confirmAge18={confirmAge18}
      onConfirmAge18Change={(v) => {
        setConfirmAge18(v);
        if (v) setError("");
      }}
    />
  );

  const privacyGate = (
    <label className="age-gate">
      <input
        type="checkbox"
        checked={acceptPrivacy}
        onChange={(e) => {
          setAcceptPrivacy(e.target.checked);
          if (e.target.checked) setError("");
        }}
      />
      <span>
        I have read and accept the{" "}
        <Link to="/privacy" target="_blank" rel="noopener noreferrer">
          Privacy Policy
        </Link>{" "}
        (India DPDP) and{" "}
        <Link to="/terms" target="_blank" rel="noopener noreferrer">
          Terms
        </Link>
        .
      </span>
    </label>
  );

  const botGate = needBotCheck ? (
    <TurnstileWidget
      onToken={(tok) => {
        setTurnstileToken(tok || "");
        if (tok) setError("");
      }}
    />
  ) : null;

  const canSubmit =
    acceptPrivacy && confirmAge18 && Boolean(dateOfBirth) && (!needBotCheck || turnstileToken);

  return (
    <div className="auth-card auth-card-x">
      <h1>Create your account</h1>
      <p className="hint auth-human-pref">
        Prefer <strong>phone OTP</strong> — built for real people. Email / Google use a bot check.
        BarathX is <strong>18+</strong>.
      </p>

      {!otpSent && (
        <>
          {ageGate}
          {privacyGate}
          {botGate}
          <GoogleSignInButton
            label="Sign up with Google"
            onError={setError}
            acceptPrivacy={acceptPrivacy}
            requirePrivacyConfirm
            dateOfBirth={dateOfBirth}
            confirmAge18={confirmAge18}
            requireAgeConfirm
            turnstileToken={turnstileToken}
            requireTurnstile={needBotCheck}
          />

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
          <button type="submit" disabled={busy || !canSubmit}>
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
          <button type="submit" disabled={busy || !acceptPrivacy || !confirmAge18 || !dateOfBirth}>
            {busy ? "Sending OTP..." : "Send OTP"}
          </button>
        </form>
      ) : (
        <form onSubmit={handleVerifyOtp}>
          <p className="hint">
            OTP sent to <strong>{phone}</strong>.{" "}
            {devOtp && (
              <>
                (Demo mode, your code is <b>{devOtp}</b>)
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
          {ageGate}
          {privacyGate}
          <button type="submit" disabled={busy || !acceptPrivacy || !confirmAge18 || !dateOfBirth}>
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
