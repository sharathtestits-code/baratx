import { useId } from "react";

/**
 * BaratX logo system:
 * - mark: BX circle (favicon / compact nav)
 * - wordmark: BaratX with custom X
 * - full: mark + wordmark
 */
export function LogoMark({ className = "", title = "BaratX" }) {
  const uid = useId().replace(/:/g, "");
  const ringId = `bxRing-${uid}`;

  return (
    <svg
      className={`logo-mark ${className}`}
      viewBox="0 0 32 32"
      xmlns="http://www.w3.org/2000/svg"
      role="img"
      aria-hidden={title ? undefined : true}
      aria-label={title || undefined}
    >
      {title ? <title>{title}</title> : null}
      <defs>
        <linearGradient id={ringId} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#FF9933" />
          <stop offset="48%" stopColor="#FFFFFF" />
          <stop offset="100%" stopColor="#138808" />
        </linearGradient>
      </defs>
      <circle cx="16" cy="16" r="15.25" fill={`url(#${ringId})`} />
      <circle cx="16" cy="16" r="12.1" fill="#FF671F" />
      <text
        x="16"
        y="20.6"
        textAnchor="middle"
        fontFamily="system-ui, -apple-system, 'Segoe UI', sans-serif"
        fontWeight="800"
        fontSize="11.5"
        letterSpacing="-0.06em"
        fill="#FFFFFF"
      >
        BX
      </text>
      <circle cx="16" cy="16" r="12.1" fill="none" stroke="#000080" strokeWidth="0.55" opacity="0.35" />
    </svg>
  );
}

export function LogoWordmark({ className = "", title = "BaratX" }) {
  return (
    <span className={`logo-wordmark ${className}`} aria-label={title || undefined} aria-hidden={title ? undefined : true}>
      <span className="logo-wordmark-barat">Barat</span>
      <span className="logo-wordmark-x" aria-hidden="true">
        X
      </span>
    </span>
  );
}

export default function Logo({
  variant = "full",
  className = "",
  markClassName = "",
  wordmarkClassName = "",
  title = "BaratX",
}) {
  if (variant === "mark") {
    return <LogoMark className={`${className} ${markClassName}`.trim()} title={title} />;
  }

  if (variant === "wordmark") {
    return <LogoWordmark className={`${className} ${wordmarkClassName}`.trim()} title={title} />;
  }

  return (
    <span className={`logo-full ${className}`.trim()} aria-label={title}>
      <LogoMark className={markClassName} title="" />
      <LogoWordmark className={wordmarkClassName} title="" />
    </span>
  );
}
