import { useEffect, useId, useRef, useState } from "react";
import { createPortal } from "react-dom";
import { useLocation, useNavigate } from "react-router-dom";
import { usePlazaMenu } from "../context/PlazaMenuContext";
import { useAuth } from "../context/AuthContext";
import { useLocale, useT } from "../context/LocaleContext";
import { notificationsApi } from "../api";
import { ARENA_TOPICS } from "../arenas";
import { IconLogout } from "./Icons";

/**
 * Change Arena drawer — arenas + Alerts + Settings + Log out (Appearance lives in Settings).
 * Brand title is always Latin BarathX (aligned with every other page).
 */
export default function PlazaSideMenu() {
  const { open, close } = usePlazaMenu();
  const { token, user, logout } = useAuth();
  const t = useT();
  const { locale } = useLocale();
  const location = useLocation();
  const navigate = useNavigate();
  const pathRef = useRef(location.pathname);
  const listId = useId();
  // Arena picker collapsed by default so site nav (Alerts, Settings, …) is usable.
  const [pickerOpen, setPickerOpen] = useState(false);
  const [unread, setUnread] = useState(0);
  const switchRef = useRef(null);

  useEffect(() => {
    if (pathRef.current !== location.pathname) {
      pathRef.current = location.pathname;
      close();
    }
  }, [location.pathname, close]);

  useEffect(() => {
    if (open) setPickerOpen(false);
  }, [open]);

  useEffect(() => {
    document.body.classList.toggle("plaza-menu-is-open", open);
    return () => document.body.classList.remove("plaza-menu-is-open");
  }, [open]);

  useEffect(() => {
    if (!token) {
      setUnread(0);
      return undefined;
    }
    let cancelled = false;
    async function refresh() {
      try {
        const data = await notificationsApi.unreadCount(token);
        if (!cancelled) setUnread(data.unread_count || 0);
      } catch {
        /* ignore */
      }
    }
    refresh();
    const onRead = () => setUnread(0);
    window.addEventListener("bx:notifications-read", onRead);
    const id = window.setInterval(refresh, 45000);
    return () => {
      cancelled = true;
      window.removeEventListener("bx:notifications-read", onRead);
      window.clearInterval(id);
    };
  }, [token, open]);

  useEffect(() => {
    if (!open) return undefined;
    function onKey(e) {
      if (e.key === "Escape") {
        if (pickerOpen) {
          setPickerOpen(false);
          return;
        }
        close();
      }
    }
    window.addEventListener("keydown", onKey);
    const prevOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => {
      window.removeEventListener("keydown", onKey);
      document.body.style.overflow = prevOverflow;
    };
  }, [open, close, pickerOpen]);

  function goArena(key) {
    setPickerOpen(false);
    close();
    navigate(`/arenas/${key}`);
  }

  function goMyArenas() {
    setPickerOpen(false);
    close();
    navigate("/arenas");
  }

  function goSettings() {
    close();
    navigate("/settings");
  }

  function goLink(path) {
    close();
    navigate(path);
  }

  function handleLogout() {
    close();
    logout();
    navigate("/");
  }

  if (typeof document === "undefined") return null;

  const activeKey = location.pathname.startsWith("/arenas/")
    ? location.pathname.split("/")[2]
    : "";

  const chevron = (
    <svg className="plaza-side-manage-chevron" viewBox="0 0 16 16" aria-hidden="true">
      <path
        d="M6 4l4 4-4 4"
        fill="none"
        stroke="currentColor"
        strokeWidth="1.75"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );

  return createPortal(
    <>
      <div
        className={`plaza-menu-backdrop${open ? " is-open" : ""}`}
        onClick={close}
        aria-hidden={!open}
      />
      <aside
        id="plaza-side-menu"
        className={`plaza-side-menu${open ? " is-open" : ""}`}
        aria-hidden={!open}
        aria-label={t("menu.aria")}
        onClick={(e) => e.stopPropagation()}
      >
        <div className="plaza-side-head">
          <button
            ref={switchRef}
            type="button"
            className={`plaza-side-arena-switch${pickerOpen ? " is-open" : ""}`}
            aria-expanded={pickerOpen}
            aria-controls={listId}
            onClick={() => setPickerOpen((v) => !v)}
          >
            <span className="plaza-side-arena-name">
              BarathX
              <svg
                className={`plaza-side-chevron${pickerOpen ? " is-open" : ""}`}
                viewBox="0 0 16 16"
                aria-hidden="true"
              >
                <path
                  d="M4 6l4 4 4-4"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="1.75"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </svg>
            </span>
            {locale.id !== "en" ? (
              <span className="plaza-side-brand-native" lang={locale.id}>
                {locale.brandNative}
              </span>
            ) : null}
            <span className="plaza-side-change">{t("menu.changeArena")}</span>
          </button>
          <button
            type="button"
            className="plaza-side-close"
            onClick={close}
            aria-label={t("nav.closeMenu")}
          >
            ×
          </button>
        </div>

        <nav
          id={listId}
          className={`plaza-side-arenas${pickerOpen ? " is-open" : ""}`}
          aria-label={t("nav.arenas")}
          hidden={!pickerOpen}
        >
          <ul className="plaza-side-arena-list">
            {ARENA_TOPICS.map((a) => {
              const isActive = activeKey === a.key;
              return (
                <li key={a.key}>
                  <button
                    type="button"
                    className={`plaza-side-arena${isActive ? " is-active" : ""}`}
                    style={{ "--arena-accent": a.accent }}
                    onClick={() => goArena(a.key)}
                  >
                    <span className="plaza-side-arena-bar" aria-hidden="true" />
                    <strong>{t(`arena.${a.key}`)}</strong>
                  </button>
                </li>
              );
            })}
          </ul>
        </nav>

        {!pickerOpen && <p className="plaza-side-picker-hint">{t("menu.pickerHint")}</p>}

        {/* Site links only when arena picker is closed — avoids overlapping layers. */}
        {!pickerOpen && (
          <div className="plaza-side-nav-links">
            <button type="button" className="plaza-side-manage" onClick={() => goLink("/notifications")}>
              <span className="plaza-side-manage-copy">
                <strong>
                  {t("menu.alerts")}
                  {unread > 0 ? (
                    <span className="plaza-side-unread" aria-label={`${unread} unread`}>
                      {unread > 9 ? "9+" : unread}
                    </span>
                  ) : null}
                </strong>
                <em>{t("menu.alertsSub")}</em>
              </span>
              {chevron}
            </button>

            <button type="button" className="plaza-side-manage" onClick={goMyArenas}>
              <span className="plaza-side-manage-copy">
                <strong>{t("menu.myArenas")}</strong>
                <em>{t("menu.myArenasSub")}</em>
              </span>
              {chevron}
            </button>

            <button type="button" className="plaza-side-manage" onClick={() => goLink("/communities")}>
              <span className="plaza-side-manage-copy">
                <strong>{t("menu.communities")}</strong>
                <em>{t("menu.communitiesSub")}</em>
              </span>
              {chevron}
            </button>

            <button type="button" className="plaza-side-manage" onClick={() => goLink("/rewards")}>
              <span className="plaza-side-manage-copy">
                <strong>{t("menu.founding")}</strong>
                <em>{t("menu.foundingSub")}</em>
              </span>
              {chevron}
            </button>

            <button type="button" className="plaza-side-manage plaza-side-settings" onClick={goSettings}>
              <span className="plaza-side-manage-copy">
                <strong>{t("menu.settings")}</strong>
                <em>{t("menu.settingsSub")}</em>
              </span>
              {chevron}
            </button>

            <button type="button" className="plaza-side-manage" onClick={() => goLink("/guidelines")}>
              <span className="plaza-side-manage-copy">
                <strong>{t("menu.guidelines")}</strong>
                <em>{t("menu.guidelinesSub")}</em>
              </span>
              {chevron}
            </button>

            {user ? (
              <button
                type="button"
                className="plaza-side-manage plaza-side-logout"
                onClick={handleLogout}
              >
                <span className="plaza-side-manage-copy">
                  <strong>
                    <IconLogout className="plaza-side-logout-icon" aria-hidden="true" />
                    {t("menu.logout")}
                  </strong>
                  <em>@{user.username}</em>
                </span>
              </button>
            ) : null}
          </div>
        )}
      </aside>
    </>,
    document.body
  );
}
