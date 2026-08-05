import { useEffect, useState } from "react";
import { api } from "../api";
import { useAuth } from "../context/AuthContext";

const USERNAME_RE = /^[a-zA-Z0-9_]{3,20}$/;

export default function EditProfileModal({ open, profile, onClose, onSaved }) {
  const { token, updateUser } = useAuth();
  const [displayName, setDisplayName] = useState("");
  const [username, setUsername] = useState("");
  const [bio, setBio] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!open || !profile) return;
    setDisplayName(profile.display_name || "");
    setUsername(profile.username || "");
    setBio(profile.bio || "");
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
    const nextUsername = username.trim().replace(/^@/, "").toLowerCase();
    if (!USERNAME_RE.test(nextUsername)) {
      setError("Username must be 3–20 characters: letters, numbers, underscore only");
      return;
    }
    setBusy(true);
    setError("");
    try {
      const updated = await api.updateMe(token, {
        display_name: displayName.trim(),
        username: nextUsername,
        bio,
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
            Username
            <div className="username-field">
              <span className="username-prefix" aria-hidden="true">
                @
              </span>
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value.replace(/\s/g, ""))}
                maxLength={20}
                autoComplete="username"
                required
              />
            </div>
          </label>
          <p className="hint modal-hint">
            3–20 characters. Letters, numbers, underscore. Your profile URL changes with this.
          </p>

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

          {error && <div className="error">{error}</div>}

          <div className="modal-actions">
            <button type="button" className="modal-cancel" onClick={onClose}>
              Cancel
            </button>
            <button
              type="submit"
              className="post-btn"
              disabled={busy || !displayName.trim() || !username.trim()}
            >
              {busy ? "Saving..." : "Save"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
