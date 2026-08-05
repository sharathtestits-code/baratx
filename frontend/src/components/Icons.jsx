// Minimal hand-written line icons (no external icon package required).
// All accept className and are sized via CSS (width/height: 1em by default).

export function IconHeart({ filled = false, className = "" }) {
  return filled ? (
    <svg viewBox="0 0 24 24" className={`icon ${className}`} fill="currentColor">
      <path d="M12 21s-6.7-4.35-9.3-8.2C.6 9.9 1.4 6.4 4.4 5.1c2.1-.9 4.3-.1 5.6 1.7.5.7 1.4.7 1.9 0C13.3 5 15.5 4.2 17.6 5.1c3 1.3 3.8 4.8 1.7 7.7C18.7 16.65 12 21 12 21Z" />
    </svg>
  ) : (
    <svg viewBox="0 0 24 24" className={`icon ${className}`} fill="none" stroke="currentColor" strokeWidth="1.8">
      <path d="M12 21s-6.7-4.35-9.3-8.2C.6 9.9 1.4 6.4 4.4 5.1c2.1-.9 4.3-.1 5.6 1.7.5.7 1.4.7 1.9 0C13.3 5 15.5 4.2 17.6 5.1c3 1.3 3.8 4.8 1.7 7.7C18.7 16.65 12 21 12 21Z" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

export function IconReply({ className = "" }) {
  return (
    <svg viewBox="0 0 24 24" className={`icon ${className}`} fill="none" stroke="currentColor" strokeWidth="1.8">
      <path d="M21 12a7 7 0 0 1-7 7H8l-5 3 1-4.5A7 7 0 1 1 21 12Z" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

export function IconRepost({ className = "" }) {
  return (
    <svg viewBox="0 0 24 24" className={`icon ${className}`} fill="none" stroke="currentColor" strokeWidth="1.8">
      <path d="M6 4v9a3 3 0 0 0 3 3h9M18 20V11a3 3 0 0 0-3-3H6" strokeLinecap="round" strokeLinejoin="round" />
      <path d="M15 13l3 3 3-3M9 11 6 8 3 11" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

export function IconTrash({ className = "" }) {
  return (
    <svg viewBox="0 0 24 24" className={`icon ${className}`} fill="none" stroke="currentColor" strokeWidth="1.8">
      <path d="M4 7h16M9 7V4h6v3m-8 0 1 13a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1l1-13" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

export function IconSearch({ className = "" }) {
  return (
    <svg viewBox="0 0 24 24" className={`icon ${className}`} fill="none" stroke="currentColor" strokeWidth="1.8">
      <circle cx="11" cy="11" r="7" />
      <path d="m20 20-3.5-3.5" strokeLinecap="round" />
    </svg>
  );
}

export function IconHome({ className = "" }) {
  return (
    <svg viewBox="0 0 24 24" className={`icon ${className}`} fill="none" stroke="currentColor" strokeWidth="1.8">
      <path d="M4 11.5 12 4l8 7.5M6 10v9a1 1 0 0 0 1 1h4v-6h2v6h4a1 1 0 0 0 1-1v-9" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

export function IconUser({ className = "" }) {
  return (
    <svg viewBox="0 0 24 24" className={`icon ${className}`} fill="none" stroke="currentColor" strokeWidth="1.8">
      <circle cx="12" cy="8" r="4" />
      <path d="M4 20c0-3.5 3.5-6 8-6s8 2.5 8 6" strokeLinecap="round" />
    </svg>
  );
}

export function IconLogout({ className = "" }) {
  return (
    <svg viewBox="0 0 24 24" className={`icon ${className}`} fill="none" stroke="currentColor" strokeWidth="1.8">
      <path d="M9 21H5a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1h4M16 17l5-5-5-5M21 12H9" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

export function IconImage({ className = "" }) {
  return (
    <svg viewBox="0 0 24 24" className={`icon ${className}`} fill="none" stroke="currentColor" strokeWidth="1.8">
      <rect x="3" y="4" width="18" height="16" rx="2" />
      <circle cx="8.5" cy="9.5" r="1.5" />
      <path d="m21 16-5-5-9 9" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

export function IconClose({ className = "" }) {
  return (
    <svg viewBox="0 0 24 24" className={`icon ${className}`} fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M5 5l14 14M19 5 5 19" strokeLinecap="round" />
    </svg>
  );
}

export function IconCamera({ className = "" }) {
  return (
    <svg viewBox="0 0 24 24" className={`icon ${className}`} fill="none" stroke="currentColor" strokeWidth="1.8">
      <path d="M4 8h3l1.5-2h7L17 8h3a1 1 0 0 1 1 1v10a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V9a1 1 0 0 1 1-1Z" strokeLinecap="round" strokeLinejoin="round" />
      <circle cx="12" cy="13.5" r="3.5" />
    </svg>
  );
}

export function IconPhone({ className = "" }) {
  return (
    <svg viewBox="0 0 24 24" className={`icon ${className}`} fill="none" stroke="currentColor" strokeWidth="1.8">
      <path
        d="M8 3h3.5l1 4.5-2 1.5a12 12 0 0 0 5 5l1.5-2L21 12.5V16a2 2 0 0 1-2 2A14 14 0 0 1 5 6a2 2 0 0 1 2-2Z"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

export function IconMore({ className = "" }) {
  return (
    <svg viewBox="0 0 24 24" className={`icon ${className}`} fill="currentColor">
      <circle cx="5" cy="12" r="1.6" />
      <circle cx="12" cy="12" r="1.6" />
      <circle cx="19" cy="12" r="1.6" />
    </svg>
  );
}

export function IconBell({ className = "" }) {
  return (
    <svg viewBox="0 0 24 24" className={`icon ${className}`} fill="none" stroke="currentColor" strokeWidth="1.8">
      <path
        d="M6 9a6 6 0 0 1 12 0c0 7 3 7 3 7H3s3 0 3-7Z"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <path d="M10 19a2 2 0 0 0 4 0" strokeLinecap="round" />
    </svg>
  );
}
