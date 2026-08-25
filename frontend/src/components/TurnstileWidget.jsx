import { useEffect, useRef, useState } from "react";
import { API_BASE } from "../api";

const BUILD_SITE_KEY = (import.meta.env.VITE_TURNSTILE_SITE_KEY || "").trim();

let cachedConfig = null;
let configPromise = null;

async function loadTurnstileConfig() {
  if (cachedConfig) return cachedConfig;
  if (BUILD_SITE_KEY) {
    cachedConfig = { required: true, siteKey: BUILD_SITE_KEY };
    return cachedConfig;
  }
  if (!configPromise) {
    configPromise = fetch(`${API_BASE}/public/config`, {
      headers: { "X-BarathX-Client": "web" },
    })
      .then(async (res) => {
        const data = await res.json().catch(() => ({}));
        const siteKey = String(data.turnstile_site_key || "").trim();
        const required = Boolean(data.turnstile_required) && Boolean(siteKey);
        cachedConfig = { required, siteKey: required ? siteKey : "" };
        return cachedConfig;
      })
      .catch(() => {
        cachedConfig = { required: false, siteKey: "" };
        return cachedConfig;
      });
  }
  return configPromise;
}

/** Hook: whether email/Google need Turnstile, and the public site key. */
export function useTurnstileConfig() {
  const [state, setState] = useState(() =>
    BUILD_SITE_KEY
      ? { loading: false, required: true, siteKey: BUILD_SITE_KEY }
      : { loading: true, required: false, siteKey: "" }
  );

  useEffect(() => {
    let cancelled = false;
    loadTurnstileConfig().then((cfg) => {
      if (cancelled) return;
      setState({ loading: false, required: cfg.required, siteKey: cfg.siteKey });
    });
    return () => {
      cancelled = true;
    };
  }, []);

  return state;
}

/**
 * Cloudflare Turnstile — bot gate for email / Google signup.
 * Phone OTP does not use this (preferred human path).
 * Site key from Vite build env, or runtime GET /public/config (Railway).
 */
export default function TurnstileWidget({ onToken, onExpire, theme = "dark", siteKey: siteKeyProp }) {
  const { siteKey: runtimeKey, loading } = useTurnstileConfig();
  const siteKey = (siteKeyProp || runtimeKey || "").trim();
  const hostRef = useRef(null);
  const widgetId = useRef(null);
  const [ready, setReady] = useState(false);
  const [error, setError] = useState("");
  const cbRef = useRef({ onToken, onExpire });
  cbRef.current = { onToken, onExpire };

  useEffect(() => {
    if (!siteKey) return undefined;
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
        sitekey: siteKey,
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
  }, [theme, siteKey]);

  if (loading && !siteKey) {
    return (
      <div className="bx-turnstile">
        <p className="hint">Loading security check…</p>
      </div>
    );
  }

  if (!siteKey) return null;

  return (
    <div className="bx-turnstile">
      <div ref={hostRef} className="bx-turnstile-host" />
      {!ready && !error ? <p className="hint">Loading security check…</p> : null}
      {error ? <p className="error">{error}</p> : null}
      <p className="hint bx-turnstile-hint">Bot check for email / Google. Phone OTP skips this.</p>
    </div>
  );
}

/** Build-time only (may be false until /public/config loads). Prefer useTurnstileConfig(). */
export function turnstileConfigured() {
  return Boolean(BUILD_SITE_KEY);
}
