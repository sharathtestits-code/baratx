import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api } from "../api";
import { useAuth } from "../context/AuthContext";

export default function Login() {
  const [method, setMethod] = useState("email");
  const navigate = useNavigate();
  const { login } = useAuth();

  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [phone, setPhone] = useState("+91");
  const [otpSent, setOtpSent] = useState(false);
  const [otp, setOtp] = useState("");
  const [devOtp, setDevOtp] = useState("");

  async function handleEmailLogin(e) {
    e.preventDefault();
    setError("");
    setBusy(true);
    try {
      const { access_token } = await api.loginEmail({ email, password });
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
      const res = await api.loginPhoneRequestOtp(phone);
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
      const { access_token } = await api.loginPhoneVerify({ phone, otp });
      login(access_token);
      navigate("/feed");
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="auth-card">
      <h1>Log in</h1>

      <div className="method-toggle">
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

      {error && <div className="error">{error}</div>}

      {method === "email" ? (
        <form onSubmit={handleEmailLogin}>
          <label>
            Email
            <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
          </label>
          <label>
            Password
            <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
          </label>
          <button type="submit" disabled={busy}>
            {busy ? "Logging in..." : "Log in"}
          </button>
        </form>
      ) : !otpSent ? (
        <form onSubmit={handleRequestOtp}>
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
            OTP sent to {phone}. {devOtp && <>(Demo mode — your code is <b>{devOtp}</b>)</>}
          </p>
          <label>
            Enter OTP
            <input value={otp} onChange={(e) => setOtp(e.target.value)} maxLength={6} required />
          </label>
          <button type="submit" disabled={busy}>
            {busy ? "Verifying..." : "Verify & log in"}
          </button>
        </form>
      )}

      <p className="switch-link">
        New here? <Link to="/signup">Create an account</Link>
      </p>
    </div>
  );
}
