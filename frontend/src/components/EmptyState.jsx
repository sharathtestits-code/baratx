import { Link } from "react-router-dom";

/**
 * Never-dead empty state: title + hint + primary CTA (+ optional secondary).
 */
export default function EmptyState({
  title,
  hint,
  primaryTo,
  primaryLabel,
  onPrimary,
  secondaryTo,
  secondaryLabel,
  onSecondary,
  className = "",
}) {
  const primary =
    onPrimary || primaryTo ? (
      onPrimary ? (
        <button type="button" className="btn btn-primary empty-state-cta" onClick={onPrimary}>
          {primaryLabel}
        </button>
      ) : (
        <Link to={primaryTo} className="btn btn-primary empty-state-cta">
          {primaryLabel}
        </Link>
      )
    ) : null;

  const secondary =
    onSecondary || secondaryTo ? (
      onSecondary ? (
        <button type="button" className="btn btn-secondary empty-state-cta" onClick={onSecondary}>
          {secondaryLabel}
        </button>
      ) : (
        <Link to={secondaryTo} className="btn btn-secondary empty-state-cta">
          {secondaryLabel}
        </Link>
      )
    ) : null;

  return (
    <div className={`empty-state${className ? ` ${className}` : ""}`}>
      <p className="empty-state-title">{title}</p>
      {hint ? <p className="hint empty-state-hint">{hint}</p> : null}
      {(primary || secondary) && (
        <div className="empty-state-actions">
          {primary}
          {secondary}
        </div>
      )}
    </div>
  );
}
