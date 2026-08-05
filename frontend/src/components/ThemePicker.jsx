import { THEMES } from "../theme";

export default function ThemePicker({ value, onChange, compact = false }) {
  return (
    <div className={`theme-picker ${compact ? "theme-picker-compact" : ""}`} role="radiogroup" aria-label="Theme">
      {THEMES.map((theme) => {
        const selected = value === theme.id;
        return (
          <button
            key={theme.id}
            type="button"
            role="radio"
            aria-checked={selected}
            className={`theme-card ${selected ? "is-selected" : ""}`}
            onClick={() => onChange(theme.id)}
          >
            <span className="theme-swatch" aria-hidden="true">
              {theme.swatch.map((color) => (
                <span key={color} className="theme-swatch-chip" style={{ background: color }} />
              ))}
            </span>
            <span className="theme-card-text">
              <strong>{theme.name}</strong>
              {!compact && <span className="hint">{theme.blurb}</span>}
            </span>
          </button>
        );
      })}
    </div>
  );
}
