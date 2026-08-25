import { useEffect, useRef, useState } from "react";

const SITE_KEY = (import.meta.env.VITE_TURNSTILE_SITE_KEY || "").trim();

/**
 * Cloudflare Turnstile — bot gate for email / Google signup.
 * Phone OTP does not use this (preferred human path).
 * Renders nothing when site key is unset.
 */
export default function TurnstileWidget({ onToken, onExpire, theme = "dark" }) {
  const hostRef = useRef(null);
  const widgetId = useRef(null);
  const [ready, setReady] = useState(false);
  const [error, setError] = useState("");
  const cbRef = useRef({ onToken, onExpire });
  cbRef.current = { onToken, onExpire };

  useEffect(() => {
    if (!SITE_KEY) return undefined;
    let cancelled = false;

    function render() {
      if (cancelled || !hostRef.current || !window.turnstile) return false;
      if (widgetId.current != null) {
        try {
          window.turnstile.remove(widgetId.current);
        } catch {
          /* ignore */
        }
        widgetId.current = null;
      }
      hostRef.current.innerHTML = "";
      widgetId.current = window.turnstile.render(hostRef.current, {
        sitekey: SITE_KEY,
        theme,
        appearance: "always",
        callback: (token) => {
          cbRef.current.onToken?.(token || "");
        },
        "expired-callback": () => {
          cbRef.current.onToken?.("");
          cbRef.current.onExpire?.();
        },
        "error-callback": () => {
          setError("Security check failed to load. Refresh and try again.");
          cbRef.current.onToken?.("");
        },
      });
      setReady(true);
      return true;
    }

    function ensureScript() {
      if (window.turnstile) {
        render();
        return;
      }
      const existing = document.querySelector('script[src*="challenges.cloudflare.com/turnstile"]');
      if (existing) {
        existing.addEventListener("load", () => render());
        const id = window.setInterval(() => {
          if (render()) window.clearInterval(id);
        }, 200);
        window.setTimeout(() => window.clearInterval(id), 10000);
        return;
      }
      const s = document.createElement("script");
      s.src = "https://challenges.cloudflare.com/turnstile/v0/api.js?render=explicit";
      s.async = true;
      s.defer = true;
      s.onload = () => render();
      document.head.appendChild(s);
    }

    ensureScript();
    return () => {
      cancelled = true;
      if (widgetId.current != null && window.turnstile) {
        try {
          window.turnstile.remove(widgetId.current);
        } catch {
          /* ignore */
        }
      }
    };
  }, [theme]);

  if (!SITE_KEY) return null;

  return (
    <div className="bx-turnstile">
      <div ref={hostRef} className="bx-turnstile-host" />
      {!ready && !error ? <p className="hint">Loading security check…</p> : null}
      {error ? <p className="error">{error}</p> : null}
      <p className="hint bx-turnstile-hint">Bot check for email / Google. Phone OTP skips this.</p>
    </div>
  );
}

export function turnstileConfigured() {
  return Boolean(SITE_KEY);
}
