import { useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { api } from "../api";
import { useAuth } from "../context/AuthContext";
import GoogleSignInButton from "../components/GoogleSignInButton";

export default function Signup() {
  const [params] = useSearchParams();
  const [method, setMethod] = useState(params.get("method") === "email" ? "email" : "phone");
  const navigate = useNavigate();
  const { login } = useAuth();

  // shared fields
  const [username, setUsername] = useState(params.get("username") || "");
  const [displayName, setDisplayName] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  // email fields
  const [email, setEmail] = useState(params.get("email") || "");
  const [password, setPassword] = useState("");

  // phone fields
  const [phone, setPhone] = useState("+91");
  const [otpSent, setOtpSent] = useState(false);
  const [otp, setOtp] = useState("");
  const [devOtp, setDevOtp] = useState("");

  async function handleEmailSignup(e) {
    e.preventDefault();
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
        // Local/dev without SMTP — keep link available after redirect via sessionStorage
        sessionStorage.setItem("bx_dev_verify_url", res.dev_verify_url);
      }
      login(res.access_token);
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
      const res = await api.signupPhoneRequestOtp(phone);
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
      const { access_token } = await api.signupPhoneVerify({
        phone,
        otp,
        username,
        display_name: displayName,
      });
      login(access_token);
      navigate("/feed");
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="auth-card auth-card-x">
      <h1>Create your account</h1>

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

      {error && <div className="error">{error}</div>}

      {method === "email" ? (
        <form onSubmit={handleEmailSignup}>
          <label>
            Display name
            <input value={displayName} onChange={(e) => setDisplayName(e.target.value)} required />
          </label>
          <label>
            Username
            <input value={username} onChange={(e) => setUsername(e.target.value)} required />
          </label>
          <label>
            Email
            <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
          </label>
          <label>
            Password
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              minLength={8}
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
            <input value={displayName} onChange={(e) => setDisplayName(e.target.value)} required />
          </label>
          <label>
            Username
            <input value={username} onChange={(e) => setUsername(e.target.value)} required />
          </label>
          <label>
            Phone number
            <input value={phone} onChange={(e) => setPhone(e.target.value)} placeholder="+919876543210" required />
          </label>
          <button type="submit" disabled={busy}>
            {busy ? "Sending OTP..." : "Send OTP"}
          </button>
        </form>
      ) : (
        <form onSubmit={handleVerifyOtp}>
          <p className="hint">
            OTP sent to {phone}. {devOtp && <>(Demo mode — no SMS provider wired up yet, your code is <b>{devOtp}</b>)</>}
          </p>
          <label>
            Enter OTP
            <input value={otp} onChange={(e) => setOtp(e.target.value)} maxLength={6} required />
          </label>
          <button type="submit" disabled={busy}>
            {busy ? "Verifying..." : "Verify & create account"}
          </button>
        </form>
      )}

      <p className="switch-link">
        Already have an account? <Link to="/login">Log in</Link>
      </p>
    </div>
  );
}
