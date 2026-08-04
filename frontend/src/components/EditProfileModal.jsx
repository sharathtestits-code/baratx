import { useEffect, useState } from "react";
import { api } from "../api";
import { useAuth } from "../context/AuthContext";

const LANGUAGES = [
  { value: "en", label: "English" },
  { value: "hi", label: "Hindi (हिन्दी)" },
  { value: "te", label: "Telugu (తెలుగు)" },
];

export default function EditProfileModal({ open, profile, onClose, onSaved }) {
  const { token, updateUser } = useAuth();
  const [displayName, setDisplayName] = useState("");
  const [bio, setBio] = useState("");
  const [language, setLanguage] = useState("en");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!open || !profile) return;
    setDisplayName(profile.display_name || "");
    setBio(profile.bio || "");
    setLanguage(profile.language || "en");
    setError("");
  }, [open, profile]);

  useEffect(() => {
    if (!open) return;
    function onKey(e) {
      if (e.key === "Escape") onClose();
    }
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, [open, onClose]);

  if (!open) return null;

  async function handleSubmit(e) {
    e.preventDefault();
    if (!token || busy) return;
    setBusy(true);
    setError("");
    try {
      const updated = await api.updateMe(token, {
        display_name: displayName.trim(),
        bio,
        language,
      });
      updateUser(updated);
      onSaved?.(updated);
      onClose();
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="modal-backdrop" onClick={onClose} role="presentation">
      <div
        className="modal-card"
        role="dialog"
        aria-modal="true"
        aria-labelledby="edit-profile-title"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="modal-header">
          <h2 id="edit-profile-title">Edit profile</h2>
          <button type="button" className="modal-close" onClick={onClose} aria-label="Close">
            ×
          </button>
        </div>

        <form className="modal-form" onSubmit={handleSubmit}>
          <label>
            Display name
            <input
              type="text"
              value={displayName}
              onChange={(e) => setDisplayName(e.target.value)}
              maxLength={50}
              required
            />
          </label>

          <label>
            Bio
            <textarea
              value={bio}
              onChange={(e) => setBio(e.target.value)}
              maxLength={280}
              rows={3}
              placeholder="Tell people about yourself"
            />
            <span className="char-count">{bio.length}/280</span>
          </label>

          <label>
            Language preference
            <select value={language} onChange={(e) => setLanguage(e.target.value)}>
              {LANGUAGES.map((lang) => (
                <option key={lang.value} value={lang.value}>
                  {lang.label}
                </option>
              ))}
            </select>
          </label>
          <p className="hint modal-hint">
            Saved on your account for Telugu / Hindi / English. Full UI translation comes later.
          </p>

          {error && <div className="error">{error}</div>}

          <div className="modal-actions">
            <button type="button" className="modal-cancel" onClick={onClose}>
              Cancel
            </button>
            <button type="submit" className="post-btn" disabled={busy || !displayName.trim()}>
              {busy ? "Saving..." : "Save"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
