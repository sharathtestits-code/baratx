import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";

const STORAGE_KEY = "bx_plaza_menu_open_v2";
const PlazaMenuContext = createContext(null);

function desktopMenuPreferred() {
  try {
    return window.matchMedia("(min-width: 900px)").matches;
  } catch {
    return true;
  }
}

function readStoredOpen() {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored === "1") return true;
    if (stored === "0") return false;
  } catch {
    // ignore
  }
  // First visit: show the Change Arena rail on desktop (matches mockup).
  return desktopMenuPreferred();
}

export function PlazaMenuProvider({ children }) {
  const [open, setOpen] = useState(readStoredOpen);

  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, open ? "1" : "0");
    } catch {
      // ignore
    }
  }, [open]);

  const toggle = useCallback(() => {
    setOpen((v) => !v);
  }, []);

  const close = useCallback(() => {
    setOpen(false);
  }, []);

  const value = useMemo(
    () => ({ open, setOpen, toggle, close }),
    [open, toggle, close]
  );

  return <PlazaMenuContext.Provider value={value}>{children}</PlazaMenuContext.Provider>;
}

export function usePlazaMenu() {
  const ctx = useContext(PlazaMenuContext);
  if (!ctx) {
    return { open: false, setOpen: () => {}, toggle: () => {}, close: () => {} };
  }
  return ctx;
}
