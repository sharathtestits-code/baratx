import { useEffect } from "react";
import Avatar from "./Avatar";
import { mediaUrl } from "../api";

/**
 * Choose keep current vs upload new for profile or cover photo.
 */
export default function ProfilePhotoSheet({
  open,
  kind,
  profile,
  busy = false,
  onClose,
  onKeepCurrent,
  onChangePhoto,
  onRemove,
}) {
  const isAvatar = kind === "avatar";
  const currentUrl = isAvatar ? profile?.avatar_url : profile?.cover_url;
  const hasCurrent = Boolean(currentUrl);
  const title = isAvatar ? "Profile photo" : "Cover photo";

  useEffect(() => {
    if (!open) return;
    function onKey(e) {
      if (e.key === "Escape" && !busy) onClose();
    }
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, [open, busy, onClose]);

  if (!open || !profile) return null;

  return (
    <div className="modal-backdrop" onClick={busy ? undefined : onClose} role="presentation">
      <div
        className="modal-card profile-photo-sheet"
        role="dialog"
        aria-modal="true"
        aria-labelledby="profile-photo-sheet-title"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="modal-header">
          <h2 id="profile-photo-sheet-title">{title}</h2>
          <button
            type="button"
            className="modal-close"
            onClick={onClose}
            aria-label="Close"
            disabled={busy}
          >
            ×
          </button>
        </div>

        <div className="profile-photo-sheet-body">
          <div
            className={`profile-photo-sheet-preview${isAvatar ? " is-avatar" : " is-cover"}${
              hasCurrent ? " has-photo" : ""
            }`}
            style={
              !isAvatar && hasCurrent
                ? { backgroundImage: `url(${mediaUrl(currentUrl)})` }
                : undefined
            }
            aria-hidden="true"
          >
            {isAvatar ? (
              <Avatar
                name={profile.display_name}
                username={profile.username}
                url={profile.avatar_url}
                size={96}
              />
            ) : !hasCurrent ? (
              <span className="profile-photo-sheet-empty">No cover yet</span>
            ) : null}
          </div>

          <p className="profile-photo-sheet-hint">
            {hasCurrent
              ? "Keep the photo you already have, or pick a new one."
              : isAvatar
                ? "Add a profile photo so people recognize you."
                : "Add a cover photo for your profile."}
          </p>

          <div className="profile-photo-sheet-actions">
            {hasCurrent ? (
              <button
                type="button"
                className="btn btn-primary"
                onClick={onKeepCurrent}
                disabled={busy}
              >
                Use current photo
              </button>
            ) : null}
            <button
              type="button"
              className={hasCurrent ? "btn btn-secondary" : "btn btn-primary"}
              onClick={onChangePhoto}
              disabled={busy}
            >
              {busy ? "Uploading…" : hasCurrent ? "Change photo" : "Add photo"}
            </button>
            {hasCurrent && onRemove ? (
              <button
                type="button"
                className="btn btn-ghost profile-photo-sheet-remove"
                onClick={onRemove}
                disabled={busy}
              >
                Remove photo
              </button>
            ) : null}
          </div>
        </div>
      </div>
    </div>
  );
}
