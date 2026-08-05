import { useEffect, useState } from "react";
import { api } from "../api";
import { useAuth } from "../context/AuthContext";

export default function EmailVerifyBanner() {
  const { token, user, updateUser } = useAuth();
  const [busy, setBusy] = useState(false);
  const [note, setNote] = useState("");
  const [devUrl, setDevUrl] = useState(() => sessionStorage.getItem("bx_dev_verify_url") || "");

  useEffect(() => {
    if (user?.is_email_verified) {
      sessionStorage.removeItem("bx_dev_verify_url");
      setDevUrl("");
    }
  }, [user?.is_email_verified]);

  if (!user || !user.email || user.is_email_verified) return null;

  async function resend() {
    setBusy(true);
    setNote("");
    try {
      const res = await api.resendVerification(token);
      setNote(res.message);
      if (res.dev_verify_url) {
        setDevUrl(res.dev_verify_url);
        sessionStorage.setItem("bx_dev_verify_url", res.dev_verify_url);
      }
      const me = await api.me(token);
      updateUser(me);
    } catch (err) {
      setNote(err.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="verify-banner" role="status">
      <div className="verify-banner-text">
        <strong>Confirm your email</strong>
        <span> We sent a link to {user.email}. Activate your account to stay secure.</span>
        {note && <div className="verify-banner-note">{note}</div>}
        {devUrl && (
          <div className="verify-banner-note">
            Dev link:{" "}
            <a href={devUrl}>{devUrl}</a>
          </div>
        )}
      </div>
      <button type="button" className="verify-banner-btn" onClick={resend} disabled={busy}>
        {busy ? "Sending…" : "Resend"}
      </button>
    </div>
  );
}
