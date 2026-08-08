import { useId } from "react";

/**
 * BharatX logo system:
 * - mark: BX circle (favicon / compact nav)
 * - wordmark: BharatX with custom X
 * - full: mark + wordmark
 *
 * Brand color only (saffron/warm ink) — no saffron–white–green flag ring.
 */
export function LogoMark({ className = "", title = "BharatX" }) {
  const uid = useId().replace(/:/g, "");
  const ringId = `bxRing-${uid}`;

  return (
    <svg
      className={`logo-mark ${className}`}
      viewBox="0 0 32 32"
      width="32"
      height="32"
      xmlns="http://www.w3.org/2000/svg"
      role="img"
      aria-hidden={title ? undefined : true}
      aria-label={title || undefined}
    >
      {title ? <title>{title}</title> : null}
      <defs>
        <linearGradient id={ringId} x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stopColor="#3D2314" />
          <stop offset="55%" stopColor="#C45A12" />
          <stop offset="100%" stopColor="#FF671F" />
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
    </svg>
  );
}

export function LogoWordmark({ className = "", title = "BharatX" }) {
  return (
    <span className={`logo-wordmark ${className}`} aria-label={title || undefined} aria-hidden={title ? undefined : true}>
      <span className="logo-wordmark-bharat">Bharat</span>
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
  title = "BharatX",
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
