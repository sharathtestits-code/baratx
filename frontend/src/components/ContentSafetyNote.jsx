import { Link } from "react-router-dom";

/** Soft reminder under compose / DM — adult content is blocked. */
export default function ContentSafetyNote({ compact = false }) {
  if (compact) {
    return (
      <p className="content-safety-note content-safety-note--compact">
        No adult or sexual content.{" "}
        <Link to="/guidelines">Guidelines</Link>
      </p>
    );
  }
  return (
    <aside className="content-safety-note" role="note">
      <strong>Safe square.</strong> Adult or sexual content is not allowed in posts,
      replies, or messages.{" "}
      <Link to="/guidelines">Community guidelines</Link>
    </aside>
  );
}
