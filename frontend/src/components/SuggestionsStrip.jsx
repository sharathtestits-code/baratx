import { useEffect, useState } from "react";
import { suggestionsApi } from "../api";

/**
 * Top 15–20 problem/question suggestions for Square or an Arena.
 * Tapping fills compose — never auto-posts.
 * Layout (stack vs horizontal) is driven by plaza-layout CSS / className.
 */
export default function SuggestionsStrip({
  token,
  surface = "square",
  arenaKey = "",
  onPick,
  title = "Suggested takes",
  className = "",
}) {
  const [items, setItems] = useState([]);
  const [source, setSource] = useState("");
  const [open, setOpen] = useState(true);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      setLoading(true);
      try {
        const data = await suggestionsApi.list(token, {
          surface,
          arena: arenaKey || undefined,
          limit: 20,
        });
        if (cancelled) return;
        setItems(Array.isArray(data?.items) ? data.items : []);
        setSource(data?.source || "");
      } catch {
        if (!cancelled) setItems([]);
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    load();
    return () => {
      cancelled = true;
    };
  }, [token, surface, arenaKey]);

  if (!open) {
    return (
      <button
        type="button"
        className={`suggestions-reopen plaza-rail-questions ${className}`.trim()}
        onClick={() => setOpen(true)}
      >
        Show suggested takes
      </button>
    );
  }

  if (loading) {
    return (
      <p className={`hint suggestions-status plaza-rail-questions ${className}`.trim()}>
        Loading suggestions…
      </p>
    );
  }

  if (!items.length) return null;

  return (
    <section className={`suggestions-strip plaza-rail-questions ${className}`.trim()} aria-label={title}>
      <div className="suggestions-head">
        <div>
          <h2 className="suggestions-title">{title}</h2>
          <p className="suggestions-sub">
            Pick one to start — or write your own. {items.length} ready
            {source.startsWith("llm") ? " · ranked" : ""}.
          </p>
        </div>
        <button type="button" className="suggestions-hide" onClick={() => setOpen(false)}>
          Hide
        </button>
      </div>
      <ul className="suggestions-list">
        {items.map((item) => (
          <li key={item.id}>
            <button
              type="button"
              className="suggestions-chip"
              onClick={() => onPick?.(item.text)}
            >
              {item.text}
            </button>
          </li>
        ))}
      </ul>
    </section>
  );
}
