import { forwardRef, useEffect, useImperativeHandle, useRef, useState } from "react";
import { searchApi } from "../api";
import { useAuth } from "../context/AuthContext";
import Avatar from "./Avatar";

/**
 * Textarea with @username suggestions. Typing @query searches people and inserts @handle.
 */
const MentionTextarea = forwardRef(function MentionTextarea(
  { value, onChange, maxLength, placeholder, rows = 3, id, className = "", disabled = false },
  ref
) {
  const { token } = useAuth();
  const localRef = useRef(null);
  const [suggestions, setSuggestions] = useState([]);
  const [mentionQuery, setMentionQuery] = useState(null); // { start, query }
  const [activeIndex, setActiveIndex] = useState(0);
  const [busy, setBusy] = useState(false);

  useImperativeHandle(ref, () => localRef.current);

  useEffect(() => {
    if (!mentionQuery || !mentionQuery.query) {
      setSuggestions([]);
      return;
    }
    let cancelled = false;
    const handle = window.setTimeout(async () => {
      setBusy(true);
      try {
        const data = await searchApi.search(mentionQuery.query, token);
        if (cancelled) return;
        setSuggestions((data?.users || []).slice(0, 6));
        setActiveIndex(0);
      } catch {
        if (!cancelled) setSuggestions([]);
      } finally {
        if (!cancelled) setBusy(false);
      }
    }, 180);
    return () => {
      cancelled = true;
      window.clearTimeout(handle);
    };
  }, [mentionQuery, token]);

  function detectMention(text, caret) {
    const before = text.slice(0, caret);
    const match = before.match(/(^|[\s([{"'])@([A-Za-z0-9._-]{0,20})$/);
    if (!match) return null;
    return { start: caret - match[2].length - 1, query: match[2] };
  }

  function handleChange(e) {
    const next = e.target.value;
    const caret = e.target.selectionStart ?? next.length;
    onChange(next);
    setMentionQuery(detectMention(next, caret));
  }

  function insertMention(user) {
    if (!mentionQuery || !localRef.current) return;
    const start = mentionQuery.start;
    const el = localRef.current;
    const caret = el.selectionStart ?? value.length;
    const inserted = `@${user.username} `;
    const next = `${value.slice(0, start)}${inserted}${value.slice(caret)}`;
    const clipped = maxLength != null ? next.slice(0, maxLength) : next;
    onChange(clipped);
    setMentionQuery(null);
    setSuggestions([]);
    requestAnimationFrame(() => {
      const pos = Math.min(start + inserted.length, clipped.length);
      el.focus();
      el.setSelectionRange(pos, pos);
    });
  }

  function handleKeyDown(e) {
    if (!mentionQuery || suggestions.length === 0) return;
    if (e.key === "ArrowDown") {
      e.preventDefault();
      setActiveIndex((i) => (i + 1) % suggestions.length);
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      setActiveIndex((i) => (i - 1 + suggestions.length) % suggestions.length);
    } else if (e.key === "Enter" || e.key === "Tab") {
      e.preventDefault();
      insertMention(suggestions[activeIndex]);
    } else if (e.key === "Escape") {
      setMentionQuery(null);
      setSuggestions([]);
    }
  }

  const showMenu = mentionQuery && (busy || suggestions.length > 0 || mentionQuery.query.length > 0);

  return (
    <div className={`mention-textarea-wrap ${className}`.trim()}>
      <textarea
        ref={localRef}
        id={id}
        placeholder={placeholder}
        value={value}
        onChange={handleChange}
        onKeyDown={handleKeyDown}
        maxLength={maxLength}
        rows={rows}
        disabled={disabled}
        aria-autocomplete="list"
        aria-expanded={!!showMenu}
      />
      {showMenu && (
        <ul className="mention-suggest" role="listbox" aria-label="People to tag">
          {busy && suggestions.length === 0 ? (
            <li className="mention-suggest-empty">Searching…</li>
          ) : suggestions.length === 0 ? (
            <li className="mention-suggest-empty">No people match “{mentionQuery.query}”</li>
          ) : (
            suggestions.map((u, i) => (
              <li key={u.id}>
                <button
                  type="button"
                  role="option"
                  aria-selected={i === activeIndex}
                  className={`mention-suggest-item${i === activeIndex ? " active" : ""}`}
                  onMouseDown={(e) => {
                    e.preventDefault();
                    insertMention(u);
                  }}
                >
                  <Avatar name={u.display_name} username={u.username} url={u.avatar_url} size={28} />
                  <span className="mention-suggest-meta">
                    <strong>{u.display_name}</strong>
                    <span>@{u.username}</span>
                  </span>
                </button>
              </li>
            ))
          )}
        </ul>
      )}
    </div>
  );
});

export default MentionTextarea;
